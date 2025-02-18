from dataclasses import dataclass
from casanova import TabularRecord


@dataclass
class BlueskyPost(TabularRecord):
    author_handle: str
    author_display_name: str
    text: str
    reply_count: int
    repost_count: int
    like_count: int
    quote_count: int

    @classmethod
    def from_payload(cls, payload) -> "BlueskyPost":
        author = payload["author"]
        record = payload["record"]

        return cls(
            author_handle=author["handle"],
            author_display_name=author["displayName"],
            text=record["text"],
            reply_count=payload["replyCount"],
            repost_count=payload["repostCount"],
            like_count=payload["likeCount"],
            quote_count=payload["quoteCount"],
        )
