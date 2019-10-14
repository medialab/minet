URL=https://docs.python.org/3.4/library/codecs.html#standard-encodings

python -m minet.cli fetch $URL | \
python -m minet.cli scrape ftest/scrapers/encodings.yml > ftest/resources/encodings.csv
