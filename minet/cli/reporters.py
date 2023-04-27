from io import StringIO
from functools import partial
from ebbe import and_join

from minet.scrape.constants import BURROWING_KEYS, LEAF_KEYS
from minet.scrape.exceptions import (
    ScraperEvalSyntaxError,
    ScraperValidationConflictError,
    InvalidCSSSelectorError,
    ScraperValidationIrrelevantPluralModifierError,
    ScraperValidationMixedConcernError,
    ScraperValidationInvalidPluralModifierError,
    ScraperValidationInvalidExtractorError,
    ScraperValidationUnknownKeyError,
    ScraperEvalError,
)
from minet.cli.utils import colored


def report_scraper_validation_errors(errors):
    output = StringIO()

    p = partial(print, file=output)

    red_alert = colored("Error", "red")

    for n, error in enumerate(errors, 1):
        path = "." + (".".join(error.path))

        p(
            "> {error} n°{n} at path {path}{root}".format(
                error=red_alert,
                n=n,
                path=colored(path, "green"),
                root=(" (root)" if not error.path else ""),
            )
        )

        if isinstance(error, ScraperValidationConflictError):
            p(
                "  the {keys} keys are conflicting and should not be found at the same level!".format(
                    keys=and_join(error.keys)
                )
            )

        elif isinstance(error, ScraperValidationIrrelevantPluralModifierError):
            p(
                "  the {modifier} modifier should not be found at a non-plural level (i.e. without iterator)!".format(
                    modifier=colored(error.modifier, "green")
                )
            )

        elif isinstance(error, ScraperValidationInvalidPluralModifierError):
            p(
                "  the {modifier} modifier cannot be a boolean without {fields} and cannot be a key/path with {fields}!".format(
                    modifier=colored(error.modifier, "green"),
                    fields=colored("fields", "green"),
                )
            )

        elif isinstance(error, ScraperValidationInvalidExtractorError):
            p(
                "  unknown {extractor} extractor!".format(
                    extractor=colored(error.extractor, "green")
                )
            )

        elif isinstance(error, ScraperValidationMixedConcernError):
            p(
                "  mixed concerns could not be interpreted (i.e. the {burrowing} keys should not be found alongside the {leaf} ones)!".format(
                    burrowing=and_join(BURROWING_KEYS), leaf=and_join(LEAF_KEYS)
                )
            )

        elif isinstance(error, InvalidCSSSelectorError):
            p(
                "  invalid CSS selector {css}".format(
                    css=colored(error.expression, "cyan")
                )
            )

        elif isinstance(error, ScraperEvalSyntaxError):
            p("  invalid python code was found:")

            for line in error.expression.split("\n"):
                p(colored("    | {line}".format(line=line), "cyan"))

        elif isinstance(error, ScraperValidationUnknownKeyError):
            p("  unknown {key} key!".format(key=colored(error.key, "cyan")))

        p()

    return output.getvalue()


def report_scraper_evaluation_error(error):
    output = StringIO()

    p = partial(print, file=output)

    red_alert = colored("Scraper error", "red")

    path = "." + (".".join(error.path))

    p(
        "> {error} at path {path}{root}".format(
            error=red_alert,
            path=colored(path, "blue"),
            root=(" (root)" if not error.path else ""),
        )
    )

    if isinstance(error, ScraperEvalError):
        msg = str(error.reason)
        p(
            "  evaluated code raised {error}{msg}!".format(
                error=colored(error.reason.__class__.__name__, "green"),
                msg=(" with message: " + colored(msg, "magenta")) if msg else "",
            )
        )

        for line in error.expression.split("\n"):
            p(colored("    | {line}".format(line=line), "cyan"))

    p()

    return output.getvalue()


def report_filename_formatting_error(error):
    return "> error when formatting filename using: [cyan]{template}[/cyan]".format(
        template=error.template
    )
