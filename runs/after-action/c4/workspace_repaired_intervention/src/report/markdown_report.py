from src.main import render_client_md, render_internal_md


def generate_markdown_report(correlated, kind: str = "client", warnings=None) -> str:
    warnings = warnings or []
    if kind == "internal":
        return render_internal_md(correlated, warnings)
    return render_client_md(correlated, warnings)
