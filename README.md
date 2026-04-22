# PDF Compressor

A single-command Python script that compresses PDF files to a target size limit — built for preparing documents as attachments in Claude Code projects.

## What it does

- Reads all PDF files from `data/`
- Re-renders each page as a JPEG at reduced DPI and quality
- Re-assembles a new compressed PDF in `output/`
- Tries up to 4 compression passes, stopping as soon as the file is ≤ 30 MB
- Prints a per-file summary with original size, compressed size, and savings

## Requirements

- [UV](https://docs.astral.sh/uv/) (Python package manager)
- Python 3.11+

## Installation

```bash
git clone https://github.com/RickyUI/pdf-compressor.git
cd pdf-compressor
uv sync
```

## Usage

1. Place your PDF files in the `data/` folder
2. Run:

```bash
uv run compress.py
```

3. Find compressed PDFs in `output/`

Example output:

```
Compressing 3 PDFs  data/ -> output/  (max 30 MB each)

  estática-hibbeler-12va.pdf       48.2 MB  pass 2  ->  11.4 MB  (76.4% saved)
  mecanica-dinamica-9th.pdf        44.8 MB  pass 2  ->  10.9 MB  (75.7% saved)
  mecanica-estatica-beer-9th.pdf   26.7 MB  pass 1  ->   9.1 MB  (65.9% saved)

────────────────────────────────────────────────────────────────────────────────
  Total                           119.7 MB         ->  31.4 MB  (73.8% saved)
```

## Configuration

Edit the constants at the top of `compress.py`:

| Constant | Default | Description |
|----------|---------|-------------|
| `MAX_MB` | `30` | Target maximum output size per file |
| `PASSES` | 4 entries | Compression levels tried in order |

The default passes:

| Pass | DPI | JPEG Quality |
|------|-----|-------------|
| 1    | 150 | 80          |
| 2    | 120 | 70          |
| 3    | 96  | 60          |
| 4    | 72  | 50          |

## How it works

Each page is rendered to a bitmap at the target DPI using [PyMuPDF](https://pymupdf.readthedocs.io/), then saved as JPEG at the target quality level. The script tries the mildest compression pass first. If the output exceeds `MAX_MB`, it retries with the next pass (lower DPI + lower quality). This continues until the file fits or all passes are exhausted.

## Running tests

```bash
uv sync --extra dev
uv run pytest tests/ -v
```

## License

MIT
