---
title: Submit your app
description: How to list your LabConstrictor app in the App Centre.
layout: wide
edit_url: https://github.com/CellMigrationLab/LabConstrictor-Site/edit/main/content/submit.md
---

# Submit your app

Built an app with LabConstrictor? Listing it takes three steps and no one needs to copy files around: **your app keeps its own description, and the App Centre reads it from your repository.**
{ .lc-lead }

## 1. Add a manifest to your repository

Create a file called `labconstrictor-app.yaml` in the root of your app's repository:

```yaml
# yaml-language-server: $schema={{schema_url}}
schema: 1
name: My App
summary: One sentence that says what it does, for the app card.
kind: analysis            # analysis, segmentation, simulation, game, training, utility
hosts: [notebook, napari] # where its tools can also run: notebook, napari, fiji, qupath
distribution:             # at least one route
  installer: true         # your latest GitHub release has LabConstrictor installers
  colab:
    - label: Notebook
      url: https://colab.research.google.com/github/you/my-app/blob/main/notebooks/App/App.ipynb
  pip: my-app             # name on PyPI
license: MIT
status: Experimental      # Experimental, Available or Deprecated
inputs:                   # what it accepts, in short lines (not README copy)
  - 2D TIFF images
outputs:
  - A table of results (CSV)
limitations:              # optional: where it may be unreliable
  - Needs a pixel size in the image metadata
quickstart:
  - Open the app and run the Welcome notebook.
categories: [tracking, segmentation]   # words a scientist would search for
icon: app/logo/logo.png   # optional square PNG in your repository
```

The [full schema]({{schema_url}}) lists every field (authors, DOI, screenshots and more) and works with the YAML extensions of most editors, which then check your file as you type.

| | Fields |
|---|---|
| **Required** | `schema`, `name`, `summary`, `kind`, `distribution` |
| **Recommended** (the page says "Not stated" or leaves it out; the build reports it, and your app stays listed) | `status`, `quickstart`, `screenshots`, a licence, and for analysis, segmentation and simulation apps `inputs` and `outputs` |
| **Optional** | `limitations`, `description`, `authors`, `doi`, `categories`, `homepage`, `docs_url`, `icon` |

## 2. Make sure your release is ready

- Your repository is **public** and has a **licence**.
- If you offer installers: your latest GitHub release carries the files LabConstrictor builds (`Name-1.0.0-Windows-x86_64.exe`, and so on).
- Colab links point to `colab.research.google.com`. **You choose which notebooks are shown:** list under `colab:` only the notebooks you want visitors to open, one entry each. A notebook that is in your repository but not in the list is not shown; each listed one appears on your app page with an *Open in Colab* button and a *View on GitHub* link.

## 3. Send us the repository

[Open the submission form]({{submit_issue}}) and give the address of your repository. A bot checks the manifest and your release, and tells you what to fix. When everything passes, it opens a pull request that adds your app to the registry; a maintainer merges it and your app appears at the next site build (daily).

The registry stores only a pointer to your repository. Version, downloads and description are always read from your latest release and manifest, so you never need to resubmit when you publish a new version.

## Good to know

- Installers are always downloaded from your own GitHub release. The App Centre never hosts files.
- We record your repository's numeric ID. If the repository moves to a different owner, the listing pauses until a maintainer re-checks it.
- To remove your app, delete its file from the registry (open an issue or a pull request) or archive your repository.
