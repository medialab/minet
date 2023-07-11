# =============================================================================
# Minet Scraper Analysis
# =============================================================================
#
# Functions performing analysis of scraper definitions.
#
from typing import Optional, List
from minet.types import Literal

import ast
import soupsieve
from soupsieve import SelectorSyntaxError

from minet.scrape.utils import get_sel, get_iterator
from minet.scrape.constants import (
    PLURAL_MODIFIERS,
    BURROWING_KEYS,
    LEAF_KEYS,
    EXTRACTOR_NAMES,
    KNOWN_KEYS,
)
from minet.scrape.exceptions import (
    ScraperEvalSyntaxError,
    ScraperValidationConflictError,
    InvalidCSSSelectorError,
    ScraperValidationIrrelevantPluralModifierError,
    ScraperValidationMixedConcernError,
    ScraperValidationInvalidPluralModifierError,
    ScraperValidationInvalidExtractorError,
    ScraperValidationUnknownKeyError,
)

ScraperAnalysisOutputType = Literal["scalar", "unknown", "collection", "dict", "list"]


class ScraperAnalysis(object):
    fieldnames: Optional[List[str]]
    plural: bool
    output_type: ScraperAnalysisOutputType

    __slots__ = ("fieldnames", "plural", "output_type")

    def __init__(
        self,
        fieldnames: Optional[List[str]] = None,
        plural: bool = False,
        output_type: ScraperAnalysisOutputType = "scalar",
    ):
        self.fieldnames = fieldnames
        self.plural = plural
        self.output_type = output_type

    def __eq__(self, other):
        return (
            self.plural == other.plural
            and self.output_type == other.output_type
            and (
                (self.fieldnames is None and other.fieldnames is None)
                or (set(self.fieldnames) == set(other.fieldnames))
            )
        )

    def __repr__(self):
        return "<{name} fieldnames={fieldnames!r} plural={plural} output_type={output_type}>".format(
            name=self.__class__.__name__,
            fieldnames=self.fieldnames,
            plural=self.plural,
            output_type=self.output_type,
        )


def fieldnames_from_definition(scraper):
    tabulate = scraper.get("tabulate")

    if tabulate is not None:
        if not isinstance(tabulate, dict):
            return None

        return tabulate.get("headers")

    fields = scraper.get("fields")

    if fields is None:
        return ["value"]
    else:
        for node in fields.values():
            if "fields" in node:
                return None

    return list(fields.keys())


def analyse(scraper):
    analysis = ScraperAnalysis()

    analysis.fieldnames = fieldnames_from_definition(scraper)

    iterator = get_iterator(scraper)

    if iterator is not None or "iterator_eval" in scraper:
        analysis.plural = True
        analysis.output_type = "list"

    if "fields" in scraper:
        if analysis.plural:
            analysis.output_type = "collection"
        else:
            analysis.output_type = "dict"

    elif "eval" in scraper:
        analysis.output_type = "unknown"

    return analysis


ERRORS_PRIORITY = {
    InvalidCSSSelectorError: 0,
    ScraperValidationUnknownKeyError: 1,
    ScraperEvalSyntaxError: 2,
    ScraperValidationConflictError: 3,
    ScraperValidationMixedConcernError: 4,
    ScraperValidationIrrelevantPluralModifierError: 5,
    ScraperValidationInvalidPluralModifierError: 6,
    ScraperValidationInvalidExtractorError: 7,
}


def errors_sorting_key(error):
    return (tuple(error.path), ERRORS_PRIORITY[type(error)])


def validate(scraper):
    errors = []

    def recurse(node, path=[]):
        # Checking conflicts
        c = []

        if "item" in node:
            c.append("item")
        if "fields" in node:
            c.append("fields")
        if "tabulate" in node:
            c.append("tabulate")

        if len(c) > 1:
            validation_error = ScraperValidationConflictError(path=path, keys=c)

            errors.append(validation_error)

        # Validating extractors
        if "extract" in node and node["extract"] not in EXTRACTOR_NAMES:
            errors.append(
                ScraperValidationInvalidExtractorError(
                    path=path, extractor=node["extract"]
                )
            )

        # Validating selectors
        # NOTE: this has the beneficial side effect of precompiling selectors
        k, sel = get_sel(node, with_key=True)

        if sel is not None:
            try:
                soupsieve.compile(sel)
            except (SelectorSyntaxError, NotImplementedError) as e:
                errors.append(
                    InvalidCSSSelectorError(path=path + [k], reason=e, expression=sel)
                )

        k, iterator = get_iterator(node, with_key=True)

        if iterator is not None:
            try:
                soupsieve.compile(iterator)
            except (SelectorSyntaxError, NotImplementedError) as e:
                errors.append(
                    InvalidCSSSelectorError(
                        path=path + [k], reason=e, expression=iterator
                    )
                )

        # Checking plural modifiers
        if iterator is None and "iterator_eval" not in node:
            for modifier in PLURAL_MODIFIERS:
                if modifier in node:
                    errors.append(
                        ScraperValidationIrrelevantPluralModifierError(
                            path=path, modifier=modifier
                        )
                    )

        for modifier in PLURAL_MODIFIERS:
            if modifier not in node or "_eval" in modifier:
                continue

            if isinstance(node[modifier], bool):
                if "fields" in node:
                    errors.append(
                        ScraperValidationInvalidPluralModifierError(
                            path=path, modifier=modifier
                        )
                    )
            else:
                if "fields" not in node:
                    errors.append(
                        ScraperValidationInvalidPluralModifierError(
                            path=path, modifier=modifier
                        )
                    )

        # Conflicting leaf keys
        conflicting_leaf_keys = []

        if "attr" in node:
            conflicting_leaf_keys.append("attr")
        if "extract" in node:
            conflicting_leaf_keys.append("extract")
        if "get_context" in node:
            conflicting_leaf_keys.append("get_context")

        if len(conflicting_leaf_keys) > 1:
            errors.append(
                ScraperValidationConflictError(path=path, keys=conflicting_leaf_keys)
            )

        # Conflicting burrowing/leaf
        if any(k in node for k in BURROWING_KEYS) and any(k in node for k in LEAF_KEYS):
            errors.append(ScraperValidationMixedConcernError(path=path))

        in_fields = path and path[-1] == "fields"

        for k, v in node.items():
            # Unknown keys
            if not in_fields and k not in KNOWN_KEYS:
                errors.append(ScraperValidationUnknownKeyError(path=path, key=k))
                continue

            p = path + [k]

            # Validating python syntax
            if k == "eval" or k.endswith("_eval"):
                if isinstance(v, str):
                    try:
                        ast.parse(v)
                    except SyntaxError as e:
                        validation_error = ScraperEvalSyntaxError(
                            reason=e, expression=v, path=p
                        )

                        errors.append(validation_error)
            else:
                k_eval = "%s_eval" % k

                if k_eval in node:
                    validation_error = ScraperValidationConflictError(
                        path=path, keys=[k, k_eval]
                    )

                    errors.append(validation_error)

            if isinstance(v, dict):
                recurse(v, p)

    recurse(scraper)

    return sorted(errors, key=errors_sorting_key)
