# Combined plan and status (five benchmark inputs, 2026-10-11)

Legend: DONE = on the site (feature branch; `main` has everything up to commit 23796cd, the rest waits for your review of this branch) · DRAFT = prepared as commits on a feature branch in another repository, no pull request · WAIT = needs a person or an answer · LATER = decided against for now.

## 1. App Centre (benchmark: napari hub, BioImage Model Zoo)
| Item | Status |
|---|---|
| Remove Community/Verified, legend, registry fields (decision 1) | DONE |
| Host wording from the plugin's own status; hero line derived | DONE |
| Search by every word, labels searched, filter options and counts built from the apps, empty state | DONE |
| Optional manifest fields (inputs, outputs, limitations, status, platforms), "Not stated", completeness warnings, Submit table | DONE |
| App page order, Get it block (version line, routes, code-signing hint, Colab sentence, pip), checksums, issue tracker, repository owner, JSON-LD | DONE |
| Screenshot alt text and sizes, focus and contrast, phone menu order and Escape, layout shifts, download detection (iPad, ARM) | DONE |
| Manifest drafts for the six apps (copy-only facts) | DRAFT (`planning/results/6-manifest-drafts.md`); owners confirm |
| VLab4Mic doi (decision 21) | DRAFT |
| NucleiSky screenshot replaced by the QC figure (decision 20) | DRAFT |
| Intel Macs / `distribution.platforms` per app (decision 18) | WAIT (owners) |
| Trust labels, "Verified" definition | LATER (removed) |
| Controlled vocabulary of tasks, tiered schemas, ratings | rejected |

## 2. Documentation (benchmark: Diataxis, Galaxy training, QuPath docs)
| Item | Status |
|---|---|
| Hub fixes: alt text, card text, five-step flow, help lines on both hubs and the Docs home, strict hub data | DONE |
| "Find your problem" page; rewritten "Open and use an app"; guide order | DONE |
| Per-system install links on the download tiles | DONE (uses the guide's current anchors) |
| Guide-shape report for critical guides; literal-Markdown report | DONE as warnings (promote to failures after the template merges) |
| Search index hygiene (hub cards and pagers excluded, with a check) | DONE |
| Search-words mechanism (hidden synonyms) | LATER (the help page already carries symptom words) |
| Template label fixes, Build path order, template sync moved after first release, use-cases link, PR checklist | DRAFT (`planning/results/7-template-drafts.md`) |
| Plugin guide fixes (Fiji (ImageJ), first-run lines, napari test-version wording) | DRAFT (`planning/results/8-plugin-guide-drafts.md`) |
| `rewrite_links` fails on links to unpublished template pages | WAIT (ships with the template change) |
| Clean installs, expected outputs, macOS/Windows wording | WAIT (a lab member; `CLEAN-INSTALL-CHECKLIST.md`) |
| Connect to a microscope guide (NucleiSky) | DRAFT, held from `main` until NucleiSky's change is merged (`microscope-guide-held.yaml`) |
| Interactive "How LabConstrictor works" page (Option A, 8 chapters) | DONE on the feature branch (home band links to it); chapters A-E and your option choice still open (`PLAN-how-it-works.md`) |

## 3. Citation and attribution
| Item | Status |
|---|---|
| Home citation block (preprint only, no Zenodo link), footer link, template README check | DONE |
| App page "How to cite" from the manifest `doi` | DONE |
| LICENSE (MIT) and README licence note | DONE |
| Logo and comic provenance | WAIT (maintainer fills `planning/doc_source-CREDITS.draft.md`) |
| Social-media screenshot in the use-cases guide | DRAFT (template) |
| People page, funding text | rejected (decision 26) |
| CITATION.cff, Zenodo clean-up | LATER (owners of the repositories) |

## 4. Interactive demo and video
| Item | Status |
|---|---|
| Notebook, napari and Fiji views, guide, installer part (Windows), bridge explainer, new notebook widgets | DONE |
| Review of the demo code (documented, contained, strict, tested) | DONE |
| Better napari and Fiji views; QuPath; "same app in Fiji, napari, QuPath" | LATER |
| Option A and apply-saved-transform steps of the notebook | LATER (`notebook-widget-audit.md`) |
| Video | LATER (needs real captures) |

## 5. Related projects
| Item | Status |
|---|---|
| Section on the Ecosystem page, 8 entries, disclosure, checked dates, validation, tests | DONE (facts re-checked: Album, Binder, DOIs on Crossref) |
| Outside reader and courtesy notes | WAIT (`LAUNCH-CHECKLIST.md`) |

## Launch
Unlisted until `LAUNCH-CHECKLIST.md` is ticked (decision 25).
