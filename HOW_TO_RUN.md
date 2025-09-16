# How to Run - Quick Reference

## 🚀 Quick Start (3 steps)

### 1. Setup Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure URLs
Edit `medicine_scraper.py` and modify the `urls` list in the `main()` function:
```python
urls = [
    "https://www.1mg.com/drugs/dolo-650-tablet-74467",
    "https://www.1mg.com/drugs/crocin-pain-relief-tablet-323789",
    # Add your URLs here...
]
```

### 3. Run the Scraper
```bash
python medicine_scraper.py
```

## 📁 Output Files
- `medicines_final.csv` - Main results
- `medicines_final.xlsx` - Excel format  
- `medicines_final.json` - JSON format
- `scraper.log` - Detailed logs

## ⚙️ Quick Configuration

**Change delay between requests:**
```python
DELAY_SECONDS = 2  # 2 seconds delay (recommended)
```

**Test with single URL:**
Uncomment this line in the script:
```python
quick_test()
```

## 🔧 Common Issues

**"python: command not found"**
- Try `python3` instead of `python`
- Install Python from python.org

**"ModuleNotFoundError"**
- Make sure virtual environment is activated
- Run: `pip install -r requirements.txt`

**No data scraped**
- Check `scraper.log` for errors
- Verify URLs are accessible in browser

## 📞 Need Help?
- Check `scraper.log` for detailed error messages
- See `INSTALLATION.md` for complete setup guide
- Test with single URL using `quick_test()`

---
**That's it! Happy scraping! 🏥**
