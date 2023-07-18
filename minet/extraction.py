from typing import Optional, List, Dict, Any

from dataclasses import dataclass, field
from casanova import TabularRecord
from trafilatura.core import bare_extraction

from minet.exceptions import TrafilaturaError
from minet.encodings import fix_surrogates


def normalize_plural_trafilatura_item(meta: Dict[str, Any], key: str) -> List[str]:
    l = meta.get(key, []) or []

    items = []

    if not l:
        return items

    for item in l:
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

    @classmethod
    def from_bare_extraction(cls, data: Dict) -> "TrafilaturaResult":
        return TrafilaturaResult(
            canonical_url=data.get("url"),
            title=data.get("title"),
            description=data.get("description"),
            content=data.get("text"),
            comments=data.get("comments"),
            author=data.get("author"),
            categories=normalize_plural_trafilatura_item(data, "categories"),
            tags=normalize_plural_trafilatura_item(data, "tags"),
            date=data.get("date"),
            sitename=data.get("sitename"),
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
        trafilatura_bare_result = bare_extraction(text)
    except Exception as e:
        raise TrafilaturaError(reason=e)

    if trafilatura_bare_result is None:
        return

    return TrafilaturaResult.from_bare_extraction(trafilatura_bare_result)
