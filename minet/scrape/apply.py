# =============================================================================
# Minet Apply Scraper Function
# =============================================================================
#
# Function taking a scraper definition and applying its logic recursively
# to yield its result.
#


def eval_expression():
    # TODO: useful to get needed deps
    pass


def apply_scraper(scraper, element):

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
                value[k] = apply_scraper(field_scraper, element)

        # Do we have a scalar?
        elif 'item' in scraper:

            # Default value is text
            value = apply_scraper(scraper['item'], element)

        else:

            # Default value is text
            value = element.get_text()

        if single_value:
            acc = value
        else:
            acc.append(value)

    return acc
