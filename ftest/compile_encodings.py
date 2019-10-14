import csv

ENCODINGS = set()

with open('./ftest/resources/encodings.csv') as f:
    reader = csv.reader(f)
    next(reader)

    for line in reader:
        encodings = line[0]

        for e in encodings.split('|'):
            ENCODINGS.add(e.replace('-', '').replace('_', '').replace(' ', ''))

for e in sorted(ENCODINGS):
    print('"%s",' % e)
