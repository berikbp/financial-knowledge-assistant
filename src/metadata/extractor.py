import re
from pathlib import Path
from pypdf import PdfReader


def infer_source_from_path(path: str) -> str:
    path_lower = path.lower()

    if "nationalbank" in path_lower:
        return "NationalBank"

    if "halykbank" in path_lower:
        return "HalykBank"

    if "banking_regulations" in path_lower:
        return "BankingRegulation"

    return "Unknown"


def infer_language_from_text(text: str) -> str:
    """
    Detect language using actual characters.
    If there are many Cyrillic characters, treat it as Russian.
    Otherwise, English.
    """

    sample = text[:3000].lower()

    cyrillic_chars = re.findall(r"[а-яәіңғүұқөһ]", sample)

    if len(cyrillic_chars) > 50:
        return "ru"

    return "en"


def infer_year_from_filename_or_text(path: str, text: str) -> int | None:
    """
    Prefer year from filename/path.
    If filename has no year, then inspect the beginning of the document.
    """

    path_years = re.findall(r"(20[0-3][0-9])", path)

    if path_years:
        return int(path_years[-1])

    text_sample = text[:5000]

    text_years = re.findall(r"(20[0-3][0-9])", text_sample)

    if not text_years:
        return None

    year_counts = {}

    for year in text_years:
        year_int = int(year)
        year_counts[year_int] = year_counts.get(year_int, 0) + 1

    return max(year_counts, key=year_counts.get)


def infer_document_type(path: str, text: str) -> str:
    combined = f"{path}\n{text[:5000]}".lower()
    filename = Path(path).name.lower()
    compact_filename = re.sub(r"[\s_.-]+", "", filename)

    # Laws / regulations first
    if "z950002444" in filename or "о банках и банковской деятельности" in combined:
        return "banking_law"

    if "z090000191" in filename or "отмыванию доходов" in combined:
        return "aml_law"

    # Very specific report types first
    if "финансовой стабильности" in combined or "financial stability" in combined:
        return "financial_stability_report"

    if "платежный баланс" in combined:
        return "balance_of_payments"

    if "внешний долг" in combined:
        return "external_debt"

    if "macro market overview" in combined or "macro & market overview" in combined:
        return "macro_market_overview"

    # Explicit Halyk financial-statement filenames
    if (
        "financial-statement" in filename
        or "financial_statement" in filename
        or "financial statement" in filename
    ):
        return "financial_statement"

    if "годовой отчет" in combined or "annual report" in combined:
        return "annual_report"

    if (
        "consolidated financial statements" in combined
        or "консолидированная финансовая отчетность" in combined
        or "консолидированнаяфинансоваяотчетность" in compact_filename
    ):
        return "financial_statement"

    # Monetary policy after financial stability
    if "дкп" in combined or "денежно-кредитной политике" in combined:
        return "monetary_policy_report"

    # General inflation
    if "инфляц" in combined or "inflation" in combined:
        return "inflation_report"

    return "unknown"


def read_pdf_internal_metadata(path: str) -> dict:
    """
    Read built-in PDF metadata.
    Useful for debugging, but not reliable enough as main metadata.
    """

    try:
        reader = PdfReader(path)
        raw_metadata = reader.metadata or {}

        return {
            str(key): str(value)
            for key, value in raw_metadata.items()
        }

    except Exception:
        return {}


def build_document_metadata(path: str, document_name: str, text: str) -> dict:
    return {
        "source": infer_source_from_path(path),
        "document_name": document_name.strip(),
        "language": infer_language_from_text(text),
        "year": infer_year_from_filename_or_text(path, text),
        "document_type": infer_document_type(path, text),
        "path": path,
    }
