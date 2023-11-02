from typing import List, Optional, Dict, Tuple

from dataclasses import dataclass
from casanova import TabularRecord
from ebbe import getpath


@dataclass
class FacebookCommentAuthor(TabularRecord):
    name: str
    short_name: str
    gender: str
    url: str
    is_verified: bool

    @classmethod
    def from_graphql_node(cls, node) -> "FacebookCommentAuthor":
        return cls(
            name=node["name"],
            short_name=node["short_name"],
            gender=node["gender"],
            url=node["url"],
            is_verified=node["is_verified"],
        )


@dataclass
class FacebookComment(TabularRecord):
    id: str
    fbid: str
    parent_id: Optional[str]
    author: FacebookCommentAuthor
    created_time: int
    text: str
    reactions: int
    replies: Optional[int]

    @classmethod
    def from_graphql_node(cls, node) -> "FacebookComment":
        feedback = node["feedback"]

        return cls(
            id=node["id"],
            fbid=node["legacy_fbid"],
            parent_id=getpath(node, ["comment_parent", "id"]),
            author=FacebookCommentAuthor.from_graphql_node(node["author"]),
            created_time=node["created_time"],
            text=node["preferred_body"]["text"],
            reactions=feedback["reactors"]["count"],
            replies=feedback.get("total_comment_count"),
        )

    @classmethod
    def from_payload(cls, payload) -> List["FacebookComment"]:
        comments = []

        for edge in payload["data"]["node"]["display_comments"]["edges"]:
            node = edge["node"]
            comments.append(cls.from_graphql_node(node))

            feedback = node["feedback"]

            if "display_comments" not in feedback:
                continue

            for sub_edge in feedback["display_comments"]["edges"]:
                comments.append(cls.from_graphql_node(sub_edge["node"]))

        return comments

    @staticmethod
    def sort(comments: List["FacebookComment"]) -> List["FacebookComment"]:
        index: Dict[str, Tuple["FacebookComment", List["FacebookComment"]]] = {}

        for comment in sorted(comments, key=lambda c: c.parent_id is not None):
            if comment.parent_id is None:
                index[comment.id] = (comment, [])
            else:
                index[comment.parent_id][1].append(comment)

        sorted_comments: List["FacebookComment"] = []

        for comment, replies in sorted(index.values(), key=lambda t: t[0].created_time):
            sorted_comments.append(comment)
            sorted_comments.extend(sorted(replies, key=lambda r: r.created_time))

        return sorted_comments
