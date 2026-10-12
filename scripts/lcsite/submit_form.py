"""The form on /submit/ that writes labconstrictor-app.yaml in the visitor's browser (docs/assets/javascripts/manifest-form.js does the
work and checks the file against the published schema). Here only its HTML: one line, because Markdown would cut a block at a blank line."""

from .text import esc

FACTS = (   # the recommended and optional fields, folded under "More about your app": (name, label, hint, rows, starting value)
    ("license", "Licence", "An SPDX name, for example MIT.", 0, "MIT"),
    ("inputs", "Works with", "One per line, up to six: file formats, dimensions, units it needs.", 3, ""),
    ("outputs", "Produces", "One per line, up to six: images, masks, tables, plots.", 3, ""),
    ("quickstart", "First steps", "One per line, up to six short steps for a first run.", 3, ""),
    ("limitations", "Limitations (optional)", "One per line, up to six.", 2, ""),
    ("description", "Longer description (optional)", "A few plain-text paragraphs, separated by a blank line.", 4, ""),
    ("categories", "Search words (optional)", "Separated by commas, up to six: tracking, segmentation.", 0, ""),
    ("authors", "Authors (optional)", "One per line: a name, then optionally a bar and an ORCID (Ada Lovelace | 0000-0002-1825-0097).", 2, ""),
    ("doi", "DOI of the paper to cite (optional)", "For example 10.1371/journal.pbio.3002740.", 0, ""),
    ("homepage", "Homepage (optional)", "An https address.", 0, ""),
    ("docs_url", "Documentation (optional)", "An https address.", 0, ""),
    ("icon", "Icon (optional)", "A square PNG in your repository, for example app/logo/logo.png.", 0, ""),
    ("screenshots", "Screenshots (optional)", "One per line, up to six: a path in your repository, a bar, then a caption.", 2, ""),
)


def field(name: str, label: str, control: str, hint: str = "") -> str:
    """One field: its label, the control, a hint and the place where its problems are written."""
    hint_html = f'<span class="lc-mf__hint" id="mf-{name}-hint">{esc(hint)}</span>' if hint else ""
    return f'<div class="lc-mf__field"><label for="mf-{name}">{esc(label)}</label>{control}{hint_html}<span class="lc-mf__error" data-mf-error="{name}" aria-live="polite"></span></div>'


def text(name: str, label: str, hint: str = "", rows: int = 0, value: str = "") -> str:
    """A text field, or a text area when `rows` is given."""
    described = f' aria-describedby="mf-{name}-hint"' if hint else ""
    control = (f'<textarea id="mf-{name}" name="{name}" rows="{rows}"{described}></textarea>' if rows
               else f'<input id="mf-{name}" name="{name}" type="text" value="{esc(value)}"{described}>')
    return field(name, label, control, hint)


def routes() -> str:
    """How people get the app (installers, Colab notebooks, pip: at least one) and the programs it also works in (filled from the schema)."""
    return ('<fieldset class="lc-mf__group"><legend>How people get it (at least one)</legend>'
            '<label class="lc-mf__check"><input id="mf-installer" type="checkbox" name="installer" checked> Installers: your latest GitHub release has LabConstrictor installers</label>'
            '<span class="lc-mf__error" data-mf-error="installer"></span><span class="lc-mf__error" data-mf-error="distribution"></span>'
            + text("colab", "Colab notebooks to show", "One per line: a label, a bar, then the Colab link (Notebook | https://colab.research.google.com/github/...).", 3)
            + text("pip", "Python package on PyPI (optional)") + "</fieldset>"
            '<fieldset class="lc-mf__group"><legend>Also works in</legend><div class="lc-mf__hosts" data-mf-hosts></div><span class="lc-mf__error" data-mf-error="hosts"></span></fieldset>')


def form_html(schema_path: str, init_form: str) -> str:
    """The section: what it does (and that the setup form may already have written the file), the fields at the left, the file at the right
    with Download and Copy. Hidden until the script has read the schema; without JavaScript only the line before the example shows."""
    required = (text("name", "Name", "As users know the app (2 to 60 characters).") + text("summary", "One-sentence summary", "Shown on your app's card (20 to 200 characters, plain text).")
                + field("kind", "Kind of app", '<select id="mf-kind" name="kind"><option value="">Choose&hellip;</option></select>'))
    status = field("status", "Development status", '<select id="mf-status" name="status"><option value="">Not stated</option></select>')
    facts = text(*FACTS[0][:3], value=FACTS[0][4]) + status + "".join(text(n, label, hint, rows) for n, label, hint, rows, _ in FACTS[1:])
    return (f'<section class="lc-mf" data-manifest-form data-schema="{esc(schema_path)}" hidden aria-labelledby="mf-title"><h3 id="mf-title">Write it with this form</h3>'
            '<p>Fill in what you know; the file updates as you type and is checked against the schema. Nothing leaves your browser. '
            f'If you set up your repository with the <a href="{esc(init_form)}">LabConstrictor web form</a> and kept "Add a description file for the LabConstrictor App Centre", '
            'you already have this file: open it in your repository and add what is missing.</p>'
            f'<div class="lc-mf__cols"><form class="lc-mf__form" novalidate>{required}{routes()}<details class="lc-fold lc-mf__more"><summary>More about your app (recommended)</summary>{facts}</details></form>'
            '<div class="lc-mf__out"><p class="lc-mf__status" data-mf-status role="status"></p><pre class="lc-mf__yaml"><code data-mf-yaml></code></pre>'
            '<p class="lc-mf__actions"><button type="button" class="lc-btn" data-mf-download disabled>Download labconstrictor-app.yaml</button>'
            '<button type="button" class="lc-btn lc-btn--ghost lc-btn--small" data-mf-copy>Copy</button></p></div></div></section>'
            '<p data-mf-fallback>Or write it yourself, starting from this example:</p>')
