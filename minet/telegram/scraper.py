# =============================================================================
# Minet Telegram Scraper
# =============================================================================
#
# Functions to scrape Telegram.
#
from bs4 import BeautifulSoup
import re

from minet.rate_limiting import (
    rate_limited_method,
    RateLimiterState,
)
from minet.utils import clean_human_readable_numbers
from minet.web import (
    create_pool_manager,
    request,
    create_request_retryer,
    retrying_method,
)

from minet.telegram.constants import (
    TELEGRAM_URL,
    TELEGRAM_DEFAULT_THROTTLE,
)
from ural.telegram import (
    convert_telegram_url_to_public,
    parse_telegram_url,
    TelegramChannel as ParsedTelegramChannel,
    TelegramGroup as ParsedTelegramGroup,
    TelegramMessage as ParsedTelegramMessage,
)
from minet.telegram.formatters import TelegramChannelInfos, TelegramChannelMessages
from minet.telegram.exceptions import TelegramInvalidTargetError

TELEGRAM_IMG_RE = re.compile(r"background-image:url\(\'(.*?)\'\)")
TELEGRAM_HASHTAG_RE = re.compile(r"\?q=%23(.*)")


def forge_telegram_channel_url(name):
    url = TELEGRAM_URL + name + "/1"
    return url


def forge_telegram_channel_url_next(url, next_after):
    url = TELEGRAM_URL + next_after
    return url


def scrape_channel_infos(html):
    soup = BeautifulSoup(html, "lxml")

    channel_infos = soup.select_one("div[class='tgme_channel_info']")

    if not channel_infos:
        raise TelegramInvalidTargetError

    channel_header_infos = channel_infos.select_one(
        "div[class='tgme_channel_info_header']"
    )

    img = channel_header_infos.select_one("img").get("src")
    title = channel_header_infos.select_one("span").get_text()
    name = channel_header_infos.select_one(
        "div[class='tgme_channel_info_header_username']"
    ).get_text()
    link = (
        channel_header_infos.select_one(
            "div[class='tgme_channel_info_header_username']"
        )
        .select_one("a")
        .get("href")
    )

    channel_description = channel_infos.select_one(
        "div[class='tgme_channel_info_description']"
    )
    if channel_description:
        description = channel_description.get_text()

    # NOTE: the counter_type can be singular or plural, so we normalize
    counters_infos = {
        counter.select_one("span[class='counter_type']")
        .get_text()
        .rstrip("s"): counter.select_one("span[class='counter_value']")
        .get_text()
        for counter in channel_infos.select("div[class='tgme_channel_info_counter']")
    }

    nb_subscribers = counters_infos["subscriber"]
    nb_photos = counters_infos["photo"]
    nb_videos = counters_infos["video"]
    nb_links = counters_infos["link"]

    return TelegramChannelInfos(
        title=title,
        name=name,
        link=link,
        img=img,
        description=description,
        nb_subscribers=clean_human_readable_numbers(nb_subscribers),
        nb_photos=clean_human_readable_numbers(nb_photos),
        nb_videos=clean_human_readable_numbers(nb_videos),
        nb_links=clean_human_readable_numbers(nb_links),
    )


def scrape_channel_messages(html):
    results = []
    soup = BeautifulSoup(html, "lxml")

    messages_section = soup.select_one(
        "section[class='tgme_channel_history js-message_history']"
    )

    if not messages_section:
        raise TelegramInvalidTargetError

    next_after = messages_section.select_one("a[data-after]")
    if next_after:
        next_after = next_after.get("href")

    messages = messages_section.select(
        "div[class*='tgme_widget_message_wrap js-widget_message_wrap']"
    )
    for message in messages:
        if message.select_one(
            "div[class='tgme_widget_message text_not_supported_wrap service_message js-widget_message']"
        ):
            continue

        link_message = (
            TELEGRAM_URL
            + "s/"
            + (
                message.select_one(
                    "div[class*='tgme_widget_message text_not_supported_wrap']"
                ).get("data-post")
            )
        )

        user = message.select_one(
            "a[class='tgme_widget_message_owner_name']"
        ).get_text()
        user_link = (
            message.select_one("div[class='tgme_widget_message_user']")
            .select_one("a")
            .get("href")
        )
        user_img = (
            message.select_one("div[class='tgme_widget_message_user']")
            .select_one("img")
            .get("src")
        )

        links = []
        hashtags = []
        nb_links = 0
        nb_hashtags = 0
        text = ""
        texts = message.select("div[class*='tgme_widget_message_text js-message_text']")
        if texts:
            for text_html in texts:
                text += text_html.get_text()
                links_html = text_html.select("a")
                if links_html:
                    for link in links_html:
                        if TELEGRAM_HASHTAG_RE.match(link.get("href")):
                            hashtags.append(
                                TELEGRAM_HASHTAG_RE.match(link.get("href")).group(1)
                            )
                            nb_hashtags += 1
                        else:
                            links.append(link.get("href"))
                            nb_links += 1
        links = "|".join(links)
        hashtags = "|".join(hashtags)

        reply_img = None
        reply_user = None
        reply_text = None
        reply_html = message.select_one("a[class='tgme_widget_message_reply']")
        if reply_html:
            reply_img = reply_html.select_one(
                "i[class='tgme_widget_message_reply_thumb']"
            )
            if reply_img:
                reply_img = TELEGRAM_IMG_RE.search(reply_img.get("style")).group(1)
            reply_user = reply_html.select_one(
                "div[class='tgme_widget_message_author accent_color']"
            ).get_text()
            reply_text = reply_html.select_one(
                "div[class='tgme_widget_message_metatext js-message_reply_text']"
            )
            if reply_text:
                reply_text = reply_text.get_text()

        stickers = None
        stickers_html = message.select_one(
            "div[class='tgme_widget_message_sticker_wrap media_supported_cont']"
        )
        if stickers_html:
            stickers = stickers_html.select_one(
                "source[type='application/x-tgsticker']"
            )
            if stickers:
                stickers = stickers.get("srcset")
            else:
                stickers = stickers_html.select_one(
                    "i[class*='tgme_widget_message_sticker js-sticker_image']"
                )
                if stickers:
                    stickers = stickers.get("data-webp")

        nb_photos = 0
        photos = []
        photos_html = message.select(
            "a[class='tgme_widget_message_photo_wrap grouped_media_wrap blured js-message_photo']"
        )
        if photos_html:
            for photo in photos_html:
                photos.append(TELEGRAM_IMG_RE.search(photo.get("style")).group(1))
                nb_photos += 1
            photos = "|".join(photos)
        else:
            photos = message.select_one("a[class*='tgme_widget_message_photo_wrap']")
            if photos:
                photos = TELEGRAM_IMG_RE.search(photos.get("style")).group(1)
                nb_photos = 1

        nb_videos = 0
        videos_times = None
        videos = None
        video_html = message.select_one("a[class*='tgme_widget_message_video_player']")
        if video_html:
            video = video_html.select_one(
                "video[class='tgme_widget_message_video js-message_video']"
            )
            if video:
                videos = video.get("src")
            else:
                videos = "media is too big"
            video_time = video_html.select_one(
                "time[class='message_video_duration js-message_video_duration']"
            )
            if video_time:
                videos_times = video_time.get_text()
            nb_videos = 1

        link_img = None
        link_site = None
        link_title = None
        link_description = None
        link_html = message.select_one("a[class='tgme_widget_message_link_preview']")
        if link_html:
            link_img = link_html.select_one("i[class='link_preview_right_image']")
            if link_img:
                link_img = TELEGRAM_IMG_RE.search(link_img.get("style")).group(1)
            link_site = link_html.select_one(
                "div[class='link_preview_site_name accent_color']"
            )
            if link_site:
                link_site = link_site.get_text()
            link_title = link_html.select_one("div[class='link_preview_title']")
            if link_title:
                link_title = link_title.get_text()
            link_description = link_html.select_one(
                "div[class='link_preview_description']"
            )
            if link_description:
                link_description = link_description.get_text()

        views = message.select_one("span[class='tgme_widget_message_views']")
        could_be_displayed = bool(views)
        if views:
            views = views.get_text()
        datetime = (
            message.select_one("a[class='tgme_widget_message_date']")
            .select_one("time")
            .get("datetime")
        )
        edited_html = message.select_one(
            "span[class='tgme_widget_message_meta']"
        ).get_text()
        edited = "edited" in edited_html

        result = TelegramChannelMessages(
            link_to_message=link_message,
            could_be_displayed=could_be_displayed,
            user=user,
            user_link=user_link,
            user_img=user_img,
            text=text,
            nb_hashtags=nb_hashtags,
            hashtags=hashtags,
            is_reply_img=reply_img,
            is_reply_user=reply_user,
            is_reply_text=reply_text,
            stickers=stickers,
            nb_photos=nb_photos,
            photos=photos,
            nb_videos=nb_videos,
            videos=videos,
            videos_times=videos_times,
            nb_links=nb_links,
            links=links,
            link_img=link_img,
            link_site=link_site,
            link_title=link_title,
            link_description=link_description,
            views=clean_human_readable_numbers(views),
            datetime=datetime,
            edited=edited,
        )

        results.append(result)

    return next_after, results


class TelegramScraper(object):
    def __init__(self, throttle=TELEGRAM_DEFAULT_THROTTLE):
        self.pool_manager = create_pool_manager()

        self.rate_limiter_state = RateLimiterState(1, throttle)
        self.retryer = create_request_retryer()

    @rate_limited_method()
    @retrying_method()
    def request_page(self, url):
        response = request(url, pool_manager=self.pool_manager)

        return response.text()

    def channel_infos(self, name):
        parsed = parse_telegram_url(name)

        if isinstance(parsed, ParsedTelegramGroup):
            raise TelegramInvalidTargetError

        if isinstance(parsed, ParsedTelegramChannel) or isinstance(
            parsed, ParsedTelegramMessage
        ):
            name = parsed.name

        url = convert_telegram_url_to_public(forge_telegram_channel_url(name))

        html = self.request_page(url)

        return scrape_channel_infos(html)

    def channel_messages(self, name):
        parsed = parse_telegram_url(name)

        if isinstance(parsed, ParsedTelegramGroup):
            raise TelegramInvalidTargetError

        if isinstance(parsed, ParsedTelegramChannel) or isinstance(
            parsed, ParsedTelegramMessage
        ):
            name = parsed.name

        url = convert_telegram_url_to_public(forge_telegram_channel_url(name))

        def generator():
            current_url = url

            while True:
                html = self.request_page(current_url)

                next_after, messages = scrape_channel_messages(html)

                for message in messages:
                    yield message

                if next_after is None:
                    break

                current_url = forge_telegram_channel_url_next(url, next_after)

        return generator()
