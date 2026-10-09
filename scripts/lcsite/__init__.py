"""Page generator and catalogue builder for the LabConstrictor site.

scripts/fetch_catalogue.py and scripts/build_site.py are the entry points;
the modules here are:

  config      paths, constants, loading YAML and JSON, failing loudly
  text        small string helpers (escaping, slugs, dates)
  page        the Page class: one generated Markdown file
  validate    JSON-Schema checks for manifests and registry entries
  registry    the registry/ pointers, one file per app
  github      a small GitHub API client that never hides a failure
  assets      release asset names -> operating system, architecture, kind
  catalogue   registry + manifests + releases -> build/snapshot.json
  cards       HTML snippets: app cards, badges, download buttons
  pages_apps  the App Centre and one page per app
  pages_site  home, ecosystem, submit and the imported guides
  guides      the template's documentation, turned into site guides
  llms        /llms.txt, the site as plain Markdown for LLMs
"""
