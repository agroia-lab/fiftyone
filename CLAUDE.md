# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FiftyOne is an open-source tool for building high-quality datasets and computer vision models. It consists of a Python SDK (`fiftyone` package) and a TypeScript/React web application (the "App") for visualizing and exploring datasets.

## Development Setup

### Source Installation

```bash
# Clone and install (Mac/Linux)
git clone https://github.com/voxel51/fiftyone
cd fiftyone
bash install.sh      # Standard install
bash install.sh -d   # Developer install (includes pre-commit hooks)

# Windows
.\install.bat
.\install.bat -d
```

Requirements: Python 3.9-3.12, Node.js (v17.9.0 recommended via nvm), Yarn

### App Development

```bash
cd app
yarn install
yarn dev           # Start dev server with hot reloading
yarn dev:wpy       # Run both App dev server and Python backend

# In another terminal, start backend manually for stack traces:
python fiftyone/server/main.py
```

### Building

```bash
# Build App only
cd app && yarn build

# Build Python package (includes App)
make python

# Build Docker image
make docker
```

## Testing

### Python Tests

```bash
# Run all unit tests
pytest tests/unittests/

# Run specific test file
pytest tests/unittests/<file>.py

# Run specific test function
pytest tests/unittests/<file>.py -s -k <test_function_name>
```

Test directories:
- `tests/unittests/` - Main unit tests
- `tests/intensive/` - Computationally intensive tests
- `tests/isolated/` - Tests requiring separate pytest processes
- `tests/benchmarking/` - Performance benchmarks

### App Tests (TypeScript)

```bash
cd app
yarn test              # Run tests
yarn test-ui           # Run with UI and coverage
yarn vitest --ui --coverage  # Watch mode with coverage
```

### E2E Tests (Playwright)

```bash
cd e2e-pw
yarn e2e              # Run E2E tests
yarn e2e:ui           # Run with Playwright UI
```

## Linting and Formatting

### Pre-commit Hooks

Pre-commit hooks run automatically on commit (if installed via `install.sh -d`):
- **Black** - Python formatting (line length 79)
- **Pylint** - Python linting (errors only)
- **Prettier** - TypeScript/CSS/Markdown formatting
- **Biome** - Frontend linting for app/spotlight packages

```bash
# Manual linting
pre-commit run --files <file>
pylint <file>  # Full pylint output
```

### Configuration Files

- `pyproject.toml` - Black and isort config
- `pylintrc` - Pylint rules
- `.prettierrc.js` - Prettier config
- `app/.eslintrc.js` - ESLint for App

## Architecture

### Python Package (`fiftyone/`)

- **`core/`** - Core SDK implementation
  - `dataset.py` - Dataset class and management
  - `sample.py`, `frame.py` - Sample and frame data structures
  - `labels.py` - Label types (Classification, Detection, Segmentation, etc.)
  - `fields.py` - Field types for schema definition
  - `view.py`, `stages.py` - DatasetView and view stages (filtering, sorting)
  - `expressions.py` - ViewField/ViewExpression for querying
  - `collections.py` - Base collection functionality
  - `aggregations.py` - Aggregation operations
  - `cli.py` - Command-line interface (`fiftyone` command)
- **`server/`** - GraphQL/Starlette backend serving the App
  - `main.py` - Server entry point
  - `query.py`, `mutation.py` - GraphQL schema
  - `routes/` - HTTP endpoints
- **`operators/`** - Plugin operator system for custom functionality
- **`utils/`** - Dataset format importers/exporters and integrations (COCO, YOLO, etc.)
- **`zoo/`** - Dataset and model zoo for downloading pre-built datasets/models

### App (`app/`)

TypeScript monorepo using Yarn workspaces. Key packages in `app/packages/`:

- **`app/`** - Main React 18 application entry point
- **`core/`** - Core App logic
- **`state/`** - Recoil state management and GraphQL (Relay)
- **`looker/`** - Sample visualization (images, video frames)
- **`looker-3d/`** - 3D point cloud visualization
- **`flashlight/`** - Grid/gallery view for samples
- **`spotlight/`** - New grid implementation
- **`components/`** - Shared React components
- **`operators/`** - Operator UI components
- **`embeddings/`** - Embeddings visualization panel
- **`map/`** - Geolocation map panel
- **`relay/`** - GraphQL Relay configuration
- **`plugins/`** - Plugin system support

Communication: App uses GraphQL (Relay) to communicate with the Python backend via Strawberry GraphQL.

### Database

FiftyOne uses MongoDB (bundled via `fiftyone-db` package) for storing dataset metadata and sample information. The ODM layer is in `fiftyone/core/odm/`.

## Code Style

### Python

- Google Python style (without type annotations)
- 79 character line limit
- 4-space indentation
- Import convention for FiftyOne modules: `import fiftyone.core.labels as fol`
- Use `@todo` for todo items
- Docstrings: Sphinx-Napoleon format

### TypeScript/App

- Function-based React components only
- Use TypeScript with full typing where possible
- Tests in `<package>/test/<module-name>.test.ts`

## Key CLI Commands

```bash
fiftyone --help              # CLI help
fiftyone app launch          # Launch App
fiftyone datasets list       # List datasets
fiftyone zoo datasets list   # List available zoo datasets
```

## Documentation

```bash
# Build docs locally (requires separate Python 3.11 environment)
pip install -r requirements/docs.txt
bash docs/generate_docs.bash
bash docs/generate_docs.bash -c  # Clean build
bash docs/generate_docs.bash -f  # Fast build (skip zoo/plugin docs)
```
