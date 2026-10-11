# Launch checklist (decision 25): the site stays unlisted (`extra.listed: false`) until all of this is true

Switch: `mkdocs.yml` `extra: listed: true`, then update `site_url` if the domain changed.

## Content
- [ ] The four scientific apps show **Works with**, **Produces** and a **real screenshot** on their pages (drafts: `planning/results/6-manifest-drafts.md`). Status on 2026-10-11: **NucleiSky merged** (NucleiSky#30). Pull requests opened for the owners to confirm and merge: CellTracksColab#53, GuessTheCondition#7 and CellMigrationLab/LabConstrictor-VLab4Mic#9 (our fork; the same change would go to the HenriquesLab repository once its owners agree).
- [ ] VLab4Mic's manifest carries its `doi` (decision 21; in the draft commit above, not merged).
- [ ] The clean-install lines exist (`CLEAN-INSTALL-CHECKLIST.md`) and the install and use guides are updated from them.
- [ ] An outside reader (not on DL4MicEverywhere, ZeroCostDL4Mic or BiaPy) has read **Related projects**; optional courtesy note to those maintainers.
- [x] The microscope guide is on the site (NucleiSky's change was merged in #30).
- [ ] The template pull request (CellMigrationLab/LabConstrictor#26: labels, Build path order, template sync moved, use-cases link) is merged, and so are the plugin guide pull requests (Tools#100, Fiji#37, napari-labconstrictor#45) and the daily build has fetched them; then switch the guide-shape report from warnings to failures.

- [ ] When the template pull request is merged: update the install anchors on the site (`pages_get.HINTS`, `content/guides/help.md`) from `#windows`, `#macos`, `#linux` to `#install-on-windows`, `#install-on-a-mac`, `#install-on-linux` in the same change (check_site fails on a broken anchor), and check the new guide "Keep your app up to date" appears in the Build track.
- [ ] Template decisions from `planning/results/7-template-drafts.md`: locked pages (`template_synchronization.md`, `app_manifest.md`) need a migration to change; root README still lists sync as Quick Start step 2; installer images now after "Create installer files" although the form takes them at initialisation; the pull request template is inherited by every app; `Welcome_template.ipynb` says "Test Connection" where the button is "Load Private GitHub Repo".

## Rights and credits
- [ ] Logo and comic provenance recorded (`planning/doc_source-CREDITS.draft.md`): creator, rights holder, licence (CC BY 4.0) and generative tools are filled in (decision 29); year and master file are still blank, and the file has to be added to the template's `doc_source` branch. Then change the README licence line ("their terms are not stated yet") to the CC BY 4.0 credit.
- [ ] NucleiSky banner rights question answered (`QUESTIONS-FOR-AUTHORS.md` #2).
- [ ] The social-media screenshot in the use-cases guide replaced by a link or confirmed by the person shown.

## Technical
- [x] Daily and push builds green on `main` (runs 66-68 green after the unit-test fix of 2026-10-11; `check_site` and `check_design` at 0 problems). Watch it: the publish workflow had failed on every push from run 53 to 65.
- [x] Phone review of the live site (2026-10-11): all 42 pages at 390 px and 768 px, no sideways scrolling, no broken pictures, no script errors.
- [ ] When the site is listed: change the names in schemas and docs from `labconstrictor.cellmig.org` to the address actually used (decision 31 keeps the GitHub Pages address for now).
- [ ] Field performance (LCP, INP, CLS) looked at once on the live address (optional).
