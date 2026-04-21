import os

import fitz
import pytest
from pathlib import Path

import compress
from compress import compress_pdf, compress_with_limit, MAX_MB, PASSES

DPI = 150
QUALITY = 80


@pytest.fixture
def tiny_pdf(tmp_path):
    path = tmp_path / "input.pdf"
    with fitz.open() as doc:
        for i in range(3):
            page = doc.new_page(width=595, height=842)
            page.insert_text((72, 72), f"Test page {i + 1}", fontsize=24)
            # Embed a random-data image so the file has meaningful size and is compressible
            samples = os.urandom(300 * 400 * 3)
            pix = fitz.Pixmap(fitz.csRGB, (0, 0, 300, 400), samples)
            page.insert_image(fitz.Rect(50, 100, 350, 500), pixmap=pix)
        doc.save(str(path))
    return path


def test_compress_pdf_creates_output(tiny_pdf, tmp_path):
    output = tmp_path / "out.pdf"
    compress_pdf(tiny_pdf, output, dpi=DPI, quality=QUALITY)
    assert output.exists()


def test_compress_pdf_output_is_valid_pdf(tiny_pdf, tmp_path):
    output = tmp_path / "out.pdf"
    compress_pdf(tiny_pdf, output, dpi=DPI, quality=QUALITY)
    with fitz.open(str(output)) as doc:
        assert len(doc) > 0
        for page in doc:
            assert page.rect.width > 0
            assert page.rect.height > 0


def test_compress_pdf_preserves_page_count(tiny_pdf, tmp_path):
    output = tmp_path / "out.pdf"
    compress_pdf(tiny_pdf, output, dpi=DPI, quality=QUALITY)
    with fitz.open(str(tiny_pdf)) as src, fitz.open(str(output)) as dst:
        assert len(dst) == len(src)


def test_compress_pdf_reduces_file_size(tiny_pdf, tmp_path):
    output = tmp_path / "out.pdf"
    compress_pdf(tiny_pdf, output, dpi=DPI, quality=QUALITY)
    assert output.stat().st_size < tiny_pdf.stat().st_size


def test_adaptive_compress_meets_size_limit(tiny_pdf, tmp_path):
    output = tmp_path / "out.pdf"
    result = compress_with_limit(tiny_pdf, output)
    assert result["success"] is True
    assert result["compressed_mb"] <= MAX_MB
    assert 1 <= result["pass_used"] <= len(PASSES)


def test_adaptive_compress_returns_metadata(tiny_pdf, tmp_path):
    output = tmp_path / "out.pdf"
    result = compress_with_limit(tiny_pdf, output)
    assert "original_mb" in result
    assert "compressed_mb" in result
    assert "pass_used" in result
    assert result["pass_used"] >= 1


def test_adaptive_compress_reports_failure_when_limit_unreachable(tiny_pdf, tmp_path, monkeypatch):
    monkeypatch.setattr(compress, "MAX_MB", 0)
    output = tmp_path / "out.pdf"
    result = compress_with_limit(tiny_pdf, output)
    assert result["success"] is False
