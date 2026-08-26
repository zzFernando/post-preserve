# PostPreserve

PostPreserve is an open-source tool for preserving social media posts as structured and verifiable web archive packages.

Given a post URL, PostPreserve performs a browser-based capture and produces a package containing WARC/WACZ data, a screenshot, extracted metadata, technical provenance, SHA-256 checksums, and a capture quality report.

> One URL in. A verifiable preservation package out.

## Project Overview

PostPreserve focuses on on-demand preservation of individual social media posts, starting with Instagram.
It is designed for international collaboration and use.

PostPreserve was initiated in Brazil as an open-source digital preservation project and is designed for international collaboration and use.

## Current Status

This repository contains an MVP implementation of the core workflow, CLI, identifier storage, package validation, and local tests.
Browsertrix Crawler is integrated as an external capture backend, but real Instagram captures still require a working Docker setup and a valid Browsertrix image.

## Key Features

- Single-URL capture workflow
- Instagram URL validation and normalization
- SQLite-backed local identifier allocation
- Browsertrix capture backend abstraction
- WACZ validation
- Screenshot handling
- Metadata extraction and normalization
- SHA-256 checksum manifest generation
- Package validation and ZIP output
- `doctor`, `archive`, `validate`, and `inspect` CLI commands

## Architecture Overview

- CLI
- Application workflow
- Platform adapters
- Browser capture backend
- Metadata extraction
- WACZ validation
- Quality assessment
- Packaging
- Checksum generation
- Local identifier storage

## Requirements

- Python 3.12
- Docker for Browsertrix-based capture
- Browsertrix Crawler image

## Installation

With Pixi:

```bash
pixi install
```

Or with pip:

```bash
python -m pip install -e .
```

## Browsertrix Setup

PostPreserve uses Browsertrix Crawler as an external tool.
The current MVP expects Docker to be available and the Browsertrix image to be runnable from the local machine.

The implementation documents the image reference in code and keeps Browsertrix isolated from the PostPreserve codebase.

## Basic Usage

```bash
postpreserve doctor
postpreserve archive "https://www.instagram.com/p/EXAMPLE/" --output ./workspace/output
postpreserve validate ./workspace/output/PP-IG-2026-000001.zip
postpreserve inspect ./workspace/output/PP-IG-2026-000001/data/web/post.wacz
```

You can also run:

```bash
python -m postpreserve archive "https://www.instagram.com/p/EXAMPLE/"
```

## Authenticated Browser Profile Usage

Use a browser profile only when you already have a valid authenticated session and the content is accessible without bypassing any platform protections.

```bash
postpreserve archive "https://www.instagram.com/p/EXAMPLE/" --browser-profile ./profiles/instagram
```

PostPreserve never asks for credentials, stores passwords, or tries to bypass authentication, CAPTCHA, or rate limits.

## Package Structure

```text
PP-IG-2026-000001/
├── data/
│   ├── web/
│   │   └── post.wacz
│   └── representations/
│       └── screenshot.png
├── metadata/
│   ├── metadata.json
│   ├── source-metadata.json
│   └── capture-report.json
├── documentation/
│   └── README.txt
├── manifest-sha256.txt
└── package-validation.json
```

## Capture Status

- `complete`: the package passed validation and required outputs are present
- `partial`: the capture ran but one or more required outputs or validations were incomplete
- `failed`: capture or packaging could not complete safely

## Validation Commands

```bash
postpreserve validate ./workspace/output/PP-IG-2026-000001.zip
postpreserve inspect ./workspace/output/PP-IG-2026-000001/data/web/post.wacz
```

## Privacy and Legal Considerations

PostPreserve is not affiliated with Instagram or Meta. The project does not bypass authentication, CAPTCHA, rate limits, access restrictions, or other platform security mechanisms. Users are responsible for ensuring that collection, preservation, and access comply with applicable laws, copyright, privacy requirements, institutional policies, and platform terms.

## Known Limitations

- Instagram capture depends on Browsertrix and Docker
- Real-world post rendering may vary by account state and content type
- The MVP does not support other social platforms yet
- Manual verification is still needed for Browsertrix runtime setup and Instagram edge cases

## Development Instructions

With Pixi:

```bash
pixi run lint
pixi run test
pixi run doctor
```

Or with pip:

```bash
python -m pip install -e .
ruff check src tests
pytest
```

## Contribution Instructions

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Roadmap

- Improve Browsertrix integration and capture reporting
- Add richer Instagram metadata extraction
- Add more robust WACZ inspection details
- Add platform adapters for future sources

## License

PostPreserve is licensed under the Apache License 2.0.

PostPreserve integrates with third-party open-source tools that remain subject to their respective licenses, including Browsertrix Crawler, licensed under the GNU Affero General Public License v3.0.
