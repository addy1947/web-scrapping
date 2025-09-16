# Medicine Scraper

A Python web scraper designed to extract medicine information from 1mg.com. This tool scrapes medicine details including name, price (MRP and discounted), quantity, manufacturer, composition, and product images.

## Features

- 🏥 Scrapes medicine data from 1mg.com
- 💰 Extracts both MRP and discounted prices
- 📊 Exports data to CSV, Excel, and JSON formats
- 🔄 Batch processing with progress tracking
- 📝 Comprehensive logging
- 🛡️ Error handling and retry mechanisms
- ⏰ Configurable delays between requests

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Setup

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd medicine-scraper
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install required dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   Or install packages individually:
   ```bash
   pip install requests beautifulsoup4 pandas lxml openpyxl
   ```

## Usage

### Quick Start

1. **Edit the URLs in the script**
   Open `medicine_scraper.py` and modify the `urls` list in the `main()` function:
   ```python
   urls = [
       "https://www.1mg.com/drugs/dolo-650-tablet-74467",
       "https://www.1mg.com/drugs/crocin-pain-relief-tablet-323789",
       # Add more URLs here...
   ]
   ```

2. **Run the scraper**
   ```bash
   python medicine_scraper.py
   ```

3. **Check the results**
   The scraper will generate:
   - `medicines_final.csv` - Main output file
   - `medicines_final.xlsx` - Excel format
   - `medicines_final.json` - JSON format
   - `scraper.log` - Detailed logs

### Configuration Options

- **Delay between requests**: Modify `DELAY_SECONDS` in the `main()` function
- **Output filename**: Change `OUTPUT_FILE` variable
- **Progress saving**: Enable/disable with `save_progress` parameter

### Test Mode

Run a quick test with a single URL:
```python
# Uncomment this line in the script:
quick_test()
```

## Output Data

The scraper extracts the following information for each medicine:

| Field | Description |
|-------|-------------|
| name | Medicine name |
| mrp | Maximum Retail Price |
| discounted_price | Current selling price |
| quantity | Number of tablets/strips |
| image | Product image URL |
| manufacturer | Brand/Company name |
| composition | Active ingredients |
| url | Source URL |
| status | Scraping status |

## File Structure

```
medicine-scraper/
├── medicine_scraper.py    # Main scraper script
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .gitignore           # Git ignore rules
├── venv/                # Virtual environment (created after setup)
└── output files         # Generated after running scraper
    ├── medicines_final.csv
    ├── medicines_final.xlsx
    ├── medicines_final.json
    └── scraper.log
```

## Important Notes

- ⚠️ **Respect website terms of service** and use reasonable delays
- 🔒 **Rate limiting**: The scraper includes delays to avoid overwhelming the server
- 📊 **Data accuracy**: Always verify scraped data for important decisions
- 🛡️ **Error handling**: Failed URLs are logged and included in the output

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Network errors**: Check your internet connection and try increasing delays

3. **Parsing errors**: Website structure may have changed; check the logs for details

4. **Permission errors**: Make sure you have write permissions in the project directory

### Getting Help

- Check the `scraper.log` file for detailed error messages
- Verify that the URLs are accessible in your browser
- Ensure you're using the latest version of the dependencies

## License

This project is for educational purposes. Please respect the website's terms of service and robots.txt file.
