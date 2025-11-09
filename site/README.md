# Retro Tongan site

This small static site is intended to be a simple 1990s-style page in Tongan. Files are under `site/`.

What I added:
- `index.html` — main page with short Tongan text and a canvas map.
- `style.css` and `script.js` — minimal styling and map script.
- `hidden/index.html` — a small page inside the hidden folder.
- `images/` — a placeholder folder for your pictures.

Security note:
- The public copy of `stego_hidden.txt` has been removed from `site/hidden/` to reduce accidental exposure. The original stego content still exists locally in your workspace under `secret/stego_hidden.txt`.
- If you plan to publish this repository publicly, consider making the repo private, encrypting sensitive content before embedding, or removing sensitive files entirely.

Publishing (GitHub Pages):
- To publish, enable GitHub Pages in repo settings and choose the `main` branch root (or move `site/` contents to repo root or `docs/`).

If you'd like, I can commit and push these changes for you, and/or help encrypt the stego payload before publishing.
