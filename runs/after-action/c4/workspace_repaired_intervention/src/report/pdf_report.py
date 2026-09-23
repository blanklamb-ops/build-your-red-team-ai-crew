"""HTML report stand-in for PDF (ACCEPTANCE allows PDF or HTML)."""

from src.main import md_to_html, render_client_md, render_internal_md


def generate_pdf_report(correlated, kind: str = "client", warnings=None) -> str:
    warnings = warnings or []
    if kind == "internal":
        md = render_internal_md(correlated, warnings)
        title = "Internal Learning Summary"
    else:
        md = render_client_md(correlated, warnings)
        title = "Client After-Action Report"
    return md_to_html(title, md)
