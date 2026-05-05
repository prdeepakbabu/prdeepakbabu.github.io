# Building Speech AI — Marketing Site

Static landing page for the book *Building Speech AI: Speech Representation, Understanding & Synthesis — A Practitioner's Guide* by Deepak Babu Piskala.

## Files

- `index.html` — single-page layout (hero, about, arc, chapters, companion code, quick-start, author, CTA, footer)
- `style.css` — modern dark theme, mel-spectrogram-inspired gradients, audio-themed accents
- `script.js` — animated multi-band waveform on hero canvas, scroll reveal, notebook hardware filter, smooth-scroll nav
- `.nojekyll` — tells GitHub Pages to skip Jekyll processing and serve files as-is

## Local preview

No build step. Open `index.html` directly in a browser, or serve the folder:

```bash
# Python
python3 -m http.server 8080
# → http://localhost:8080
```

## Deploying to GitHub Pages

This folder is GitHub-Pages-ready as static HTML. Two common deployment patterns:

### Option A — serve from a subfolder of an existing repo
1. Push the `webpage/` folder to a repo (e.g. the book's companion repo).
2. In the repo on GitHub: **Settings → Pages → Build & deployment → Source: "Deploy from a branch"**.
3. Pick the branch (e.g. `main`) and folder (`/webpage`). Save.
4. The site goes live at `https://<user>.github.io/<repo>/`.

### Option B — dedicated `username.github.io` repo
1. Create a repo named exactly `<your-username>.github.io`.
2. Copy the **contents** of this `webpage/` folder (not the folder itself) into the repo root.
3. Push to `main`. Pages serves automatically at `https://<your-username>.github.io/`.

The included `.nojekyll` file ensures GitHub Pages serves the files directly without running them through Jekyll (which can mangle paths starting with `_` and other edge cases).

## What's linked

Every notebook card links directly to:
- The pre-executed Jupyter notebook on GitHub (`notebooks/##_*.ipynb`)
- The matching CLI script (`examples/##_*.py`)
- A one-click Colab launch URL (`colab.research.google.com/github/...`)

All 12 chapters of the companion repo are covered.

## Customization quick-reference

- Colors: edit the CSS variables at the top of `style.css` (`:root { --accent: ... }`)
- Hero animation: tune the `bands` array in `script.js`
- Author photo: replace the `.author-avatar` block in `index.html` with an `<img>` if you have one
