from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

#Setup Chrome Installation with Selenium
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920, 1080")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
def login():
    driver.get("https://chat.openai.com")

if __name__ == "__main__":
    login()