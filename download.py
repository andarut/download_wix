# 'Download' project
# Download site with all files, recursivly, with authorization

import os
import time
import re
from bs4 import BeautifulSoup

import os
import time
import inspect # for debug
import filecmp # for chunk diff

import selenium
from selenium.webdriver.remote.webelement import WebElement
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class Logger:

	class Colors:
		HEADER = '\033[95m'
		BLUE = '\033[94m'
		CYAN = '\033[96m'
		GREEN = '\033[92m'
		YELLOW = '\033[93m'
		RED = '\033[91m'
		END = '\033[0m'
		BOLD = '\033[1m'
		UNDERLINE = '\033[4m'

	def print(self, text, color):
		print("[" + inspect.stack()[2].function.capitalize() + "]: " + color + text + self.Colors.END)

	def log(self, log_text):
		self.print(log_text, self.Colors.CYAN)

	def error(self, error_text):
		self.print(error_text, self.Colors.RED)

	def warning(self, warning_text):
		self.print(warning_text, self.Colors.YELLOW)

	def ok(self, ok_text):
		self.print(ok_text, self.Colors.GREEN)

class Engine:

	ACTION_TIMEOUT = 5
	STARTUP_TIMEOUT = 5

	class Element:

		def __init__(self, name: str, xpath: str):
			self.name = name
			self.xpath = xpath
			self.selenium_element = WebElement(None, None)
			self.logger = Logger()

		def text(self, value_type=str):
			# TODO: rewrite
			if value_type == str:
				return self.selenium_element.text

			try:
				if value_type == int:
					return int(self.selenium_element.text)
			except TypeError:
				self.logger.error(f"{self.name} text is {self.selenium_element.text}, not {value_type}")
				exit(1)

		def click(self):
			self.selenium_element.click()

		def type(self, text: str, erase=False, enter=False):
			if erase:
				old_text = self.text()
				for _ in range(len(old_text)):
					self.selenium_element.send_keys(Keys.BACKSPACE)

			self.selenium_element.send_keys(text)

			if enter:
				self.selenium_element.send_keys(Keys.ENTER)

	def __init__(self, url:str, debug=False):
		self.url = url
		self.logger = Logger()
		self.options = webdriver.ChromeOptions()
		self.options.add_argument("--mute-audio")
		self.DEBUG = debug

	def start(self):
		self.driver = webdriver.Chrome(options=self.options)
		self.driver.get(self.url)
		time.sleep(self.STARTUP_TIMEOUT)
		# self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		body = self.driver.find_element(By.TAG_NAME, "body")
		for _ in range(100):
			body.send_keys(Keys.ARROW_DOWN)
		time.sleep(self.STARTUP_TIMEOUT)

	def find_element(self, name: str, xpath: str) -> Element:
		element = self.Element(name, xpath)

		try:
			element.selenium_element = self.driver.find_element(By.XPATH, element.xpath)
		except selenium.common.exceptions.NoSuchElementException:
			self.logger.error(f"{element.name} not found")
			exit(1)

		if self.DEBUG:
			self.logger.log(f"{element.name} found")

		return element

	def download(self, path):
		# get all urls (all resources)
		urls = []
		for request in self.driver.requests:
			urls.append(request.url)

		# save source code
		data = self.driver.page_source

		self.quit()


		# download all resources
		for url in urls:
			url_path = os.path.basename(url).split('?')[0]
			download_url = url
			if '[' in url:
				download_url = re.sub(r'\[.*?\]', '', url)
			if len(url_path) > 0:
				os.system(f'curl "{download_url}" -o "{url_path}"')
				data = data.replace(url, url_path)

		print(path)

		# set wix-ads-height to 0
		# data = data.replace("--wix-ads-height:50px", "--wix-ads-height:0px")

		with open(path, "w+") as f:
			f.write(data)

		# os.system(f"open {path}")


	def find_elements(self, name: str, class_name: str) -> [Element]:
		elements = []

		try:
			for el in self.driver.find_elements(By.CLASS_NAME, class_name):
				element = self.Element(name, "")
				element.selenium_element = el
				elements.append(element)
		except selenium.common.exceptions.NoSuchElementException:
			self.logger.error(f"{name} not found")
			exit(1)

		if self.DEBUG:
			self.logger.log(f"{name} found {len(elements)} times")

		return elements

	def click(self, element: Element):
		element.click()
		if self.DEBUG:
			self.logger.log(f"{element.name} clicked")
		time.sleep(self.ACTION_TIMEOUT)

	def type(self, element: Element, text: str, erase=False, enter=False):
		element.type(text, erase, enter)
		if self.DEBUG:
			self.logger.log(f"{element.name} typed {text} with erase={erase}, enter={enter}")
		time.sleep(self.ACTION_TIMEOUT)

	def quit(self):
		self.driver.quit()

def download(url, path=''):
	engine = Engine(url, True)
	engine.start()
	engine.download(path)


URL = "https://andreylzwl.wixsite.com/andreybestcoder"

download(URL, "index.html")

# TODO:
# set --wix-ads-height to 0
# remove WIX_ADS div


# <span class="aGHwBE"><span class="areOb6">This site was designed with the <div data-testid="bannerLogo" style="direction:ltr;display:inline-flex"><div><svg class="e5cW_9" viewBox="0 0 28 10.89" aria-label="wix"><path d="M16.02.2c-.55.3-.76.78-.76 2.14a2.17 2.17 0 0 1 .7-.42 3 3 0 0 0 .7-.4A1.62 1.62 0 0 0 17.22 0a3 3 0 0 0-1.18.2z" class="o4sLYL"></path><path d="M12.77.52a2.12 2.12 0 0 0-.58 1l-1.5 5.8-1.3-4.75a4.06 4.06 0 0 0-.7-1.55 2.08 2.08 0 0 0-2.9 0 4.06 4.06 0 0 0-.7 1.55L3.9 7.32l-1.5-5.8a2.12 2.12 0 0 0-.6-1A2.6 2.6 0 0 0 0 .02l2.9 10.83a3.53 3.53 0 0 0 1.42-.17c.62-.33.92-.57 1.3-2 .33-1.33 1.26-5.2 1.35-5.47a.5.5 0 0 1 .34-.4.5.5 0 0 1 .4.5c.1.3 1 4.2 1.4 5.5.4 1.5.7 1.7 1.3 2a3.53 3.53 0 0 0 1.4.2l2.8-11a2.6 2.6 0 0 0-1.82.53zm4.43 1.26a1.76 1.76 0 0 1-.58.5c-.26.16-.52.26-.8.4a.82.82 0 0 0-.57.82v7.36a2.47 2.47 0 0 0 1.2-.15c.6-.3.75-.6.75-2V1.8zm7.16 3.68L28 .06a3.22 3.22 0 0 0-2.3.42 8.67 8.67 0 0 0-1 1.24l-1.34 1.93a.3.3 0 0 1-.57 0l-1.4-1.93a8.67 8.67 0 0 0-1-1.24 3.22 3.22 0 0 0-2.3-.43l3.6 5.4-3.7 5.4a3.54 3.54 0 0 0 2.32-.48 7.22 7.22 0 0 0 1-1.16l1.33-1.9a.3.3 0 0 1 .57 0l1.37 2a8.2 8.2 0 0 0 1 1.2 3.47 3.47 0 0 0 2.33.5z"></path></svg></div><div class="uJDaUS">.com</div></div> website builder. Create your website today.</span><span class="O0tKs2 Oxzvyr">Start Now</span></span>

# <div id="WIX_ADS" class="WIX_ADS L27qsU c7bzh_"><a data-testid="linkElement" href="//www.wix.com/lpviral/enviral?utm_campaign=vir_wixad_live&amp;adsVersion=white&amp;orig_msid=c8f45476-9df7-4d1c-8f12-1c5fe2e49f01" target="_blank" rel="nofollow" class="Oxzvyr YD5pSO has-custom-focus"></a></div>
