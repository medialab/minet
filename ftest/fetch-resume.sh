# Fetching url from csv file
python -m minet.cli fetch url ftest/resources/urls.csv \
  -O ftest/content \
  --total 10000 \
  --filename id \
  --resume \
  --filename-template '{value[:4]}/{value}{ext}' \
  --grab-cookies firefox \
  --compress \
  -s id,url \
  -t 25 \
  -o ftest/report.csv
