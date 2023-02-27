# Cleanup
rm -f ftest/resolved.csv

# Fetching url from csv file
python -m minet.cli resolve url -i ftest/resources/urls.csv \
  -s id,url \
  -t 25 > ftest/resolved.csv
