# =============================================================================
# Minet Crawl CLI Action
# =============================================================================
#
# Logic of the crawl action.
#
import os
import csv
from os.path import join, isfile
from tqdm import tqdm
from shutil import rmtree

from minet.crawl import Crawler
from minet.utils import load_definition
from minet.cli.reporters import report_error
from minet.cli.utils import print_err

JOBS_HEADERS = [
    'spider',
    'url',
    'resolved',
    'status',
    'error',
    'filename',
    'encoding',
    'next',
    'level'
]


def format_job_for_csv(result):
    if result.error is not None:
        return [
            result.job.spider,
            result.job.url,
            '',
            '',
            report_error(result.error),
            '',
            '',
            '0',
            result.job.level
        ]

    resolved = result.response.geturl()

    return [
        result.job.spider,
        result.job.url,
        resolved if resolved != result.job.url else '',
        result.response.status,
        '',
        '',
        result.meta.get('encoding', ''),
        len(result.next_jobs) if result.next_jobs is not None else '0',
        result.job.level
    ]


def open_report(path, headers, resume=False):
    flag = 'w'

    if resume and isfile(path):
        flag = 'a'

    f = open(path, flag)
    writer = csv.writer(f)

    if flag == 'w':
        writer.writerow(headers)

    return f, writer


def crawl_action(namespace):

    if namespace.resume:
        print_err('Resuming crawl...')
    else:
        rmtree(namespace.output_dir)

    # Scaffolding output directory
    os.makedirs(namespace.output_dir, exist_ok=True)

    jobs_output_path = join(namespace.output_dir, 'jobs.csv')
    jobs_output, jobs_writer = open_report(
        jobs_output_path,
        JOBS_HEADERS,
        resume=namespace.resume
    )

    queue_path = join(namespace.output_dir, 'queue')

    # Loading crawler definition
    definition = load_definition(namespace.crawler)

    crawler = Crawler(
        definition,
        throttle=namespace.throttle,
        queue_path=queue_path
    )

    # Loading bar
    loading_bar = tqdm(
        desc='Crawling',
        unit=' pages',
        dynamic_ncols=True
    )

    def update_loading_bar():
        state = crawler.state

        loading_bar.set_postfix(queue=state.jobs_queued)
        loading_bar.update()

    # Starting crawler
    crawler.start()

    # Running crawler
    for result in crawler:
        update_loading_bar()
        jobs_writer.writerow(format_job_for_csv(result))

    loading_bar.close()
    jobs_output.close()
