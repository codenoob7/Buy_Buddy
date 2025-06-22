import os
import re
import shutil
import sys
import time
import random
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class VijaySalesScrapper:
    def __init__(self,query):
        self.query = query.lower()
        self.data = {'Title':[],'Price':[],'Rating':[],'Available':[],'Platform':[],'Link':[],'Image-Link':[]}

    @staticmethod
    def get_driver():
        try:
            options = Options()
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--no-sandbox")
            # Block geolocation (works same)
            options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.geolocation": 2
            })
            options.add_experimental_option("prefs",{
                "profile.default_content_setting_values.notifications": 2
            })

            driver = webdriver.Chrome(options=options)
            driver.set_window_size(1920, 1080)  # Just to be safe

            # # Apply stealth to avoid bot detection
            # stealth(driver,
            #         languages=["en-US", "en"],
            #         vendor="Google Inc.",
            #         platform="Win32",
            #         webgl_vendor="Intel Inc.",
            #         renderer="Intel Iris OpenGL Engine",
            #         fix_hairline=True,
            #         )

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
            os.mkdir(f'{self.query}_VijaySales_Dataset')
        except FileExistsError:
            print("Directory already exists... \nData already Scrapped.")
            self.get_product_details()
            sys.exit(0)
        except OSError as e:
            print('Error Creating the Directory: ', e)
            sys.exit(1)

    def get_dir_name(self):
        return f'{self.query}_VijaySales_Dataset'

    def get_data_from_site(self):
        driver = self.get_driver()
        url = f'https://www.vijaysales.com/search-listing?q={self.query}'
        driver.get(url)

        wait = WebDriverWait(driver, 10)
        last_height = 0
        file_no = 1
        count = 1

        try:
            # Wait and locate the NEXT button
            next_btn = wait.until(
                EC.presence_of_element_located((By.XPATH, "//*[@jsname='nextBtn']"))
            )

            # Wait until the products are loaded
            wait.until(
                EC.presence_of_element_located((By.XPATH, "//*[starts-with(@class, 'product-card show')]"))
            )
        except:
            print("Vijay Sales: ❌ Products didn't load. Saving page for debugging...")
            with open("debug_headless.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            self.close_driver(driver)
            sys.exit(1)


        while True:
            try:
                #After Products Loaded Write the html file
                elems = driver.find_elements(By.XPATH, "//*[starts-with(@class, 'product-card show')]")
                print(f'Vijay Sales: Total {len(elems)} products found in Page-{count}')
                for elem in elems:
                    doc = elem.get_attribute('innerHTML')
                    with open(f'{self.get_dir_name()}/{self.query}_{file_no}.html', 'w',
                              encoding='utf-8') as f:
                        f.write(doc)
                        file_no += 1

                # Scroll to the button
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
                time.sleep(2)

                # Wait until clickable
                wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@jsname='nextBtn']")))

                # Check if button is visible and enabled
                if next_btn.is_displayed() and next_btn.is_enabled():
                    next_btn.click()
                    count += 1
                    # print("Clicked NEXT")
                    time.sleep(2)  # wait for next page content to load
                else:
                    print("NEXT button is not clickable. Ending loop.")
                    break

            except Exception as e:
                print('Vijay Sales: No more Products')
                # print("No more NEXT button or an error occurred:", e)
                break

        self.close_driver(driver)


    def get_product_details(self):
        for file in os.listdir(self.get_dir_name()):
            with open(f'{self.get_dir_name()}/{file}','r',encoding='utf-8') as f:
                html_doc = f.read()
            soup = BeautifulSoup(html_doc, 'html.parser')

            title = soup.find('div',class_='product-name').text
            # print(title)
            self.data['Title'].append(title)

            link = soup.find('a',class_='product-card__link')['href']
            # print(link)
            self.data['Link'].append(link)

            img_link = soup.find('img',class_='product__image')['src']
            # print(img_link)
            self.data['Image-Link'].append(img_link)

            price_div = soup.find('div',class_='discountedPrice')
            price = price_div.get('data-price')
            # print(price)
            self.data['Price'].append(price)

            self.data['Platform'].append('Vijay Sales')

            ots = soup.find('p',class_='product-stock')
            if ots:
                self.data['Available'].append('Out of Stock')
            else:
                self.data['Available'].append('Available')

            def get_rating():
                rating_div = soup.find('div', class_='product__title--reviews-star')
                style_atr = rating_div.get('style')
                match = re.search(r'--rating:\s*([\d.]+)', style_atr)
                if match:
                    rating = float(match.group(1))
                    # print(rating)
                    self.data['Rating'].append(rating)
                else:
                    print('Rating not found.')

            get_rating()

    def create_csv(self):
        df = pd.DataFrame(self.data)
        df.to_csv(f'CSV_Dataset/{self.query}_VijaySales.csv',mode='a',index=False)
        shutil.rmtree(self.get_dir_name())

class VijaySalesProduct(VijaySalesScrapper):
    def __init__(self):
        pass

    def get_price(self,url):
        driver = self.get_driver()
        driver.get(url)

        try:
            wait = WebDriverWait(driver, 15)
            price_tag = wait.until(
                EC.presence_of_element_located((By.XPATH, "//p[@class='product__price--price']"))
            )
            price = price_tag.get_attribute('data-final-price')

            return int(price)


        except Exception as e:
            print("Error Locating element: ", e)
            return None

def run_scraper(search_query):
    obj = VijaySalesScrapper(search_query)
    obj.create_directory()
    obj.get_data_from_site()
    obj.get_product_details()
    obj.create_csv()


if __name__ == '__main__':
    query = input('Enter the product query: ')
    run_scraper(query)
