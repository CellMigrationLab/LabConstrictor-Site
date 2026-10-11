# Decisions by the maintainer (answers to the open questions, in order)

Raw material for the final plan. Each entry: the question, the answer, what it changes.

1. **Verified / Community badges: remove altogether.** (Asked 2026-10-11.) The App Centre will not show a Community or Verified tier. Consequences to carry into the final plan: remove the tier badge and legend from cards and app pages (`cards.py` is_verified/tier badge, `pages_apps.py` LEGEND and the Details row), the `verified_version`/`verified_on` registry fields and their schema/tests/docs (`content/submit.md` tier text, README, AGENTS.md, DESIGN.md badge colour rules); drop the App Centre plan's item 13 (trust-label definitions) and the docs plan's question on redefining Verified. No replacement trust label unless asked later.

2. **Missing scientific facts in a manifest: warn only, show "Not stated".** New fields (inputs, outputs, limitations, development status, quickstart, screenshot, docs link) are optional; build/problems.md lists what each app lacks; no app is delisted; no hard requirement until the six manifests are filled and the initialiser collects the fields.
