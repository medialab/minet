# =============================================================================
# Minet Scraper Analysis
# =============================================================================
#
# Functions performing analysis of scraper definitions.
#
import ast

from minet.scrape.exceptions import (
    ScrapeEvalSyntaxError
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
        for k, v in node.items():
            p = path + [k]

            if k == 'eval' or k.endswith('_eval'):
                try:
                    ast.parse(v)
                except SyntaxError as e:
                    raise ScrapeEvalSyntaxError(
                        reason=e,
                        expression=v,
                        path=p
                    )

            if isinstance(v, dict):
                recurse(v, p)

    try:
        recurse(scraper)
    except ScrapeEvalSyntaxError as e:
        errors.append(
            (e.path, e)
        )

    return errors
