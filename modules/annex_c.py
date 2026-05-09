import re
import requests
import fitz


FIFA_REGULATIONS_PDF_URL = (
    "https://digitalhub.fifa.com/m/636f5c9c6f29771f/original/"
    "FWC2026_regulations_EN.pdf"
)

ANNEX_C_COLUMNS = ["1A", "1B", "1D", "1E", "1G", "1I", "1K", "1L"]


_cached_mapping = None


def get_annex_c_mapping():
    global _cached_mapping

    if _cached_mapping is not None:
        return _cached_mapping

    response = requests.get(FIFA_REGULATIONS_PDF_URL, timeout=30)
    response.raise_for_status()

    doc = fitz.open(stream=response.content, filetype="pdf")

    text_parts = []

    for page_index in range(len(doc)):
        text_parts.append(doc[page_index].get_text("text"))

    text = "\n".join(text_parts)

    mapping = parse_annex_c_text(text)

    if len(mapping) != 495:
        raise ValueError(
            f"Annex C mapping bevat {len(mapping)} combinaties in plaats van 495."
        )

    _cached_mapping = mapping
    return mapping


def parse_annex_c_text(text):
    mapping = {}

    text = text.replace("\u2011", "-")
    text = text.replace("\u2013", "-")
    text = text.replace("\u2014", "-")

    pattern = re.compile(
        r"\b(\d{1,3})\s+"
        r"(3[A-L])\s+"
        r"(3[A-L])\s+"
        r"(3[A-L])\s+"
        r"(3[A-L])\s+"
        r"(3[A-L])\s+"
        r"(3[A-L])\s+"
        r"(3[A-L])\s+"
        r"(3[A-L])"
    )

    for match in pattern.finditer(text):
        option_number = int(match.group(1))

        if option_number < 1 or option_number > 495:
            continue

        values = list(match.groups()[1:])

        qualified_groups = "".join(sorted([v[-1] for v in values]))

        mapping[qualified_groups] = {
            ANNEX_C_COLUMNS[i]: values[i]
            for i in range(8)
        }

    return mapping
