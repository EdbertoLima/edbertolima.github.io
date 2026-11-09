"""Compare the works on an ORCID record with the DOIs listed in the CV.

Prints works whose DOI is not in the CV. With --report, also writes a Markdown report
(only when something is missing), which the monthly GitHub workflow posts as an issue.
DOIs that should never be added (e.g. preprint copies) go in tools/orcid_ignore.txt.
"""

import json
import re
import urllib.request
from pathlib import Path
from typing import Annotated

import typer

REPO = Path(__file__).resolve().parent.parent
ORCID_ID = "0000-0002-8447-8460"
IGNORE_FILE = REPO / "tools" / "orcid_ignore.txt"
CV_SOURCES = (REPO / "_pages", REPO / "_includes" / "cv")
DOI_RE = re.compile(r"doi\.org/(10\.[^)\s\"<>]+)", re.IGNORECASE)

app = typer.Typer(help=__doc__)


def orcid_works(orcid_id: str) -> list[dict[str, str]]:
    """Return title, year, type and DOI (lower case) for each ORCID work that has a DOI."""
    request = urllib.request.Request(
        f"https://pub.orcid.org/v3.0/{orcid_id}/works",
        headers={"Accept": "application/json", "User-Agent": "cv-orcid-check/1.0"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        data = json.load(response)

    works = []
    for group in data["group"]:
        summary = group["work-summary"][0]
        dois = [
            ext["external-id-value"].lower()
            for ext in group["external-ids"]["external-id"]
            if ext["external-id-type"] == "doi"
        ]
        if not dois:
            continue
        year = (summary.get("publication-date") or {}).get("year") or {}
        works.append(
            {
                "title": summary["title"]["title"]["value"],
                "year": year.get("value", "?"),
                "type": summary["type"],
                "doi": dois[0],
            }
        )
    return works


def cv_dois() -> set[str]:
    """All DOIs linked anywhere in the CV pages and shared publication lists."""
    found: set[str] = set()
    for folder in CV_SOURCES:
        for path in folder.glob("*.md"):
            found.update(m.lower() for m in DOI_RE.findall(path.read_text(encoding="utf-8")))
    if not found:
        raise RuntimeError("No DOIs found in the CV sources; check CV_SOURCES")
    return found


def ignored_dois() -> set[str]:
    lines = IGNORE_FILE.read_text(encoding="utf-8").splitlines()
    return {line.split("#")[0].strip().lower() for line in lines if line.split("#")[0].strip()}


@app.command()
def main(
    report: Annotated[
        Path | None, typer.Option(help="Write a Markdown report here if works are missing")
    ] = None,
) -> None:
    known = cv_dois() | ignored_dois()
    missing = [w for w in orcid_works(ORCID_ID) if w["doi"] not in known]

    if not missing:
        typer.echo("CV is up to date with ORCID.")
        return

    lines = [
        f"ORCID ({ORCID_ID}) lists {len(missing)} work(s) with a DOI that the CV does not include:",
        "",
    ]
    for w in sorted(missing, key=lambda w: w["year"], reverse=True):
        lines.append(f"- **{w['year']}** ({w['type']}) {w['title']} - https://doi.org/{w['doi']}")
    lines += [
        "",
        (
            "Add them to `_includes/cv/` (and the home page if recent), or list the DOI in "
            "`tools/orcid_ignore.txt` to stop this reminder."
        ),
    ]
    text = "\n".join(lines) + "\n"
    typer.echo(text)
    if report:
        report.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    app()
