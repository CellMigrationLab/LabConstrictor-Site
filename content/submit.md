---
title: Submit your app
description: How to list your LabConstrictor app in the App Centre.
---

# Submit your app

Built an app with LabConstrictor? Listing it takes three steps and no one needs to copy files around: **your app keeps its own description, and the App Centre reads it from your repository.**

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
icon: app/logo/logo.png   # optional square PNG in your repository
```

The [full schema]({{schema_url}}) lists every field (authors, DOI, screenshots and more) and works with the YAML extensions of most editors, which then check your file as you type.

## 2. Make sure your release is ready

- Your repository is **public** and has a **license**.
- If you offer installers: your latest GitHub release carries the files LabConstrictor builds (`Name-1.0.0-Windows-x86_64.exe`, and so on).
- Colab links point to `colab.research.google.com`.

## 3. Send us the repository

[Open the submission form]({{submit_issue}}) and give the address of your repository. A bot checks the manifest and your release, and tells you what to fix. When everything passes, it opens a pull request that adds your app to the registry; a maintainer merges it and your app appears at the next site build (daily).

The registry stores only a pointer to your repository. Version, downloads and description are always read from your latest release and manifest, so you never need to resubmit when you publish a new version.

## What the labels mean

- **Community**: listed after automatic checks (public repository, valid manifest, downloads served from your GitHub release).
- **Verified**: a maintainer also installed and ran a specific version. The badge applies to that version; a newer release is shown as Community until it is checked again.

## Good to know

- Installers are always downloaded from your own GitHub release. The App Centre never hosts files.
- We record your repository's numeric ID. If the repository moves to a different owner, the listing pauses until a maintainer re-checks it.
- To remove your app, delete its file from the registry (open an issue or a pull request) or archive your repository.
