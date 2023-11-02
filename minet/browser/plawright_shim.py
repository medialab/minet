# Taken from playwright.__main__ so it is possible to run the command line
# tool directly from a python execution
import subprocess
from glob import iglob
from os.path import join, isdir

from playwright._impl._driver import compute_driver_executable, get_driver_env

from minet.loggers import downloaders_logger
from minet.browser.utils import get_browsers_path


def run_playwright(*args: str) -> int:
    env = get_driver_env()
    env.setdefault("PLAYWRIGHT_BROWSERS_PATH", get_browsers_path())

    driver_executable = compute_driver_executable()
    completed_process = subprocess.run(
        [str(driver_executable), *args], env=env, stdout=subprocess.DEVNULL
    )

    return completed_process.returncode


def install_browser(name: str) -> None:
    path = join(get_browsers_path(), name + "-*")

    if any(isdir(p) for p in iglob(path)):
        return

    downloaders_logger.info(
        "Installing browser: %s (this can take a little while, hang tight)" % name,
        extra={"namespace": "browser", "target": name},
    )

    run_playwright("install", name)
