# KAI MkDocs Documentation

This directory contains the MkDocs documentation site for KAI.

## Quick Start

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Development Server

```bash
mkdocs serve
```

Open http://localhost:8000 to view the documentation.

### Build Static Site

```bash
mkdocs build
```

The static site will be generated in the `site/` directory.

### Deploy to GitHub Pages

```bash
mkdocs gh-deploy
```

## Structure

```
mkdocs/
├── mkdocs.yml              # MkDocs configuration
├── requirements.txt        # Python dependencies
└── docs/
    ├── index.md            # Homepage
    ├── getting-started/    # Installation and setup guides
    ├── tutorials/          # Step-by-step tutorials
    ├── user-guide/         # Feature guides
    ├── apis/               # API reference
    ├── cli/                # CLI reference
    ├── architecture/       # System architecture
    └── stylesheets/        # Custom CSS
```

## Theme

This documentation uses the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme with:

- Dark/light mode toggle
- Navigation tabs and sections
- Search with suggestions
- Code copy buttons
- Git revision dates

## Contributing

To add or update documentation:

1. Edit the Markdown files in `docs/`
2. Update `mkdocs.yml` navigation if adding new pages
3. Test with `mkdocs serve`
4. Submit a pull request
