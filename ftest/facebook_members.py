from tqdm import tqdm
import csv

from minet.facebook.members import FacebookMemberScraper

group_url = 'https://m.facebook.com/groups/StarAdventurer'
scraper = FacebookMemberScraper(cookie='chrome')

with open('./members.csv', 'w') as w:
    writer = csv.DictWriter(w, fieldnames=[
        'user_id',
        'user_handle',
        'user_url',
        'user_label',
        'admin',
        'formatted_joined',
        'joined'
    ])
    writer.writeheader()

    for member in tqdm(scraper(group_url)):
        writer.writerow(member)
