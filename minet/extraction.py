from typing import Optional, List, cast

from dataclasses import dataclass, field
from casanova import TabularRecord
from trafilatura.settings import Document as TrafilaturaDocument
from trafilatura.core import bare_extraction

from minet.exceptions import TrafilaturaError
from minet.encodings import fix_surrogates


def normalize_plural_trafilatura_items(raw_items: Optional[List[str]]) -> List[str]:
    items = []

    if not raw_items:
        return items

    for item in raw_items:
        if isinstance(item, dict):
            item = item.get("name")

            if item is None:
                continue

        if isinstance(item, (int, float)):
            item = str(item)

        if not isinstance(item, str):
            continue

        for subitem in item.split(","):
            subitem = subitem.strip()

            if subitem:
                items.append(subitem)

    # NOTE: trafilatura metadata extraction seem to produce invalid utf-8
    # sometimes, so we fix it here. We might need to fix this elsewhere
    # at some point also.
    items = [fix_surrogates(item) for item in items]

    return items


@dataclass
class TrafilaturaResult(TabularRecord):
    _serializer_options = {"plural_separator": "§"}

    canonical_url: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    comments: Optional[str] = None
    author: Optional[str] = None
    categories: List[str] = field(default_factory=lambda: [])
    tags: List[str] = field(default_factory=lambda: [])
    date: Optional[str] = None
    sitename: Optional[str] = None
    image: Optional[str] = None
    pagetype: Optional[str] = None

    @classmethod
    def from_bare_extraction(cls, data: TrafilaturaDocument) -> "TrafilaturaResult":
        return TrafilaturaResult(
            canonical_url=data.url,
            title=data.title,
            description=data.description,
            content=data.text,
            comments=data.comments,
            author=data.author,
            categories=normalize_plural_trafilatura_items(data.categories),
            tags=normalize_plural_trafilatura_items(data.tags),
            date=data.date,
            sitename=data.sitename,
            image=data.image,
            pagetype=data.pagetype,
        )

    def blurb(self, fields=None) -> str:
        selection = fields if fields else self.fieldnames()
        items = []
        for s in selection:
            attr = getattr(self, s, "")
            if isinstance(attr, list):
                items.append(" ".join(attr))
            elif attr:
                items.append(attr)

        return "\n".join(items)


def extract(text: str) -> Optional[TrafilaturaResult]:
    # Attempting extraction
    try:
        # https://trafilatura.readthedocs.io/en/latest/corefunctions.html
        trafilatura_bare_result = bare_extraction(text, with_metadata=True)
    except Exception as e:
        raise TrafilaturaError(reason=e)

    if trafilatura_bare_result is None:
        return

    trafilatura_bare_result = cast(TrafilaturaDocument, trafilatura_bare_result)

    return TrafilaturaResult.from_bare_extraction(trafilatura_bare_result)
