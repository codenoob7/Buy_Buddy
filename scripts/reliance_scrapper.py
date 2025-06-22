import math
import shutil
import sys
import time
import os
import re
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class RelianceScrapper:
    def __init__(self,query):
        self.query = query.lower()
        self.page = 1
        self.data = {'Title': [], 'Price': [], 'Rating': [],'Available':[],'Platform':[], 'Link': [], 'Image-Link': []}

    @staticmethod
    def get_driver():
        try:
            options = Options()
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--no-sandbox")
            driver = webdriver.Chrome(options=options)
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
            os.mkdir(f'{self.query}_Reliance_Dataset')
        except FileExistsError:
            print("Directory already exists... \nData already Scrapped.")
            self.get_product_details()
            self.create_csv()
            sys.exit(0)
        except OSError as e:
            print('Error Creating the Directory: ', e)
            sys.exit(1)

    def get_dir_name(self):
        return f'{self.query}_Reliance_Dataset'

    def get_data_from_site(self):
        total_pages = None
        driver = self.get_driver()
        file_no = 1

        def get_url():
            return f'https://www.reliancedigital.in/products?q={self.query}&page_no={self.page}&page_size=12&page_type=number'

        driver.get(get_url())

        wait = WebDriverWait(driver, 15)

        #For Getting the total Pages
        try:
            header_tag = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME,'sub-header'))
            ).text
            digits = re.findall(r'\d+', header_tag)
            if digits:
                total_products = int(digits[0])
                total_pages = int(math.ceil(total_products / 12))
                print("Reliance: Total Pages -",total_pages)
        except Exception as e:
            print("Reliance: ❌ Sub-header not found in headless mode:", e)
            with open("debug_headless.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            self.close_driver(driver)
            sys.exit(1)

        #Get the products when it is present
        def get_elements():
            nonlocal file_no
            nonlocal total_pages

            if total_pages > 5:
                total_pages = 5
            try:
                wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'card-info-container'))
                )
                elems = driver.find_elements(By.CLASS_NAME,'card-info-container')
                print(f'Reliance: Total {len(elems)} Products found in Page-{self.page}')
                for elem in elems:
                    doc = elem.get_attribute('innerHTML')
                    with open(f'{self.get_dir_name()}/{self.query}_{file_no}.html', 'w', encoding='utf-8') as f:
                        f.write(doc)
                        file_no += 1
                time.sleep(1)

            except Exception as e:
                print(e)

        get_elements()

        #Scrap all the pages
        for i in range(2, total_pages + 1):
            self.page = i
            driver.get(get_url())
            get_elements()

        self.close_driver(driver)

    def get_product_details(self):
        for file in os.listdir(self.get_dir_name()):
            with open(f'{self.get_dir_name()}/{file}', 'r', encoding='utf-8') as f:
                html_doc = f.read()
            soup = BeautifulSoup(html_doc, 'html.parser')

            title = soup.find('div', class_='product-card-title').text
            self.data['Title'].append(title)

            a_tag = soup.find('a', class_='details-container').get('href')
            link = f'https://www.reliancedigital.in{a_tag}'
            self.data['Link'].append(link)

            img_link = soup.find('img', class_='fy__img').get('src')
            self.data['Image-Link'].append(img_link)

            price_str = soup.find('div', class_='price').text
            price_str = price_str[2:]
            price = int(float(price_str.replace(',', '')))
            self.data['Price'].append(price)

            ots = soup.find('div', class_='out-of-stock')
            if ots:
                self.data['Available'].append('Not Available')
            else:
                self.data['Available'].append('Available')

            self.data['Platform'].append('Reliance Digital')

            def get_rating():
                # Get the container with rating stars
                stars_ul = soup.select_one('ul.rating-star')

                if stars_ul:
                    star_items = stars_ul.find_all('li')

                    full_stars = 0
                    half_star = 0

                    for li in star_items:
                        svg_tag = li.find('svg')
                        if svg_tag and (svg_tag.find('path').get('fill') == '#F7AB20'):
                            full_stars += 1
                        elif li.find('img') and 'star-half' in li.find('img')['src']:
                            half_star = 0.5

                    rate = full_stars + half_star
                else:
                    rate = 'Nan'

                return rate

            rating = get_rating()
            self.data['Rating'].append(rating)


    def create_csv(self):
        df = pd.DataFrame(self.data)
        df.to_csv(f'CSV_Dataset/{self.query}_Reliance.csv',mode='a',index=False)
        shutil.rmtree(self.get_dir_name())

class RelianceProduct(RelianceScrapper):
    def __init__(self):
        pass

    def get_price(self,url):
        driver = self.get_driver()
        driver.get(url)

        try:
            wait = WebDriverWait(driver, 10)
            price_tag = wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='product-price']"))
            )
            price_text = price_tag.text.split('.')
            price = price_text[0]
            for letter in price:
                if not letter.isnumeric():
                    price = price.replace(letter, '')

            return int(price)


        except Exception as e:
            print("Error Locating element: ", e)
            return None

def run_scraper(search_query):
    obj = RelianceScrapper(search_query)
    obj.create_directory()
    obj.get_data_from_site()
    obj.get_product_details()
    obj.create_csv()


if __name__ == '__main__':
    query = input('Enter the product query: ')
    run_scraper(query)