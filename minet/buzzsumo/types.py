from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from casanova import TabularRecord


@dataclass
class BuzzsumoArticle(TabularRecord):
    buzzsumo_id: Optional[str]
    twitter_shares: Optional[int]
    facebook_shares: Optional[int]
    url: Optional[str]
    updated_at: Optional[datetime]
    facebook_likes: Optional[int]
    total_facebook_shares: Optional[int]
    title: Optional[str]
    published_date: Optional[datetime]
    pinterest_shares: Optional[int]
    og_url: Optional[str]
    article_amplifiers: Optional[str]
    domain_name: Optional[str]
    author_name: Optional[str]
    num_words: Optional[int]
    subdomain: Optional[str]
    twitter_user_id: Optional[str]
    video_length: Optional[int]
    language: Optional[str]
    alexa_rank: Optional[int]
    facebook_comments: Optional[int]
    num_linking_domains: Optional[int]
    youtube_views: Optional[int]
    wow_count: Optional[int]
    love_count: Optional[int]
    haha_count: Optional[int]
    sad_count: Optional[int]
    angry_count: Optional[int]
    youtube_likes: Optional[int]
    youtube_dislikes: Optional[int]
    youtube_comments: Optional[int]
    youtube_trending_score: Optional[str]
    tiktok_download_count: Optional[int]
    tiktok_play_count: Optional[int]
    tiktok_share_count: Optional[int]
    tiktok_comment_count: Optional[int]
    tiktok_digg_count: Optional[int]
    tiktok_author: Optional[str]
    tiktok_music_id: Optional[str]
    tiktok_music_author: Optional[str]
    tiktok_music_title: Optional[str]
    total_shares: Optional[int]
    thumbnail: Optional[str]
    total_reddit_engagements: Optional[int]
    evergreen_score: Optional[float]
    evergreen_score2: Optional[float]
    article_types: Optional[List[str]]
    author_image: Optional[str]
    ecommerce: Optional[str]
    is_general_article: bool
    is_how_to_article: bool
    is_infographic: bool
    is_interview: bool
    is_list: bool
    is_newsletter: bool
    is_podcast: bool
    is_presentation: bool
    is_press_release: bool
    is_review: bool
    is_video: bool
    is_what_post: bool
    is_why_post: bool

    @classmethod
    def from_payload(cls, payload: Dict) -> "BuzzsumoArticle":
        return cls(
            buzzsumo_id=payload.get("id"),
            twitter_shares=payload.get("twitter_shares"),
            facebook_shares=payload.get("facebook_shares"),
            url=payload.get("url"),
            updated_at=datetime.fromtimestamp(payload["updated_at"]) or None,
            facebook_likes=payload.get("facebook_likes"),
            total_facebook_shares=payload.get("total_facebook_shares"),
            title=payload.get("title"),
            published_date=datetime.fromtimestamp(payload["updated_at"]) or None,
            pinterest_shares=payload.get("pinterest_shares"),
            og_url=payload.get("og_url"),
            article_amplifiers=payload.get("article_amplifiers"),
            domain_name=payload.get("domain_name"),
            author_name=payload.get("author_name"),
            num_words=payload.get("num_words"),
            subdomain=payload.get("subdomain"),
            twitter_user_id=payload.get("twitter_user_id"),
            video_length=payload.get("video_length"),
            language=payload.get("language"),
            alexa_rank=payload.get("alexa_rank"),
            facebook_comments=payload.get("facebook_comments"),
            num_linking_domains=payload.get("num_linking_domains"),
            youtube_views=payload.get("youtube_views"),
            wow_count=payload.get("wow_count"),
            love_count=payload.get("love_count"),
            haha_count=payload.get("haha_count"),
            sad_count=payload.get("sad_count"),
            angry_count=payload.get("angry_count"),
            youtube_likes=payload.get("youtube_likes"),
            youtube_dislikes=payload.get("youtube_dislikes"),
            youtube_comments=payload.get("youtube_comments"),
            youtube_trending_score=payload.get("youtube_trending_score"),
            tiktok_download_count=payload.get("tiktok_download_count"),
            tiktok_play_count=payload.get("tiktok_play_count"),
            tiktok_share_count=payload.get("tiktok_share_count"),
            tiktok_comment_count=payload.get("tiktok_comment_count"),
            tiktok_digg_count=payload.get("tiktok_digg_count"),
            tiktok_author=payload.get("tiktok_author"),
            tiktok_music_id=payload.get("tiktok_music_id"),
            tiktok_music_author=payload.get("tiktok_music_author"),
            tiktok_music_title=payload.get("tiktok_music_title"),
            total_shares=payload.get("total_shares"),
            thumbnail=payload.get("thumbnail"),
            total_reddit_engagements=payload.get("total_reddit_engagements"),
            evergreen_score=payload.get("evergreen_score"),
            evergreen_score2=payload.get("evergreen_score2"),
            article_types=payload.get("article_types"),
            author_image=payload.get("author_image"),
            ecommerce=payload.get("ecommerce"),
            is_general_article=bool(payload.get("general_article")),
            is_how_to_article=bool(payload.get("how_to_article")),
            is_infographic=bool(payload.get("infographic")),
            is_interview=bool(payload.get("interview")),
            is_list=bool(payload.get("list")),
            is_newsletter=bool(payload.get("newsletter")),
            is_podcast=bool(payload.get("podcast")),
            is_presentation=bool(payload.get("presentation")),
            is_press_release=bool(payload.get("press_release")),
            is_review=bool(payload.get("review")),
            is_video=bool(payload.get("video")),
            is_what_post=bool(payload.get("what_post")),
            is_why_post=bool(payload.get("why_post")),
        )
