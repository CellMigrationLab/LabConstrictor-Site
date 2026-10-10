You are an adversarial UX and information-architecture auditor with accessibility and front-end expertise. Audit the website below as if you were trying to make a real visitor fail. Do not praise. Do not give generic advice. Every finding must be specific, evidenced, and actionable.

## The site
- URL (public, unlisted preview; the search engines are told to ignore it): https://cellmigrationlab.github.io/LabConstrictor-Site/
- Source: https://github.com/CellMigrationLab/LabConstrictor-Site (README.md says where each page is edited; AGENTS.md says how it is built). Please read both first.
- What it is: the site for LabConstrictor, a template that turns Jupyter notebooks into installable desktop apps (Windows, macOS, Linux) for bioimage analysis. It has: Home, **Apps** (an App Centre: filterable grid, one page per app with a download tile per operating system, Colab and pip routes, and a separate "Testing and maintenance" group), **Docs** (a front page, two tracks "Use an app" and "Build an app", a collapsible docs sidebar, previous/next pager, 25+ guides), **Ecosystem** (projects around LabConstrictor, with GitHub badges), and **Submit your app**. The picture cards on the "Use an app" and "Build an app" pages are screenshots of the real products.
- Two audiences: **users** (biologists who install and use an app, some of whom use napari, Fiji or QuPath plugins that are still experimental) and **developers** (lab members who build and publish an app, and maintainers of the site).
- Known and already fixed (do not report again unless you can show it is still broken): top menu is Home, Apps, Docs, Ecosystem, Submit; the docs sidebar appears on Docs, Use, Build and every guide, folding into a "Docs menu" drawer on phones; menu titles equal each page's heading; each page has an "Edit this page on GitHub" link; host chips on app pages ("Soon in napari") link to guides; every app page links to the install guide.

## Do this, in order
1. Crawl every page (start from the home page and the sitemap-less links; the site has about 36 pages). Build a table: URL, title, H1, how many clicks from Home, which menu item is highlighted, whether the docs sidebar is present, where the page leads next.
2. Simulate these personas on desktop (1280 px) and on a phone (390 px), and for each one record the exact click path, the number of clicks, and where they hesitate or fail:
   a. A biologist on a Mac who wants to install NucleiSky and open it.
   b. A biologist on Windows who sees "Windows protected your PC" and does not know what to do.
   c. A microscopist who wants to run an app inside napari (or Fiji, or QuPath) and does not know the words "plugin" or "tools".
   d. A PhD student who wants to turn their notebook into an app and let others install it.
   e. A principal investigator deciding in two minutes whether this is worth the lab's time.
   f. A developer from another lab who wants to list an existing app.
   g. A screen-reader user (use the heading outline and landmarks) and a keyboard-only user (tab order, focus visibility, skip link, the search dialog, the docs menu).
   h. A visitor with JavaScript disabled and a visitor on a slow mobile connection.
   i. A maintainer who needs to fix a typo in a guide: can they find where to edit it from the page alone?
3. Attack the information architecture: labels that mean different things to different readers; the same place named differently in the menu, the footer and the page; dead ends (pages with no next step); pages reachable only from one place; duplicated content; contradictory instructions; the difference between "Use an app" and the App Centre; whether "Docs" is the right word; whether the two-track split helps or hurts; where a new visitor would expect the Troubleshooting pages; depth of the sidebar; order of items.
4. Attack consistency and trust: title case versus sentence case, wording of calls to action, claims that may be false or stale (for example the statuses "Experimental", "Available", "Soon in ..."), screenshots that look dated or show personal data, anything a cautious scientist would distrust (unsigned installers, "Community" versus "Verified").
5. Check technical quality visible from the outside: heading order, link text such as "here", images without alt text or with decorative alt text that should be empty, colour contrast of small grey text, tap-target sizes on a phone, horizontal scrolling, focus order in the filter form, `target="_blank"` links without `rel`, broken or redirecting links, page weight and the largest images, console errors, behaviour of the OS-aware download tile (it highlights the visitor's operating system and chip), and the search dialog (queries that should find something but do not).
6. Read five guides end to end as a first-time reader and list every place where a step is missing, ambiguous, or relies on knowledge the reader does not have.

## Rules for your answer
- Verify before you claim. If you could not verify something (for example you cannot run a browser), say "unverified" and say what you would check.
- Give concrete evidence for each finding: the URL, the exact text or element, and what the visitor sees.
- Do not suggest a redesign. Suggest the smallest change that fixes each problem, and say in which file or repository it would be made if you can tell from the README.
- Separate what you observed from what you infer.

## Output format
1. A one-paragraph verdict for each persona (could they finish the task? how many clicks? what stopped them?).
2. A table of findings sorted by severity (blocker, major, minor, nit), with columns: ID, persona, URL, what is wrong (evidence), why it matters, smallest fix.
3. The five changes that would improve the site most.
4. A list of things you tried to break and could not.
