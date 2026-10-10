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
| Menu | Exactly one top-menu entry is marked as the current one (apps → Apps; guides, Use and Build → Docs). |
| Edit | Every page except the home page ends with "Edit this page on GitHub", pointing to the file where its text is really written. |
| Reach | Every page is reachable from the home page in at most 3 clicks. |
| App header | The app's icon sits **next to its name** on one line; the summary, the badges (tier, kind, programs) and the pills (GitHub, Documentation and Website when the manifest gives `docs_url` and `homepage`) follow below. |
| Back link | Apps: "← All apps". Guides and the Use and Build pages: "← Use an app" or "← Build an app". |

## Headings and text

- **Headings**: `h1` page name (36 px); `h2` section (21 px, sentence case); `h3` sub-section. A level is never skipped.
- **Label**: small capitals (12 px, spaced) are only for the names of groups inside a list or the docs menu. They are written in sentence case in the source; the style does the capitals.
- **Lead**: the sentence under a page's `h1` (`lc-lead`). **Helper text** (`lc-small`) is muted and small: hints, legends, footnotes.
- Sentence case everywhere. Plain words ("Install", "Open", "Submit"), no "click here".

## Links (three kinds, nothing else)

1. **Text link**: inside a sentence. Underlined, ink colour. The text says where it goes; "here", "this link" and "more" are not allowed.
2. **Action link** (`lc-go`): a destination at the end of a card or block ("Open", "Guide", "Install an app"). Green, bold, no underline, with an arrow that the style adds. The text never contains an arrow.
3. **Pill**: a small rounded link that names a thing. The **GitHub pill** (mark + repository name, or a short label) is the only way to link to a repository; the **program pill** (the program's logo + its name) is the only way to link to napari, Fiji or QuPath (their own websites); the **documentation pill** (a book) links to an app's documentation. Badges that link (for example "Soon in napari", which goes to our guide) are pills.

Behaviour: a link that leaves the site opens in a new tab with `rel="noopener"` (done by `finish_site.py` for Markdown, by `page.py` for generated pages); a link inside the site never does. Every link has a name a screen reader can read.

## Buttons

- Only a **link** navigates; a `<button>` only acts inside the page (copy, open the menu, search). A button never goes anywhere.
- **Filled button** (`lc-btn`): the main action of a block: download an installer, the page's call to action ("Add your app"). **Ghost button** (`lc-btn--ghost`): the alternative route in the same block (the other Mac chip, Open in Colab). **Small ghost** (`lc-btn--small`): in-page actions such as Copy.
- A card contains no button. A page has at most one filled button outside the download tiles.
- Before adding a button, ask whether a link would do. "Get" on a card was a link to the card's own page, so it was removed.

## Cards

A card is **one link** (the whole card) to one destination: icon or logo and name, kind, summary, badges, a footer with its facts. App cards show the logo of each program the app works in as a chip (the chips are not links; the name is there for screen readers). Ecosystem cards put the repository, the program and the guide in the footer. Cards that need separate actions (ecosystem cards) put them in the footer as a GitHub pill and an action link, never inside the main text. Cards of the same kind have the same parts in the same order.

## Badges and pills

One size (12 px, bold). Colour says the role: green = tier or route (Community, Verified, Desktop, Colab), grey = Testing, orange = a program (Soon in napari), white with a border = a link to a repository. A badge without an address is plain text; with one it is a pill.

## Images

- Every image has an `alt` attribute. An empty `alt` is allowed only for a logo, icon or brand mark whose name is written next to it.
- Pictures of the real product (screenshots) have a description in `alt` and, if they teach something, a caption.
- Content images load lazily; images above the fold do not. Icons are square. Formats: PNG, JPEG, GIF; no SVG from app authors.
- Logos of other programs (napari, Fiji, QuPath) come only from `data/hosts.yaml` (downloaded from the project's own repository) and are always shown with the program's name.

## Interactions

- Hover: text links underline; cards lift; pills change border colour. Focus: one visible outline for everything (`:focus-visible`). Everything works from the keyboard.
- The filter on the App Centre updates as you type and keeps its state in the address. Sections (`details`) open and close with the keyboard.
- On phones the docs menu folds into a "Docs menu" drawer above the content; nothing scrolls sideways.

## Where this is enforced

| Rule | By |
|---|---|
| Titles, descriptions, tags, one `h1`, heading order, links (new tab, generic text, GitHub pill), buttons, images, nested links | `scripts/check_design.py` |
| Dead links and anchors, edit links, menu state, reachability, unescaped author text | `scripts/check_site.py` |
| Annotations, docstrings, function and file size in the code | `tests/test_code_rules.py` |
| Everything else in this file | review; change this file in the same pull request as the change |

Known breaks of a rule in content that comes from another repository are listed, with the reason, in `KNOWN_EXCEPTIONS` in `scripts/check_design.py`.
