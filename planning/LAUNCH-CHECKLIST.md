# Launch checklist (decision 25): the site stays unlisted (`extra.listed: false`) until all of this is true

Switch: `mkdocs.yml` `extra: listed: true`, then update `site_url` if the domain changed.

## Content
- [ ] The four scientific apps (CellTracksColab, GuessTheCondition, NucleiSky, VLab4Mic) show **Works with**, **Produces** and a **real screenshot** on their pages (drafts: `planning/results/6-manifest-drafts.md`; owners confirm and merge in their repositories).
- [ ] VLab4Mic's manifest carries its `doi` (decision 21).
- [ ] The clean-install lines exist (`CLEAN-INSTALL-CHECKLIST.md`) and the install and use guides are updated from them.
- [ ] An outside reader (not on DL4MicEverywhere, ZeroCostDL4Mic or BiaPy) has read **Related projects**; optional courtesy note to those maintainers.
- [ ] The microscope guide is on the site (after NucleiSky's change is merged; `planning/microscope-guide-held.yaml`).
- [ ] The template pull requests (labels, Build path order, template sync moved, use-cases link) are merged and the daily build has fetched them; then switch the guide-shape report from warnings to failures.

- [ ] When the template pull request is merged: update the install anchors on the site (`pages_get.HINTS`, `content/guides/help.md`) from `#windows`, `#macos`, `#linux` to `#install-on-windows`, `#install-on-a-mac`, `#install-on-linux` in the same change (check_site fails on a broken anchor), and check the new guide "Keep your app up to date" appears in the Build track.
- [ ] Template decisions from `planning/results/7-template-drafts.md`: locked pages (`template_synchronization.md`, `app_manifest.md`) need a migration to change; root README still lists sync as Quick Start step 2; installer images now after "Create installer files" although the form takes them at initialisation; the pull request template is inherited by every app; `Welcome_template.ipynb` says "Test Connection" where the button is "Load Private GitHub Repo".

## Rights and credits
- [ ] Logo and comic provenance recorded (`planning/doc_source-CREDITS.draft.md`, to be filled in by the maintainer); until then the README keeps them out of the CC BY text licence.
- [ ] NucleiSky banner rights question answered (`QUESTIONS-FOR-AUTHORS.md` #2).
- [ ] The social-media screenshot in the use-cases guide replaced by a link or confirmed by the person shown.

## Technical
- [ ] Daily and push builds green on `main`; `check_site` and `check_design` at 0 problems.
- [ ] Field performance (LCP, INP, CLS) looked at once on the live address (optional).
