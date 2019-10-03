# =============================================================================
# Minet Apply Scraper Function
# =============================================================================
#
# Function taking a scraper definition and applying its logic recursively
# to yield its result.
#
import re

DEFAULT_CONTEXT = {}
EXTRACTOR_NAMES = set(['text', 'html', 'inner_html', 'outer_html'])

TRANSFORMERS = {
    'lower': lambda x: x.lower(),
    'strip': lambda x: x.strip(),
    'upper': lambda x: x.upper()
}


def merge_contexts(global_context, local_context):
    if global_context is None:
        return local_context

    for k, v in global_context.items():
        if k not in local_context:
            local_context[k] = v

    return local_context


def extract(element, extractor_name):
    if extractor_name == 'text':
        return element.get_text()

    if extractor_name == 'html' or extractor_name == 'inner_html':
        return element.encode_contents().decode()

    if extractor_name == 'outer_html':
        return str(element)

    raise TypeError('Unknown "%s" extractor' % extractor_name)


def eval_expression(expression, element=None, elements=None, value=None,
                    context=None, html=None, root=None):

    return eval(expression, None, {

        # Dependencies
        're': re,

        # Local values
        'element': element,
        'elements': elements,
        'value': value,

        # Context
        'context': context or DEFAULT_CONTEXT,
        'html': html,
        'root': root
    })


def apply_transform_chain(chain, value):
    if not isinstance(chain, list):
        chain = [chain]

    for transform in chain:
        fn = TRANSFORMERS.get(transform)

        if fn is None:
            raise TypeError('Unknown "%s" transformer' % transform)

        value = fn(value)

    return value


def apply_scraper(scraper, element, root=None, html=None, context=None):

    # Is this a tail call of item
    if isinstance(scraper, str):
        if scraper in EXTRACTOR_NAMES:
            return extract(element, scraper)

        return element.get(scraper)

    # First we need to solve local selection
    if 'sel' in scraper:
        element = element.select_one(scraper['sel'])
    elif 'sel_eval' in scraper:
        element = eval_expression(
            scraper['sel_eval'],
            element=element,
            elements=[],
            context=context,
            html=html,
            root=root
        )

    # Then we need to solve iterator
    single_value = True

    if 'iterator' in scraper:
        elements = element.select(scraper['iterator'])
        single_value = False
    elif 'iterator_eval' in scraper:
        elements = eval_expression(
            scraper['iterator_eval'],
            element=element,
            elements=[],
            context=context,
            html=html,
            root=root
        )
        single_value = False
    else:
        elements = [element]

    # Handling local context
    if 'context' in scraper:
        local_context = {}

        for k, field_scraper in scraper['context'].items():
            local_context[k] = apply_scraper(
                field_scraper,
                element,
                root=root,
                html=html,
                context=context
            )

        context = merge_contexts(context, local_context)

    # Actual iteration
    acc = None if single_value else []

    for element in elements:
        value = None

        # Do we have fields?
        if 'fields' in scraper:
            value = {}

            for k, field_scraper in scraper['fields'].items():
                value[k] = apply_scraper(
                    field_scraper,
                    element,
                    root=root,
                    html=html,
                    context=context
                )

        # Do we have a scalar?
        elif 'item' in scraper:

            # Default value is text
            value = apply_scraper(
                scraper['item'],
                element,
                root=root,
                html=html,
                context=context
            )

        else:

            try:
                if 'attr' in scraper:
                    value = element.get(scraper['attr'])
                elif 'extract' in scraper:
                    value = extract(element, scraper['extract'])
                elif 'get' in scraper:
                    value = context[scraper['get']]
                elif 'constant' in scraper:
                    value = scraper['constant']
                else:

                    # Default value is text
                    value = element.get_text()

                # Eval?
                if 'eval' in scraper:
                    value = eval_expression(
                        scraper['eval'],
                        element=element,
                        elements=elements,
                        value=value,
                        context=context,
                        html=html,
                        root=root
                    )
            except:
                value = None

        # Transform
        if 'transform' in scraper and value is not None:
            value = apply_transform_chain(scraper['transform'], value)

        # Default value?
        if 'default' in scraper and value is None:
            value = scraper['default']

        if single_value:
            acc = value
        else:
            acc.append(value)

    return acc
