# Updating Apio Docs

Apio documentation is written in Markdown and published using the `mkdocs`
tool at <https://fpgawars.github.io/apio/docs>. The rest of this page explains
how to update and preview the documentation.

> NOTE: The Apio github workflow that publishes the Apio docs, also publishes the
> test coverage report at <https://fpgawars.github.io/apio/coverage>

## Installing MkDocs

Install MkDocs and the Material theme with:

```
pip install mkdocs-material
```

## Navigation

The structure and navigation of the docs are defined in `mkdocs.yml`,
including the site layout and page mappings.

## Pages

Markdown page files (`*.md`) are stored in the `docs` directory.

## Graphics

Pictures, diagrams, and other graphics are stored in the `docs/assets`
directory.

## Stylesheets

Apio's custom styles are defined in `docs/stylesheets/extra.css`, which is
referenced from `mkdocs.yml`.

## Previewing Local Changes

To start a local web server and preview changes as you edit:

```
invoke docs-viewer
```

This enables live reloading in your browser.

## Sending a Pull Request

Before sending a pull request to the Apio repository, check the following on your forked repository:

1.  The following workflows in the **Actions** tab of your fork repo completed successfully:

    - **publish-mkdocs-docs**
    - **pages-build-deployment**
    - **monitor-apio-latest**
    - **test**

2.  The docs at `https://${user}.github.io/apio/docs` are live and include
    your changes (replace _${user}_ with the username of your fork repo).

## Publishing

Documentation is automatically published when changes are pushed
to `mkdocs.yml` or the `docs` directory. This triggers the GitHub Actions
workflow:

```
.github/workflows/publish-mkdocs-docs.yaml
```

The workflow updates the site on GitHub Pages via the `gh-pages`
branch. You can monitor workflow runs in the repository's **Actions** tab.
