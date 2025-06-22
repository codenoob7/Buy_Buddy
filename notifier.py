import json
from multiprocessing import Process

import requests
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from bs4 import BeautifulSoup
import re
from flipkart_scrapper import FlipkartProduct
from croma_scrapper import CromaProduct
from vijaysales_scrapper import VijaySalesProduct
from reliance_scrapper import RelianceProduct

import logging
import os

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure general log
logging.basicConfig(
    filename="logs/price_notifier.log",
    filemode='a',
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Optional: separate logger for errors
error_logger = logging.getLogger("error_logger")
error_handler = logging.FileHandler("logs/errors.log")
error_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
error_logger.addHandler(error_handler)
error_logger.setLevel(logging.WARNING)


class Notifier:
    def __init__(self):
        with open('data/product_data.json', 'r') as f:
            self.products = json.load(f)['products']
            self.failed_links = []


    def get_price_by_requests(self,url):
        headers = {"User-Agent": "Mozilla/5.0"}
        html = requests.get(url, headers=headers).text
        soup = BeautifulSoup(html, 'html.parser')

        # 1. Try schema.org JSON-LD
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and 'offers' in data:
                    price = data['offers'].get('price')
                    if price:
                        return int(price)
                        # return f"₹{price}"
            except Exception:
                continue

        # 2. Try matching ₹ price text using regex
        price_tags = soup.find_all(string=re.compile(r"₹\s?\d{1,3}(,\d{3})*(\.\d+)?"))
        if price_tags:
            return price_tags[0].strip()

        return None


    def get_price_by_selenium(self,products,scraper):
        for p in products:
            try:
                price = scraper.get_price(p['url'])
                price_drop = None

                if price is None:
                    logging.warning(f"[PRICE NOT FOUND] {p['name']} - {p['url']}")
                    self.failed_links.append(p)
                else:
                    price_drop = p['budget'] >= price

                    if price_drop:
                        print('Sending the mail...')
                        sender = EmailSender()
                        sender.send_messages(p['name'], price)
                    else:
                        print('Product price not in the budget.')

                    logging.info(
                        f"[{p['platform']}] {p['name']} | Budget: ₹{p['budget']} | Price: ₹{price} | Drop: {price_drop}")

                print(f'---------------{p["platform"]}---------------\n'
                      f'Product Name: {p["name"]}\n'
                      f'Budget: {p["budget"]}\n'
                      f'Price: {price}\n'
                      f'Price Drop: {price_drop if price else "N/A"}')


            except Exception as e:
                error_logger.error(f"[ERROR] {p['name']} - {p['url']} => {e}")

        # Save failed links to a JSON file
        if self.failed_links:
            with open("logs/failed_products.json", "w", encoding="utf-8") as f:
                json.dump({"failed": self.failed_links}, f, indent=4)
            print(f"Saved {len(self.failed_links)} failed products for retry.")

    def flipkart_process(self, url):
        fp = FlipkartProduct()
        self.get_price_by_selenium(url, fp)

    def croma_process(self, url):
        cp = CromaProduct()
        self.get_price_by_selenium(url, cp)



import smtplib
class EmailSender():
    def __init__(self):
        self.host = 'smtp.gmail.com'
        self.port = 587

        self.sender = 'shreyashpatel1001@gmail.com'
        self.receiver = 'logo7440@gmail.com'
        self.password = 'fvcu vyax jldg gnlj'


    def send_messages(self,product,price):
        self.message = f"""Subject: PRICE NOTIFIER
Heyy Buddy, Your {product} is now available!
Your Wish listed product price is now in you budget: {price}
HURRY UP!! Go grab the deal now, before it's too late.
        """


        server = smtplib.SMTP(self.host, self.port)
        server.starttls()
        server.login(self.sender,self.password)
        server.sendmail(self.sender, self.receiver, self.message)
        print('Mail Sent Successfully')
        server.quit()


if __name__ == '__main__':

    notifier = Notifier()
    # Categorize
    rv_products = [p for p in notifier.products if p['platform'] in ['Vijay Sales', 'Reliance Digital']]

    # --- 1. Scrape Vijay Sales + Reliance (Fast with requests)
    def fetch_rv_price(p):
        price = notifier.get_price_by_requests(p['url'])
        return {**p, 'price': price}


    with ThreadPoolExecutor(max_workers=8) as executor:
        rv_results = list(executor.map(fetch_rv_price, rv_products))

    print("\n--- Vijay Sales - Reliance Digital ---")
    for p in rv_results:
        print(f'----------{p['platform']}-----------\n'
              f'Product Name: {p['name']}\n'
              f'Budget: {p['budget']}\n'
              f'Price: {p['price']}\n'
              f'Link: {p['url']}\n')

        if p['price']  is not None and p['price'] <= p['budget']:
            print('Sending the mail...')
            sender = EmailSender()
            sender.send_messages(p['name'], p['price'])
        else:
            print('Product price not in the budget.')


    #--- 2. Scrape Flipkart + Croma (Slow with Selenium)
    flipkart_products = [p for p in notifier.products if p['platform'] == 'Flipkart']
    croma_products = [p for p in notifier.products if p['platform'] == 'Croma']
    print(flipkart_products)

    scrapers = [
        (notifier.flipkart_process, flipkart_products),
        (notifier.croma_process, croma_products)
    ]

    processes = []
    for func,args in scrapers:
        process = Process(target=func, args=(args,))
        process.start()
        processes.append(process)

