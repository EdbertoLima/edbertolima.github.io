"""Build PDF versions of the CV from the Jekyll sources.

Commands:
  full        PDF of a CV page as published (English or German).
  scientific  Condensed scientific CV with profile and job duties (for applications).

The PDF is rendered with headless Chrome/Chromium using assets/css/cv-screen.css.
"""

import os
import re
import shutil
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import markdown
import typer

REPO = Path(__file__).resolve().parent.parent
FA_CSS = "https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.7.2/css/all.min.css"
PRINT_CSS = """
@page { size: A4; margin: 16mm 14mm 16mm 10mm; }
body { margin: 0; font-size: 10pt; }
h1 { font-size: 2.4em; }
h2 { margin-top: 1.6em; break-after: avoid; }
h3 { break-after: avoid; }
p, li { break-inside: avoid; }
hr { border: 0; }
a { text-decoration: none; }
ul { width: 55%; }
"""
CHROME_CANDIDATES = (
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "chrome",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
)
INCLUDE_RE = re.compile(r"\{% include (cv/[\w-]+\.md) %\}")
LAST_UPDATED_RE = re.compile(r'\{\{ page\.last_modified_at \| date: "([^"]+)" \}\}')

app = typer.Typer(help=__doc__, no_args_is_help=True)


# ---------------------------------------------------------------- source handling


def load_page(page: Path) -> str:
    """Read a Jekyll page: drop front matter and HTML comments, resolve cv/ includes."""
    text = page.read_text(encoding="utf-8")
    text = re.sub(r"\A---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

    def include(match: re.Match[str]) -> str:
        path = REPO / "_includes" / match.group(1)
        if not path.is_file():
            raise FileNotFoundError(f"Include not found: {path}")
        return path.read_text(encoding="utf-8").rstrip("\n")

    return INCLUDE_RE.sub(include, text)


def to_html(src: str, title: str) -> str:
    """Convert CV markdown to a standalone HTML document styled for print."""
    # The web page collapses conference abstracts; the PDF shows them all.
    src = re.sub(
        r"^(<details[^>]*>|<summary>.*</summary>|</details>)\n", "", src, flags=re.MULTILINE
    )
    # The web page shows short "DOI" links; the PDF keeps the full DOI text.
    src = re.sub(r"\[DOI\]\(https://doi\.org/([^)]+)\)", r"doi: [\1](https://doi.org/\1)", src)

    today = datetime.now(tz=UTC).date()
    src, n = LAST_UPDATED_RE.subn(lambda m: today.strftime(m.group(1)), src)
    if n != 1:
        raise ValueError(f"Expected one last-updated tag, found {n}")
    if "{{" in src or "{%" in src:
        raise ValueError("Unhandled Liquid tags remain in the CV source")

    # Scholarship detail lines ("- **Label:** ...") follow a paragraph without a blank line;
    # force a hard line break after each so they stay on separate lines.
    src = re.sub(r"^(- \*\*.*?)\s*$", r"\1  ", src, flags=re.MULTILINE)

    body = markdown.markdown(src, extensions=["extra"])
    screen_css = (REPO / "assets" / "css" / "cv-screen.css").read_text(encoding="utf-8")
    return f"""<!doctype html>
<html><head><meta charset="utf-8">
<title>{title}</title>
<link rel="stylesheet" href="{FA_CSS}">
<style>{screen_css}</style>
<style>{PRINT_CSS}</style>
</head><body><div id="main"><div id="content">
{body}
</div></div></body></html>
"""


# ---------------------------------------------------------------- PDF printing


def find_chrome(explicit: str | None) -> str:
    """Return a Chrome/Chromium executable: --chrome, $CHROME, or a known install."""
    for candidate in (explicit, os.environ.get("CHROME"), *CHROME_CANDIDATES):
        if not candidate:
            continue
        found = shutil.which(candidate) or (candidate if Path(candidate).is_file() else None)
        if found:
            return found
    raise typer.BadParameter("Chrome/Chromium not found; pass --chrome or set $CHROME")


def print_pdf(html: str, out: Path, chrome: str) -> None:
    """Print HTML to PDF with headless Chrome."""
    out = out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "cv.html"
        page.write_text(html, encoding="utf-8")
        subprocess.run(
            [
                chrome,
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--no-pdf-header-footer",
                "--virtual-time-budget=10000",
                f"--print-to-pdf={out}",
                page.as_uri(),
            ],
            check=True,
            capture_output=True,
            timeout=180,
        )
    if not out.is_file() or out.stat().st_size == 0:
        raise RuntimeError(f"Chrome did not write {out}")
    typer.echo(f"Wrote {out} ({out.stat().st_size // 1024} KB)")


# ---------------------------------------------------------------- scientific CV

PROFILE = """## Profile

**Position:** Senior Researcher, BAW Research, Petzenkirchen, Austria<br/>
**Field of expertise:** Ecohydrology; remote sensing of evapotranspiration; hydrological and \
water quality modelling (SWAT, APEX); soil management and land use; nature-based solutions for \
climate adaptation

Environmental scientist and ecohydrological modeller specialising in natural resource \
management, hydrological and water quality modelling, model development and integration, and \
data analysis. Research interests lie in nature-based solutions for sustainable land use, \
ecosystem restoration and climate adaptation. Developed a framework to spatially allocate \
management practice scenarios in a hydrological model to assess water quality and nutrient \
losses, and an R-scripted workflow to automate and parallelise hydrological model simulations. \
Experienced in multidisciplinary and multicultural research teams in Brazil, Canada and Austria.

## Education
"""

BAW_DUTIES = """

- \\- Contribute to remote sensing estimation of reed-belt evapotranspiration at Lake Neusiedl \
(project VeSchN).
- \\- Estimate daily actual evapotranspiration from Sentinel-2 imagery (OPTRAM-ET) and compare it \
with global ET products (MODIS, SSEBop, PML, WaPOR, Copernicus) in Google Earth Engine.
- \\- Map reed-belt zones with Sentinel-2 and reed flooding with Sentinel-1; evaluate satellite \
ET against eddy covariance, lysimeter and crop-coefficient (ET0-Kc) estimates.
- \\- Develop a reproducible Python data pipeline for climate, hydrological and remote sensing \
data.
"""

POSTDOC_DUTIES = """

- \\- Managed work-package activities of an EU-funded project.
- \\- Implemented soil management modelling to mitigate climate change impacts; assessed crop \
growth, nutrient loss and carbon storage.
- \\- Developed a framework to incorporate nature-based solutions and land-use dynamics \
scenarios into a hydrological model.
- \\- Developed R-scripted workflows for hydrological data analysis and GIS applications for \
hydrological and ecological planning.
- \\- Trained and supervised graduate students.
"""

CONSULTANT_DUTIES = """

- \\- Organised spatial databases for environmental impact assessments in the Athabasca oil \
sands region.
- \\- Processed LiDAR data and applied statistical models to evaluate ecosystem disturbance \
from industrial activities.
"""

TUTOR_DUTIES = """

- \\- Online tutor: "Soil and Water Management in Rural Properties and Hydrographic Basins" and \
"Getting Started with QGIS".
"""

INTERN_DUTIES = """

- \\- Projeto Biomas: planned and developed restoration strategies for stream buffer areas in \
the Atlantic Forest and Cerrado biomes.
"""


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f"Anchor found {count} times (expected 1): {old[:60]!r}")
    return text.replace(old, new)


def cut(text: str, start: str, end: str, after: str | None = None) -> str:
    """Remove text from `start` (inclusive) to `end` (exclusive), searching after `after`."""
    origin = text.index(after) if after else 0
    i = text.index(start, origin)
    j = text.index(end, i + len(start))
    return text[:i] + text[j:]


def make_scientific(md: str, phone: str | None) -> str:
    """Condense the English web CV into the scientific CV used for applications."""
    # Trim early-career items, student-era abstracts and minor publications.
    md = cut(md, "`2015`\n**Intern**", "## Projects and research visits")
    md = cut(md, "*Publication list also available", "\n")
    md = cut(md, "`2019`\nWeiler", "`2018`\n**Lima, E. M.**, Curcio")
    md = cut(md, "`2014`\n**Lima, E. M.**, Rezende", "### Other Publications")
    md = cut(md, "### Other Publications", "## Grants and Scholarships")
    md = cut(md, "`2008`\n**6th Place**", "## Conference activity")
    md = cut(md, "`2013`", "## Teaching", after="### Presentations")

    md = replace_once(md, "## Education \n", PROFILE)
    md = replace_once(
        md,
        ' - <a href="mailto:edberto.moura@gmail.com">edberto.moura@gmail.com</a>',
        "",
    )
    if phone:
        md = replace_once(
            md,
            "edberto.mouralima@baw.at</a>\n",
            f'edberto.mouralima@baw.at</a><br/><i class="fa-solid fa-phone fa-2xs"></i> {phone}\n',
        )
    # Keep only website and ORCID from the link block.
    start = md.index('<div id="webaddress">')
    end = md.index("</div>", start) + len("</div>")
    md = (
        md[:start]
        + '<div id="webaddress">\n'
        + '  <a href="https://edbertolima.github.io"><i class="fa-solid fa-house"></i>'
        + " edbertolima.github.io</a> - \n"
        + '  <a href="https://orcid.org/0000-0002-8447-8460"><i class="fa-brands fa-orcid"></i>'
        + " ORCID 0000-0002-8447-8460</a>\n"
        + "</div>"
        + md[end:]
    )

    md = replace_once(
        md,
        "Pollnbergstraße 1, 3252 Petzenkirchen, Austria.\n",
        "Pollnbergstraße 1, 3252 Petzenkirchen, Austria." + BAW_DUTIES,
    )
    md = replace_once(
        md,
        "BOKU University*, Vienna, Austria.\n",
        "BOKU University*, Vienna, Austria." + POSTDOC_DUTIES,
    )
    md = replace_once(
        md,
        "University of Lethbridge*, Lethbridge, AB, Canada.\n",
        "University of Lethbridge*, Lethbridge, AB, Canada. (Remote)" + CONSULTANT_DUTIES,
    )
    md = replace_once(
        md,
        "*Serviço Nacional de Aprendizagem Rural do Paraná (SENAR-PR)*, PR, Brazil.\n",
        "*Serviço Nacional de Aprendizagem Rural do Paraná (SENAR-PR)*, PR, Brazil." + TUTOR_DUTIES,
    )
    md = replace_once(
        md,
        "**Research Intern** <br/> EMBRAPA FLORESTA, PR, Brazil\n",
        "**Research Intern** <br/> *EMBRAPA Florestas*, Curitiba, PR, Brazil." + INTERN_DUTIES,
    )
    md = replace_once(
        md,
        "`2009-2016`\n**B.S., in Forest Engineering**",
        "`2013-2015`\n**Exchange (Science Without Borders), Environmental Protection**, "
        "*Institute of Technology Sligo*, Ireland.\n\n"
        "`2009-2016`\n**B.S., in Forest Engineering**",
    )
    md = replace_once(
        md,
        "### Teaching Assistant\n",
        "### Supervision\n`2021`\n**Undergraduate student supervision**, *Restaura PAMPA project, "
        "Forest Engineering, Universidade Federal de Santa Maria*, RS, Brazil.\n\n"
        "### Teaching Assistant\n",
    )
    # Personal details are covered by the Profile section.
    return cut(md, "## Personal\n", "<br/>Last updated:")


# ---------------------------------------------------------------- commands

ChromeOption = Annotated[
    str | None, typer.Option(help="Chrome/Chromium executable (default: auto-detect)")
]


@app.command()
def full(
    out: Annotated[Path, typer.Option(help="Output PDF path")],
    page: Annotated[Path, typer.Option(help="CV page source")] = REPO / "_pages" / "index.md",
    title: Annotated[str, typer.Option(help="PDF document title")] = "Edberto Moura Lima - CV",
    chrome: ChromeOption = None,
) -> None:
    """PDF of a CV page as published (use --page _pages/lebenslauf.md for German)."""
    print_pdf(to_html(load_page(page), title), out, find_chrome(chrome))


@app.command()
def scientific(
    out: Annotated[Path, typer.Option(help="Output PDF path")],
    phone: Annotated[
        str | None, typer.Option(help="Phone number to show (private copies only)")
    ] = None,
    chrome: ChromeOption = None,
) -> None:
    """Condensed scientific CV with profile and job duties."""
    md = make_scientific(load_page(REPO / "_pages" / "index.md"), phone)
    print_pdf(to_html(md, "Edberto Moura Lima - Scientific CV"), out, find_chrome(chrome))


if __name__ == "__main__":
    app()
