# Instagram Scraper

A simple Python script that scrapes Instagram profiles using Apify API and exports data in multiple formats.

## Requirements

- Python 3.6+
- An Apify account with API token
- Required packages:
  - `requests` (required)
  - `pandas` and `openpyxl` (optional, for Excel export)

## Installation

1. Clone this repository or download the files
2. Install the required packages:

```bash
pip install requests

# Optional dependencies for Excel export
pip install pandas openpyxl
```

## Usage

Run the script with the Instagram username you want to scrape and your Apify API token:

```bash
python instagram_scraper.py USERNAME --api-token YOUR_APIFY_TOKEN [--format FORMAT_LIST]
```

### Parameters

- `USERNAME`: Instagram username to scrape
- `--api-token`: Your Apify API token
- `--format`: Optional comma-separated list of output formats (default: json)

### Available Formats

The `--format` parameter accepts the following values:

- `json`: Standard JSON format (default)
- `jsonl`: JSON Lines format (one object per line)
- `csv`: Comma-separated values
- `xml`: XML format
- `excel`: Excel spreadsheet (requires pandas and openpyxl)
- `html`: HTML table
- `rss`: RSS feed
- `all`: Export to all available formats

### Examples

Export to JSON (default):
```bash
python instagram_scraper.py natgeo --api-token apify_api_xxxxxxxxxxxxxxxxxxxx
```

Export to CSV and Excel:
```bash
python instagram_scraper.py natgeo --api-token apify_api_xxxxxxxxxxxxxxxxxxxx --format csv,excel
```

Export to all available formats:
```bash
python instagram_scraper.py natgeo --api-token apify_api_xxxxxxxxxxxxxxxxxxxx --format all
```

## Output

The script will:
1. Create a timestamped folder for the scraped data
2. Save Instagram data in all requested formats
3. Display progress and results in the console

The data is saved to: `instagram_data/USERNAME_TIMESTAMP/USERNAME.FORMAT`

## How It Works

This scraper uses Apify's "shu8hvrXbJbY3Eb9W" actor, which is a reliable Instagram scraper. It's configured to use the "directUrls" approach, which has proven to be the most effective method for retrieving Instagram profile data.

## Data Structure

The exported data contains the following information for each Instagram post:
- Post ID and shortcode
- Post type (image, video, etc.)
- Caption and description
- Number of likes and comments
- Timestamp
- Owner username
- URL
- And more depending on what the API returns

## Troubleshooting

If you encounter errors:
1. Check your Apify API token is valid
2. Verify the Instagram username exists and is public
3. Ensure you have an active internet connection
4. For Excel export issues, make sure pandas and openpyxl are installed

## Note

Instagram scraping is subject to Instagram's terms of service. Use this tool responsibly and ensure you have the right to scrape the content. 