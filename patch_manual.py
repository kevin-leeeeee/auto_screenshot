import pathlib
import sys
import os

# Locate file
p = pathlib.Path('main_playwright.py')
if not p.exists():
    print("File not found")
    sys.exit(1)

lines = p.read_text(encoding='utf-8').splitlines()

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if 'Switching to INTERACTIVE mode for manual solve' in line:
        start_idx = i
    if 'Manual solve process failed' in line and (start_idx != -1 and i > start_idx):
        # The block ends about 8 lines after this
        end_idx = i + 8
        break

if start_idx != -1 and end_idx != -1:
    print(f'Found block: {start_idx} to {end_idx}')
    
    # New Content
    indent = '                '
    new_block = [
        indent + 'logger.info("Switching to INTERACTIVE mode for manual solve...")',
        indent + 'if cfg.cdp_mode:',
        indent + '    # CDP Mode is already visible and interactive',
        indent + '    if page:',
        indent + '        try: await page.bring_to_front()',
        indent + '        except: pass',
        indent + '    await wait_for_enter(">>> 請在瀏覽器中完成驗證或登入，完成後請回到此視窗按 Enter 繼續 <<<")',
        indent + '    ts = datetime.now().strftime("%Y%m%d_%H%M%S")',
        indent + '    fn = f"{idx:03d}_{ts}_MANUAL_{safe_filename(page.url)}.png"',
        indent + '    out = cfg.output_dir / fn',
        indent + '    try:',
        indent + '        await page.screenshot(path=out, full_page=True)',
        indent + '        logger.info(f"  Manual Snapshot: {out}")',
        indent + '    except: pass',
        indent + '    done.add(url)',
        indent + '    processed_this_run += 1',
        indent + '    flush_done()',
        indent + '    continue',
        indent + 'else:',
        indent + '    try:',
        indent + '        await context.close()',
        indent + '        # Relaunch Visible',
        indent + '        context = await launch_context(p, headless=False)',
        indent + '        page = await context.new_page()',
        indent + '        # Stealth Injection for Visible Mode',
        indent + '        for script in STEALTH_SCRIPTS:',
        indent + '            await page.add_init_script(script)',
        indent + '        page.set_default_navigation_timeout(NAV_TIMEOUT_MS)',
        indent + '        try: await page.goto(current_url, wait_until="domcontentloaded")',
        indent + '        except: pass',
        indent + '        await wait_for_enter(">>> 請在瀏覽器中完成驗證或登入，完成後請回到此視窗按 Enter 繼續 <<<")',
        indent + '        ts = datetime.now().strftime("%Y%m%d_%H%M%S")',
        indent + '        fn = f"{idx:03d}_{ts}_MANUAL_{safe_filename(page.url)}.png"',
        indent + '        out = cfg.output_dir / fn',
        indent + '        try:',
        indent + '            await page.screenshot(path=out, full_page=True)',
        indent + '            logger.info(f"  Manual Snapshot: {out}")',
        indent + '        except: pass',
        indent + '        done.add(url)',
        indent + '        processed_this_run += 1',
        indent + '        flush_done()',
        indent + '        await context.close()',
        indent + '        context = await launch_context(p, headless=cfg.headless)',
        indent + '        page = await context.new_page()',
        indent + '        for script in STEALTH_SCRIPTS:',
        indent + '            await page.add_init_script(script)',
        indent + '        page.set_default_navigation_timeout(NAV_TIMEOUT_MS)',
        indent + '        continue',
        indent + '    except Exception as e:',
        indent + '        logger.error(f"Manual solve process failed: {e}")',
        indent + '        try: await context.close()',
        indent + '        except: pass',
        indent + '        context = await launch_context(p, headless=cfg.headless)',
        indent + '        page = await context.new_page()',
        indent + '        continue'
    ]
    
    # Replace (start_idx is included, end_idx is included)
    final_lines = lines[:start_idx] + new_block + lines[end_idx+1:]
    
    p.write_text('\n'.join(final_lines), encoding='utf-8')
    print('Patched successfully.')
else:
    print('Block not found.')
