from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image
from weasyprint import HTML
from pypdf import PdfReader, PdfWriter
import io

BASE = Path(__file__).resolve().parents[1]
SOURCE_URL = "https://images.ctfassets.net/ss5kfr270og3/6ZboKn1oc54UJZkM4vpGfu/ae294d9c6cb303f9bf8c932e7b9bbb1a/WVA_Jerry_Thumbnail_600x400.png?fm=webp&q=60&w=1438"
SOURCE_PATH = BASE / "assets/company/jerry-plaid-customer-story.webp"
WORDMARK_PATH = BASE / "assets/brand/jerry-wordmark.png"

DOCUMENTS = {
    "resume.html": ("Russell-Dudek-Jerry-Resume.pdf", 2, "Russell Dudek Jerry Resume", "Senior Product Manager, Agentic AI candidate resume"),
    "cover-letter.html": ("Russell-Dudek-Jerry-Cover-Letter.pdf", 1, "Russell Dudek Jerry Cover Letter", "Senior Product Manager, Agentic AI candidate cover letter"),
    "interview-brief.html": ("Russell-Dudek-Jerry-Interview-Brief.pdf", 3, "Russell Dudek Jerry Interview Brief", "Interview thesis brief for Jerry Senior Product Manager, Agentic AI"),
    "90-day-plan.html": ("Russell-Dudek-Jerry-90-Day-Plan.pdf", 2, "Russell Dudek Jerry 90 Day Plan", "First 90 days plan for Jerry Senior Product Manager, Agentic AI"),
    "behavior-manifest.html": ("Russell-Dudek-Jerry-Agent-Behavior-Manifest.pdf", 2, "Russell Dudek Jerry Agent Behavior Manifest", "Independent candidate working artifact for Jerry Senior Product Manager, Agentic AI"),
    "objection-analysis.html": ("Russell-Dudek-Jerry-Hard-Objection.pdf", 2, "Russell Dudek Jerry Hard Objection Analysis", "Candidate risk and de-risking analysis for Jerry Senior Product Manager, Agentic AI"),
}


def build_brand_assets() -> None:
    request = Request(SOURCE_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=45) as response:
        payload = response.read()
    source = Image.open(io.BytesIO(payload)).convert("RGB")
    if source.size != (1200, 800):
        raise RuntimeError(f"Unexpected partner asset size: {source.size}; refusing an unsafe crop")
    SOURCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    WORDMARK_PATH.parent.mkdir(parents=True, exist_ok=True)
    source.save(SOURCE_PATH, "WEBP", quality=80, method=6)
    source.crop((85, 70, 520, 210)).save(WORDMARK_PATH, "PNG", optimize=True)


def rewrite_metadata(path: Path, title: str, subject: str) -> None:
    reader = PdfReader(str(path))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.add_metadata({
        "/Title": title,
        "/Author": "Russell Dudek",
        "/Subject": subject,
        "/Keywords": "Jerry, Agentic AI, Product Management, Russell Dudek",
    })
    temporary = path.with_suffix(".tmp.pdf")
    with temporary.open("wb") as handle:
        writer.write(handle)
    temporary.replace(path)


def build_documents() -> None:
    docs = BASE / "docs"
    docs.mkdir(exist_ok=True)
    for html_name, (pdf_name, expected_pages, title, subject) in DOCUMENTS.items():
        output = docs / pdf_name
        HTML(filename=str(BASE / html_name), base_url=str(BASE)).write_pdf(str(output))
        rewrite_metadata(output, title, subject)
        reader = PdfReader(str(output))
        if len(reader.pages) != expected_pages:
            raise RuntimeError(f"{pdf_name}: expected {expected_pages} pages, got {len(reader.pages)}")
        for page in reader.pages:
            width = float(page.mediabox.width)
            height = float(page.mediabox.height)
            if abs(width - 612) > 1 or abs(height - 792) > 1:
                raise RuntimeError(f"{pdf_name}: expected US Letter, got {width} x {height}")


if __name__ == "__main__":
    build_brand_assets()
    build_documents()
    print("Built brand assets and validated 12 US Letter PDF pages.")
