# LabConstrictor App Centre — design benchmark (as given by the user)

Benchmark LabConstrictor as a scientific software catalogue with a straightforward download experience, not as a commercial app store. Closest models: napari hub (discoverability) and BioImage Model Zoo (scientific information). Apple and Microsoft: standards for app pages, screenshots, install options.
Central principle: users should be able to decide whether software is suitable BEFORE downloading it or visiting GitHub.

## 1. What visitors need to know (in order of importance)

| Visitor's question | What LabConstrictor should show | Priority |
|---|---|---|
| What does this app actually do? | One sentence describing the scientific task and outcome, no marketing language | Essential |
| Will it work with my images or data? | Supported input formats and dimensionality, plus important limitations | Essential |
| What will I get out of it? | Expected results: images, masks, tracks, measurements, tables, plots or reports | Essential |
| What does it look like? | Real screenshots of the interface and a representative analysis result | Essential |
| Can I run it on my computer? | Windows, macOS Intel/Apple Silicon, Linux; minimum requirements when relevant | Essential |
| How do I get started? | One prominent download or launch action, followed by a short first-run guide | Essential |
| Is it reliable, and who maintains it? | Development status, version, release date, maintainer, precisely defined verification status | Essential |
| Can I try it without installing? | Colab route where actually available, clearly distinguished from the desktop version | High |
| Can I use it inside napari, Fiji or QuPath? | Compatibility and maturity for each integration, with install instructions | High |
| Where can I get help? | Documentation, troubleshooting and issue-reporting link | Essential |
| Can I use and cite it in research? | License, source repository, relevant publication and DOI | High |
| Does my data stay on my computer? | Brief local-versus-cloud processing explanation, especially when Colab or external services are involved | High when relevant |

BioImage Model Zoo asks contributors for example inputs and outputs, validation information, compatible software and citations. napari's listing guidance emphasises who the plugin serves, what data it handles, what problem it solves and supported formats.

## 2. Benchmark for each part of the website

### A. App Centre: finding and comparing applications
- App cards: app name, one-sentence scientific purpose, icon, primary task, available ways to run it.
- Search: match app names, descriptions, biological tasks and common synonyms, not just exact names.
- Filters: prioritise "What do you want to do?" and "How do you want to run it?".
- Result count: update immediately when filtering; clear way to reset all filters.
- Categories: terms such as Cell tracking, Segmentation, Image restoration, Simulation, Image analysis.
- Special-purpose apps: keep Testing and maintenance separate from scientific applications.
- Navigation: clicking anywhere in a card opens its detail page; the action to obtain the app should remain obvious.
The catalogue is small: fewer, more meaningful filters, not more sophisticated search infrastructure. Do not add download counts, popularity rankings or recommendation algorithms.

### B. Individual app pages: making an informed decision (should be the strongest part)
Recommended content order:
1. App name
2. One sentence explaining what scientific problem the app solves
3. Scientific task | Desktop | Colab (if available)
4. Works with: specific image/data types, dimensionality, relevant limitations
5. Produces: masks, tracks, measurements, plots or other outputs
6. Real application screenshot (ideally input image, interface, representative output)
7. Get the app: Desktop (OS and architecture choices); Colab (when a cloud route is offered). Version, release date, download size and verification status accompany the actual download.
Below the initial decision area: first-run instructions -> example data or workflow -> limitations -> scientific reference -> developer, license, source, support and release notes.
This is a content hierarchy, not a redesign. Apple: authentic UI screenshots. Microsoft: description and at least one screenshot. BMZ: example inputs and outputs. One informative input-to-output example is worth more than several decorative screenshots.

### C. Downloads: avoid wrong installers and false expectations
- Windows installer: download button, architecture support, file size, version, unsigned-installer warning, launch instructions.
- macOS installer: explicit Apple Silicon/Intel choice, how to check the processor, handling macOS security warnings, where the app appears after installation.
- Linux installer: supported architecture, whether a terminal is required, executable command, prerequisites.
- Google Colab: opens in the browser, no local installation, what happens to uploaded data, internet and account requirements.
- pip: clearly labelled advanced route; exact package/install command.
- napari/Fiji/QuPath: genuinely usable now, experimental, or merely planned? What else must be installed? Which host versions have been tested?
The main action should match the visitor's OS without concealing alternatives. A system-detection failure must not silently recommend the wrong architecture.

## 3. Scientific trust needs its own standard
Separate five concepts that are often mixed:
- Availability: a downloadable installer or usable Colab notebook exists.
- Development status: stable, experimental, under development or discontinued.
- Compatibility: versions of Windows/macOS/Linux or host software known to work.
- Verification: what a maintainer actually tested, on which system, for which release, and when.
- Scientific validation: whether the method has been evaluated or published, and what that evidence supports.
A Community listing that passes automated metadata checks must not be mistaken for a scientifically validated application. A published paper does not mean the latest release was tested on every OS. FAIR for research software: clear licensing, version identification, rich metadata, provenance, interoperability, citation.
Practical rules:
- Community: repository and distribution metadata checked automatically; no claim about scientific correctness or installer safety.
- Maintainer-tested: link the statement to a specific version, tested OS and date.
- Experimental integration: distinguish actual experimental functionality from functionality still planned.
- Published method: provide the reference, but do not represent publication as certification of the software.
Privacy: a small factual disclosure when cloud execution is available (whether user data remains local or is uploaded to another service); no large privacy dashboard.

## 4. Submission benchmark for external laboratories
An external author should not have to learn how the website is generated. Enough information for a scientist to choose, no duplication of a full README.
| Field | Recommendation |
|---|---|
| App name and plain-language summary | Required |
| Scientific task/category | Required |
| Input data and expected output | Required or strongly enforced for analysis apps |
| One real screenshot | Required for a public scientific-app listing |
| Working distribution route | Required |
| Source repository, license and maintainer | Required |
| Short first-use instructions | Required |
| Documentation and support link | Required |
| Supported OS/host integrations | Required where claimed |
| Development status and known limitations | Required |
| DOI/publication | Optional, displayed when provided |
| Example/test data | Strongly recommended |
| Hardware or cloud requirements | Required when nontrivial |
Most fits the existing labconstrictor-app.yaml. Principal additional scientific fields: inputs, outputs, limitations, example data. They live in the app repository and feed the website automatically, not a second manually maintained description.

## 5. Technical and usability standards (acceptance criteria, not advertised features)
- Accessibility: WCAG 2.2 AA (keyboard, visible focus, semantic headings, labelled controls).
- Contrast: at least 4.5:1 normal text.
- Touch targets: at least 24x24 CSS px or adequate spacing; larger for primary actions.
- Mobile: no horizontal overflow; install options and key scientific information remain readable.
- Core functionality: catalogue browsing, app-page navigation and download links must work WITHOUT JavaScript.
- Search: clear results, predictable filters, reset action, helpful empty state.
- Performance: LCP <= 2.5 s, INP <= 200 ms, CLS <= 0.1 (75th percentile).
- Content integrity: automatically check internal links, GitHub release assets, version metadata and manifest validity.

### Proposed usability acceptance tests (project-specific)
| Task | Passing result |
|---|---|
| Find an app for cell tracking or nuclei segmentation | relevant result identifiable within 30 seconds |
| Decide whether an app supports a particular image type | input/output requirements identifiable without opening GitHub |
| Install NucleiSky on a Mac | visitor selects the correct chip-specific installer without guessing |
| Understand an unsigned Windows installer | visitor can verify the source and locate the exact installation instructions |
| Find an app usable in napari | current functionality and experimental status unambiguous |
| Start an app for the first time | instructions lead to an actual runnable first example |
| Report a problem or cite the app | correct links present on the app page |
| Browse on a phone with a keyboard | every navigation and download control operable |

## 6. Deliberately exclude
Star ratings, written consumer reviews, popularity rankings, download-count badges, carts, accounts, payments, personalised recommendations, advertising, elaborate sorting, autoplay promo videos.

## 7. Practical priorities
- P0: every app's scientific purpose, inputs and outputs clear (strengthen descriptions and structured metadata)
- P0: downloads and compatibility claims accurate (tighten OS, host-integration, verification labels)
- P0: each app gets a real first-run example and screenshot (make scientific examples a listing requirement)
- P1: search by scientific task (index richer descriptions, biological terminology)
- P1: trust status transparent (separate development maturity, metadata checks, actual testing)
- P1: distinguish local, cloud and embedded-host execution (clarify download/Colab/pip/host routes)
- P1: standardise support, limitations, citations, updates (reuse metadata from each repository)
- P2: measure task completion, accessibility, performance (regression checks, first-time-user testing)

One-sentence benchmark: A scientist should be able to find an application, understand what data it accepts and what results it produces, assess its reliability, and choose the correct way to run it, all from the App Centre, without inspecting source code or decoding a GitHub README.
