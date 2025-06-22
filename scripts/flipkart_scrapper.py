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

class FlipkartScraper:
    def __init__(self,query,hardcore_search):
        self.query = query.lower()
        self.hardcore_search = hardcore_search      #For Getting More Products scrap more pages
        self.page = 1
        self.data = {'Title': [], 'Price': [], 'Rating': [], 'Available': [], 'Platform': [], 'Link': [],
                     'Image-Link': []}

        self._class_name = None
        self._titleCname = None
        self._linkCname = None
        self._priceCname = None
        self._ratingCname = None
        self._imageCname = None
        self._avlCname = None

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
            os.mkdir(f'{self.query}_Flipkart_Dataset')
        except FileExistsError:
            print("Directory already exists... \nData already Scrapped.")
            self.get_product_details()
            self.create_csv()
            sys.exit(0)
        except OSError as e:
            print('Error Creating the Directory: ',e)
            sys.exit(1)

    def get_dir_name(self):
        return f'{self.query}_Flipkart_Dataset'

    def set_class_names(self,cname,title,link,price,rating,image,avl):
        self._class_name = cname
        self._titleCname = title
        self._linkCname = link
        self._priceCname = price
        self._ratingCname = rating
        self._imageCname = image
        self._avlCname = avl


    def get_data(self):
        total_pages = None
        driver = self.get_driver()
        file_no = 1

        def get_url():
            return f'https://www.flipkart.com/search?q={self.query}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&page={self.page}'

        driver.get(get_url())

        wait = WebDriverWait(driver, 10)

        #For Getting the total pages
        try:
            header_text = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME,'BUOuZu'))
            ).text
            header_text = header_text.replace(',','').split(' ')
            product_in_page = int(header_text[3])
            total_product = int(header_text[5])
            total_pages = int(math.ceil(total_product/product_in_page))

            if (not self.hardcore_search and
                    ((product_in_page == 24 and total_product>=120) or (product_in_page==40 and total_product>=200))):
                total_pages = 5
            else:
                if total_pages >= 15:
                    total_pages = 15

        except Exception as e:
            print("Flipkart: ❌ Sub-header not found in headless mode:", e)
            with open("debug_headless.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            self.close_driver(driver)
            sys.exit(1)

        #Get the products when it is present
        def get_elements():
            nonlocal file_no
            nonlocal total_pages

            # To get 3 different types of classes that are present in flipkart so that list won't be empty
            temp1 = driver.find_elements(By.CLASS_NAME, 'slAVV4')
            self.set_class_names('slAVV4', 'wjcEIp', 'wjcEIp', 'Nx9bqj', 'XQDdHH', 'DByuf4', 'vfSpSs')
            if len(temp1) == 0:
                temp2 = driver.find_elements(By.CLASS_NAME, 'LFEi7Z')
                if len(temp2) == 0:
                    self.set_class_names('tUxRFH', 'KzDlHZ', 'CGtC98', 'Nx9bqj _4b5DiR', 'XQDdHH', 'DByuf4', 'vfSpSs')
                else:
                    self.set_class_names('LFEi7Z', 'WKTcLC', 'WKTcLC', 'Nx9bqj', '', '_53J4C-', 'vfSpSs')

            # Finding the elements and Storing the HTML File in Folder
            elems = driver.find_elements(By.CLASS_NAME, self._class_name)
            print(f'Flipkart: There are {len(elems)} items found in page-{self.page}.')
            for elem in elems:
                d = elem.get_attribute('innerHTML')
                with open(f'{self.get_dir_name()}/{self.query}_{file_no}.html', 'w', encoding='utf-8') as f:
                    f.write(d)
                    file_no += 1

        get_elements()

        for i in range(2,total_pages+1):
            self.page = i
            driver.get(get_url())
            get_elements()

        self.close_driver(driver)


    def get_product_details(self):
        for file in os.listdir(self.get_dir_name()):
            with open(f"{self.get_dir_name()}/{file}") as f:
                html_doc = f.read()
            soup = BeautifulSoup(html_doc, 'html.parser')

            #For Getting Title Element
            if self._titleCname == 'KzDlHZ':
                div = soup.find('div',attrs={'class': self._titleCname})
                title = div.get_text()
                self.data['Title'].append(title)
            else:
                a = soup.find('a', attrs={'class': self._titleCname})
                title = a.get_text()
                self.data['Title'].append(title)

            #For Getting Link Element
            l = soup.find('a', attrs={'class': self._linkCname})
            link = "https://flipkart.com" + l.get('href')
            self.data['Link'].append(link)

            #For Getting Image Link
            img = soup.find('img',attrs={'class': self._imageCname})
            img = img['src']
            self.data['Image-Link'].append(img)

            #For Getting Product Availability
            ots = soup.find('span',attrs={'class': self._avlCname})
            if ots:
                self.data['Available'].append('Out of Stock')
            else:
                self.data['Available'].append('Available')

            #For Getting Price Element
            p = soup.find('div', attrs={'class': self._priceCname})
            # For Getting Rating Element
            r = soup.find('div', attrs={'class': self._ratingCname})


            if p:
                price = p.get_text()[3:]
            else:
                price = 'N/A'
            if r:
                rating = r.get_text()
            else:
                rating = 'N/A'

            self.data['Price'].append(price)
            self.data['Rating'].append(rating)
            self.data['Platform'].append('Flipkart')

    def create_csv(self):
        df = pd.DataFrame(self.data)
        df.to_csv(f'CSV_Dataset/{self.query}_Flipkart.csv',mode='a',index=False)
        shutil.rmtree(self.get_dir_name())

class FlipkartProduct(FlipkartScraper):
    def __init__(self):
        pass

    def get_price(self, url):
        driver = self.get_driver()

        for attempt in range(5):  # retry 5 times
            try:
                driver.set_page_load_timeout(20)
                driver.get(url)
                time.sleep(2)  # let content fully load

                driver.execute_script("window.scrollTo(0, 500);")

                wait = WebDriverWait(driver, 10)

                # Try known Flipkart price locators
                price_tag = wait.until(EC.presence_of_element_located((
                    By.XPATH, "//div[@class='Nx9bqj CxhGGd']"
                )))

                price_text = price_tag.text
                # print(f"[DEBUG] Raw price text: {price_text}")

                # Extract numeric price from text like ₹12,499
                price_num = re.sub(r"[^\d]", "", price_text)
                return int(price_num)

            except Exception as e:
                print(f"[ERROR] Attempt {attempt + 1}: Failed to get price for {url} -> {e}")
                time.sleep(2)  # backoff before retry

        print(f"[FAILED] Could not retrieve price after retries for: {url}")
        return None


def run_scraper(query,hardcore):
    obj = FlipkartScraper(query,hardcore)
    obj.create_directory()
    obj.get_data()
    obj.get_product_details()
    obj.create_csv()




if __name__ == '__main__':

    search_text = input("Enter the Search Query you want to search for: ")

    run_scraper(search_text,False)