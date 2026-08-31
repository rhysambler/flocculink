def render_folder(folder_data):
    html = []
    folder_name = folder_data.get('title', 'Folder')
    bookmarks = folder_data.get('bookmarks', [])
    subfolders = folder_data.get('subfolders', [])
    total_count = folder_data.get('count', len(bookmarks))

    html.append(f'<details class="bookmark-category">')
    html.append(f'  <summary class="category-header">')
    html.append(f'    <span class="folder-title">{folder_name}</span>')
    html.append(f'    <span class="badge">{total_count}</span>')
    html.append(f'  </summary>')
    html.append(f'  <div class="category-content">')

    # 1. Render links in a clean <ul> list
    if bookmarks:
        html.append('    <ul class="bookmark-grid">')
        for b in bookmarks:
            title = b.get('title', 'Link')
            url = b.get('url', '#')
            domain = b.get('domain', '')
            html.append(f'      <li>')
            html.append(f'        <img src="https://www.google.com/s2/favicons?domain={domain}&sz=32" alt="" class="favicon" />')
            html.append(f'        <a href="{url}" target="_blank" rel="noopener" class="bookmark-link">{title}</a>')
            html.append(f'        <button class="copy-btn" onclick="copyUrl(this, \'{url}\')" title="Copy URL">')
            html.append(f'          <svg class="copy-icon" viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>')
            html.append(f'        </button>')
            html.append(f'      </li>')
        html.append('    </ul>')

    # 2. Render subfolders sequentially below the link list (OUTSIDE the <ul>)
    if subfolders:
        for sub in subfolders:
            html.append(render_folder(sub))

    html.append('  </div>')
    html.append('</details>')
    return '\n'.join(html)
