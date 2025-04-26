import requests
import json
import os
import time
import argparse
import csv
import xml.dom.minidom
import xml.etree.ElementTree as ET
from datetime import datetime
import re

# Try importing optional dependencies
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

def safe_get(obj, key, default=''):
    """Safely gets a value from a dictionary, handling nested keys and returning a default if not found."""
    if obj is None:
        return default
    
    # If key contains dots, treat it as a nested lookup
    if '.' in key:
        parts = key.split('.')
        current = obj
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current
    
    # Simple key lookup
    return obj.get(key, default)

def run_instagram_scraper(api_token, username):
    """Run the Instagram scraper using the successful actor and configuration."""
    # The actor ID that was successful
    actor_id = "shu8hvrXbJbY3Eb9W"
    
    # The configuration that yielded the most data
    input_config = {
        "directUrls": [f"https://www.instagram.com/{username}/"],
        "resultsLimit": 100
    }
    
    print(f"Starting Instagram scraper for user: {username}")
    print(f"Using actor ID: {actor_id}")
    
    # Start the actor run
    start_url = f"https://api.apify.com/v2/acts/{actor_id}/runs?token={api_token}"
    start_response = requests.post(start_url, json=input_config)
    
    if start_response.status_code != 201:
        print(f"❌ Failed to start actor: {start_response.status_code}, {start_response.text}")
        return None
    
    run_data = start_response.json()
    run_id = run_data.get('data', {}).get('id')
    
    if not run_id:
        print("❌ No run ID returned")
        return None
    
    print(f"✅ Actor started, run ID: {run_id}")
    
    # Poll for run status
    status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={api_token}"
    max_attempts = 60  # 10 minutes with 10-second intervals
    
    for attempt in range(max_attempts):
        time.sleep(10)  # Wait 10 seconds between checks
        
        status_response = requests.get(status_url)
        if status_response.status_code != 200:
            print(f"❌ Failed to get run status: {status_response.status_code}")
            continue
        
        status_data = status_response.json()
        status = status_data.get('data', {}).get('status')
        
        print(f"Run status: {status} (attempt {attempt+1}/{max_attempts})")
        
        if status in ['SUCCEEDED', 'FAILED', 'TIMED-OUT', 'ABORTED']:
            break
    
    if status != 'SUCCEEDED':
        print(f"❌ Run did not succeed, final status: {status}")
        return None
    
    # Get the run results
    dataset_id = status_data.get('data', {}).get('defaultDatasetId')
    if not dataset_id:
        print("❌ No dataset ID found")
        return None
    
    items_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={api_token}"
    items_response = requests.get(items_url)
    
    if items_response.status_code != 200:
        print(f"❌ Failed to get dataset items: {items_response.status_code}")
        return None
    
    data = items_response.json()
    print(f"✅ Retrieved {len(data)} items from the dataset")
    
    return data

def create_output_folder(username):
    """Create output folder for a specific username."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder_path = f"instagram_data/{username}_{timestamp}"
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def save_data(data, folder_path, filename="instagram_data", formats=None):
    """Save data to multiple file formats."""
    if formats is None:
        formats = ["json", "csv", "html"]  # Default formats
    
    print(f"Saving data to {folder_path} in formats: {formats}")
    print(f"Found {len(data)} items to save")
    
    results = {}
    
    # Save JSON data
    if "json" in formats:
        json_path = os.path.join(folder_path, f"{filename}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Saved JSON data to {json_path}")
        results["json"] = json_path
    
    # Save as CSV
    if "csv" in formats:
        # Flatten the data for CSV (extract common fields)
        flattened_data = []
        for item in data:
            flat_item = {}
            # Extract common fields - adjust these based on your data structure
            flat_item["id"] = item.get("id", "")
            flat_item["type"] = item.get("type", "")
            flat_item["shortCode"] = item.get("shortCode", "")
            flat_item["caption"] = item.get("caption", "")
            flat_item["commentsCount"] = item.get("commentsCount", 0)
            flat_item["likesCount"] = item.get("likesCount", 0)
            flat_item["timestamp"] = item.get("timestamp", "")
            flat_item["ownerUsername"] = item.get("ownerUsername", "")
            flat_item["url"] = item.get("url", "")
            
            # Add any additional fields here
            flattened_data.append(flat_item)
        
        # Write to CSV
        if flattened_data:
            csv_path = os.path.join(folder_path, f"{filename}.csv")
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=flattened_data[0].keys())
                writer.writeheader()
                writer.writerows(flattened_data)
            print(f"✅ Saved CSV data to {csv_path}")
            results["csv"] = csv_path
    
    # Save as HTML Table with dark mode
    if "html" in formats:
        try:
            html_path = os.path.join(folder_path, f"{filename}.html")
            print(f"Starting HTML generation to {html_path}...")
            
            # Create HTML content with dark theme and requested colors
            html = [
                "<!DOCTYPE html>",
                "<html>",
                "<head>",
                "<meta charset='UTF-8'>",
                f"<title>Instagram Data for @{filename}</title>",
                "<style>",
                "/* Dark theme with specified color palette */",
                "/* Colors: #9d4edd, #c77dff, #ff9e00, #ddff00, #9d4edd */",
                ":root {",
                "  --bg-color: #111420;",
                "  --card-bg: #1e2132;",
                "  --text-color: #f5f5f5;",
                "  --primary: #9d4edd;",
                "  --secondary: #c77dff;",
                "  --accent1: #ff9e00;",
                "  --accent2: #ddff00;",
                "  --muted-text: #a0a0a0;",
                "  --border-color: #333648;",
                "}",
                "body { font-family: 'Segoe UI', Roboto, Arial, sans-serif; margin: 0; padding: 0; background-color: var(--bg-color); color: var(--text-color); }",
                ".container { max-width: 1200px; margin: 20px auto; background: var(--card-bg); border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.2); padding: 25px; }",
                "h1 { color: var(--primary); margin-bottom: 20px; text-align: center; }",
                "table { width: 100%; border-collapse: collapse; margin-bottom: 20px; border-radius: 8px; overflow: hidden; }",
                "th, td { padding: 15px; text-align: left; border-bottom: 1px solid var(--border-color); }",
                "th { background-color: var(--primary); color: white; font-weight: 600; position: sticky; top: 0; }",
                "tr:hover { background-color: rgba(157, 78, 221, 0.1); transition: all 0.2s; }",
                ".caption { max-width: 400px; }",
                ".stats { display: flex; margin-bottom: 30px; gap: 20px; flex-wrap: wrap; }",
                ".stat-block { flex: 1; background: var(--card-bg); padding: 20px; border-radius: 12px; text-align: center; border: 1px solid var(--primary); box-shadow: 0 4px 12px rgba(157, 78, 221, 0.2); transition: transform 0.3s, box-shadow 0.3s; }",
                ".stat-block:hover { transform: translateY(-5px); box-shadow: 0 8px 15px rgba(157, 78, 221, 0.3); }",
                ".stat-value { font-size: 28px; font-weight: bold; color: var(--accent1); margin-bottom: 10px; }",
                ".stat-label { font-size: 16px; color: var(--text-color); }",
                ".tabs { display: flex; margin-bottom: 20px; border-bottom: 1px solid var(--border-color); gap: 10px; }",
                ".tab { padding: 12px 25px; cursor: pointer; background: none; border: none; font-size: 16px; color: var(--text-color); border-radius: 8px 8px 0 0; transition: all 0.3s; }",
                ".tab:hover { background-color: rgba(157, 78, 221, 0.2); }",
                ".tab.active { color: white; background-color: var(--primary); }",
                ".tab-content { display: none; animation: fadeEffect 0.5s; }",
                "@keyframes fadeEffect { from {opacity: 0;} to {opacity: 1;} }",
                ".tab-content.active { display: block; }",
                ".search-container { margin-bottom: 25px; position: relative; }",
                ".search-container input { width: 100%; padding: 14px 20px; font-size: 16px; border: 2px solid var(--border-color); border-radius: 8px; background: var(--card-bg); color: var(--text-color); box-sizing: border-box; transition: all 0.3s; }",
                ".search-container input:focus { outline: none; border-color: var(--secondary); box-shadow: 0 0 0 3px rgba(199, 125, 255, 0.25); }",
                ".search-container input::placeholder { color: var(--muted-text); }",
                ".search-container::after { content: '🔍'; position: absolute; right: 15px; top: 50%; transform: translateY(-50%); color: var(--muted-text); font-size: 18px; }",
                ".list-view { display: flex; flex-direction: column; gap: 20px; }",
                ".list-item { border: 1px solid var(--border-color); border-radius: 12px; padding: 20px; background: var(--card-bg); transition: all 0.3s; }",
                ".list-item:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.15); border-color: var(--secondary); }",
                ".list-caption { margin-bottom: 15px; line-height: 1.5; }",
                ".list-meta { display: flex; flex-wrap: wrap; justify-content: space-between; color: var(--muted-text); font-size: 14px; gap: 10px; }",
                ".list-meta span, .list-meta a { margin-right: 10px; }",
                "a { color: var(--accent1); text-decoration: none; transition: color 0.2s; }",
                "a:hover { color: var(--accent2); text-decoration: none; }",
                ".tag { display: inline-block; background: var(--primary); color: white; font-size: 12px; padding: 4px 8px; border-radius: 4px; margin-right: 5px; }",
                ".likes-comments { display: flex; gap: 15px; }",
                ".likes-comments span { display: flex; align-items: center; }",
                ".likes-comments span svg { margin-right: 5px; }",
                "/* Scrollbar styling */",
                "::-webkit-scrollbar { width: 10px; height: 10px; }",
                "::-webkit-scrollbar-track { background: var(--card-bg); }",
                "::-webkit-scrollbar-thumb { background: var(--primary); border-radius: 5px; }",
                "::-webkit-scrollbar-thumb:hover { background: var(--secondary); }",
                "/* Responsive adjustments */",
                "@media (max-width: 768px) {",
                "  .container { margin: 10px; padding: 15px; }",
                "  .stats { flex-direction: column; }",
                "  .tab { padding: 10px 15px; font-size: 14px; }",
                "  .list-meta { flex-direction: column; }",
                "}",
                "</style>",
                "<script>",
                "function openTab(evt, tabName) {",
                "  const tabcontent = document.getElementsByClassName('tab-content');",
                "  for (let i = 0; i < tabcontent.length; i++) {",
                "    tabcontent[i].style.display = 'none';",
                "  }",
                "  const tablinks = document.getElementsByClassName('tab');",
                "  for (let i = 0; i < tablinks.length; i++) {",
                "    tablinks[i].className = tablinks[i].className.replace(' active', '');",
                "  }",
                "  document.getElementById(tabName).style.display = 'block';",
                "  evt.currentTarget.className += ' active';",
                "  // Save the active tab to localStorage",
                "  localStorage.setItem('activeInstagramTab', tabName);",
                "}",
                "",
                "function searchTable() {",
                "  const input = document.getElementById('table-search');",
                "  const filter = input.value.toUpperCase();",
                "  const table = document.getElementById('post-table');",
                "  const tr = table.getElementsByTagName('tr');",
                "",
                "  for (let i = 1; i < tr.length; i++) {",
                "    let found = false;",
                "    const td = tr[i].getElementsByTagName('td');",
                "    for (let j = 0; j < td.length; j++) {",
                "      if (td[j]) {",
                "        const txtValue = td[j].textContent || td[j].innerText;",
                "        if (txtValue.toUpperCase().indexOf(filter) > -1) {",
                "          found = true;",
                "          break;",
                "        }",
                "      }",
                "    }",
                "    tr[i].style.display = found ? '' : 'none';",
                "  }",
                "}",
                "",
                "function searchList() {",
                "  const input = document.getElementById('list-search');",
                "  const filter = input.value.toUpperCase();",
                "  const items = document.getElementsByClassName('list-item');",
                "",
                "  for (let i = 0; i < items.length; i++) {",
                "    const content = items[i].textContent || items[i].innerText;",
                "    items[i].style.display = content.toUpperCase().indexOf(filter) > -1 ? '' : 'none';",
                "  }",
                "}",
                "",
                "window.onload = function() {",
                "  // Check if there's a saved tab preference",
                "  const activeTab = localStorage.getItem('activeInstagramTab') || 'table-view';",
                "  // Find the tab button for the saved tab and click it",
                "  const tabs = document.getElementsByClassName('tab');",
                "  for (let i = 0; i < tabs.length; i++) {",
                "    if (tabs[i].getAttribute('data-tab') === activeTab) {",
                "      tabs[i].click();",
                "      break;",
                "    }",
                "  }",
                "  // If no matching tab found, click the first one",
                "  if (!document.querySelector('.tab.active')) {",
                "    document.querySelector('.tab').click();",
                "  }",
                "};",
                "</script>",
                "</head>",
                "<body>",
                "<div class='container'>",
                f"<h1>Instagram Data for @{filename}</h1>",
                "",
                "<!-- Statistics -->",
                "<div class='stats'>",
                f"  <div class='stat-block'><div class='stat-value'>{len(data)}</div><div class='stat-label'>Posts</div></div>",
                f"  <div class='stat-block'><div class='stat-value'>{sum(item.get('likesCount', 0) for item in data if isinstance(item.get('likesCount', 0), (int, float))):,}</div><div class='stat-label'>Total Likes</div></div>",
                f"  <div class='stat-block'><div class='stat-value'>{sum(item.get('commentsCount', 0) for item in data if isinstance(item.get('commentsCount', 0), (int, float))):,}</div><div class='stat-label'>Total Comments</div></div>",
                "</div>",
                "",
                "<!-- Tabs -->",
                "<div class='tabs'>",
                "  <button class='tab' data-tab='table-view' onclick=\"openTab(event, 'table-view')\">Table View</button>",
                "  <button class='tab' data-tab='list-view' onclick=\"openTab(event, 'list-view')\">List View</button>",
                "</div>",
                "",
                "<!-- Table View -->",
                "<div id='table-view' class='tab-content'>",
                "  <div class='search-container'>",
                "    <input type='text' id='table-search' onkeyup=\"searchTable()\" placeholder='Search posts...'>",
                "  </div>",
                "  <div style='overflow-x: auto; max-height: 70vh; overflow-y: auto;'>",
                "  <table id='post-table'>",
                "    <thead>",
                "      <tr>",
                "        <th>Type</th>",
                "        <th>Caption</th>",
                "        <th>Likes</th>",
                "        <th>Comments</th>",
                "        <th>Date</th>",
                "        <th>Username</th>",
                "        <th>Link</th>",
                "      </tr>",
                "    </thead>",
                "    <tbody>"
            ]
            
            # Add table rows
            for item in data:
                if not isinstance(item, dict):
                    continue
                
                # Get values
                post_type = item.get("type", "Post")
                caption = item.get("caption", "")
                likes = item.get("likesCount", 0)
                comments = item.get("commentsCount", 0)
                timestamp = item.get("timestamp", "")
                username = item.get("ownerUsername", "")
                url = item.get("url", "")
                
                # Format values
                safe_caption = caption.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                if len(safe_caption) > 150:
                    safe_caption = safe_caption[:150] + "..."
                
                # Format date
                formatted_date = timestamp
                if timestamp and isinstance(timestamp, str):
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        formatted_date = dt.strftime("%Y-%m-%d %H:%M")
                    except:
                        pass
                
                # Add table row
                html.append("      <tr>")
                html.append(f"        <td>{post_type}</td>")
                html.append(f"        <td class='caption'>{safe_caption}</td>")
                html.append(f"        <td>{likes:,}</td>")
                html.append(f"        <td>{comments:,}</td>")
                html.append(f"        <td>{formatted_date}</td>")
                html.append(f"        <td><a href='https://instagram.com/{username}/' target='_blank'>@{username}</a></td>")
                html.append(f"        <td><a href='{url}' target='_blank'>View</a></td>")
                html.append("      </tr>")
            
            html.append("    </tbody>")
            html.append("  </table>")
            html.append("  </div>")
            html.append("</div>")
            
            # List View
            html.append("<div id='list-view' class='tab-content'>")
            html.append("  <div class='search-container'>")
            html.append("    <input type='text' id='list-search' onkeyup=\"searchList()\" placeholder='Search posts...'>")
            html.append("  </div>")
            html.append("  <div class='list-view'>")
            
            # Sort by date
            sorted_items = sorted(
                [item for item in data if isinstance(item, dict)],
                key=lambda x: x.get('timestamp', ''),
                reverse=True
            )
            
            # Add list items
            for item in sorted_items:
                caption = item.get("caption", "")
                likes = item.get("likesCount", 0)
                comments = item.get("commentsCount", 0)
                timestamp = item.get("timestamp", "")
                username = item.get("ownerUsername", "")
                url = item.get("url", "")
                post_type = item.get("type", "Post")
                
                # Format values
                safe_caption = caption.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                
                # Format date
                formatted_date = timestamp
                if timestamp and isinstance(timestamp, str):
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        formatted_date = dt.strftime("%Y-%m-%d %H:%M")
                    except:
                        pass
                
                html.append("    <div class='list-item'>")
                html.append(f"      <span class='tag'>{post_type}</span>")
                html.append(f"      <div class='list-caption'>{safe_caption}</div>")
                html.append("      <div class='list-meta'>")
                html.append("        <div class='likes-comments'>")
                html.append(f"          <span><svg width='16' height='16' viewBox='0 0 24 24' fill='none' xmlns='http://www.w3.org/2000/svg'><path d='M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z' fill='var(--accent1)'/></svg> {likes:,}</span>")
                html.append(f"          <span><svg width='16' height='16' viewBox='0 0 24 24' fill='none' xmlns='http://www.w3.org/2000/svg'><path d='M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v10z' fill='var(--secondary)'/></svg> {comments:,}</span>")
                html.append("        </div>")
                html.append(f"        <span>{formatted_date}</span>")
                html.append(f"        <a href='https://instagram.com/{username}/' target='_blank'>@{username}</a>")
                html.append(f"        <a href='{url}' target='_blank'>View on Instagram</a>")
                html.append("      </div>")
                html.append("    </div>")
            
            html.append("  </div>")
            html.append("</div>")
            
            # Close HTML
            html.append("</div>")
            html.append("</body>")
            html.append("</html>")
            
            # Write HTML to file
            print(f"HTML generation complete. Writing {len(html)} lines to file...")
            try:
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write("\n".join(html))
                print(f"✅ Saved HTML Table to {html_path}")
                # Check file exists and has content
                if os.path.exists(html_path):
                    file_size = os.path.getsize(html_path)
                    print(f"  ✓ HTML file created successfully: {html_path} ({file_size} bytes)")
                else:
                    print(f"  ✗ HTML file not found after writing: {html_path}")
                results["html"] = html_path
            except Exception as write_error:
                print(f"❌ Failed to write HTML file: {str(write_error)}")
                import traceback
                traceback.print_exc()
        except Exception as e:
            print(f"❌ Failed to generate HTML: {str(e)}")
            import traceback
            traceback.print_exc()
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Instagram Scraper using Apify")
    parser.add_argument("username", help="Instagram username to scrape")
    parser.add_argument("--api-token", required=True, help="Your Apify API token")
    parser.add_argument("--format", default="html,json,csv", help="Output format(s), comma-separated: html,json,csv")
    args = parser.parse_args()
    
    username = args.username
    api_token = args.api_token
    
    # Parse formats
    formats = [fmt.strip().lower() for fmt in args.format.split(",")]
    
    # Create output folder
    output_folder = create_output_folder(username)
    print(f"Created output folder: {output_folder}")
    
    # Run the scraper
    data = run_instagram_scraper(api_token, username)
    
    if data and len(data) > 0:
        print(f"Processing {len(data)} items...")
        # Save the data in requested formats
        saved_files = save_data(data, output_folder, username, formats)
        
        print(f"\n✅ Successfully retrieved Instagram data for {username}")
        print(f"Found {len(data)} items")
        print(f"Output saved to {output_folder}")
        
        # Print summary of saved files
        print("\n📁 Saved in the following formats:")
        for fmt, path in saved_files.items():
            print(f"  - {fmt.upper()}: {os.path.basename(path)}")
            # Verify file exists
            if os.path.exists(path):
                print(f"    ✓ File exists: {path} ({os.path.getsize(path)} bytes)")
            else:
                print(f"    ✗ File does not exist: {path}")
    else:
        print(f"\n❌ Failed to retrieve any Instagram data for {username}")

if __name__ == "__main__":
    main()