from typing import List, Any

from minet.crawl import CrawlResult, FocusCrawlInfo, FocusSpider

from minet.cli.crawl.crawl import crawl_action
from minet.cli.loading_bar import LoadingBar


def action(cli_args):
    additional_fieldnames = FocusCrawlInfo.CRAWL_RESULT_ADDENDUM_FIELDNAMES
    padding = [None] * len(additional_fieldnames)

    spider = FocusSpider(
        regex_content=cli_args.content_filter,
        invert_content_match=cli_args.invert_content_match,
        regex_url=cli_args.url_filter,
        invert_url_match=cli_args.invert_url_match,
        irrelevant_continue=cli_args.irrelevant_continue,
        only_html=cli_args.only_html,
        extract=cli_args.extract,
    )

    def format_job_row_addendum(result: CrawlResult[Any, FocusCrawlInfo]) -> List:
        info = result.data

        if not info:
            return padding

        return info.as_crawl_result_csv_addendum()

    def result_callback(
        cli_args, loading_bar: LoadingBar, result: CrawlResult[Any, FocusCrawlInfo]
    ):
        if result.data is not None and result.data.relevant:
            loading_bar.inc_stat("relevant", style="success")
        else:
            loading_bar.inc_stat("irrelevant", style="warning")

    return crawl_action(
        cli_args,
        target=spider,
        additional_job_fieldnames=additional_fieldnames,
        format_job_row_addendum=format_job_row_addendum,
        result_callback=result_callback,
    )
