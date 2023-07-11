# Taken from playwright.__main__ so it is possible to run the command line
# tool directly from a python execution
import sys
import subprocess

from playwright._impl._driver import compute_driver_executable, get_driver_env


def run_playwright(*args: str) -> int:
    env = get_driver_env()

    # NOTE: we do this to deal with pyinstaller
    if getattr(sys, "frozen", False):
        env.setdefault("PLAYWRIGHT_BROWSERS_PATH", "0")

    driver_executable = compute_driver_executable()
    completed_process = subprocess.run([str(driver_executable), *args], env=env)

    return completed_process.returncode
