# Installation & Setup Guide

This guide will walk you through setting up and running the Medicine Scraper project step by step.

## 📋 Prerequisites

Before you begin, make sure you have:

- **Python 3.7 or higher** installed on your system
- **pip** (Python package installer) - usually comes with Python
- **Git** (optional, for cloning the repository)
- **Internet connection** for downloading dependencies

### Check Python Installation

Open your terminal/command prompt and run:
```bash
python --version
# or
python3 --version
```

If Python is not installed, download it from [python.org](https://www.python.org/downloads/)

## 🚀 Quick Setup (5 minutes)

### Step 1: Get the Project Files

**Option A: If you have the files already**
- Skip to Step 2

**Option B: Clone from Git**
```bash
git clone <your-repository-url>
cd medicine-scraper
```

**Option C: Download ZIP**
- Download the project as ZIP file
- Extract it to your desired location
- Open terminal in the project folder

### Step 2: Create Virtual Environment

**Why use a virtual environment?**
- Keeps project dependencies isolated
- Prevents conflicts with other Python projects
- Makes the project portable

**Create virtual environment:**
```bash
python -m venv venv
```

**Activate virtual environment:**

**On Windows:**
```bash
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**Verify activation:**
You should see `(venv)` at the beginning of your command prompt.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `requests` - For making HTTP requests
- `beautifulsoup4` - For parsing HTML
- `pandas` - For data manipulation
- `lxml` - For XML/HTML parsing
- `openpyxl` - For Excel file support

### Step 4: Test Installation

Run a quick test to make sure everything is working:
```bash
python -c "import requests, bs4, pandas; print('✅ All dependencies installed successfully!')"
```

## 🏃‍♂️ How to Run

### Method 1: Quick Test (Recommended for first run)

1. **Open the scraper file:**
   ```bash
   # Make sure you're in the project directory
   python medicine_scraper.py
   ```

2. **The script will run with default URLs and create output files**

### Method 2: Custom URLs

1. **Edit the script:**
   - Open `medicine_scraper.py` in any text editor
   - Find the `main()` function
   - Modify the `urls` list:

   ```python
   def main():
       # 🔹 ADD YOUR MEDICINE URLS HERE
       urls = [
           "https://www.1mg.com/drugs/your-medicine-url-1",
           "https://www.1mg.com/drugs/your-medicine-url-2",
           # Add more URLs here...
       ]
   ```

2. **Run the scraper:**
   ```bash
   python medicine_scraper.py
   ```

### Method 3: Test Mode

For testing with a single URL:

1. **Edit the script:**
   - Open `medicine_scraper.py`
   - Find the line at the bottom:
   ```python
   # Uncomment line below to run quick test first:
   # quick_test()
   ```
   
2. **Uncomment the test line:**
   ```python
   # Uncomment line below to run quick test first:
   quick_test()
   ```

3. **Run the test:**
   ```bash
   python medicine_scraper.py
   ```

## 📁 Output Files

After running the scraper, you'll find these files in your project directory:

| File | Description |
|------|-------------|
| `medicines_final.csv` | Main data file (Excel compatible) |
| `medicines_final.xlsx` | Excel format |
| `medicines_final.json` | JSON format |
| `scraper.log` | Detailed logs and error messages |

## ⚙️ Configuration Options

### Change Delay Between Requests

In `medicine_scraper.py`, find this line in the `main()` function:
```python
DELAY_SECONDS = 0  # No delay between requests
```

**Recommended values:**
- `0` - Fast (use responsibly)
- `1` - Moderate
- `2` - Conservative (recommended for large batches)

### Change Output Filename

```python
OUTPUT_FILE = "medicines_final.csv"
```

### Enable/Disable Progress Saving

```python
df = scrape_medicines_batch(urls, delay=DELAY_SECONDS, save_progress=True)
```

## 🔧 Troubleshooting

### Common Issues

**1. "python: command not found"**
- Python is not installed or not in PATH
- Try `python3` instead of `python`
- Install Python from [python.org](https://www.python.org/downloads/)

**2. "pip: command not found"**
- pip is not installed
- Try `python -m pip` instead of `pip`
- On Windows, try `py -m pip`

**3. "ModuleNotFoundError"**
- Dependencies not installed
- Make sure virtual environment is activated
- Run: `pip install -r requirements.txt`

**4. "Permission denied"**
- On Windows: Run terminal as Administrator
- On macOS/Linux: Use `sudo` if needed

**5. "Network errors"**
- Check internet connection
- Try increasing delay between requests
- Some URLs might be temporarily unavailable

**6. "No data scraped"**
- Check if URLs are valid and accessible
- Look at `scraper.log` for detailed error messages
- Website structure might have changed

### Getting Help

1. **Check the log file:**
   ```bash
   cat scraper.log
   # or on Windows:
   type scraper.log
   ```

2. **Run with verbose output:**
   The script already includes detailed logging

3. **Test with a single URL:**
   Use the `quick_test()` function

## 🎯 Example Workflow

Here's a complete example of setting up and running the scraper:

```bash
# 1. Navigate to project directory
cd /path/to/medicine-scraper

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Edit URLs in medicine_scraper.py (optional)
# Open the file and modify the urls list

# 5. Run the scraper
python medicine_scraper.py

# 6. Check results
ls -la *.csv *.xlsx *.json  # macOS/Linux
dir *.csv *.xlsx *.json     # Windows
```

## 📞 Support

If you encounter issues:

1. Check the `scraper.log` file for error details
2. Verify all dependencies are installed correctly
3. Test with a single URL first using `quick_test()`
4. Make sure the target URLs are accessible in your browser

## 🔄 Deactivating Virtual Environment

When you're done working on the project:
```bash
deactivate
```

This will return you to your system's default Python environment.

---

**Happy Scraping! 🏥💊**
