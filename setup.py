from setuptools import setup, find_packages

with open('./README.md', 'r') as f:
    long_description = f.read()

setup(name='minet',
      version='0.0.1',
      description='A webmining CLI tool & library for python.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://github.com/medialab/minet',
      license='MIT',
      author='Jules Farjas',
      keywords='webmining',
      python_requires='>=3',
      packages=find_packages(exclude=['test']),
      install_requires=[
          'ural==0.5.0',
          'urllib3==1.24.1',
          'bs4',
          'lxml==4.3.0',
          'numpy==1.16.1',
          'cython==0.29.4',
          'progress==1.4'
      ],
      entry_points={
          'console_scripts': ['minet=minet.cli.__main__:main']
      },
      zip_safe=True)
