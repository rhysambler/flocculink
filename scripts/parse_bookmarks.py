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

def count_bookmarks(element):
    """Recursively counts all bookmarks inside a folder."""
    count = 0
    for child in element:
        if child.tag == "bookmark":
            count += 1
        elif child.tag == "folder":
            count += count_bookmarks(child)
    return count

def parse_xbel_folder(element, depth=0):
    html_out = ""
    for child in element:
        if child.tag == "folder":
            title_elem = child.find("title")
            folder_title = title_elem.text if title_elem is not None else "Bookmarks"
            item_count = count_bookmarks(child)
            
            # Sub-folders expand by default if preferred, root categories start collapsed
            open_attr = "" if depth == 0 else "open"
            
            html_out += f'<details class="bookmark-category" {open_attr}>\n'
            html_out += f'  <summary class="category-header">\n'
            html_out += f'    <span class="folder-title">{folder_title}</span>\n'
            html_out += f'    <span class="badge">{item_count}</span>\n'
            html_out += f'  </summary>\n'
            html_out += f'  <div class="category-content">\n'
            
            # Recurse for sub-folders/links
            sub_content = parse_xbel_folder(child, depth + 1)
            
            # Separate direct links into a grid container if present
            if '<li>' in sub_content:
                html_out += f'    <ul class="bookmark-grid">\n{sub_content}    </ul>\n'
            else:
                html_out += sub_content
                
            html_out += f'  </div>\n'
            html_out += f'</details>\n'
            
        elif child.tag == "bookmark":
            url = child.attrib.get("href", "#")
            title_elem = child.find("title")
            title = title_elem.text if title_elem is not None else url
            domain = get_domain(url)
            
            favicon_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=32" if domain else ""
            img_tag = f'<img src="{favicon_url}" alt="" class="favicon" /> ' if favicon_url else ""
            
            html_out += f'      <li>{img_tag}<a href="{url}" target="_blank" rel="noopener">{title}</a></li>\n'
            
    return html_out

def main():
    if not os.path.exists(XBEL_PATH):
        print(f"{XBEL_PATH} not found. Skipping build.")
        return

    tree = ET.parse(XBEL_PATH)
    root = tree.getroot()

    bookmarks_html = parse_xbel_folder(root)

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Link Directory</title>
    <style>
        :root {{
            --bg: #f4f5f7;
            --card-bg: #ffffff;
            --text: #172b4d;
            --text-subtle: #6b778c;
            --border: #dfe1e6;
            --accent: #0969da;
            --hover-bg: #f8f9fa;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0 auto;
            max-width: 1200px;
            padding: 2rem 1rem;
            background: var(--bg);
            color: var(--text);
        }}
        h1 {{
            font-size: 1.75rem;
            margin-bottom: 1.5rem;
        }}
        
        /* Details & Summary Styling */
        details.bookmark-category {{
            background: var(--card-bg);
            border-radius: 8px;
            border: 1px solid var(--border);
            margin-bottom: 0.75rem;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            overflow: hidden;
            transition: border-color 0.2s ease;
        }}
        details.bookmark-category[open] {{
            border-color: #c1c7d0;
        }}
        summary.category-header {{
            padding: 1rem 1.25rem;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            user-select: none;
            display: flex;
            align-items: center;
            justify-content: space-between;
            list-style: none; /* Removes default disclosure triangle */
        }}
        summary.category-header::-webkit-details-marker {{
            display: none; /* Removes Webkit disclosure triangle */
        }}
        summary.category-header::before {{
            content: "▶";
            font-size: 0.75rem;
            margin-right: 0.75rem;
            color: var(--text-subtle);
            transition: transform 0.2s ease;
        }}
        details[open] > summary.category-header::before {{
            transform: rotate(90deg);
        }}
        summary.category-header:hover {{
            background: var(--hover-bg);
        }}
        
        /* Badges & Content */
        .folder-title {{
            flex-grow: 1;
        }}
        .badge {{
            background: #ebecf0;
            color: var(--text-subtle);
            font-size: 0.8rem;
            font-weight: 500;
            padding: 0.2rem 0.55rem;
            border-radius: 12px;
        }}
        .category-content {{
            padding: 0 1.25rem 1.25rem 1.25rem;
            border-top: 1px solid #f4f5f7;
        }}
        
        /* Grid for Bookmarks */
        ul.bookmark-grid {{
            list-style: none;
            padding: 0;
            margin: 0;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
            gap: 0.5rem;
            margin-top: 0.75rem;
        }}
        ul.bookmark-grid li {{
            display: flex;
            align-items: center;
            background: var(--hover-bg);
            padding: 0.5rem 0.75rem;
            border-radius: 6px;
            border: 1px solid var(--border);
        }}
        ul.bookmark-grid li:hover {{
            background: #e9ecef;
        }}
        .favicon {{
            width: 16px;
            height: 16px;
            margin-right: 8px;
            flex-shrink: 0;
        }}
        ul.bookmark-grid a {{
            text-decoration: none;
            color: var(--accent);
            font-weight: 500;
            font-size: 0.95rem;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
    </style>
</head>
<body>
    <h1>Bookmarks</h1>
    {bookmarks_html}
</body>
</html>"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(full_html)
    print("Updated index.html successfully with collapsible sections.")

if __name__ == "__main__":
    main()
