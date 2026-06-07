# CMU MSA Brand Guide

This repository is the **single source of truth** for the visual brand, communications, and web standards of the **Muslim Student Association of Carnegie Mellon University (CMU MSA)**.

- **Read the brand guide:** [`cmu-msa-brand-guide.md`](cmu-msa-brand-guide.md)
- **Printable PDF:** [`cmu-msa-brand-guide.pdf`](cmu-msa-brand-guide.pdf) — rebuilt automatically from the Markdown on every change, so it never drifts.

> **Scope of this repo.** This repository holds the Brand Guide (and the tooling that turns it into a PDF). It defines the *standards* — colors, type, contrast, voice, Arabic handling, and the web UI **values** (radius, transitions, focus ring, named tokens). When you build or update MSA websites, follow this brand guide as the single source of truth.

---

## New maintainer? Read this first (3 things)

1. **There is one file you edit: the Markdown.** Everything else is either generated or plumbing.
2. **Never hand-edit the PDF.** It is built automatically and your changes would be overwritten on the next build.
3. **You don't need to "run" anything to publish.** Editing the Markdown on `main` (via a pull request) makes a robot rebuild and commit the PDF for you.

If you only ever remember those three things, the repo will keep working.

---

## What's in here

```
brand-guide/
├── cmu-msa-brand-guide.md                # THE BRAND GUIDE — this is the only file you edit
├── cmu-msa-brand-guide.pdf               # generated automatically — DO NOT edit by hand
├── tokens/
│   ├── tokens.json                       # machine-readable design tokens — canonical values
│   └── tokens.schema.json                # JSON schema to validate tokens.json structure
├── assets/
│   └── logo/
│       └── cmu-msa-logo.jpg              # interim logo asset
├── build/
│   ├── build_pdf.py                      # converts the Markdown into the PDF
│   └── style.css                         # how the PDF looks (brand colors, fonts, tables)
├── requirements.txt                      # Python packages the build needs
├── .github/workflows/build-pdf.yml       # the robot: rebuilds + commits the PDF on every change
├── .gitignore
└── README.md                             # you are here
```

**Edit freely:** `cmu-msa-brand-guide.md`.
**Edit if you mean to change design values:** `tokens/tokens.json` (the single machine-readable source of truth).
**Edit only if you mean to change how the PDF looks or builds:** `build/style.css`, `build/build_pdf.py`, `.github/workflows/build-pdf.yml`.
**Never edit by hand:** `cmu-msa-brand-guide.pdf` (it's regenerated).

### Using the design tokens

The `tokens/` directory contains the machine-readable layer of the brand guide — inspired by how companies like Apple maintain visual consistency across entirely different tech stacks.

- **`tokens/tokens.json`** contains every design value (colors, fonts, spacing, radii, motion, dark mode) as structured JSON. Any build tool, design plugin (e.g., Figma Tokens Studio), or platform-specific constants file can consume it directly.
- **`tokens/tokens.schema.json`** defines the exact structure and validation rules for the token data. Modern code editors read this schema automatically to provide live linting, error validation, and auto-complete inside `tokens.json`.

Downstream web projects can compile these tokens to CSS custom properties or configuration variables during their build step. For example, a simple Node.js script can convert the JSON to CSS custom properties:

```javascript
const tokens = require('./tokens/tokens.json');
const fs = require('fs');

let css = `@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Plus+Jakarta+Sans:wght@500;600;700&family=Lora:wght@400;500&family=Amiri:wght@400;700&family=Cairo:wght@600;700&display=swap');\n\n`;
css += `:root {\n`;

// Generate colors
for (const [name, value] of Object.entries(tokens.color)) {
  if (!name.startsWith('$')) {
    css += `  --msa-color-${name}: ${value};\n`;
  }
}
// Generate spacing, radii, motion, etc. as needed...
css += `}\n`;

fs.writeFileSync('brand.css', css);
```

For Tailwind CSS, you can directly import `tokens/tokens.json` and map its values into your `tailwind.config.js` `theme.extend`. See Section 6 of the brand guide for the full cross-platform implementation guide, including iOS, Android, and Flutter mappings.

---

## How the automatic PDF works

The Markdown is the source; the PDF is a build artifact. The pipeline is:

```
You edit the Markdown  ──►  GitHub runs build_pdf.py  ──►  new PDF  ──►  robot commits it back
   (on a branch / PR)        (Markdown → HTML → PDF)                      (you see it in the repo)
```

When you push a change that touches the brand guide, GitHub spins up a fresh temporary Linux machine, installs the tools, runs `build/build_pdf.py` (which turns the Markdown into HTML and then into a PDF using **WeasyPrint**), and then commits the regenerated PDF back into the repo. When the job finishes the temporary machine is destroyed — committing the PDF back is the only reason it survives.

**Cost:** free. GitHub Actions has no minute limit on public repositories; on a private repo this job uses ~1–2 minutes per run and the free plan includes far more than that per month. Either way this repo will not cost the MSA money.

**Who makes that commit:** a bot. The auto-commit appears in the history as `github-actions[bot]` with the message `build: regenerate brand guide PDF`, touching only the PDF. It is clearly machine-generated, not attributed to a person.

**Why it can't loop forever:** two guards. (1) The workflow only triggers on changes to the Markdown / build files, not the PDF. (2) Commits made with the built-in Actions token don't trigger new workflow runs by design.

---

## Building the PDF locally (optional)

You only need this if you want to preview the PDF before pushing.

```bash
# 1. System libraries + fonts (Debian/Ubuntu)
sudo apt-get install -y \
  libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0 libffi-dev libcairo2 \
  fonts-open-sans fonts-noto-core fonts-noto-color-emoji

# 2. Python dependencies
pip install -r requirements.txt

# 3. Build (writes cmu-msa-brand-guide.pdf to the repo root)
python build/build_pdf.py
```

On **macOS**, replace step 1 with `brew install pango gdk-pixbuf libffi cairo`.

The brand fonts (DM Serif Display, Plus Jakarta Sans, Lora, Amiri, Cairo) are pulled from Google Fonts at build time; the Arabic/emoji fallbacks come from the system font packages above.

---

## Known gotchas (read before changing `build/style.css`)

These bit us once already. They are subtle because the document mixes English, Arabic, and symbols.

- **Don't put an Arabic font early in the body `font-family` stack.** If an Arabic face is listed before the Latin serif, the layout engine uses it for English runs too and it silently drops the digits (e.g. `2/3` renders as `/`). The body stack must be Latin-only; Arabic is substituted automatically per-glyph. The Arabic font belongs only in the `[lang="ar"] / .ar` rule.
- **Avoid using color emojis.** The PDF renderer cannot draw color-emoji bitmap fonts, so they print as empty boxes. To ensure clean and consistent rendering, the brand guide uses text-based HTML/CSS badges (like `[OK]`, `[BANNED]`, `[!]`) instead of emojis.
- **Arabic renders right-to-left automatically** — you don't need to do anything special in the Markdown; just type the Arabic. The CSS and the renderer handle shaping and direction.
- **Offline builds** will fall back to system fonts because the brand fonts load from Google Fonts over the network. The build still succeeds; it just won't look exactly on-brand. To build fully offline, install the missing font packages locally.

If something looks wrong, the fastest debugging move is to open the intermediate HTML: temporarily print the `document` string in `build_pdf.py`, or render a single page to an image with `pdftoppm`.

---

## The CI workflow (`.github/workflows/build-pdf.yml`)

Plain-language summary of each step: check out the repo → install system fonts/libraries → install Python packages → run the build script → upload the PDF as a downloadable artifact → commit the PDF back to the repo.

**Optional hardening:** the commit step uses a popular third-party action (`stefanzweifel/git-auto-commit-action`). It's fine as-is, but if the org wants to be strict about supply-chain safety, pin it to an exact commit hash instead of a moving `@v5` tag:

```yaml
# from:
uses: stefanzweifel/git-auto-commit-action@v5
# to (grab the real SHA from that action's releases page):
uses: stefanzweifel/git-auto-commit-action@<commit-sha>  # v5.x.x
```

If you'd rather not use a third-party action at all, the same commit-back can be done with a few plain `git` commands in the workflow.

---

## Accounts & Handover

At each board transition, confirm the incoming board has access to:

- [ ] This **GitHub repository** (with owner/admin permissions)
- [ ] All associated hosting accounts, domain registrars, and digital tools

Ensure credentials and access keys are stored securely in the board's password manager and handed over directly. Wherever possible, use organization-owned shared accounts rather than individual personal logins to prevent lost access.
