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


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    if old in text:
        path.write_text(text.replace(old, new, 1))


def normalize_public_files() -> None:
    resume = BASE / "resume.html"
    cover = BASE / "cover-letter.html"
    readme = BASE / "README.md"
    index = BASE / "index.html"
    brief = BASE / "interview-brief.html"

    replace_once(resume, "View cover letter", "View Cover Letter")
    replace_once(
        resume,
        'Candidate vision: <a href="https://russelldudek.github.io/jerry/">russelldudek.github.io/jerry/</a> | Source: <a href="https://github.com/russelldudek/jerry">github.com/russelldudek/jerry</a>',
        'Candidate vision: <a href="https://russelldudek.github.io/jerry/">russelldudek.github.io/jerry/</a>',
    )
    replace_once(cover, "View resume", "View Resume")
    replace_once(
        cover,
        "I would prefer that concern be tested through this work sample and a concrete thin-slice plan rather than answered with title equivalence.",
        "I would prefer that concern be tested through the linked candidate vision, where the Agent Behavior Manifest and Behavior Diff Lab demonstrate the product reasoning, and through a concrete thin-slice plan rather than answered with title equivalence.",
    )
    replace_once(
        cover,
        'Candidate vision: <a href="https://russelldudek.github.io/jerry/">russelldudek.github.io/jerry/</a> | Source: <a href="https://github.com/russelldudek/jerry">github.com/russelldudek/jerry</a>',
        'Candidate vision: <a href="https://russelldudek.github.io/jerry/">russelldudek.github.io/jerry/</a>',
    )
    replace_once(
        readme,
        "Designed for static hosting at `https://russelldudek.github.io/jerry/` with source at `https://github.com/russelldudek/jerry`.",
        "Designed for static hosting at `https://russelldudek.github.io/jerry/`.",
    )
    replace_once(
        index,
        '<div><strong>Russell Dudek</strong><p>Operator-technologist and AI product systems builder. Currently in Pittsburgh and actively relocating to the Tampa Bay area, Florida.</p></div>',
        '<div><strong>Russell Dudek</strong><p>Operator-technologist and AI product systems builder. Currently in Pittsburgh and actively relocating to the Tampa Bay area, Florida.</p><p class="source-note">Independent candidate work; not affiliated with or endorsed by Jerry.</p></div>',
    )

    location = '<section class="report-section"><h2>Location</h2><p>Currently in Pittsburgh and actively relocating to Tampa Bay. Prepared to establish Florida residency and confirm timing directly; no claim of current Florida residency is made.</p></section>'
    source_section = '<section class="report-section"><h2>Public sources</h2><p>Jerry role description supplied with this campaign; Jerry home, about, careers, and newsroom pages; Plaid official Jerry customer story. Full URLs and observation date are recorded in the campaign research file.</p></section>'
    brief_text = brief.read_text().replace('\n' + source_section, '').replace(source_section, '')
    if location not in brief_text:
        raise RuntimeError("Interview brief location section is missing; refusing an unsafe normalization")
    brief.write_text(brief_text.replace(location, location + '\n' + source_section, 1))


def build_brand_assets() -> None:
    SOURCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    WORDMARK_PATH.parent.mkdir(parents=True, exist_ok=True)
    if SOURCE_PATH.exists():
        source = Image.open(SOURCE_PATH).convert("RGB")
    else:
        request = Request(SOURCE_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(request, timeout=45) as response:
            payload = response.read()
        source = Image.open(io.BytesIO(payload)).convert("RGB")
        source.save(SOURCE_PATH, "WEBP", quality=80, method=6)
    if source.size != (1200, 800):
        raise RuntimeError(f"Unexpected partner asset size: {source.size}; refusing an unsafe crop")
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
    normalize_public_files()
    build_brand_assets()
    build_documents()
    print("Normalized public files, built brand assets, and validated 12 US Letter PDF pages.")
