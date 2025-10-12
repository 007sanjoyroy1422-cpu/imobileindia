
I'mobileindia — Pro Website + Auto Data (GitHub Actions -> Netlify)
=================================================================

What's included:
- index.html, styles.css, app.js
- devices.json (sample)
- fetch_api.py (script to fetch phone data from an API)
- .github/workflows/update.yml (GitHub Actions workflow to run fetch_api.py daily and commit devices.json)
- README.md (this file)

Goal:
- Use a phones API (or another source) to update devices.json automatically once per day.
- Netlify serves the frontend and redeploys automatically when the repo is updated.

Step-by-step (minimal actions you need to do):
1) Create a GitHub account (if you don't have one).
2) Create a new public repository named "imobileindia" (or any name).
3) Upload all files from this package to the repository root (you can do from phone using the GitHub app or website).
   - Or: Create repo and drag & drop files on GitHub's "Add files" -> "Upload files".
4) On GitHub repo, go to Settings -> Secrets -> Actions -> New repository secret:
   - Name: PHONES_API_URL
   - Value: <the phones API endpoint that returns JSON list of phones>
   - (Optional) Name: PHONES_API_KEY and its value.
5) Enable GitHub Actions (allowed by default). The included workflow will run daily at 02:00 UTC and on manual dispatch.
6) Connect Netlify:
   - Go to Netlify (app.netlify.com) -> Sites -> New site -> Import from Git -> Connect to GitHub and select your repo.
   - Follow prompts; Netlify will build and deploy the site. For this simple static site there's no build command.
7) When the workflow updates devices.json and pushes, Netlify will auto-deploy the latest site.

Notes about data source:
- You must provide a valid API URL in PHONES_API_URL secret. Many public phone APIs exist; adapt fetch_api.py if response structure differs.
- If you'd prefer a custom scraper, I can provide a scraping script — be mindful of site terms of service.
- If you want me to prepare the repo-ready ZIP with branding/images and more sample data, tell me and I will build it now.

Need help?
- I can prepare the final ZIP and you just upload to GitHub + connect Netlify.
- Or if you'd like, I can walk you through each step on your phone (I'll give precise taps/clicks).
