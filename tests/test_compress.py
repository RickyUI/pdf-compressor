import fitz
import pytest
from pathlib import Path

from compress import compress_pdf, compress_with_limit, MAX_MB, PASSES


@pytest.fixture
def tiny_pdf(tmp_path):
    path = tmp_path / "input.pdf"
    doc = fitz.open()
    for i in range(3):
        page = doc.new_page(width=595, height=842)
        page.insert_text((72, 72), f"Test page {i + 1}", fontsize=24)
    doc.save(str(path))
    doc.close()
    return path


def test_compress_pdf_creates_output(tiny_pdf, tmp_path):
    output = tmp_path / "out.pdf"
    compress_pdf(tiny_pdf, output, dpi=150, quality=80)
    assert output.exists()


def test_compress_pdf_output_is_valid_pdf(tiny_pdf, tmp_path):
    output = tmp_path / "out.pdf"
    compress_pdf(tiny_pdf, output, dpi=150, quality=80)
    doc = fitz.open(str(output))
    assert len(doc) == 3
    doc.close()


def test_compress_pdf_preserves_page_count(tiny_pdf, tmp_path):
    output = tmp_path / "out.pdf"
    compress_pdf(tiny_pdf, output, dpi=150, quality=80)
    src = fitz.open(str(tiny_pdf))
    dst = fitz.open(str(output))
    assert len(dst) == len(src)
    src.close()
    dst.close()


def test_adaptive_compress_meets_size_limit(tiny_pdf, tmp_path):
    output = tmp_path / "out.pdf"
    result = compress_with_limit(tiny_pdf, output)
    assert result["success"] is True
    assert result["compressed_mb"] <= MAX_MB


def test_adaptive_compress_returns_metadata(tiny_pdf, tmp_path):
    output = tmp_path / "out.pdf"
    result = compress_with_limit(tiny_pdf, output)
    assert "original_mb" in result
    assert "compressed_mb" in result
    assert "pass_used" in result
    assert result["pass_used"] >= 1
