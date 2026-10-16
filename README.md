# GoTech Solutions Website

A 6-page static site (Home, Services, Portfolio, Contact, Privacy Policy, Terms of
Service) with a contact form backed by a real **Python (Flask) API**, which
can store submissions in either **MySQL** or **Google Sheets**. The static
site is ready to deploy on **GitHub Pages**; the backend deploys separately
(Render, Railway, a VPS, etc.).

```
gotech-solutions/
├── index.html              Home page
├── services.html           Services page (7 service cards)
├── contact.html            Contact page with inquiry form + WhatsApp QR code
├── portfolio.html          Portfolio / Resource Center (project showcase)
├── privacy.html            Privacy Policy
├── terms.html              Terms of Service
├── assets/
│   ├── css/style.css       Shared custom styles
│   ├── js/tailwind-config.js  Shared Tailwind theme config
│   ├── js/main.js          Mobile nav + contact form logic (EDIT THIS)
│   └── images/             All site images (local, no external links)
│       └── whatsapp-qr.jpg  WhatsApp contact QR code (shown on Contact page)
├── tools/portfolio.py       Terminal for adding/editing portfolio projects
├── backend/                 Python (Flask) API — see backend/README.md
│   ├── app.py
│   ├── storage/              MySQL and Google Sheets backends (pick one)
│   └── README.md              Full backend setup + deployment guide
├── apps-script/
│   └── Code.gs               Legacy Google Apps Script option (no longer
│                              wired up by default — kept for reference)
└── README.md                 This file
```

## 1. Connect the contact form to the Python backend

The form on `contact.html` now posts to a Python API you run yourself
(`backend/`), which validates the submission and saves it to **MySQL** or
**Google Sheets** — whichever you choose in one setting.

**Steps (short version — full detail in [`backend/README.md`](backend/README.md)):**

1. `cd backend && pip install -r requirements.txt`
2. `cp .env.example .env` and set `STORAGE_BACKEND` to `mysql` or
   `google_sheets`, then fill in that section's credentials.
3. Run it: `python app.py` (defaults to `http://localhost:5000`).
4. In `assets/js/main.js`, set `CONTACT_API_URL` to your backend's
   `/api/contact` endpoint (local URL while testing, live URL once deployed).
5. Deploy the backend somewhere that can run Python (Render, Railway, a VPS
   with gunicorn) — GitHub Pages only serves static files, so it cannot run
   the API itself.
6. Add your site's URL to `ALLOWED_ORIGINS` in the backend's `.env` so the
   browser is allowed to call it (CORS).

> The old Google Apps Script option (`apps-script/Code.gs`) still works if
> you'd rather not run a backend at all, but it's no longer the default —
> `main.js` now calls the Python API described above.

### Sending inquiries to WhatsApp
Inquiries are forwarded to WhatsApp **0707490519**. See section 8 of
[`backend/README.md`](backend/README.md) for the two delivery options
(`callmebot` or Meta `cloud_api`). Until the backend is deployed and
`CONTACT_API_URL` is set, the contact form falls back to opening WhatsApp with
the visitor's message pre-filled, so it works from day one.

## 2. Legal pages

`privacy.html` and `terms.html` are built from GoTech Solutions' Privacy
Policy and Terms of Service and use the same design system as the rest of
the site. Both pages are linked from the footer on every page.

## 3. WhatsApp QR code

`contact.html` shows a large WhatsApp QR code (`assets/images/whatsapp-qr.jpg`)
above the "Contact Details" card, so visitors can scan it to start a chat
directly.

## 4. Deploy the static site to GitHub Pages

1. Create a new GitHub repository (e.g. `gotech-solutions`).
2. Upload/push the contents of this folder to the repo (keep the file
   structure exactly as-is — `index.html` must be at the repo root). The
   `backend/` folder can live in the same repo or a separate one — it isn't
   served by GitHub Pages either way.
3. In the repo, go to **Settings → Pages**.
4. Under "Build and deployment", set **Source: Deploy from a branch**,
   branch: `main`, folder: `/ (root)`. Save.
5. GitHub will give you a live URL like
   `https://<your-username>.github.io/gotech-solutions/` within a minute or two.

## 5. What's already wired up

- **Navigation** — Services / About / Testimonials / Contact links work
  across all pages (About and Testimonials scroll to sections on the home
  page). Footer Privacy Policy / Terms of Service links go to the new pages.
- **Mobile menu** — the hamburger icon on small screens opens/closes a
  real mobile nav menu.
- **"Get Started" buttons** — link to the Contact page.
- **"Explore Solutions" / "Contact Us" hero buttons** — link to Services /
  Contact respectively.
- **"Learn More" links on service cards** — link to the Contact page and
  automatically pre-select that service in the "Area of Interest" dropdown.
- **Contact form** — client-side + server-side validation, a loading/disabled
  state on submit, and success/error messages sourced from the backend's
  real JSON response, then POSTs to your Python API.
- **WhatsApp QR code** — large, scannable code on the Contact page.
- **Images** — all images are local files in `assets/images/`, no external
  links, so they'll always load reliably (including on GitHub Pages).

## 6. Testing locally

Static site (from this folder):

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000` in your browser.

Backend (from `backend/`, in a separate terminal):

```bash
python app.py
```

With both running and `CONTACT_API_URL` pointed at `http://localhost:5000/api/contact`
in `assets/js/main.js`, the contact form will submit end-to-end locally.

## 7. Updating the portfolio from your terminal

```bash
python3 tools/portfolio.py        # opens the "gotech:$" terminal
```

Inside it: `add`, `edit <name>`, `rm <name>`, `img <name> <files>`,
`top <name>`, `ls`, `preview`, `publish`. Needs only Python 3. Project data is
stored in `assets/data/projects.json`; the tool regenerates
`assets/js/projects.js`, which `portfolio.html` loads. `publish` runs
`git add/commit/push`, or upload the changed files to GitHub manually.
