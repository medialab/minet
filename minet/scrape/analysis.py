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
    InvalidCSSSelectorError,
    ScraperValidationPluralModifierError
)


class ScraperAnalysis(object):
    __slots__ = ('headers', 'plural', 'output_type')

    def __init__(self, headers=None, plural=False, output_type='scalar'):
        self.headers = headers
        self.plural = plural
        self.output_type = output_type

    def __eq__(self, other):
        return (
            self.plural == other.plural and
            self.output_type == other.output_type and
            set(self.headers) == set(other.headers)
        )

    def __repr__(self):
        return '<{name} headers={headers!r} plural={plural} output_type={output_type}>'.format(
            name=self.__class__.__name__,
            headers=self.headers,
            plural=self.plural,
            output_type=self.output_type
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

    return list(fields.keys())


def analyse(scraper):
    analysis = ScraperAnalysis()

    analysis.headers = headers_from_definition(scraper)

    iterator = get_iterator(scraper)

    if iterator is not None or 'iterator_eval' in scraper:
        analysis.plural = True
        analysis.output_type = 'list'

    if 'fields' in scraper:
        if analysis.plural:
            analysis.output_type = 'collection'
        else:
            analysis.output_type = 'dict'

    elif 'eval' in scraper:
        analysis.output_type = 'unknown'

    return analysis


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

        # Checking plural modifiers
        if iterator is None and 'iterator_eval' not in node:
            if 'filter' in node or 'filter_eval' in node or 'uniq' in node:
                errors.append(ScraperValidationPluralModifierError(path=path))

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
