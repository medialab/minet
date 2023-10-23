import io
import zipfile
from os import makedirs, rmdir
from os.path import isdir, join
from shutil import move
from glob import iglob

from minet.web import request
from minet.exceptions import InvalidStatusError
from minet.browser.utils import get_browsers_path
from minet.loggers import downloaders_logger

AVAILABLE_EXTENSIONS = {
    "i-still-dont-care-about-cookies": {
        "url": "https://github.com/OhMyGuus/I-Still-Dont-Care-About-Cookies/releases/download/v1.1.1/ISDCAC-chrome-source.zip",
        "root": "./",
    },
    "ublock-origin": {
        "url": "https://github.com/gorhill/uBlock/releases/download/1.52.2/uBlock0_1.52.2.chromium.zip",
        "root": "./uBlock0.chromium",
    },
}


def ensure_extension_is_downloaded(name: str) -> bool:
    if name not in AVAILABLE_EXTENSIONS:
        raise TypeError("unknown extension %s" % name)

    extension_info = AVAILABLE_EXTENSIONS[name]

    browsers_dir = get_browsers_path()
    extensions_dir = join(browsers_dir, "extensions")
    extension_dir = join(extensions_dir, name)

    makedirs(extensions_dir, exist_ok=True)

    if isdir(extension_dir):
        return True

    downloaders_logger.info(
        "Downloading browser extension: %s" % name,
        extra={"namespace": "extension", "target": name},
    )
    response = request(extension_info["url"])

    if response.status != 200:
        raise InvalidStatusError(response.status)

    with zipfile.ZipFile(io.BytesIO(response.body)) as z:
        z.extractall(extension_dir)

    root = extension_info["root"]

    if root != "./":
        for p in iglob(join(extension_dir, root, "*")):
            move(p, extension_dir)

        rmdir(join(extension_dir, root))

    return False


def get_extension_path(name: str) -> str:
    if name not in AVAILABLE_EXTENSIONS:
        raise TypeError("unknown extension %s" % name)

    return join(get_browsers_path(), "extensions", name)


if __name__ == "__main__":
    print("Downloading missing extensions...\n")

    for name in AVAILABLE_EXTENSIONS:
        print("  -> %s" % name)
        already_downloaded = ensure_extension_is_downloaded(name)
        print("     Already ok." if already_downloaded else "     Acquired.")
        print()
