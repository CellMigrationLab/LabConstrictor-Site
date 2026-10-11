# Launch checklist (decision 25): the site stays unlisted (`extra.listed: false`) until all of this is true

Switch: `mkdocs.yml` `extra: listed: true`, then update `site_url` if the domain changed.

## Content
- [ ] The four scientific apps (CellTracksColab, GuessTheCondition, NucleiSky, VLab4Mic) show **Works with**, **Produces** and a **real screenshot** on their pages (drafts: `planning/results/6-manifest-drafts.md`; owners confirm and merge in their repositories).
- [ ] VLab4Mic's manifest carries its `doi` (decision 21).
- [ ] The clean-install lines exist (`CLEAN-INSTALL-CHECKLIST.md`) and the install and use guides are updated from them.
- [ ] An outside reader (not on DL4MicEverywhere, ZeroCostDL4Mic or BiaPy) has read **Related projects**; optional courtesy note to those maintainers.
- [ ] The microscope guide is on the site (after NucleiSky's change is merged; `planning/microscope-guide-held.yaml`).
- [ ] The template pull requests (labels, Build path order, template sync moved, use-cases link) are merged and the daily build has fetched them; then switch the guide-shape report from warnings to failures.

## Rights and credits
- [ ] Logo and comic provenance recorded (`planning/doc_source-CREDITS.draft.md`, to be filled in by the maintainer); until then the README keeps them out of the CC BY text licence.
- [ ] NucleiSky banner rights question answered (`QUESTIONS-FOR-AUTHORS.md` #2).
- [ ] The social-media screenshot in the use-cases guide replaced by a link or confirmed by the person shown.

## Technical
- [ ] Daily and push builds green on `main`; `check_site` and `check_design` at 0 problems.
- [ ] Field performance (LCP, INP, CLS) looked at once on the live address (optional).
