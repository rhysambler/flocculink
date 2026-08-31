import os
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

# File paths
XBEL_PATH = "bookmarks.xbel"
OUTPUT_HTML = "index.html"

# Dynamic Versioning (Uses env variable from GitHub Action, or generates local fallback)
BUILD_VERSION = os.getenv("BUILD_VERSION")
if not BUILD_VERSION:
    import datetime
    today_str = datetime.datetime.now().strftime("%Y%m%d")
    BUILD_VERSION = f"v0.1.{today_str}.dev"

def extract_domain(url):
    try:
        parsed = urlparse(url)
        return parsed.netloc or parsed.path.split('/')[0]
    except Exception:
        return ""

def parse_xbel_element(element):
    """Recursively parse XBEL elements into structured dicts."""
    folders = []
    bookmarks = []

    for child in element:
        # Strip XML namespace if present
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag

        if tag == "folder":
            title_elem = child.find("{http://www.python.org/dtds/xbel-1.0.dtd}title")
            if title_elem is None:
                title_elem = child.find("title")
            folder_title = title_elem.text if title_elem is not None and title_elem.text else "Folder"

            sub_bookmarks, sub_folders = parse_xbel_element(child)
            
            # Count total links inside this folder tree
            total_count = len(sub_bookmarks) + sum(sf['count'] for sf in sub_folders)

            folders.append({
                'title': folder_title,
                'bookmarks': sub_bookmarks,
                'subfolders': sub_folders,
                'count': total_count
            })

        elif tag == "bookmark":
            url = child.attrib.get('href', '#')
            title_elem = child.find("{http://www.python.org/dtds/xbel-1.0.dtd}title")
            if title_elem is None:
                title_elem = child.find("title")
            bookmark_title = title_elem.text if title_elem is not None and title_elem.text else url

            bookmarks.append({
                'title': bookmark_title,
                'url': url,
                'domain': extract_domain(url)
            })

    return bookmarks, folders

def render_folder_html(folder_data, is_root=False):
    """Recursively render folders with proper DOM hierarchy and single-column layout."""
    html = []
    folder_title = folder_data['title']
    bookmarks = folder_data['bookmarks']
    subfolders = folder_data['subfolders']
    count = folder_data['count']

    open_attr = " open" if is_root else ""

    html.append(f'<details class="bookmark-category"{open_attr}>')
    html.append(f'  <summary class="category-header">')
    html.append(f'    <span class="folder-title">{folder_title}</span>')
    html.append(f'    <span class="badge">{count}</span>')
    html.append(f'  </summary>')
    html.append(f'  <div class="category-content">')

    # Render bookmarks as single-column vertical list
    if bookmarks:
        html.append('    <ul class="bookmark-list">')
        for b in bookmarks:
            title = b['title'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            url = b['url'].replace("'", "\\'")
            domain = b['domain']
            html.append(f'      <li>')
            html.append(f'        <img src="https://www.google.com/s2/favicons?domain={domain}&sz=32" alt="" class="favicon" />')
            html.append(f'        <a href="{b["url"]}" target="_blank" rel="noopener" class="bookmark-link">{title}</a>')
            html.append(f'        <button class="copy-btn" onclick="copyUrl(this, \'{url}\')" title="Copy URL">')
            html.append(f'          <svg class="copy-icon" viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>')
            html.append(f'        </button>')
            html.append(f'      </li>')
        html.append('    </ul>')

    # Render subfolders cleanly below the link list (outside <ul>)
    if subfolders:
        for sub in subfolders:
            html.append(render_folder_html(sub, is_root=False))

    html.append('  </div>')
    html.append('</details>')

    return '\n'.join(html)

def generate_full_html(folders):
    folders_html = "\n".join([render_folder_html(f, is_root=True) for f in folders])

    html_document = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bookmarks Directory {BUILD_VERSION}</title>
    <!-- Favicon link -->
    <link rel="icon" type="image/x-icon" href="bookmark.ico">
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
            max-width: 800px;
            padding: 2rem 1rem;
            background: var(--bg);
            color: var(--text);
        }}
        .header-container {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.5rem;
            border-bottom: 2px solid var(--border);
            padding-bottom: 0.75rem;
        }}
        h1 {{
            font-size: 1.75rem;
            margin: 0;
        }}
        .version-tag {{
            font-size: 0.85rem;
            color: var(--text-subtle);
            font-family: monospace;
            background: #ebecf0;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
        }}

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
            padding: 0.85rem 1.25rem;
            font-size: 1.05rem;
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
            padding: 0.5rem 1.25rem 1.25rem 1.25rem;
            border-top: 1px solid #f4f5f7;
        }}

        /* STRICT SINGLE-COLUMN LAYOUT */
        ul.bookmark-list {{
            list-style: none;
            padding: 0;
            margin: 0.5rem 0;
            display: flex;
            flex-direction: column;
            gap: 0.4rem;
        }}
        ul.bookmark-list li {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: var(--hover-bg);
            padding: 0.5rem 0.75rem;
            border-radius: 6px;
            border: 1px solid var(--border);
            width: 100%;
            box-sizing: border-box;
        }}
        ul.bookmark-list li:hover {{
            background: #e9ecef;
        }}
        .favicon {{
            width: 16px;
            height: 16px;
            margin-right: 10px;
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
    <div class="header-container">
        <h1>Bookmarks Directory</h1>
        <span class="version-tag">{BUILD_VERSION}</span>
    </div>

    {folders_html}

    <script>
        function copyUrl(btn, url) {{
            navigator.clipboard.writeText(url).then(() => {{
                btn.classList.add('copied');
                setTimeout(() => btn.classList.remove('copied'), 1500);
            }}).catch(err => console.error('Copy failed:', err));
        }}
    </script>
</body>
</html>"""
    return html_document

def main():
    if not os.path.exists(XBEL_PATH):
        print(f"Error: Could not find '{XBEL_PATH}'")
        return

    tree = ET.parse(XBEL_PATH)
    root = tree.getroot()

    _, folders = parse_xbel_element(root)

    html_content = generate_full_html(folders)

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Successfully generated {OUTPUT_HTML} ({BUILD_VERSION})")

if __name__ == "__main__":
    main()
