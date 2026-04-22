# pdf-compressor

Compresses PDF files to ≤ 30 MB each for use as attachments in Claude Code projects.
Uses pymupdf to re-render each page as a compressed JPEG, then re-assembles a new PDF.

## Usage

    uv run compress.py

Input PDFs must be in `data/`. Compressed outputs are written to `output/` (created automatically).

## Settings

Edit these constants at the top of `compress.py`:

| Constant | Default | Purpose |
|----------|---------|---------|
| `MAX_MB` | `30` | Maximum allowed output size in MB |
| `PASSES` | 4 entries | DPI + JPEG quality tried in order until size limit is met |

The script stops at the first pass that produces a file ≤ `MAX_MB`. If all passes are
exhausted and the file is still too large, a warning is printed.

## Dependencies

Managed by UV. Install with:

    uv sync --extra dev   # includes pytest for tests
    uv sync               # runtime only

## Run tests

    uv run pytest tests/ -v

## Project structure

    data/          Input PDFs (not modified)
    output/        Compressed PDFs (auto-created)
    compress.py    All compression logic
    tests/         Pytest test suite
