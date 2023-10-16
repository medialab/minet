# Taken from playwright.__main__ so it is possible to run the command line
# tool directly from a python execution
import subprocess
from os.path import expanduser

from playwright._impl._driver import compute_driver_executable, get_driver_env


def run_playwright(*args: str) -> int:
    env = get_driver_env()
    env.setdefault("PLAYWRIGHT_BROWSERS_PATH", expanduser("~/.minet-browsers"))

    driver_executable = compute_driver_executable()
    completed_process = subprocess.run([str(driver_executable), *args], env=env)

    return completed_process.returncode
