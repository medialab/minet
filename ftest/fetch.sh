rm -rf ftest/content
rm ftest/report.csv
python -m minet.cli fetch url ftest/resources/urls.csv \
  -d ftest/content \
  --total 10000 \
  --filename id \
  -o ftest/report.csv \
  -s id,url
