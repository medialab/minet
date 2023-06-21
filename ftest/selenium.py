from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chromium.service import ChromiumService
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType

driver_path = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
service = ChromiumService(executable_path=driver_path)
# service.start()
# print(service.service_url, service.port)

driver = webdriver.Chrome(service=service)
driver.get("https://echojs.com")

print(driver)

driver.quit()
# service.stop()
