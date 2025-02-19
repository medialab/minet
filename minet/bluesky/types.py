from typing import Optional, List

from dataclasses import dataclass
from casanova import TabularRecord

# TODO: embeds, mentions, tags, links, reply, quote


@dataclass
class BlueskyPost(TabularRecord):
    uri: str
    author_handle: str
    author_did: str
    author_display_name: Optional[str]
    created_at: str
    text: str
    reply_count: int
    repost_count: int
    like_count: int
    quote_count: int
    langs: List[str]

    @classmethod
    def from_payload(cls, payload) -> "BlueskyPost":
        author = payload["author"]
        record = payload["record"]

        return cls(
            uri=payload["uri"],
            author_handle=author["handle"],
            author_did=author["did"],
            author_display_name=author.get("displayName"),
            created_at=record["createdAt"],
            text=record["text"],
            reply_count=payload["replyCount"],
            repost_count=payload["repostCount"],
            like_count=payload["likeCount"],
            quote_count=payload["quoteCount"],
            langs=record.get("langs", []),
        )
