from setuptools import setup, find_packages

with open('./README.md', 'r') as f:
    long_description = f.read()

# Version
# Info: https://packaging.python.org/guides/single-sourcing-package-version/
# Example: https://github.com/pypa/warehouse/blob/64ca42e42d5613c8339b3ec5e1cb7765c6b23083/warehouse/__about__.py
meta_package = {}
with open('./minet/__version__.py') as f:
    exec(f.read(), meta_package)


setup(name='minet',
      version=meta_package['__version__'],
      description='A webmining CLI tool & library for python.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://github.com/medialab/minet',
      license='MIT',
      author='Jules Farjas, Guillaume Plique, Pauline Breteau',
      keywords='webmining',
      python_requires='>=3.6',
      packages=find_packages(exclude=['ftest', 'scripts', 'test']),
      install_requires=[
        'beautifulsoup4>=4.7.1',
        'browser-cookie3==0.12.1',
        'casanova>=0.15.4,<0.16',
        'cchardet>=2.1.7',
        'colorama>=0.4.0',
        'dateparser>=1.0.0',
        'ebbe>=1.3.1,<2',
        'json5>=0.8.5',
        'keyring<19.3',
        'lxml>=4.3.0',
        'ndjson>=0.3.1',
        'persist-queue>=0.4.2',
        'pyyaml',
        'quenouille>=1.4.2,<2',
        'soupsieve>=2.1',
        'tenacity>=7.0.0',
        'termcolor>=1.0.0',
        'tqdm>=4.60.0',
        'trafilatura>=0.8.1,<0.9',
        'twitwi>=0.8.0,<0.9.0',
        'ural>=0.30.0,<0.31',
        'urllib3[secure]>=1.25.3,<2'
      ],
      entry_points={
        'console_scripts': ['minet=minet.cli.__main__:main']
      },
      zip_safe=True)
