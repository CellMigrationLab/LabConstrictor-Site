# Questions only the authors/owners can answer

Collected from the audits; none blocks the demo build. Send them on, then record the answers in DECISIONS.md.

## Artwork, rights and licence
1. **Logo and comic** (template `doc_source`): who created each (a person, several, a tool; named only if they agree), who holds the rights, and under what licence may others reuse them? May apps built from the template keep using them?
2. **NucleiSky banner** (shown on its app page): it carries a sparkle mark and the repo has `Gemini_Generated_Image_*` files. Who made the banner and logo, and do the tool's terms allow this use? (The audit asks the question; it does not claim the answer.)
3. **Use-cases guide** hot-links a screenshot of a named person's public social-media post. Does the person agree, or should it become a plain link?
4. **Demo images** (HUVEC DAPI reference): CC BY 4.0 (Zenodo 10.5281/zenodo.20721416); the page cites the deposit and the NucleiSky paper. Anything further wanted in the credit line?

## Citation
5. **Zenodo records** (LabConstrictor 10.5281/zenodo.20758747 / concept 10.5281/zenodo.19074199; NucleiSky's concept record lists "Iván Hidalgo" and a GitHub handle as creators): will the owners edit them (relation `describes` vs `isDescribedBy`, affiliations, creator names)? Until then the site shows the preprint only.
6. **Name forms**: Hidalgo-Cenalmor (arXiv, Crossref, ORCID credit name) or Hidalgo Cenalmor (Zenodo)? Rivera Pineda (the preprint) is split wrongly by DataCite; references are written by hand.
7. **VLab4Mic**: is the bioRxiv preprint 10.64898/2026.06.02.729521 the preferred citation (the README links v1, the template guide links v2)? Which repository is canonical (CellMigrationLab or HenriquesLab)? Add `doi` to its manifest.
8. **Guess the Condition, LabConstrictor Demo, LabConstrictor Playground**: is there really no publication? (Predecessor repos napari-guess-the-condition and jupyter-guess-the-condition could not be read.)
9. **People/funding**: do the five authors agree to be listed with institutions, with which affiliations (March 2026 or current), and do funders want a mention on the site?

## Apps and platforms
10. **NucleiSky authors**: agree to be shown in the demo and cite the paper from the manifest `doi`? Is macOS Intel supported for NucleiSky 0.1.1 (release lists x86_64 files, lab protocol says unsupported)? May the banner be replaced by a panel of `2D_QC.jpg` and real screenshots listed in the manifest?
11. **Intel Macs** for GuessTheCondition, Playground and VLab4Mic: stop building the Intel .pkg, or keep it and declare `distribution.platforms`? (VLab4Mic's README says both "ARM64 or Intel" and "Intel Macs are not supported".)
12. **Who fills the six apps' manifests** (inputs, outputs, limitations, status, quickstart, screenshots, docs_url, platforms): the app owners, as six pull requests copying only what their READMEs already say.

## Documentation and template
13. **Template synchronisation** (fine-grained token, secret, ~15 GitHub actions): mandatory before the first init, or an optional step after the first release? Ask the template maintainers.
14. **Clean installs**: who can run clean installs on Windows, macOS and Linux and one throwaway initialise-to-release run, so labels, durations and expected outputs are checked before they are written down?
15. **napari guide** hard-codes `cellmigrationlab.github.io/LabConstrictor-Site/...`: which is the canonical address to keep?
16. **Related projects**: a courtesy note to DL4MicEverywhere, ZeroCostDL4Mic and BiaPy, and an outside reader before listing? Confirm open facts (BiaPy Docker/Colab routes, what JupyterLab Desktop bundles, whether DL4MicEverywhere is maintained).
17. **Launch**: `extra.listed` stays false until at least the four non-testing apps show Works with, Produces and a real screenshot.
