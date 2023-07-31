from minet.scrape.soup import WonderfulSoup

html = "<div><p>wonderful</p></div>"
soup = WonderfulSoup(html)

p = soup.force_select_one("p")

print(p.get_display_text())
print(soup.get_display_text())
