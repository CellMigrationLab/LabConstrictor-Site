# Attribution and citation audit — preliminary findings (third-party audit pasted by the user; claims are UNVERIFIED input)

Main gap claimed: not the absence of a citation link but absence of clear guidance about WHAT to cite. LabConstrictor is a packaging framework; NucleiSky, CellTracksColab and VLab4Mic are distinct scientific tools.

## LabConstrictor paper
Preprint "Packaging Jupyter notebooks as installable desktop apps using LabConstrictor", Ivan Hidalgo-Cenalmor, Marcela Xiomara Rivera Pineda, Bruno M. Saraiva, Ricardo Henriques, Guillaume Jacquemet; arXiv March 2026; DOI 10.48550/arXiv.2603.10704. The LabConstrictor GitHub README gives it as the recommended citation. It credits Ivan Hidalgo-Cenalmor with framework development, documents contributions, institutional support, funding.
BUT the site footer's "Cite LabConstrictor" link points to 10.5281/zenodo.20758747 (a Zenodo software record), not the preprint. Both may be legitimate (paper vs archived software release) but a visitor is not told which the authors recommend. Correction: expose the recommended paper citation explicitly; offer the software DOI separately for citing a particular archived release.

## Apps have different primary citations
- NucleiSky: Hidalgo-Cenalmor et al., Journal of Cell Science (2026), multimodal microscopy registration; DOI 10.1242/jcs.265152
- CellTracksColab: Gomez-de-Mariscal et al., PLOS Biology (2024), compilation, analysis and exploration of tracking data; DOI 10.1371/journal.pbio.3002740
- VLab4Mic: Martinez et al., bioRxiv (2026), predicting structural resolvability in super-resolution microscopy; DOI 10.64898/2026.06.02.729521
All three upstream projects provide citation information; the problem is surfacing it at the point of use.
Site generator (scripts/lcsite/pages_apps.py) puts a citation in the Details section only when the manifest has a `doi`; it shows a DOI link, not a full reference; the field is optional; the section is after downloads and usage.
Wanted: a dedicated "How to cite this app" subsection with authors, title, venue, year, DOI, copyable reference or BibTeX; the app's version visible separately for reproducibility.
Rule: researcher uses an app for results -> show the app's scientific citation; discusses LabConstrictor itself / notebook packaging / software distribution -> show the LabConstrictor preprint; additional algorithms -> the app's docs identify other relevant methods, without requiring citations for every dependency. (FORCE11 Software Citation Principles: attribution to the appropriate software, persistent identifiers, identification of the version used.)

## Credits, authorship, visuals
Preprint documents collaboration of Abo Akademi University, Turku Bioscience Centre, ITQB NOVA, UCL; funding from Research Council of Finland, Sigrid Juselius Foundation, Cancer Society of Finland, Solutions for Health, InFLAMES, ERC, EIC, EMBO, Chan Zuckerberg Initiative and others. The site ends with "A project of the Cell Migration Lab" and "(c) Cell Migration Lab": not incorrect but does not show collaborative authorship. Give it visibility without a lengthy footer.

| Priority | Finding | Smallest correction |
|---|---|---|
| High | Preprint not displayed on the home page; footer cite link uses the Zenodo DOI | Short "Publication & citation" subsection on Home or Docs: preprint reference + separate software-archive link |
| High | App citations depend on an optional DOI and sit near the bottom of each app page | "How to cite" section on every scientific app page; state clearly when no publication exists |
| High | overrides/main.html attributes the project to one lab, no link to full paper authorship/collaborators | Compact "People and acknowledgements" section linked from the footer: the five authors and institutions |
| Medium | Logo (green snake / orange notebook) imported from the template's doc_source branch; no named illustrator or provenance | Identify creator, document permitted reuse, add credit if appropriate |
| Medium | Homepage three-panel comic from doc_source/comic.png; creator/rights not exposed | Record creator, source, license in a small visual-credits file |
| Medium | Use/Build hub screenshots fetched from the template and LabConstrictor-Tools | Consolidated "Visual credits" note with source repositories, individual credits where required |
| Medium | Website repo had no root LICENSE | Add a license for site code; document any different terms for illustrations |
| Medium | Paper's author-contribution paragraph names G.J., I.H.-C., M.R.; Saraiva and Henriques roles not specified | Ask authors whether an updated CRediT statement is warranted (about the preprint, not the site) |
| Low | Funding detailed in the preprint but not on the site | Modest funding paragraph from the verified acknowledgements; check grant-specific communication requirements |
The correct next step for the logo is provenance verification, not redesign; same for the comic. Do NOT assign authorship to a person or claim AI generation. No personal information seen in screenshots. Inter and Bricolage Grotesque font license files exist in the visual sources. To verify on published pages: logo legibility at ~30 px nav size; whether screenshots borrowed from host-integration repos distinguish experimental from fully supported.

## Ideal citation experience
App page: "How to cite NucleiSky" - Journal article - short bibliographic citation, DOI, copy function ("Copy reference", "Read paper"). Place it close to "Using it", not in Details. Also a version-specific software citation if available. For LabConstrictor itself a comparable block with the 5-author preprint as recommended and the Zenodo archive separate. Add CITATION.cff to relevant repos (GitHub exposes "Cite this repository" with APA and BibTeX). Zenodo record 10.5281/zenodo.20758747 titled LabConstrictor: creator metadata not inspected; .zenodo.json can fix creators/related publications/funding.

## Proposed order
1 Expose preprint directly; distinguish paper DOI from software DOI (data/site.yaml, overrides/main.html, home generator).
2 Auto-populated "How to cite this app" with copy reference (pages_apps.py, manifest schema).
3 Require verified citation metadata or an explicit "No publication available" for scientific apps (each app's labconstrictor-app.yaml; submission validation).
4 Concise author, institutional, funding credits tied to the preprint (footer + small acknowledgements section).
5 Establish authorship and usage rights for logo, comic, external screenshots (template doc_source, data/hubs.yaml, a credits file).
6 CITATION.cff in LabConstrictor and applications; verify Zenodo creators and relationship to the preprint.
Priority: citation accuracy ahead of more content or visual polish. The auditor could not access the live preview; verdict is based on site source examined earlier plus publication records.
