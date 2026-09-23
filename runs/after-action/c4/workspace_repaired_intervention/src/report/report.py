from src.report.markdown_report import generate_markdown_report
from src.report.pdf_report import generate_pdf_report


def generate_report(correlated, format: str = "markdown", kind: str = "client", warnings=None) -> str:
    if format in ("markdown", "md"):
        return generate_markdown_report(correlated, kind=kind, warnings=warnings)
    if format in ("html", "pdf"):
        # PDF optional; HTML satisfies acceptance "PDF or HTML"
        return generate_pdf_report(correlated, kind=kind, warnings=warnings)
    raise ValueError(f"Unsupported report format: {format}")
