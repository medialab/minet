from setuptools import setup, find_packages

with open('./README.md', 'r') as f:
    long_description = f.read()

setup(name='minet',
      version='0.6.0',
      description='A webmining CLI tool & library for python.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://github.com/medialab/minet',
      license='MIT',
      author='Jules Farjas, Guillaume Plique',
      keywords='webmining',
      python_requires='>=3',
      packages=find_packages(exclude=['ftest', 'test']),
      install_requires=[
        'beautifulsoup4>=4.7.1',
        'chardet>=3.0.4',
        'cython>=0.29.4',
        'lxml>=4.3.0',
        'numpy>=1.16.1',
        'pycookiecheat>=0.4.3',
        'quenouille>=0.3.0',
        'tqdm>=4.31.1',
        'ural>=0.7.0',
        'urllib3[secure]>=1.24.2',
        # 'dragnet>=2.0.3'
      ],
      entry_points={
        'console_scripts': ['minet=minet.cli.__main__:main']
      },
      zip_safe=True)
