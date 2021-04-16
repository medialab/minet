# =============================================================================
# Minet Apply Scraper Function
# =============================================================================
#
# Function taking a scraper definition and applying its logic recursively
# to yield its result.
#
import textwrap
import soupsieve
from bs4 import Tag
from ebbe import getpath
from functools import partial

from minet.scrape.std import get_default_evaluation_context, get_display_text
from minet.scrape.constants import EXTRACTOR_NAMES
from minet.scrape.utils import get_sel, get_iterator
from minet.scrape.exceptions import (
    ScraperEvalError,
    ScraperEvalTypeError,
    ScraperEvalNoneError,
    NotATableError
)

DEFAULT_CONTEXT = {}
DATA_TYPES = (str, int, float, bool, list, dict)

nested_getter = partial(getpath, split_char='.', parse_indices=True, attributes=True)


def is_list_of_tags(value):
    if not isinstance(value, list):
        return False

    return all(isinstance(tag, Tag) for tag in value)


def is_valid_iterator_eval_output(value):
    return isinstance(value, str) or is_list_of_tags(value)


def merge_contexts(global_context, local_context):
    if global_context is None:
        return local_context

    for k, v in global_context.items():
        if k not in local_context:
            local_context[k] = v

    return local_context


def extract(element, extractor_name):
    if extractor_name == 'text':
        return element.get_text().strip()

    if extractor_name == 'display_text':
        return get_display_text(element)

    if extractor_name == 'html' or extractor_name == 'inner_html':
        return element.decode_contents().strip()

    if extractor_name == 'outer_html':
        return str(element).strip()

    raise TypeError('Unknown "%s" extractor' % extractor_name)


class EvaluationScope(object):
    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __getattr__(self, key):
        return self.__dict__.get(key)


EVAL_CONTEXT = get_default_evaluation_context()


# NOTE: this is not threadsafe, but it does not have to be
def eval_expression(expression, element=None, elements=None, value=None,
                    context=None, root=None, scope=None,
                    path=None, expect=None, check=None, allow_none=False):

    if callable(expression):
        try:
            result = expression(
                element=element,
                elements=elements,
                value=value,
                context=context,
                root=root
            )
        except Exception as e:
            raise ScraperEvalError(
                reason=e,
                path=path,
                expression=expression
            )
    else:

        # Local variables
        EVAL_CONTEXT['element'] = element
        EVAL_CONTEXT['elements'] = elements
        EVAL_CONTEXT['value'] = value

        # Context
        EVAL_CONTEXT['context'] = context
        EVAL_CONTEXT['root'] = root
        EVAL_CONTEXT['scope'] = scope

        if '\n' in expression:

            # Multiline expression
            scope = {}

            wrapped_expression = 'def __run__():\n%s\n__return_value__ = __run__()' % textwrap.indent(expression, '  ')

            try:
                exec(wrapped_expression, EVAL_CONTEXT, scope)
                result = scope['__return_value__']
            except Exception as e:
                raise ScraperEvalError(
                    reason=e,
                    path=path,
                    expression=expression
                )
        else:

            # Simple expression
            try:
                result = eval(expression, EVAL_CONTEXT, None)
            except Exception as e:
                raise ScraperEvalError(
                    reason=e,
                    path=path,
                    expression=expression
                )

    if not allow_none and result is None:
        raise ScraperEvalNoneError(
            path=path,
            expression=expression
        )

    if (expect is not None or check is not None) and result is not None:
        if not (check(result) if check else isinstance(result, expect)):
            raise ScraperEvalTypeError(
                path=path,
                expression=expression,
                expected=expect,
                got=result
            )

    return result


def tabulate(element, headers_inference='th', headers=None, path=None):
    if element.name != 'table':
        raise NotATableError(path=path)

    def generator():
        nonlocal headers

        body = element.find('tbody', recursive=False)
        head = element.find('thead', recursive=False)

        if body is None:
            body = element

        if head is None:
            head = element

        trs = body.select('tr:has(td)', recursive=False)
        ths = head.select('tr > th', recursive=False)

        if headers is None:
            if headers_inference == 'th':
                headers = [th.get_text() for th in ths]

        if headers is not None:
            for tr in trs:
                yield {headers[i]: td.get_text() for i, td in enumerate(tr.find_all('td', recursive=False))}
        else:
            for tr in trs:
                yield [td.get_text() for td in tr.find_all('td', recursive=False)]

    return generator()


def interpret_scraper(scraper, element, root=None, context=None, path=[], scope=None):
    if scope is None:
        scope = EvaluationScope()

    # Is this a tail call of item?
    if isinstance(scraper, str):
        if scraper in EXTRACTOR_NAMES:
            return extract(element, scraper)

        return element.get(scraper)

    sel = get_sel(scraper)
    iterator = get_iterator(scraper)

    # First we need to solve local selection
    if sel is not None:
        element = soupsieve.select_one(sel, element)
    elif 'sel_eval' in scraper:

        evaluated_sel = eval_expression(
            scraper['sel_eval'],
            element=element,
            elements=[],
            context=context,
            root=root,
            path=path + ['sel_eval'],
            expect=(Tag, str),
            allow_none=True,
            scope=scope
        )

        if isinstance(evaluated_sel, str):
            element = soupsieve.select_one(evaluated_sel, element)
        else:
            element = evaluated_sel

    if element is None:
        return None

    # Then we need to solve iterator
    single_value = True

    if iterator is not None:
        single_value = False
        elements = soupsieve.select(iterator, element)
    elif 'iterator_eval' in scraper:
        single_value = False
        evaluated_elements = eval_expression(
            scraper['iterator_eval'],
            element=element,
            elements=[],
            context=context,
            root=root,
            path=path + ['iterator_eval'],
            check=is_valid_iterator_eval_output,
            scope=scope
        )

        if isinstance(evaluated_elements, str):
            elements = soupsieve.select(evaluated_elements, element)
        else:
            elements = evaluated_elements
    else:
        elements = [element]

    # Handling local context
    if 'set_context' in scraper:
        local_context = {}

        for k, field_scraper in scraper['set_context'].items():
            local_context[k] = interpret_scraper(
                field_scraper,
                element,
                root=root,
                context=context,
                path=path + ['set_context', k],
                scope=scope
            )

        context = merge_contexts(context, local_context)

    # Actual iteration
    acc = None if single_value else []

    already_seen = set() if 'uniq' in scraper and not single_value else None

    for element in elements:
        value = None

        # Do we have fields?
        if 'fields' in scraper:
            value = {}

            for k, field_scraper in scraper['fields'].items():
                value[k] = interpret_scraper(
                    field_scraper,
                    element,
                    root=root,
                    context=context,
                    path=path + ['fields', k],
                    scope=scope
                )

        # Do we have a scalar?
        elif 'item' in scraper:

            # Default value is text
            value = interpret_scraper(
                scraper['item'],
                element,
                root=root,
                context=context,
                path=path + ['item'],
                scope=scope
            )

        else:

            if 'attr' in scraper:
                value = element.get(scraper['attr'])
            elif 'extract' in scraper:
                value = extract(element, scraper['extract'])
            elif 'get_context' in scraper:
                value = nested_getter(context, scraper['get_context'])
            elif 'default' not in scraper:

                # Default value is text
                value = extract(element, 'text')

            # Eval?
            if 'eval' in scraper:
                value = eval_expression(
                    scraper['eval'],
                    element=element,
                    elements=elements,
                    value=value,
                    context=context,
                    root=root,
                    path=path + ['eval'],
                    expect=DATA_TYPES,
                    allow_none=True,
                    scope=scope
                )

        # Default value after all?
        if 'default' in scraper and value is None:
            value = scraper['default']

        if single_value:
            acc = value
        else:

            # Filtering?
            if 'filter_eval' in scraper:
                passed_filter = eval_expression(
                    scraper['filter_eval'],
                    element=element,
                    elements=elements,
                    value=value,
                    context=context,
                    root=root,
                    path=path + ['filter_eval'],
                    expect=bool,
                    allow_none=True,
                    scope=scope
                )

                if not passed_filter:
                    continue

            if 'filter' in scraper:
                filtering_clause = scraper['filter']

                if filtering_clause is True and not value:
                    continue

                if isinstance(filtering_clause, str) and not nested_getter(value, filtering_clause):
                    continue

            if 'uniq' in scraper:
                uniq_clause = scraper['uniq']
                k = value

                if uniq_clause is True and value in already_seen:
                    continue

                if isinstance(uniq_clause, str):
                    k = nested_getter(value, uniq_clause)

                    if k in already_seen:
                        continue

                already_seen.add(k)

            acc.append(value)

    return acc
