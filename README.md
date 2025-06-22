
<h1 align="center">
  <img src="Images/logo_icon.png" alt="Buy Buddy Icon" width="40" height="40"/>
  <span style="vertical-align: middle;">Buy Buddy</span>
</h1>

A cross-platform desktop application built using **Python**, **CustomTkinter**, and **Selenium** that scrapes product data from major Indian e-commerce platforms and notifies users when prices drop below their set budgets.

---

## ✨ Features

- 🔍 **Search products** from:
  - Flipkart
  - Croma
  - Vijay Sales
  - Reliance Digital
- 📊 **Track & compare prices**
- 🔔 **Set a budget** and get **email alerts** on price drops
- ♻️ **Retry failed checks** due to timeout or network issues
- ⚡ **Fast multi-processing** scraping
- 🖥️ Built with **CustomTkinter** for a modern UI
- 📦 Converted to `.exe` using **PyInstaller**

---

## 📁 Folder Structure

```
E_Commerce_Scraper/
│
├── scripts/                # Platform-specific scrapers
│   ├── flipkart_scrapper.py
│   ├── croma_scrapper.py
│   ├── vijaysales_scrapper.py
│   ├── reliance_scrapper.py
│   └── ...
│
├── Images/                 # Icons and UI images
├── Fonts/                  # Custom fonts (JetBrains Mono, etc.)
├── data/
│   └── product_data.json   # Product save file (created on first run)
│
├── CSV_Dataset/            # Scraped CSV files (ignored in git)
├── Saved CSVs/             # Combined CSV files of product (ignored in git)
│
├── main.py                 # Entry point for the application
├── notifier.py             # Wishlist price-checker & email notifier
├── retry_failed.py         # Retry logic for failed product checks
├── main.spec               # PyInstaller spec file
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/E_Commerce_Scraper.git
cd E_Commerce_Scraper
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

Make sure you have:
- **Google Chrome**
- Compatible **ChromeDriver** added to your `PATH`
- Internet connection for scraping and email alerts

### 3. Run the App
```bash
python main.py
```

---

## 🔔 Run Notifier Script

To automatically check prices and send an email if a product is under your budget:
```bash
python notifier.py
```

Configure email sender, recipient, and credentials in `notifier.py` if needed.

---

## ♻️ Retry Failed Products

If any product failed to load in `notifier.py` (due to timeout or scraping issues), you can rerun them with:
```bash
python retry_failed.py
```

This script reads the failed items from the log and attempts again using the appropriate scrapers.

---

## 🕒 Scheduled Automation (Windows Task Scheduler / Cron)

To automate price tracking:

1. **Schedule `notifier.py`**
   - Set it to run daily or multiple times a day.
   - Recommended method: Use Task Scheduler (Windows) or cron (Linux/macOS).

2. **Schedule `retry_failed.py` shortly after**
   - Ensure this runs a few minutes after `notifier.py` finishes.
   - It will attempt to scrape any items that failed in the notifier script.

Example (Windows Task Scheduler):

- `notifier.py` at 10:00 AM
- `retry_failed.py` at 10:20 AM

> 💡 You can schedule the `.exe` versions of both scripts as well after converting using PyInstaller.

---

## 🛠️ Build as `.exe` (Windows only)

To convert into a standalone app:
```bash
pyinstaller --onefile --noconsole --icon=Images/logo_icon.ico ^
  --add-data "Images;Images" --add-data "Fonts;Fonts" --add-data "data;data" main.py
```

For proper `selenium-stealth` support, include required JS files manually in the `.spec` file under `datas`.

---

## ⚠️ Notes

- Results are not the accurate everytime, sometimes products didn't load properly
- Notifier script is not accurate, sometimes it fails to fetch the price, make sure to execute retry_failed after that.
- `product_data.json` is created if it doesn’t exist on first run
- Avoid bundling `product_data.json` as a read-only asset

---

## 📌 TODO

- [ ] Add push/email config through GUI
- [ ] Logging of all scraping actions
- [ ] Product availability alerts
- [ ] Search on result screen
- [ ] Notifier Screen
- [ ] Wishlist Screen
- [ ] Search Method Options
- [ ] Optional cloud backup

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
