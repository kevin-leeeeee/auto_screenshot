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

for i, line in enumerate(lines):
    if '# End Loop' in line:
        start_idx = i
    if 'print("Run finished.")' in line and (start_idx != -1 and i > start_idx):
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    print(f'Found block: {start_idx} to {end_idx}')
    
    indent = '        '
    # New Content
    # Start after "# End Loop"
    new_block = [
        indent + '# End Loop',
        indent + 'logger.info("Closing browser...")',
        indent + 'try:',
        indent + '    if context: await context.close()',
        indent + '    if browser: await browser.close()',
        indent + 'except Exception: pass',
        '',
        indent + 'if proc:',
        indent + '    logger.info("Terminating System Chrome...")',
        indent + '    try: proc.kill()',
        indent + '    except: pass',
        '',
        indent + 'flush_done(force=True)',
        indent + 'print("Run finished.")'
    ]
    
    # Check if lines match structure to avoid damaging if slightly different
    # But replacing from End Loop to Run finished is safe enough.
    
    final_lines = lines[:start_idx] + new_block + lines[end_idx+1:]
    
    p.write_text('\n'.join(final_lines), encoding='utf-8')
    print('Cleanup Patched successfully.')
else:
    print('Cleanup Block not found.')
