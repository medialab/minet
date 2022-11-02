# =============================================================================
# Minet Telegram Constants
# =============================================================================
#
# General constants used throughout the Telegram functions.
#
from urllib3 import Timeout

TELEGRAM_URL = "https://t.me/"
TELEGRAM_DEFAULT_THROTTLE = 0.5
TELEGRAM_INFOS_CSV_HEADERS = [
    "title",
    "name",
    "link",
    "img",
    "description",
    "nb_subscribers",
    "nb_photos",
    "nb_videos",
    "nb_links",
]
TELEGRAM_MESSAGES_CSV_HEADERS = [
    "link_to_message",
    "user",
    "user_link",
    "user_img",
    "text",
    "nb_hashtags",
    "hashtags",
    "is_reply_img",
    "is_reply_user",
    "is_reply_text",
    "stickers",
    "nb_photos",
    "photos",
    "nb_videos",
    "video",
    "video_time",
    "nb_links",
    "links",
    "link_img",
    "link_site",
    "link_title",
    "link_description",
    "views",
    "datetime",
    "edited",
]
