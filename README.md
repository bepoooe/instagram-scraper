# Instagram Scraper

A Python script that scrapes Instagram profiles using the Apify API and exports data in JSON, CSV, and HTML formats.

## Requirements

- Python 3.6+
- An Apify account with API token
- Required packages:
  - `requests`
  - `json`
  - `csv`

## Installation

1. Clone this repository or download the files
2. Install the required packages:

```bash
pip install requests
```

## Usage

Run the script with the Instagram username you want to scrape and your Apify API token:

```bash
python instagram_scraper.py USERNAME --api-token YOUR_APIFY_TOKEN [--format FORMAT_LIST]
```

### Parameters

- `USERNAME`: Instagram username to scrape
- `--api-token`: Your Apify API token
- `--format`: Optional comma-separated list of output formats (default: json,csv,html)

### Available Formats

The `--format` parameter accepts the following values:

- `json`: Standard JSON format with all data
- `csv`: Comma-separated values with main post fields
- `html`: Interactive HTML page with table and list views

### Examples

Export to all formats (default):
```bash
python instagram_scraper.py nasa --api-token apify_api_xxxxxxxxxxxxxxxxxxxx
```

Export to JSON only:
```bash
python instagram_scraper.py nasa --api-token apify_api_xxxxxxxxxxxxxxxxxxxx --format json
```

Export to CSV and HTML:
```bash
python instagram_scraper.py nasa --api-token apify_api_xxxxxxxxxxxxxxxxxxxx --format csv,html
```

## Output

The script will:
1. Create a timestamped folder for the scraped data
2. Save Instagram data in all requested formats
3. Display progress and results in the console

The data is saved to: `instagram_data/USERNAME_TIMESTAMP/USERNAME.FORMAT`

### HTML Report Features

The HTML report includes:
- Dark mode design
- Tab-based navigation between table and list views
- Summary statistics (posts count, total likes, total comments)
- Search functionality for posts
- Responsive design for mobile and desktop
- Interactive elements with hover effects

## How It Works

This scraper uses Apify's "shu8hvrXbJbY3Eb9W" actor, which is a reliable Instagram scraper. It's configured to use the "directUrls" approach with a limit of 100 posts per profile.

## Data Structure

The exported data contains the following information for each Instagram post:
- Post ID and shortcode
- Post type (image, video, etc.)
- Caption
- Number of likes and comments
- Timestamp
- Owner username
- URL

### JSON Format
Contains the complete data structure with all fields as returned by the API.

### CSV Format
Contains a flattened version with the most important fields in tabular format.

### HTML Format
An interactive web page that allows browsing, filtering, and searching the data.

## Troubleshooting

If you encounter errors:
1. Check your Apify API token is valid
2. Verify the Instagram username exists and is public
3. Ensure you have an active internet connection
4. Check the script output for specific error messages

## Note

Instagram scraping is subject to Instagram's terms of service. Use this tool responsibly and ensure you have the right to scrape the content. 