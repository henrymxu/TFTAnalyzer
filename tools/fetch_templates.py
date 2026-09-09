"""One-time (or occasional refresh) download of champion tile icons from
Community Dragon into data/templates/champions/, for use by
tft.vision.templates.TemplateLibrary.

Usage:
    python -m tools.fetch_templates
"""

from __future__ import annotations

from pathlib import Path

from tft.static_data.cdragon import CDragonClient

OUTPUT_DIR = Path("data/templates/champions")


def main() -> None:
    client = CDragonClient()
    champions = client.get_champions()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for champion in champions:
        if not champion.icon_path:
            continue
        destination = OUTPUT_DIR / f"{champion.api_name}.png"
        try:
            icon_bytes = client.download_icon(champion.icon_path)
        except Exception as exc:  # noqa: BLE001 - best-effort batch download
            print(f"skip {champion.api_name}: {exc}")
            continue
        destination.write_bytes(icon_bytes)
        print(f"saved {destination}")


if __name__ == "__main__":
    main()
