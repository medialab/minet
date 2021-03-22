# =============================================================================
# Minet Scraper Analysis
# =============================================================================
#
# Functions performing analysis of scraper definitions.
#
import ast

from minet.scrape.exceptions import (
    ScrapeEvalSyntaxError,
    ScrapeValidationConflictError
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
            validation_error = ScrapeValidationConflictError(
                path=path,
                keys=c
            )

            errors.append(validation_error)

        for k, v in node.items():
            p = path + [k]

            # Validating python syntax
            if k == 'eval' or k.endswith('_eval'):
                try:
                    ast.parse(v)
                except SyntaxError as e:
                    validation_error = ScrapeEvalSyntaxError(
                        reason=e,
                        expression=v,
                        path=p
                    )

                    errors.append(validation_error)

            if isinstance(v, dict):
                recurse(v, p)

    recurse(scraper)

    return errors
