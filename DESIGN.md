# Design rules

How the pages of the site look and behave, so that the same thing is always done the same way. The rules that can be checked by a
program are checked on every build (`scripts/check_design.py`, `scripts/check_site.py`); the others are reviewed here. When you add something new,
find its type below and use that pattern; if there is no pattern, add one here first.

## Every page

| Rule | Detail |
|---|---|
| One `h1` | The page's name, in sentence case, at most one line; no emoji. |
| Title | `<title>` is "Page name – LabConstrictor" (the home page has its tagline). |
| Description | A meta description of 20-200 characters, **different on every page**. Guides use their opening paragraph; apps use the app's summary; other pages say it in their data file. |
| Machine tags | `lang="en"`, canonical address, `og:title`, `og:description`; `noindex` while `extra.listed` is false. |
| Menu | Exactly one top-menu entry is marked as the current one (apps → Apps; guides, Use and Build → Docs; the demo → Demo). |
| Edit | Every page except the home page ends with "Edit this page on GitHub", pointing to the file where its text is really written. |
| Reach | Every page is reachable from the home page in at most 3 clicks. |
| App header | The app's icon sits **next to its name** on one line; the summary, the badges (kind, development status when Experimental or Deprecated, programs with their plugin stage) and the pills (GitHub, Documentation and Website when the manifest gives `docs_url` and `homepage`) follow below. |
| Back link | Apps: "← All apps". Guides and the Use and Build pages: "← Use an app" or "← Build an app". |

## The design system (one look per role)

Everything below is defined once, in the last section of `docs/assets/stylesheets/lc.css` ("roles"), and enforced by two checks:
`tests/test_design_system.py` (every font size is a token; part of the unit tests) and `tests/browser/smoke.py` (`consistency`: in a real browser, every role has
exactly one computed look across 14 pages; run by hand). **Add a new part to an existing role; never give a part its own size, weight or colour.**

| Token | Value (root is 20 px) | Used for |
|---|---|---|
| `--fs-xs` | 12.8 px | badges and pills, labels, small buttons, credits in the footer, the legal line |
| `--fs-sm` | 13.6 px | helper text (`lc-small`), captions, breadcrumbs, the footer's links, card footers |
| `--fs-ui` | 14.4 px | action links, buttons, tables, the docs menu, card and tile descriptions, code |
| `--fs-body` | 16 px | running text, lists, callouts |
| `--fs-lead` | 19.2 px | the light sentence under a title |
| `--fs-h3` | 22 px | `h3` and the title of every tile and card |
| `--fs-h2` | 28 px | `h2`, also the section titles of the home page |
| `--fs-h1` | 36 px (fluid down to 27 px) | the page's `h1` |
| `--fs-hero` | home page only | the hero title |

| Role | Look |
|---|---|
| Headings | Bricolage Grotesque, strong ink; `h1` 700, `h2` and `h3` 600; `h4` is bold body text. Margins: `h2` 2.4 rem above and .8 rem below, `h3` 1.6 and .5 rem. |
| Title of a tile or card | Same font, size (22 px) and weight (600) as an `h3`: `lc-card__title`, `lc-choice`, `lc-cat`, `lc-feature`, `lc-tile`, `lc-ostile`. |
| Description in a tile or card | 14.4 px, line height 1.55, body ink. |
| Label | 12.8 px, 600, uppercase, tracked .08 em, muted: the kicker, group names in the docs menu and on the Docs home, filter labels, a card's kind, the "Good to know" and "Guides" names on How it works. |
| Lead | 19.2 px, weight 300, line height 1.6; text never runs wider than 52 rem on any page. |
| Box (tile, card, step card, panel, related item, OS tile, How it works tile) | 1 px line border, 12 px corner (`--radius-box`), 1.2 rem padding (`--pad-box`), white; grids of boxes have a 1.2 rem gap (`--gap-grid`). |
| Box that is a link | The border turns dark green, a green shadow appears, the box rises 2 px; the focus ring is the same 2 px green outline. Tiles, cards, step cards, hub features, the docs pager and the How it works tabs all do this. |
| Callout | A 4 px edge on the left, 12 px corners on the right, soft green background, body text: `lc-help`, quotes in guides, the citation, the demo hint, the How it works hand-over. Orange instead of green for a warning, "Make it yours" and an experimental part (admonitions). |
| Table | 14.4 px, strong 600 header, a thin line between rows, no frame or shading, in guides, on app pages and in the demo. |
| Button | A rectangle with a 6 px corner everywhere (also the menu's call to action); 14.4 px 600; small buttons 12.8 px. Pills (badges, GitHub pills) have the full round corner. |
| Pictures and code | Pictures 8 px corner (`--radius-img`), code blocks 6 px (`--radius-code`), code 14.4 px. |

## Headings and text

- **Headings**: `h1` page name; `h2` section; `h3` sub-section (sizes in the table above). Sentence case. A level is never skipped.
- **Label**: small capitals are only for the names of groups inside a list or the docs menu. They are written in sentence case in the source; the style does the capitals.
- **Lead**: the sentence under a page's `h1` (`lc-lead`), on every page that the site writes itself (guides, which are imported documents, start with their own text). **Helper text** (`lc-small`) is muted and small: hints, legends, footnotes.
- Sentence case everywhere. Plain words ("Install", "Open", "Submit"), no "click here".

## Links (three kinds, nothing else)

1. **Text link**: inside a sentence. Underlined, ink colour. The text says where it goes; "here", "this link" and "more" are not allowed.
2. **Action link** (`lc-go`): a destination at the end of a card or block ("Open", "Guide", "Install an app"). Green, bold, no underline, with an arrow that the style adds. The text never contains an arrow.
3. **Pill**: a small rounded link that names a thing. The **GitHub pill** (mark + repository name, or a short label) is the only way to link to a repository; the **program pill** (the program's logo + its name) is the only way to link to napari, Fiji or QuPath (their own websites); the **documentation pill** (a book) links to an app's documentation. Badges that link (for example "napari plugin: experimental", which goes to our guide) are pills.

Behaviour: a link that leaves the site opens in a new tab with `rel="noopener"` (done by `finish_site.py` for Markdown, by `page.py` for generated pages); a link inside the site never does. Every link has a name a screen reader can read.

## Buttons

- Only a **link** navigates; a `<button>` only acts inside the page (copy, clear filters, open the menu, search). A button never goes anywhere.
- **Filled button** (`lc-btn`): the main action of a block: the page's call to action ("Add your app"), the installer of the visitor's own system. **Light button** (`lc-btn--soft`): the downloads of the other systems, in the same green family so none looks unavailable (every download starts light; `lc.js` makes the visitor's system filled, on a Mac only the matching chip when the browser says which). **Ghost button** (`lc-btn--ghost`): the alternative route in the same block (Open in Colab, View on GitHub). **Small ghost** (`lc-btn--small`): in-page actions such as Copy.
- A card contains no button. A page has at most one filled button outside the download tiles.
- **Demo controls** (only on `/demo/`, inside an element marked `data-demo`): `data-demo-act` is a control of the demo itself (view tabs, category tabs), a small site button (the category and view tabs; there is no reset button: changing the view starts again); `data-demo-sim` is a control inside a simulated window (Run, Open the notebook, layer eye, Update). Both are `<button type="button">`; a simulated-window control keeps the look of the program it imitates instead of `lc-btn`. A control that would do nothing is not drawn as a control: it is `disabled`, or plain text.
- Before adding a button, ask whether a link would do. "Get" on a card was a link to the card's own page, so it was removed.

## Cards

A card is **one link** (the whole card) to one destination: icon or logo and name, kind, summary, badges, a footer with its facts. App cards show the logo of each program the app declares a plugin for as a chip (the chips are not links; the plugin's stage, taken from the plugin's own project file, is there for screen readers). Ecosystem cards put the repository, the program and the guide in the footer. Cards that need separate actions (ecosystem cards) put them in the footer as a GitHub pill and an action link, never inside the main text. Cards of the same kind have the same parts in the same order.

## Badges and pills

One size (12 px, bold). Colour says the role: green = route (Desktop, Colab), grey = Testing, orange = a program's plugin and its stage (napari plugin: experimental), white with a border = a link to a repository. A badge without an address is plain text; with one it is a pill.

## Images

- Every image has an `alt` attribute. An empty `alt` is allowed only for a logo, icon or brand mark whose name is written next to it.
- Pictures of the real product (screenshots) have a description in `alt` and, if they teach something, a caption.
- Content images load lazily; images above the fold do not. Icons are square. Formats: PNG, JPEG, GIF; no SVG from app authors.
- Logos of other programs (napari, Fiji, QuPath) and of services (Google Colab) come only from `data/hosts.yaml` (downloaded at build time; an SVG is reduced to one checked path) and are always shown with the name. "Open in Colab" is the small ghost button with the Colab logo; the notebooks on an app page are exactly the ones the author lists in the manifest (`distribution.colab`), each with Open in Colab and View on GitHub.

## The demo page

- It is the **user's journey**, in the order a colleague meets it: **1 See how installation works (Windows)**, shown first, then **2 Explore the installed app** (the app icon, the Welcome notebook, then NucleiSky as one real example in the notebook and, as experimental previews, napari and Fiji). The two parts are wide numbered buttons; under them come the Notebook, napari and Fiji tabs with their logos (only with the installed app), then the green hint line. Under the installer, one line says how macOS and Linux differ and links to the install guide (no macOS or Linux walkthrough). A line under the lead links back to How it works ("See how an app is packaged"), and How it works ends with a hand-over to this page. Switching between Notebook, napari and Fiji always resets the demo (decision of the project lead). In "How the connection works" the three diagram boxes select their step like the numbered steps do. The address names the part shown: `/demo/` (or `?demo=install`) opens the installation walkthrough, `/demo/?demo=use` the installed app; `demo.js` reads it before the first drawing and rewrites it (without a new history entry) when the reader changes part, so a reload or a shared link opens the same part. Without JavaScript the page says that the installation walkthrough needs it.
- It is a **simulation of one precomputed result** and says so in the lead paragraph at the top (no separate notice); the napari and Fiji views also carry the experimental notice. No result number is typed in the HTML: every value comes from `content/demo/example.json` (the only made-up number is the version 9.9.9 of the illustrative update scenario, labelled as such) (made by `tools/demo_assets/`) through `{{placeholders}}` in the window partials.
- Each window partial is one element with no blank lines (Markdown would cut it). Window chrome that is only decoration (menus, tool icons) is `aria-hidden`; everything operable is a native `button`, `input` or `label`, with an accessible name.
- The picture stack (`lc-view`) is one `role="img"` with one `aria-label`; its layer images have an empty `alt` (class `lc-view__layer` is the checker's one exception).
- Without JavaScript the live windows are hidden and three real figures with captions are shown instead.
- The page loads its own style and script through the `page_css` and `page_js` front matter, so no other page pays for them.

## Home page

Order, as the story goes: the hero (the notebook-first sentence, then the two paths **find an app** and **make an app**, no list of programs); the **make an app** path opens How it works, which walks through the steps (the Build hub stays in the Docs menu); **the problem**, the comic across the full width (three stacked panels on a phone); **two demo tiles** under the heading "See it in action" (`tiles_title`; tile titles are `h3`), text only, equal in size, side by side and stacked on a phone, each opening one part of the same demo page in its order: "See how installation works (Windows)" (`demo/`) and "Explore an installed app" (`demo/?demo=use`) (the `tiles` of `data/demo.yaml`); the optional plugin section; Featured apps; the citation. Section titles are left-aligned so the cards and tiles share their left edge, and each title is larger than the titles of the tiles inside it.

- Wording rules (issue #15): write as you would to another scientist; say notebook, workflow, app, install, Python function. Never "packaged once, runs everywhere", "no coding required", "turn any notebook into a plugin" or "one click on every operating system". Installers per system are separate build outputs. The author needs Python; colleagues who install the app do not.
- Featured apps are the registry's `featured` apps that are listed for users (never testing apps); with none, a plain sentence replaces the grid.
- The plugin section is short: one sentence, a chip with the plugins' own stage (taken from their project files) beside the program pills, and one link to the Ecosystem page. It makes no claim about operating systems. No microscope hardware control is claimed.
- Every link that leaves a section is the green arrow link (`lc-go`).

## Citation

- **Home block** (`#cite`, `citation.cite_band`): the heading "Cite LabConstrictor", the template README's sentence and the reference formatted as a citation (authors, title, venue in italics, year, DOI link) in a quote block, the preprint's DOI as a text link and one action link ("Read the preprint"), and one small line saying that each app page names what to cite. Its text is `citation:` in `data/site.yaml`, copied from the template README; `build_site.py` stops if the README no longer has that DOI. The footer's "Cite LabConstrictor" is an internal link to this block. The site shows the preprint only, not a software archive.
- **App page** (`#cite`, `citation.app_section`, right after "Using it"): "How to cite" with the manifest's `doi` as a text link and an action link ("Read the paper"), then the latest release as the version to name. Without a `doi` it says only that the listing names no publication to cite (a testing app without one has no section). The site never builds a reference from a DOI registry.

## App page facts

- **Order**, as a visitor needs it: header, **About** (the manifest's description), the authors' screenshots as a gallery of small pictures (each opens the full picture), **Works with / Produces**, **Get it on your computer**, **Notebooks to open in your browser**, **Using it**, **Limitations**, **How to cite**, **All downloads** (folded: a disclosure with the table and checksums), **Details**.
- **Get it on your computer** starts with one sentence (download the installer for your system; its steps open below; installing needs internet), then the version line and the three system tiles. Clicking a download (or a tile's "steps" link) opens the install steps of that system, folded under the tiles and taken from the template's `install.md` (`guides.install_sections`: one `##` section per system, so the steps are written once); the download itself goes ahead. Without JavaScript the reader opens the fold. There is no separate "How to install" section. An app with neither installers nor pip has no such section.
- **Notebooks to open in your browser** is its own section: the sentence about Google Colab comes first, then each listed notebook with Open in Colab and a View on GitHub button.
- Under the app header, **Works with** and **Produces** (`pages_facts.works_with`) are two plain-text lists from the manifest's `inputs` and `outputs`, introduced by "The authors say it works with / produces". A scientific app (analysis, segmentation, simulation) that gives neither shows one muted line, "Input and output formats: not stated by the author"; other kinds and testing apps show nothing.
- **Limitations** (after "Using it") appears only when the manifest lists some, with no placeholder when it does not.
- **Development status** is a Details row, "Development status (stated by the authors)", reading the manifest's `status` or "Not stated". A grey chip in the header appears only for Experimental and Deprecated. The status is never inferred from a version number.
- Every value is escaped plain text; a missing recommended fact is a warning in `build/problems.md`, never a reason to unlist an app.

## The How it works page

- `/how-it-works/` (`pages_how`, from `data/how-it-works.yaml`) is a **quick overview of the author's journey**, one step at a time, in five steps, numbered like the developer workflow of the preprint (Figure 2A): **1 Build your notebook(s), 2 Create your repository, 3 Define your requirements, 4 Add your notebook, 5 Create a release and share it**. A row of five numbered links comes first, then the figure at the left (half the page, desktop only) and the steps at the right; with JavaScript only the step named by the address (`#step-3`, the first by default) is shown, with the step's text, **the whole developer workflow** of the preprint's Figure 2 (CC BY 4.0, credited in the caption; `content/how/figures/`, made by `tools/how_figures/`) with the demo's red loop round the current step and the rest faded, an optional orange **Make it yours** tile (what the author can customise there: the notebook's interface, name and version, installer images, code hiding, a tools file for napari, Fiji and QuPath, the App Centre description), **Good to know** (short points, no code), **Guides** (links to the docs, which hold the detail) and Back / Next; without JavaScript (and on screens narrower than 1024 px, where the figure is hidden) all five steps are shown one under the other. The last step (the release, with sharing and the App Centre listing) also lists the optional later parts (updates, branding, template updates) as guide links and hands over to the installed-app demo. The page has no code samples, no panels and no controls: the guides do the detail, and every statement follows the guide it links to.
- Every statement follows the guide the chapter links to, and a mocked form uses only labels read from the real form's code. Parts about the napari, Fiji and QuPath plugins carry the experimental notice.

## Related-project page

- Lives on `/related-projects/` (`pages_related.page_related`, from `data/related-projects.yaml`, checked by `related.py`; no top-level menu entry: its menu entry is Ecosystem, with a "&larr; Ecosystem" link at the top). The Ecosystem page ends with a heading "Related projects" (`pages_related.teaser`, id `related`, the address older links use), one sentence and one card in the same grid as the tiers above, which leads to it. The page has a kicker, an `h1` ("Other ways to share notebooks and scientific tools"), an intro, a **visible disclosure sentence** (not a footnote), four **category tiles** (ordinary in-page links: Desktop tools, Containers, Browser and cloud, Related microscopy initiatives), then one `h2` section per group with its entries as **text-first cards** (two columns, one on phones), entries alphabetical within a group, nothing ranked. A group is chosen by the project's principal use (repo2docker builds container images, so it is under Containers; Binder is under Browser and cloud). No filters, carousel or script.
- Each entry has the same parts in the same order: the name (bold text, **not a link**), what it does in the project's own terms, "A good fit when", an optional paper line with a DOI text link, a plain "Shares authors with LabConstrictor" note where it applies, "Checked <date>", then pills.
- Links are only pills: the GitHub pill for a repository, the Documentation and Website pills for its pages (these two pills may be used for third-party projects here), plus the DOI text link. Prose holds no address, bracket or volatile word (popular, fastest, best, stars, downloads), and makes no maintenance, popularity or superiority claim. No logos.
- The closing paragraph says it is our view, and the helper line links to the home `#cite` block, to "Edit this list on GitHub" (the second edit link of a page written from two files) and to the issues.

## Interactions

- Hover: text links underline; cards lift; pills change border colour. Focus: one visible outline colour for all links (white in the dark footer; content links keep the theme's ring), and the skip link shows above the header. Everything works from the keyboard.
- The filter on the App Centre updates as you type and keeps its state in the address. Sections (`details`) open and close with the keyboard.
- On phones the docs menu folds into a "Docs menu" drawer above the content; nothing scrolls sideways.

## Where this is enforced

| Rule | By |
|---|---|
| Titles, descriptions, tags, one `h1`, heading order, links (new tab, generic text, GitHub pill), buttons, images, nested links | `scripts/check_design.py` |
| Dead links and anchors, edit links, menu state, reachability, unescaped author text | `scripts/check_site.py` |
| Annotations, docstrings, function and file size in the code | `tests/test_code_rules.py` |
| Related projects: keys, links, wording, dates | `scripts/lcsite/related.py`, `tests/test_related.py` |
| Everything else in this file | review; change this file in the same pull request as the change |

Known breaks of a rule in content that comes from another repository are listed, with the reason, in `KNOWN_EXCEPTIONS` in `scripts/check_design.py`.
