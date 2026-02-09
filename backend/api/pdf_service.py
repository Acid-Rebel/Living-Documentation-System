import markdown
from xhtml2pdf import pisa
import io

def convert_markdown_to_pdf(markdown_content, output_path):
    """
    Converts Markdown content to a PDF file.
    """
    # 1. Convert Markdown to HTML
    html_content = markdown.markdown(markdown_content)
    
    # 2. Add minimal CSS for better PDF rendering
    full_html = f"""
    <html>
    <head>
    <style>
        body {{ font-family: Helvetica, sans-serif; font-size: 10pt; line-height: 1.5; }}
        h1 {{ color: #2c3e50; font-size: 18pt; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
        h2 {{ color: #2980b9; font-size: 14pt; margin-top: 20px; }}
        h3 {{ color: #16a085; font-size: 12pt; }}
        code {{ font-family: Courier, monospace; background-color: #f4f4f4; padding: 2px 4px; }}
        pre {{ background-color: #f4f4f4; padding: 10px; border: 1px solid #ddd; word-wrap: break-word; white-space: pre-wrap; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 15px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
    </head>
    <body>
    {html_content}
    </body>
    </html>
    """

    # 3. Convert HTML to PDF
    try:
        with open(output_path, "wb") as f:
            pisa_status = pisa.CreatePDF(
                io.StringIO(full_html),
                dest=f
            )
        return not pisa_status.err
    except Exception as e:
        print(f"PDF generation failed: {e}")
        return False
