# Cleanup
rm -rf ftest/content
rm -f ftest/report.csv

# Fetching url from csv file
python -m minet.cli fetch url ftest/resources/urls.csv \
  -d ftest/content \
  --total 10000 \
  --filename id \
  -H 'X-Options: True' \
  -H 'X-Frame: nosniff;' \
  --grab-cookies firefox \
  -s id,url \
  -t 25 > ftest/report.csv
