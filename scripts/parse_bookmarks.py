import xml.etree.ElementTree as ET
import os
from urllib.parse import urlparse

XBEL_PATH = "bookmarks.xbel"
OUTPUT_HTML = "index.html"

def get_domain(url):
    """Extracts domain from URL, removing 'www.' if present."""
    try:
        domain = urlparse(url).netloc
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return ""

def generate_fallback_name(domain):
    """Generates a clean name from the domain when a bookmark title is blank."""
    if not domain:
        return "Untitled Link"
    parts = domain.split('.')
    name = parts[0] if len(parts) > 1 else domain
    return name.capitalize()

def count_bookmarks(element):
    """Recursively counts valid bookmarks inside a folder element."""
    count = 0
    for child in element:
        if child.tag == "bookmark":
            count += 1
        elif child.tag == "folder":
            count += count_bookmarks(child)
    return count

def parse_xbel_folder(element, depth=0):
    """Recursively parses XML folders into HTML <details> components."""
    html_out = ""
    for child in element:
        if child.tag == "folder":
            title_elem = child.find("title")
            folder_title = title_elem.text.strip() if (title_elem is not None and title_elem.text) else "Bookmarks"
            
            item_count = count_bookmarks(child)
            if item_count == 0:
                continue

            # Root folders start collapsed to save real estate; sub-folders expand automatically
            open_attr = "" if depth == 0 else "open"
            
            html_out += f'<details class="bookmark-category" {open_attr}>\n'
            html_out += f'  <summary class="category-header">\n'
            html_out += f'    <span class="folder-title">{folder_title}</span>\n'
            html_out += f'    <span class="badge">{item_count}</span>\n'
            html_out += f'  </summary>\n'
            html_out += f'  <div class="category-content">\n'
            
            sub_content = parse_xbel_folder(child, depth + 1)
            
            if '<li>' in sub_content:
                html_out += f'    <ul class="bookmark-grid">\n{sub_content}    </ul>\n'
            else:
                html_out += sub_content
                
            html_out += f'  </div>\n'
            html_out += f'</details>\n'
            
        elif child.tag == "bookmark":
            url = child.attrib.get("href", "#")
            domain = get_domain(url)
            
            title_elem = child.find("title")
            raw_title = title_elem.text.strip() if (title_elem is not None and title_elem.text) else ""
            
            # Fallback auto-naming if title is missing/empty
            title = raw_title if raw_title else generate_fallback_name(domain)
            
            favicon_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=32" if domain else ""
            img_tag = f'<img src="{favicon_url}" alt="" class="favicon" /> ' if favicon_url else ""
            
            # SVG Copy Icon
            copy_svg = '''<svg class="copy-icon" viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>'''
            
            html_out += f'      <li>'
            html_out += f'{img_tag}<a href="{url}" target="_blank" rel="noopener" class="bookmark-link">{title}</a>'
            html_out += f'<button class="copy-btn" onclick="copyUrl(this, \'{url}\')" title="Copy URL">{copy_svg}</button>'
            html_out += f'</li>\n'
            
    return html_out

def main():
    if not os.path.exists(XBEL_PATH):
        print(f"Error: {XBEL_PATH} not found.")
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
            max-width: 900px; /* Constrains folders to a clean, single-column alignment */
            padding: 2rem 1rem;
            background: var(--bg);
            color: var(--text);
        }}
        h1 {{
            font-size: 1.75rem;
            margin-bottom: 1.5rem;
        }}

        /* Single Column Stack for Category Folders */
        details.bookmark-category {{
            background: var(--card-bg);
            border-radius: 8px;
            border: 1px solid var(--border);
            margin-bottom: 0.75rem;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            overflow: hidden;
            width: 100%;
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
            list-style: none;
        }}
        summary.category-header::-webkit-details-marker {{
            display: none;
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

        /* Links Grid inside Opened Folders */
        ul.bookmark-grid {{
            list-style: none;
            padding: 0;
            margin: 0;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
            gap: 0.5rem;
            margin-top: 0.75rem;
        }}
        ul.bookmark-grid li {{
            display: flex;
            align-items: center;
            justify-content: space-between;
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
        a.bookmark-link {{
            text-decoration: none;
            color: var(--accent);
            font-weight: 500;
            font-size: 0.95rem;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            flex-grow: 1;
            margin-right: 8px;
        }}

        /* Copy Button Styling */
        .copy-btn {{
            background: transparent;
            border: none;
            cursor: pointer;
            padding: 4px;
            border-radius: 4px;
            color: var(--text-subtle);
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }}
        .copy-btn:hover {{
            background: #dfe1e6;
            color: var(--text);
        }}
        .copy-btn.copied {{
            color: #22c55e;
        }}
    </style>
</head>
<body>
    <h1>Bookmarks Directory</h1>
    {bookmarks_html}

    <script>
    function copyUrl(button, url) {{
        navigator.clipboard.writeText(url).then(() => {{
            button.classList.add('copied');
            button.innerHTML = '<svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>';
            setTimeout(() => {{
                button.classList.remove('copied');
                button.innerHTML = '<svg class="copy-icon" viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';
            }}, 1500);
        }}).catch(err => {{
            console.error('Failed to copy: ', err);
        }});
    }}
    </script>
</body>
</html>"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(full_html)
    print("Successfully built index.html with single-column layout, full Bookmarks Bar support, and copy buttons.")

if __name__ == "__main__":
    main()
