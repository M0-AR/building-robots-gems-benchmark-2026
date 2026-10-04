"""Screenshot docs/preview.html via Playwright (verified artifact for README).

Usage: python scripts/screenshot.py [--width 1280] [--full]
Writes docs/preview_shot.png (viewport) + docs/preview_full.png (full page).
Step-by-step: launch chromium -> open file:// -> wait for GIFs -> shoot.
"""
import pathlib
import sys

def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright not installed; run: pip install playwright && playwright install chromium")
        sys.exit(2)
    root = pathlib.Path(__file__).resolve().parents[1]
    url = (root / "docs" / "preview.html").as_uri()
    out1 = root / "docs" / "preview_shot.png"
    out2 = root / "docs" / "preview_full.png"
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        pg.goto(url)
        pg.wait_for_timeout(2500)
        pg.screenshot(path=str(out1))
        pg.screenshot(path=str(out2), full_page=True)
        b.close()
    for f in (out1, out2):
        print(f"OK {f.name} {f.stat().st_size/1024:.1f} KB" if f.exists() else f"MISSING {f}")

if __name__ == "__main__":
    main()
