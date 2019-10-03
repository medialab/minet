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


def extract(element, extractor_name):
    if extractor_name == 'text':
        return element.get_text()

    if extractor_name == 'html' or extractor_name == 'inner_html':
        return element.encode_contents()

    if extractor_name == 'outer_html':
        return str(element)


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


def apply_scraper(scraper, element, root=None, html=None):

    # Is this a tail call of item
    if isinstance(scraper, str):
        if scraper in EXTRACTOR_NAMES:
            return extract(element, scraper)

        return element.get(scraper)

    # First we need to solve local selection
    if 'sel' in scraper:
        element = element.select_one(scraper['sel'])
    elif 'sel_eval' in scraper:
        # TODO
        pass

    # Then we need to solve iterator
    single_value = True

    if 'iterator' in scraper:
        elements = element.select(scraper['iterator'])
        single_value = False
    elif 'iterator_eval' in scraper:
        # TODO
        single_value = False
        pass
    else:
        elements = [element]

    # Actual iteration
    acc = None if single_value else []

    for element in elements:

        # Do we have fields?
        if 'fields' in scraper:
            value = {}

            for k, field_scraper in scraper['fields'].items():
                value[k] = apply_scraper(
                    field_scraper,
                    element,
                    root=root,
                    html=html
                )

        # Do we have a scalar?
        elif 'item' in scraper:

            # Default value is text
            value = apply_scraper(
                scraper['item'],
                element,
                root=root,
                html=html
            )

        else:

            # Attribute
            if 'attr' in scraper:
                value = element.get(scraper['attr'])
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
                    context=None,
                    html=html,
                    root=root
                )

        if single_value:
            acc = value
        else:
            acc.append(value)

    return acc
