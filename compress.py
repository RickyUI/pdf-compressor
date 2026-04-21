from pathlib import Path
import fitz

INPUT_DIR = Path("data")
OUTPUT_DIR = Path("output")
MAX_MB = 30

PASSES = [
    {"dpi": 150, "quality": 80},
    {"dpi": 120, "quality": 70},
    {"dpi": 96,  "quality": 60},
    {"dpi": 72,  "quality": 50},
]


def compress_pdf(input_path: Path, output_path: Path, dpi: int, quality: int) -> None:
    src = fitz.open(str(input_path))
    dst = fitz.open()
    for page in src:
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        jpeg_bytes = pix.tobytes("jpeg", jpg_quality=quality)
        new_page = dst.new_page(width=page.rect.width, height=page.rect.height)
        new_page.insert_image(new_page.rect, stream=jpeg_bytes)
    dst.save(str(output_path), deflate=True, garbage=4)
    src.close()
    dst.close()


def compress_with_limit(input_path: Path, output_path: Path) -> dict:
    original_mb = input_path.stat().st_size / (1024 * 1024)
    result = {
        "input": input_path.name,
        "original_mb": original_mb,
        "pass_used": None,
        "compressed_mb": None,
        "success": False,
    }
    for i, pass_settings in enumerate(PASSES, 1):
        compress_pdf(input_path, output_path, **pass_settings)
        compressed_mb = output_path.stat().st_size / (1024 * 1024)
        result["pass_used"] = i
        result["compressed_mb"] = compressed_mb
        if compressed_mb <= MAX_MB:
            result["success"] = True
            break
    return result


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    pdfs = sorted(INPUT_DIR.glob("*.pdf"))

    if not pdfs:
        print(f"No PDFs found in {INPUT_DIR}/")
        return

    print(f"Compressing {len(pdfs)} PDFs  {INPUT_DIR}/ -> {OUTPUT_DIR}/  (max {MAX_MB} MB each)\n")

    results = []
    for pdf in pdfs:
        try:
            result = compress_with_limit(pdf, OUTPUT_DIR / pdf.name)
            results.append(result)
            saved_pct = (1 - result["compressed_mb"] / result["original_mb"]) * 100
            flag = "" if result["success"] else "  WARNING: exceeds limit"
            print(
                f"  {pdf.name:<58} "
                f"{result['original_mb']:>6.1f} MB  "
                f"pass {result['pass_used']}  ->  "
                f"{result['compressed_mb']:>5.1f} MB  "
                f"({saved_pct:.1f}% saved){flag}"
            )
        except Exception as exc:
            print(f"  ERROR {pdf.name}: {exc}")

    if results:
        total_in = sum(r["original_mb"] for r in results)
        total_out = sum(r["compressed_mb"] for r in results if r["compressed_mb"] is not None)
        total_saved = (1 - total_out / total_in) * 100 if total_in else 0
        print(f"\n{'─' * 80}")
        print(
            f"  {'Total':<58} "
            f"{total_in:>6.1f} MB         ->  "
            f"{total_out:>5.1f} MB  "
            f"({total_saved:.1f}% saved)"
        )


if __name__ == "__main__":
    main()
