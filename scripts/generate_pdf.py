import markdown
import weasyprint
import base64
import os
import re

with open('docs/preprint.md', 'r') as f:
    md_content = f.read()

# Embed images as base64
def embed_image(match):
    alt   = match.group(1)
    path  = match.group(2)
    abs_path = os.path.join(os.path.dirname('docs/preprint.md'), path)
    if os.path.exists(abs_path):
        with open(abs_path, 'rb') as f:
            data = base64.b64encode(f.read()).decode()
        return f'![{alt}](data:image/png;base64,{data})'
    return match.group(0)

md_content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', embed_image, md_content)

html_content = markdown.markdown(md_content, extensions=['tables'])

styled_html = f'''<!DOCTYPE html>
<html><head><meta charset='utf-8'>
<style>
body {{ font-family: Arial, sans-serif; font-size: 11px; line-height: 1.6;
       max-width: 800px; margin: 40px auto; padding: 0 20px; color: #333; }}
h1 {{ font-size: 16px; font-weight: bold; margin-bottom: 10px; }}
h2 {{ font-size: 13px; font-weight: bold; margin-top: 20px;
     border-bottom: 1px solid #ccc; padding-bottom: 4px; }}
h3 {{ font-size: 12px; font-weight: bold; margin-top: 15px; }}
table {{ border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 10px; }}
th, td {{ border: 1px solid #ddd; padding: 4px 8px; text-align: left; }}
th {{ background-color: #f5f5f5; }}
code {{ background: #f5f5f5; padding: 2px 4px; border-radius: 3px; font-size: 10px; }}
hr {{ border: none; border-top: 1px solid #ccc; margin: 20px 0; }}
img {{ max-width: 100%; height: auto; margin: 10px 0; }}
</style></head><body>
{html_content}
</body></html>'''

weasyprint.HTML(string=styled_html).write_pdf('docs/preprint.pdf')
size = os.path.getsize('docs/preprint.pdf') / 1024
print(f'[OK] PDF saved: docs/preprint.pdf ({size:.0f} KB)')