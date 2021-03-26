# =============================================================================
# Minet Scraper Analysis
# =============================================================================
#
# Functions performing analysis of scraper definitions.
#
import ast
import soupsieve
from io import StringIO
from functools import partial
from soupsieve import SelectorSyntaxError
from termcolor import colored

from minet.scrape.utils import get_sel, get_iterator
from minet.scrape.constants import (
    PLURAL_MODIFIERS,
    BURROWING_KEYS,
    LEAF_KEYS
)
from minet.scrape.exceptions import (
    ScraperEvalSyntaxError,
    ScraperValidationConflictError,
    InvalidCSSSelectorError,
    ScraperValidationIrrelevantPluralModifierError,
    ScraperValidationMixedConcernError,
    ScraperValidationInvalidPluralModifierError
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
            return None

        return tabulate.get('headers')

    fields = scraper.get('fields')

    if fields is None:
        return ['value']
    else:
        for node in fields.values():
            if 'fields' in node:
                return None

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


ERRORS_PRIORITY = {
    InvalidCSSSelectorError: 0,
    ScraperEvalSyntaxError: 1,
    ScraperValidationConflictError: 2,
    ScraperValidationMixedConcernError: 3,
    ScraperValidationIrrelevantPluralModifierError: 4,
    ScraperValidationInvalidPluralModifierError: 5
}


def errors_sorting_key(error):
    return (tuple(error.path), ERRORS_PRIORITY[type(error)])


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
                errors.append(InvalidCSSSelectorError(path=path + [k], reason=e, expression=sel))

        k, iterator = get_iterator(node, with_key=True)

        if iterator is not None:
            try:
                soupsieve.compile(iterator)
            except (SelectorSyntaxError, NotImplementedError) as e:
                errors.append(InvalidCSSSelectorError(path=path + [k], reason=e, expression=iterator))

        # Checking plural modifiers
        if iterator is None and 'iterator_eval' not in node:
            for modifier in PLURAL_MODIFIERS:
                if modifier in node:
                    errors.append(ScraperValidationIrrelevantPluralModifierError(path=path, modifier=modifier))

        for modifier in PLURAL_MODIFIERS:
            if modifier not in node:
                continue

            if isinstance(node[modifier], bool):
                if 'fields' in node:
                    errors.append(ScraperValidationInvalidPluralModifierError(path=path, modifier=modifier))
            else:
                if 'fields' not in node:
                    errors.append(ScraperValidationInvalidPluralModifierError(path=path, modifier=modifier))

        # Conflicting leaf keys
        conflicting_leaf_keys = []

        if 'attr' in node:
            conflicting_leaf_keys.append('attr')
        if 'extract' in node:
            conflicting_leaf_keys.append('extract')
        if 'get_context' in node:
            conflicting_leaf_keys.append('get_context')

        if len(conflicting_leaf_keys) > 1:
            errors.append(ScraperValidationConflictError(path=path, keys=conflicting_leaf_keys))

        # Conflicting burrowing/leaf
        if any(k in node for k in BURROWING_KEYS) and any(k in node for k in LEAF_KEYS):
            errors.append(ScraperValidationMixedConcernError(path=path))

        for k, v in node.items():
            p = path + [k]

            # Validating python syntax
            if k == 'eval' or k.endswith('_eval'):
                if isinstance(v, str):
                    try:
                        ast.parse(v)
                    except SyntaxError as e:
                        validation_error = ScraperEvalSyntaxError(
                            reason=e,
                            expression=v,
                            path=p
                        )

                        errors.append(validation_error)
            else:
                k_eval = '%s_eval' % k

                if k_eval in node:
                    validation_error = ScraperValidationConflictError(
                        path=path,
                        keys=[k, k_eval]
                    )

                    errors.append(validation_error)

            if isinstance(v, dict):
                recurse(v, p)

    recurse(scraper)

    return sorted(errors, key=errors_sorting_key)


def and_join(strings):
    strings = [colored(s, 'green') for s in strings]

    if len(strings) < 2:
        return strings[0]

    return (', '.join(strings[:-1])) + ' and ' + strings[-1]


def report_validation_errors(errors):
    output = StringIO()

    p = partial(print, file=output)

    red_alert = colored('Error', 'red')

    for n, error in enumerate(errors, 1):
        path = '.' + ('.'.join(error.path))

        p('> {error} n°{n} at path {path}{root}'.format(error=red_alert, n=n, path=colored(path, 'blue'), root=(' (root)' if not error.path else '')))

        if isinstance(error, ScraperValidationConflictError):
            p('  the {keys} keys are conflicting and should not be found at the same level!'.format(keys=and_join(error.keys)))

        if isinstance(error, ScraperValidationIrrelevantPluralModifierError):
            p('  the {modifier} modifier should not be found at a non-plural level (i.e. without iterator)!'.format(modifier=colored(error.modifier, 'green')))

        if isinstance(error, ScraperValidationInvalidPluralModifierError):
            p('  the {modifier} modifier cannot be a boolean without {fields} and cannot be a key/path with {fields}!'.format(modifier=colored(error.modifier, 'green'), fields=colored('fields', 'green')))

        if isinstance(error, ScraperValidationMixedConcernError):
            p('  mixed concerns could not be interpreted (i.e. the {burrowing} keys should not be found alongside the {leaf} ones)!'.format(burrowing=and_join(BURROWING_KEYS), leaf=and_join(LEAF_KEYS)))

        if isinstance(error, InvalidCSSSelectorError):
            p('  invalid CSS selector {css}'.format(css=colored(error.expression, 'cyan')))

        if isinstance(error, ScraperEvalSyntaxError):
            p('  invalid python code was found:')

            for line in error.expression.split('\n'):
                p(colored('    | {line}'.format(line=line), 'cyan'))

        p()

    return output.getvalue()
