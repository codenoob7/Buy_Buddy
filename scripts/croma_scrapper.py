import shutil
import sys
import time
from bs4 import BeautifulSoup
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class CromaScrapper:
    def __init__(self,query):
        self.query = query.lower()
        self.data = {'Title':[],'Price':[],'Rating':[],'Available':[],'Platform':[],'Link':[],'Image-Link':[]}

    @staticmethod
    def get_driver():
        try:
            options = Options()

            # Use stable new headless mode
            options.add_argument("--headless=new")  # Use "new" headless mode

            # Proper viewport simulation
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--window-size=1920,1080")
            # options.add_argument("--disable-dev-shm-usage")

            # Block geolocation (works same)
            options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.geolocation": 2
            })

            driver = webdriver.Chrome(options=options)
            driver.set_window_size(1920, 1080)  # Just to be safe

            # Apply stealth to avoid bot detection
            stealth(driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True,
                    )

            return driver

        except Exception as e:
            print(e)
            sys.exit(1)

    @staticmethod
    def close_driver(d):
        time.sleep(2)
        d.close()

    # Creating the Folder to store the HTML Files
    def create_directory(self):
        try:
            os.mkdir(f'{self.query}_Croma_Dataset')
        except FileExistsError:
            print("Directory already exists... \nData already Scrapped.")
            self.get_product_details()
            self.create_csv()
            sys.exit(0)
        except OSError as e:
            print('Error Creating the Directory: ',e)
            sys.exit(1)

    def get_dir_name(self):
        return f'{self.query}_Croma_Dataset'

    def get_data_from_site(self):
        driver = self.get_driver()
        url = f'https://www.croma.com/searchB?q={self.query}%3Arelevance&text={self.query}'
        driver.get(url)

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "product-item"))
            )
        except:
            print("Croma: ❌ Products didn't load. Saving page for debugging...")
            with open("debug_headless.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            self.close_driver(driver)
            sys.exit(1)

        file_no = 1

        #Scroll Through Every Product
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            try:
                more_btn = driver.find_element(By.XPATH, "//button[@class='btn btn-secondary btn-viewmore']")
                driver.execute_script("arguments[0].click();", more_btn)
                time.sleep(2)
            except:
                pass

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        elems = driver.find_elements(By.CLASS_NAME,'product-item')
        print('Chroma: Total products found:', len(elems))
        for elem in elems:
            html_doc = elem.get_attribute('innerHTML')
            with open(f'{self.get_dir_name()}/{self.query}_Croma_{file_no}.html', 'w', encoding='utf-8') as f:
                f.write(html_doc)
                file_no += 1

        self.close_driver(driver)

    def get_product_details(self):
        for file in os.listdir(self.get_dir_name()):
            with open(f'{self.get_dir_name()}/{file}', 'r', encoding='utf-8') as f:
                html_doc = f.read()
            soup = BeautifulSoup(html_doc, 'html.parser')

            div = soup.find('h3', class_='product-title')
            title = div.text
            self.data['Title'].append(title)

            link = div.find('a').get('href')
            link = f'https://croma.com{link}'
            self.data['Link'].append(link)

            img = soup.find('img')
            img_link = img.get('data-src')
            self.data['Image-Link'].append(img_link)

            try:
                rating = soup.find('span', class_='rating-text').text
            except:
                rating = 'N/A'
            self.data['Rating'].append(rating)

            self.data['Platform'].append('Croma')

            ots = soup.find('span', class_='not-available-text')
            if ots:
                self.data['Available'].append('Out of Stock')
            else:
                self.data['Available'].append('Available')

            price_tag = soup.find('span', class_='plp-srp-new-amount')
            if price_tag:
                price = price_tag.text
                price = price[2:]
            else:
                price = 'Nan'
            self.data['Price'].append(price)

    def create_csv(self):
        df = pd.DataFrame(self.data)
        df.to_csv(f'CSV_Dataset/{self.query}_Croma.csv',mode='a',index=False)
        shutil.rmtree(self.get_dir_name())

class CromaProduct(CromaScrapper):
    def __init__(self):
        pass

    def get_price(self,url):
        driver = self.get_driver()
        driver.get(url)

        try:
            wait = WebDriverWait(driver, 10)
            price_tag = wait.until(
                EC.presence_of_element_located((By.XPATH, "//span[@id='pdp-product-price']"))
            )
            price = price_tag.get_attribute('value')

            return int(price)


        except Exception as e:
            print("Error Locating element: ", e)
            return None

def run_scraper(search_text):
    obj = CromaScrapper(search_text)
    obj.create_directory()
    obj.get_data_from_site()
    obj.get_product_details()
    obj.create_csv()


if __name__ == '__main__':
    query = input('Enter the query you want to search: ')
    run_scraper(query)