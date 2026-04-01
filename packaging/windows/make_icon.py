from __future__ import annotations

from pathlib import Path


def main() -> None:
    """
    Build a multi-resolution .ico for Windows from the existing PNG.

    Requires: Pillow (install only for build time).
    """
    from PIL import Image  # type: ignore[import-not-found]

    repo_root = Path(__file__).resolve().parents[2]
    src = repo_root / "resources" / "icons" / "momentum.png"
    dst = repo_root / "resources" / "icons" / "momentum.ico"

    img = Image.open(src).convert("RGBA")

    # Standard Windows icon sizes.
    sizes = [(16, 16), (20, 20), (24, 24), (32, 32), (40, 40), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(dst, format="ICO", sizes=sizes)

    print(f"Wrote {dst}")


if __name__ == "__main__":
    main()

