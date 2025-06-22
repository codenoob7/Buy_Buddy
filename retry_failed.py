import json
from flipkart_scrapper import FlipkartProduct
from notifier import EmailSender

with open("logs/failed_products.json", "r") as f:
    data = json.load(f)['failed']


fp = FlipkartProduct()

for p in data:
    print(f"Retrying: {p['name']}")
    price = fp.get_price(p['url'])
    if price is not None and price <= p['budget']:
        print('sending the mail...')
        sender = EmailSender()
        sender.send_messages(p['name'], price)
    else:
        print('Product price not in the budget.')
