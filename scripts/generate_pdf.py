import markdown
import weasyprint
import os

with open('docs/preprint.md', 'r') as f:
    md_content = f.read()

html_content = markdown.markdown(md_content, extensions=['tables'])

styled_html = f'''
<!DOCTYPE html>
<html>
<head>
<meta charset='utf-8'>
<style>
    body {{ font-family: Arial, sans-serif; font-size: 12px; line-height: 1.6;
            max-width: 800px; margin: 40px auto; padding: 0 20px; color: #333; }}
    h1 {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
    h2 {{ font-size: 15px; font-weight: bold; margin-top: 20px; border-bottom: 1px solid #ccc; }}
    h3 {{ font-size: 13px; font-weight: bold; margin-top: 15px; }}
    table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
    th, td {{ border: 1px solid #ddd; padding: 6px 10px; text-align: left; }}
    th {{ background-color: #f5f5f5; }}
    code {{ background: #f5f5f5; padding: 2px 4px; border-radius: 3px; }}
    hr {{ border: none; border-top: 1px solid #ccc; margin: 20px 0; }}
</style>
</head>
<body>
{html_content}
</body>
</html>
'''

weasyprint.HTML(string=styled_html).write_pdf('docs/preprint.pdf')
print('[OK] PDF saved to docs/preprint.pdf')