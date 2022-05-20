from minet import Crawler

crawler = Crawler("./ftest/crawlers/echojs_multiple.yml", throttle=2)

for result in crawler:
    print(result.job)
