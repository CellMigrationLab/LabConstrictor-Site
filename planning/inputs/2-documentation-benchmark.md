# LabConstrictor documentation — recommended benchmark (as given by the user)

Goal: documentation that lets a first-time visitor complete a real task independently, not documentation that merely explains how LabConstrictor works. Success: a biologist can install an app and obtain a scientific result, or a researcher can turn a working notebook into a distributable app, without contacting developers.

Benchmarks: Diataxis (learn / do / understand / look up), The Good Docs Project (templates for quickstarts, procedures, references, troubleshooting), Google developer documentation style guide + Microsoft procedural-writing guidance (precise executable instructions), QuPath docs, napari installation docs, Galaxy Training Network (closest examples for bioimage analysis and researchers without much programming experience).
Retain the existing two-track structure "Use an app" and "Build an app" (matches the two audiences). Diataxis should guide content INSIDE those tracks, not require four new top-level sections (Diataxis itself favours incremental improvement).

## 1. What readers need
| Question | Documentation must provide | Priority |
|---|---|---|
| Where do I start? | A clearly marked beginner path requiring no prior knowledge of LabConstrictor | Essential |
| Is this guide for me? | Intended reader, prerequisite knowledge, OS and relevant software versions | Essential |
| What will I achieve? | An explicit outcome at the beginning of a guide | Essential |
| What do I need before starting? | Files, accounts, permissions, installations, example data | Essential |
| Exactly what do I click or type? | Ordered steps using the real labels in the current interface | Essential |
| Did it work? | The expected message, file, screen or scientific result after a critical step | Essential |
| What if my screen looks different? | Platform-specific alternatives and relevant version information | High |
| What if something fails? | Troubleshooting based on visible symptoms and error messages | Essential |
| Can I reproduce the example? | Downloadable sample data, known parameters, expected result | Essential for scientific tutorials |
| What should I do next? | A link to the next relevant TASK, not merely the next document in a list | Essential |
| Is this still accurate? | Current commands, links, screenshots, compatibility statements, identifiable maintenance responsibility | Essential |
| Where can I get help? | Links to existing issues, bug reports or a community support channel | High |
Diataxis: tutorials give a successful learning experience; how-to guides accomplish a specific task; references give facts; explanations answer why.

## 2. Two user journeys
Track A, Use an app: choose an app -> install or open -> run an example -> save results. Cover installation, first launch, the Welcome notebook, opening example data, running one notebook, identifying the output, saving/exporting it. Troubleshooting accessible at each likely failure point.
Track B, Build an app: create repository -> initialise -> add notebook -> build release -> test and share. Every stage states what must already exist, what to do, how to verify completion, where to go next. Template synchronisation, branding, custom code, advanced dependency management and tool integration appear exactly when relevant, not obscuring the main workflow.
Project-specific paths, not a proposal to remove the detailed guides. QuPath: task-based entry points for installation problems, unsupported image formats, first steps. Galaxy: prerequisites, objectives, datasets, workflows, known-working environments.

## 3. What every (task-based) guide should contain
Standard for a how-to guide, e.g. "Create your first installer": one-sentence outcome; audience chips (For app authors, GitHub required); Before you start (what must already exist, link to preceding steps); Instructions (numbered; where to perform, what to select); Check that it worked (what success looks like); If something fails (link to the specific troubleshooting page); Next (useful continuation).
| Component | Requirement |
|---|---|
| Title | A concrete action or user question, not an abstract topic |
| Outcome | What the reader will have achieved |
| Prerequisites | Accounts, files, software, OS, versions, permissions |
| Estimated time | Useful for longer tutorials; distinguish human work from CI/build waiting |
| Steps | Exact UI labels, filenames, paths, copyable commands |
| Verification | What success looks like, preferably an actual result |
| Troubleshooting | Relevant symptoms and recovery |
| Next step | A useful continuation or completion point |
Not every reference or explanatory article needs this structure; apply it to task-based guides only.

## 4. Scientific tutorials need a higher standard (borrow from Galaxy Training Network)
Example input (small downloadable dataset with known format/dimensions); preparation (how to load, configure); parameters (values used, which are safe to change); expected output (representative result, where saved); interpretation (what it means biologically); reproducibility (app version, dataset, environment); limitations (the most important case where analysis may be unreliable); transfer to own data.
The generic Docs site explains how notebook applications operate; the application's own repository should provide its scientific example; the App Centre links to it. Avoid maintaining two copies of app-specific instructions.

## 5. Information architecture
| Area | First | Secondary |
|---|---|---|
| Docs home | Two choices Use/Build; immediate troubleshooting link | Full guide index |
| Use an app | Install -> Open -> Run an example -> Work with your data | Colab, pip, host integrations, advanced notebook usage |
| Build an app | Create repo -> Initialise -> Add notebook -> Build release -> Test -> Submit | Branding, custom code, portability, template maintenance, tool authoring |
| Troubleshooting | Problems organised by symptoms and tasks | Detailed environment diagnostics and logs |
| Reference | Manifest fields, requirements format, release naming, supported integrations | Internal architecture, advanced APIs |
Previous/Next links follow TASK order, not the order source documents happen to be listed. A visitor arriving from an app's download page (e.g. NucleiSky) should land on installation instructions, not restart at the Docs homepage.
Search should understand the problem, not just terminology. Searches that should reach an actionable page:
- "Windows protected your PC" -> Windows installation/security warning
- "Mac cannot open app" -> macOS installer troubleshooting
- "JupyterLab does not start" -> installed-app troubleshooting
- "how to run a notebook" -> Open and use an app
- "put my notebook online" -> Build an app quickstart
- "requirements.yaml" -> generate and validate notebook requirements
- "GitHub build failed" -> workflow troubleshooting
- "use inside Fiji" -> Fiji integration and installation guide
- "app not showing in napari" -> host registration/discovery troubleshooting
Test with technical language AND non-programmer expressions; exact match for "plugin" is insufficient for someone who only knows they want an app inside Fiji.

## 6. Accuracy, maintenance, accessibility
Version accuracy (commands/screenshots/claims match a supported version; record tested version where compatibility matters). Link integrity (zero broken internal links and anchors; check external regularly). Command correctness (tested in documented environment). Workflow correctness (the whole sequence tested from a clean repository). UI accuracy (button/menu names match the current software). Troubleshooting freshness (checked against current error messages). Editing (every guide points to its true source file; generated files never editing targets). Release changes (user-affecting changes trigger review of the relevant docs). Accessibility (WCAG 2.2 AA, keyboard, meaningful link text, logical headings, accessible images). Mobile (readable code, no horizontal scroll, appropriately sized screenshots, no unnecessary large animations).
Google image guidance: cropped screenshots that clarify a step; discourage images of code/text; more efficient alternatives to GIF. W3C: text alternatives convey function or information.
Read the Docs: version-specific docs, non-stable versions identifiable. Do NOT introduce a complex version selector yet; important guides should identify which version/release they were tested against. A strong process: preview per relevant pull request, validate links, run basic docs tests before publishing.

## 7. Measurable acceptance criteria (project targets, measured with people unfamiliar with the project)
| Measure | Target | Test |
|---|---|---|
| Findability | Critical task guide found within 60 s | Give a new visitor a goal, no keywords suggested |
| First-time completion | >=4 of 5 testers finish a core task without intervention | Observe install/use and build/publish journeys |
| First successful analysis | Novice runs the documented example in ~15 minutes after installation | Clean installation + provided test data |
| Guide completeness | 100% of critical how-to guides have prerequisites, expected result, failure route | Automated content checklist + manual review |
| Broken links | Zero broken internal links | Build-time validation |
| Platform instructions | Each advertised installation route exercised on that platform | Windows, macOS Intel/Apple Silicon, Linux |
| Scientific examples | Every featured scientific app has >=1 reproducible example | Fresh-run test against pinned sample data |
| Accessibility | WCAG 2.2 AA, no keyboard blockers | Automated + manual keyboard/screen-reader |
| Maintenance | Each release affecting a documented workflow triggers review of that guide | Release/PR checklist and ownership rules |
Measure whether visitors finish tasks, not whether they read docs; a visitor repeatedly opening troubleshooting pages may signal failure.

## 8. Five priorities
1. Two fully tested first-time tutorials: (a) install an app -> analysis result with example data; (b) working notebook -> tested downloadable installer. Keep all detailed existing guides as supporting material.
2. Standardise critical how-to guides (prerequisites, exact actions, verification, recovery, next step), first for installation, initialisation, notebook upload, dependency generation, release creation, app submission.
3. Organise troubleshooting by recognisable symptoms; discoverable from the relevant task pages; avoid terms like TLS, environments, manifests, registry entries.
4. Require reproducible scientific examples for applications (small example data, workflow, expected output, limitations), owned by the application repository, not duplicated in the template.
5. Test documentation as part of the release process: validate links and commands, review screenshots, test key workflows, generate previews; especially for imported guides and external tools that change independently.

## 9. Do not build
A large documentation platform, a separate page for every minor option, tutorials that explain all of Python or GitHub, videos for every interaction, an AI documentation chatbot, a complex version-selection system. Long architecture explanations and API references should not interrupt a biologist installing an app or a researcher making a first release.

One-sentence benchmark: A reader with the stated prerequisites can follow any critical LabConstrictor guide from beginning to end, reproduce its expected outcome, recognise when something fails, and reach a working solution without guessing a missing step. For scientific tutorials, the outcome must be an actual analysis result, not merely a successfully opened application.
