# luvurava 💗 — a Python 3D heart that runs in the browser

A tiny terminal animation (`luvurava.py`) that renders a rotating 3D heart whose
surface is built from the letters of a name — now served as a **public web page**
through **GitHub Pages**, running on **Pyodide** (CPython compiled to WebAssembly).

* **No server.** GitHub Pages is static hosting only; Pyodide runs entirely in the visitor's browser.
* **No JavaScript rewrite.** The animation logic is 100% Python. `index.html` only loads Pyodide, fetches your `.py` file, and calls two functions on a timer.
* **No build step, no dependencies.**

---

## 1. What this project is

| File | Purpose |
|------|---------|
| `luvurava.py` | The Python program. Works in a normal terminal **and** in the browser. |
| `index.html` | Loads Pyodide from a CDN, fetches `luvurava.py`, shows its output on the page, and provides the **Run** / **Stop** buttons, a loading message, and error handling. |
| `.nojekyll` | Optional. Tells GitHub Pages to skip Jekyll processing. |

### Why two entry points in the Python file?

* **Terminal:** `python luvurava.py` → `main()` keeps the original `while True` + `time.sleep()` loop.
* **Browser:** `index.html` calls `init_animation(name)` once and then `next_frame()` every 50 ms.

`next_frame()` uses *exactly* the same rendering code as the terminal loop — it just
returns the frame as a string instead of printing it. Nothing was ported to JavaScript.

### Pyodide compatibility notes (and what was done about them)

| Original code | In the browser | Solution used |
|---|---|---|
| `import math, os, sys, time` | ✅ all available | none needed |
| `if os.name == "nt": os.system("")` | ✅ skipped (`os.name` is `"posix"`) | none needed |
| `os.system("cls"/"clear")` | ❌ no shell in a browser | `index.html` installs an `os.system` shim that clears the page instead |
| `time.sleep(0.05)` | ❌ would freeze the tab | `index.html` installs a `time.sleep` shim that raises a clear error; the browser's `setInterval(…, 50)` drives the frames |
| `while True:` loop | ❌ would freeze the tab | replaced by `next_frame()`, called once per frame by the browser |
| `except KeyboardInterrupt` | ⚠️ no Ctrl+C in a browser | harmless; the **Stop** button does the same job |
| file I/O | ✅ **none used** | nothing to change |
| all `math.*` / rendering functions | ✅ fully supported | **unchanged** |

---

## 2. Upload and get your public link

### Step A — create the repository

1. Go to <https://github.com/new>
2. **Repository name:** e.g. `my-love` (this becomes part of your URL)
3. Choose **Public** (Pages requires a public repo on the free plan)
4. Leave *Add a README file* **unchecked** (you already have one)
5. Click **Create repository**

### Step B — upload the files

**Option 1 — web upload (easiest)**

1. On your new repo page, click **Add file → Upload files**
2. Drag in `index.html`, `luvurava.py`, `README.md`, `.nojekyll`
3. Click **Commit changes**

**Option 2 — Git**

```bash
git init
git add .
git commit -m "Add Pyodide-powered heart animation"
git branch -M main
git remote add origin https://github.com/<YOUR-USERNAME>/<YOUR-REPO>.git
git push -u origin main
```

> ⚠️ Files must sit in the **repository root** (same folder as `index.html`),
> not in a subfolder — otherwise the browser cannot fetch `luvurava.py`.

### Step C — enable GitHub Pages

1. In your repo, open **Settings → Pages** (left sidebar, near the bottom)
2. Under **Build and deployment**:
   * **Source:** `Deploy from a branch`
   * **Branch:** `main`
   * **Folder:** `/ (root)`
3. Click **Save**
4. Wait ~1 minute, then refresh the Settings page. A message appears at the top:
   > Your site is live at `https://<YOUR-USERNAME>.github.io/<YOUR-REPO>/`

### Step D — get the final link

```
https://<YOUR-USERNAME>.github.io/<YOUR-REPO>/
```

Example: user `farzad`, repo `my-love` →
`https://farzad.github.io/my-love/`

Open it, wait for **"Ready — press Run."**, then click **Run**. 🎉

> If your repo is literally named `<YOUR-USERNAME>.github.io`, the site lives at the
> root: `https://<YOUR-USERNAME>.github.io/`

---

## 3. Running locally (optional)

GitHub Pages is needed for the *public link*, but you can test locally with any
static server (a plain `file://` open will fail because `fetch()` is blocked):

```bash
python -m http.server 8000
# then open http://localhost:8000
```

---

## 4. Troubleshooting

| Symptom | Fix |
|---|---|
| Stuck on *"Loading Python runtime…"* | First visit downloads ~10 MB of WebAssembly. Check your network, then hard-refresh with **Ctrl+F5**. |
| *"Could not load luvurava.py (HTTP 404)"* | The `.py` file is not next to `index.html` in the repo root. |
| Blank page / 404 on the site itself | Pages may still be building — wait 1–2 minutes. Confirm the branch/folder settings in Step C. |
| Old version showing after an update | GitHub Pages caches aggressively: **Ctrl+F5**. |
| Colors missing | The page converts your ANSI codes to HTML automatically; if you change the color codes in the Python file, update `ANSI_COLORS` in `index.html`. |
| Changed the Pyodide version | Edit `PYODIDE_VERSION` in `index.html` (current: `v314.0.8`). |
| Changes not appearing | Pages rebuilds on every push to `main`. Wait ~1 minute and refresh. |
