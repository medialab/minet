from typing import List, Optional, Dict, Tuple, Iterable

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


# NOTE: we could better collect attachments, and we could get the reaction details
@dataclass
class FacebookComment(TabularRecord):
    id: str
    fbid: str
    depth: int
    parent_id: Optional[str]
    author: FacebookCommentAuthor
    created_time: int
    text: Optional[str]
    attachments: int
    reactions: int
    replies: int

    @classmethod
    def from_graphql_node(cls, node) -> "FacebookComment":
        feedback = node["feedback"]
        attachments = node.get("attachments", [])

        return cls(
            id=node["id"],
            fbid=node["legacy_fbid"],
            depth=node.get("depth", 0),
            parent_id=getpath(
                node,
                ("reply_parent_comment", "id"),
                getpath(node, ("comment_parent", "id")),
            ),
            author=FacebookCommentAuthor.from_graphql_node(node["author"]),
            created_time=node["created_time"],
            text=getpath(node, ("preferred_body", "text")),
            attachments=len(attachments),
            reactions=feedback["reactors"]["count"],
            replies=feedback.get("total_comment_count", 0),
        )

    @classmethod
    def from_payload(cls, payload) -> List["FacebookComment"]:
        comments = []

        # Top-level
        edges = getpath(payload, ("data", "node", "display_comments", "edges"))

        # Replies
        if edges is None:
            edges = getpath(payload, ("display_comments", "edges"))

        # Sub-replies
        if edges is None:
            edges = getpath(payload, ("data", "feedback", "display_comments", "edges"))

        # Tail call
        if not isinstance(edges, list):
            return comments

        for edge in edges:
            node = edge["node"]
            comments.append(cls.from_graphql_node(node))

            # Recursion
            feedback = node["feedback"]
            comments.extend(cls.from_payload(feedback))

        return comments

    @staticmethod
    def sort(comments: List["FacebookComment"]) -> List["FacebookComment"]:
        index: Dict[str, Tuple["FacebookComment", List["FacebookComment"]]] = {}

        for comment in sorted(comments, key=lambda c: c.depth):
            index[comment.id] = (comment, [])

            if comment.parent_id is not None:
                index[comment.parent_id][1].append(comment)

        sorted_comments: List["FacebookComment"] = []

        # NOTE: we sort in visual DFS order
        def walk(entries: Iterable[Tuple["FacebookComment", List["FacebookComment"]]]):
            for comment, replies in entries:
                sorted_comments.append(comment)

                walk((index[reply.id] for reply in replies))

        walk(filter(lambda entry: entry[0].depth == 0, index.values()))

        return sorted_comments
