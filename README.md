# edbertolima.github.io

Personal academic website of Edberto Moura Lima, Senior Researcher at BAW Research (Austria).

| What | Where |
|------|-------|
| Home page | `_pages/about.md` |
| CV (English, `/CV`) | `_pages/index.md` |
| Lebenslauf (German, `/lebenslauf`) | `_pages/lebenslauf.md` |
| Publication lists shared by both CVs | `_includes/cv/*.md` |
| Site settings, sidebar and footer links | `_config.yml` |

Built with Jekyll and the [Minimal Mistakes](https://github.com/mmistakes/minimal-mistakes) theme.
Every push to `master` runs `.github/workflows/jekyll.yml`, which also generates the PDF
downloads (`assets/files/*.pdf`) from the CV pages, so they never need updating by hand.

## Tools

Requires Python 3.12+, `pip install markdown typer`, and Chrome or Chromium.

```bash
# PDFs as published on the site
python tools/cv_pdf.py full --out Edberto_Moura_Lima_CV.pdf
python tools/cv_pdf.py full --page _pages/lebenslauf.md --out Edberto_Moura_Lima_Lebenslauf.pdf

# Condensed scientific CV for applications (phone only for private copies)
python tools/cv_pdf.py scientific --out Edberto_Moura_Lima_Scientific_CV.pdf --phone "+43 ..."

# Works on ORCID that are missing from the CV
python tools/check_orcid.py
```

`.github/workflows/orcid-check.yml` runs the ORCID check on the 1st of every month and opens an
issue when a new publication appears. DOIs that should not be added go in
`tools/orcid_ignore.txt`.
