import xml.etree.ElementTree as ET
import os

XBEL_PATH = "bookmarks.xbel"
OUTPUT_HTML = "index.html"

def get_domain(url):
    try:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        return domain if domain else ""
    except Exception:
        return ""

def parse_xbel_folder(element):
    html_out = ""
    for child in element:
        if child.tag == "folder":
            title_elem = child.find("title")
            folder_title = title_elem.text if title_elem is not None else "Bookmarks"
            html_out += f'<div class="bookmark-category"><h2>{folder_title}</h2><ul>\n'
            html_out += parse_xbel_folder(child)
            html_out += '</ul></div>\n'
        elif child.tag == "bookmark":
            url = child.attrib.get("href", "#")
            title_elem = child.find("title")
            title = title_elem.text if title_elem is not None else url
            domain = get_domain(url)
            
            # Inject Google Favicon API URL
            favicon_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=32" if domain else ""
            img_tag = f'<img src="{favicon_url}" alt="" class="favicon" /> ' if favicon_url else ""
            
            html_out += f'  <li>{img_tag}<a href="{url}" target="_blank" rel="noopener">{title}</a></li>\n'
    return html_out

def main():
    if not os.path.exists(XBEL_PATH):
        print(f"{XBEL_PATH} not found. Skipping build.")
        return

    tree = ET.parse(XBEL_PATH)
    root = tree.getroot()

    bookmarks_html = parse_xbel_folder(root)

    # Shell HTML template
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Link Directory</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 2rem; background: #f4f5f7; color: #333; }}
        .bookmark-category {{ background: #fff; padding: 1.5rem; margin-bottom: 1.5rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        h2 {{ margin-top: 0; font-size: 1.25rem; color: #111; border-bottom: 1px solid #eee; padding-bottom: 0.5rem; }}
        ul {{ list-style: none; padding: 0; margin: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 0.75rem; }}
        li {{ display: flex; align-items: center; background: #f8f9fa; padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid #e9ecef; }}
        li:hover {{ background: #e9ecef; }}
        .favicon {{ width: 16px; height: 16px; margin-right: 8px; flex-shrink: 0; }}
        a {{ text-decoration: none; color: #0969da; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    </style>
</head>
<body>
    <h1>Bookmarks</h1>
    {bookmarks_html}
</body>
</html>"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(full_html)
    print("Updated index.html successfully.")

if __name__ == "__main__":
    main()
