# =============================================================================
# Minet Scraper Analysis
# =============================================================================
#
# Functions performing analysis of scraper definitions.
#
import ast
import soupsieve
from soupsieve import SelectorSyntaxError

from minet.scrape.utils import get_sel, get_iterator
from minet.scrape.exceptions import (
    ScraperEvalSyntaxError,
    ScraperValidationConflictError,
    InvalidCSSSelectorError
)


def headers_from_definition(scraper):
    tabulate = scraper.get('tabulate')

    if tabulate is not None:
        if not isinstance(tabulate, dict):
            return

        return tabulate.get('headers')

    fields = scraper.get('fields')

    if fields is None:
        return ['value']

    return list(scraper['fields'].keys())


def validate(scraper):

    errors = []

    def recurse(node, path=[]):

        # Checking conflicts
        c = []

        if 'item' in node:
            c.append('item')
        if 'fields' in node:
            c.append('fields')
        if 'tabulate' in node:
            c.append('tabulate')

        if len(c) > 1:
            validation_error = ScraperValidationConflictError(
                path=path,
                keys=c
            )

            errors.append(validation_error)

        # Validating selectors
        # NOTE: this has the beneficial side effect of precompiling selectors
        k, sel = get_sel(node, with_key=True)

        if sel is not None:
            try:
                soupsieve.compile(sel)
            except (SelectorSyntaxError, NotImplementedError) as e:
                errors.append(InvalidCSSSelectorError(path=path + [k], reason=e))

        k, iterator = get_iterator(node, with_key=True)

        if iterator is not None:
            try:
                soupsieve.compile(iterator)
            except (SelectorSyntaxError, NotImplementedError) as e:
                errors.append(InvalidCSSSelectorError(path=path + [k], reason=e))

        for k, v in node.items():
            p = path + [k]

            # Validating python syntax
            if k == 'eval' or k.endswith('_eval'):
                try:
                    ast.parse(v)
                except SyntaxError as e:
                    validation_error = ScraperEvalSyntaxError(
                        reason=e,
                        expression=v,
                        path=p
                    )

                    errors.append(validation_error)

            if isinstance(v, dict):
                recurse(v, p)

    recurse(scraper)

    return errors
