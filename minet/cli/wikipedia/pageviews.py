from minet.wikipedia import WikimediaRestAPIClient
from minet.cli.utils import with_enricher_and_loading_bar, with_ctrl_c_warning


def get_headers(cli_args):
    if cli_args.sum:
        return ["views"]

    return ["timestamp", "views"]


@with_enricher_and_loading_bar(
    headers=get_headers, title="Collecting pageviews", unit="pages"
)
@with_ctrl_c_warning
def action(cli_args, enricher, loading_bar):
    client = WikimediaRestAPIClient()

    lang_pos = (
        enricher.headers[cli_args.lang_column]
        if cli_args.lang_column is not None
        else None
    )

    page_pos = enricher.headers[cli_args.column]

    def key(row):
        if lang_pos is not None:
            lang = row[lang_pos]
        else:
            lang = cli_args.lang

        return (lang, row[page_pos])

    for row, pageviews in client.pageviews(
        enricher.rows(),
        key=key,
        start_date=cli_args.start_date,
        end_date=cli_args.end_date,
        granularity=cli_args.granularity,
        access=cli_args.access,
        agent=cli_args.agent,
        threads=cli_args.threads,
    ):
        with loading_bar.step():
            if cli_args.sum:
                s = 0

                for item in pageviews:
                    s += item.views

                enricher.writerow(row, [s])
                continue

            for item in pageviews:
                enricher.writerow(row, [item.timestamp, item.views])
