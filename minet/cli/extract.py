# =============================================================================
# Minet Extract Content CLI Action
# =============================================================================
#
# Logic of the extract action.
#
import warnings
from os.path import join
from glob import iglob
from multiprocessing import Pool
from tqdm import tqdm
from dragnet import extract_content


def worker(path):

    # Reading file
    with open(path, 'r') as f:
        try:
            raw_html = f.read()
        except UnicodeDecodeError as e:
            return e, path, None

    # Attempting extraction
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            content = extract_content(raw_html)
    except BaseException as e:
        return e, path, None

    return None, path, content


def extract_action(namespace):

    files = iglob(join(namespace.directory, '*.html'))

    loading_bar = tqdm(
        desc='Extracting content',
        total=namespace.total,
        dynamic_ncols=True,
        unit=' doc'
    )

    with Pool(namespace.processes) as pool:
        for error, path, content in pool.imap_unordered(worker, files):
            loading_bar.update()

            if error is not None:
                continue

            # Writing file
            new_path = path[0:-5] + '.txt'

            with open(new_path, 'w') as f:
                f.write(content)
