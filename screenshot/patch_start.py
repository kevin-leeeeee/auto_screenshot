import pathlib
import sys

# Locate file
p = pathlib.Path('main_playwright.py')
if not p.exists():
    print("File not found")
    sys.exit(1)

lines = p.read_text(encoding='utf-8').splitlines()

start_idx = -1
end_idx = -1

# Look for async with async_playwright
for i, line in enumerate(lines):
    if 'async with async_playwright() as p:' in line:
        start_idx = i
    # Look for loop start
    if 'for idx, (url, note) in enumerate(urls, start=1):' in line and (start_idx != -1 and i > start_idx):
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    print(f'Found block: {start_idx} to {end_idx}')
    
    indent = '    '
    sub_indent = '        '
    # New Content
    new_block = [
        indent + 'async with async_playwright() as p:',
        sub_indent + 'proc = None',
        sub_indent + 'browser = None',
        sub_indent + 'context = None',
        sub_indent + 'page = None',
        '',
        sub_indent + 'try:',
        sub_indent + '    if cfg.cdp_mode:',
        sub_indent + '        logger.info("Starting Chrome in CDP Mode (Port 9222)...")',
        sub_indent + '        proc = launch_system_chrome_cdp(CHROME_USER_DATA_DIR)',
        sub_indent + '        # Give it a moment to start',
        sub_indent + '        await asyncio.sleep(3)',
        sub_indent + '        try:',
        sub_indent + '            browser = await p.chromium.connect_over_cdp("http://localhost:9222")',
        sub_indent + '            context = browser.contexts[0]',
        sub_indent + '            if context.pages:',
        sub_indent + '                page = context.pages[0]',
        sub_indent + '            else:',
        sub_indent + '                page = await context.new_page()',
        sub_indent + '        except Exception as e:',
        sub_indent + '            logger.error(f"CDP Connect Failed: {e}")',
        sub_indent + '            if proc: proc.kill()',
        sub_indent + '            return',
        sub_indent + '    else:',
        sub_indent + '        context = await launch_context(p, headless=cfg.headless) # Default Headless',
        sub_indent + '        page = await context.new_page()',
        sub_indent + '        ',
        sub_indent + '        # Only inject stealth scripts in standard mode (CDP is naturally stealthy)',
        sub_indent + '        for script in STEALTH_SCRIPTS:',
        sub_indent + '            await page.add_init_script(script)',
        '',
        sub_indent + '    page.set_default_navigation_timeout(NAV_TIMEOUT_MS)',
        ''
    ]
    
    # Check lines range. The loop line is end_idx.
    # We replace from start_idx to end_idx (exclusive of end_idx?)
    # Python slice [start:end] excludes end.
    # enumerate lines includes the loop line.
    # Original content ends with `page.set_default_navigation_timeout(NAV_TIMEOUT_MS)`.
    # And then the loop.
    
    final_lines = lines[:start_idx] + new_block + lines[end_idx:]
    
    p.write_text('\n'.join(final_lines), encoding='utf-8')
    print('Start Block Patched successfully.')
else:
    print('Start Block not found.')
