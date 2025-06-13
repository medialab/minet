from setuptools import setup, find_packages

with open("./README.md", "r") as f:
    long_description = f.read()

# Version
# Info: https://packaging.python.org/guides/single-sourcing-package-version/
# Example: https://github.com/pypa/warehouse/blob/64ca42e42d5613c8339b3ec5e1cb7765c6b23083/warehouse/__about__.py
meta_package = {}
with open("./minet/__version__.py") as f:
    exec(f.read(), meta_package)

packages = [pkg for pkg in find_packages() if pkg.startswith("minet")]

setup(
    name="minet",
    version=meta_package["__version__"],
    description="A webmining CLI tool & library for python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://github.com/medialab/minet",
    author="Guillaume Plique, Pauline Breteau, Jules Farjas, Héloïse Théro, Jean Descamps, Amélie Pellé, Laura Miguel, César Pichon, Kelly Christensen, Julien Pontoire, Béatrice Mazoyer",
    keywords="webmining",
    license="GPL-3.0",
    python_requires=">=3.8",
    packages=packages,
    install_requires=[
        "about-time>=4,<5",
        "beautifulsoup4>=4.7.1,<5",
        "browser-cookie3==0.19.1",
        "casanova>=2.0.1,<3",
        "charset-normalizer>=3,<4",
        "dateparser>=1.1.1",
        "ebbe>=1.14,<2",
        "json5>=0.8.5",
        "libipld>=3,<4",
        "lxml == 4.9.2; platform_system == 'Darwin' and python_version <= '3.8'",
        "lxml >= 5.3.0; platform_system != 'Darwin' or python_version > '3.8'",
        "nanoid>=2,<3",
        "playwright>=1.46,<1.47",
        "playwright_stealth>=1.0.6,<2",
        "pyyaml",
        "quenouille>=1.9.1,<2",
        "rich>=13,<14",
        "rich-argparse>=1,<2",
        "soupsieve>=2.1,<3",
        "tenacity>=8,<9",
        "trafilatura>=2,<2.1",
        "twitter==2.0a2",
        "twitwi>=0.21.1,<0.22",
        "ural>=1.5.0,<2",
        "urllib3>=1.26.16,<2",
        "websockets>=13,<14",
    ],
    extras_require={
        ":python_version<'3.11'": ["typing_extensions>=4.3"],
    },
    entry_points={"console_scripts": ["minet=minet.cli.__main__:main"]},
    zip_safe=True,
)
