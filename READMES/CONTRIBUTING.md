# Contributing Guide

Guidelines for contributing to MSuite.

---

## 📑 Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Branching Strategy](#branching-strategy)
- [Commit Messages](#commit-messages)
- [Pull Requests](#pull-requests)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Release Process](#release-process)

---

## Code of Conduct

Be respectful, collaborative, and constructive. Harassment or discrimination is not tolerated.

---

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a new branch: `feature/<short-description>`
4. Install dependencies: `poetry install`
5. Run the app locally and tests

---

## Branching Strategy

- `main`: stable, production-ready
- `develop`: integration branch (optional)
- `feature/*`: new features
- `fix/*`: bug fixes

---

## Commit Messages

Follow Conventional Commits:
- `feat: add new endpoint`
- `fix: correct auth bug`
- `docs: update README`
- `test: add unit tests`
- `refactor: simplify service`

---

## Pull Requests

- Rebase onto latest `main`
- Ensure tests pass locally
- Include relevant documentation updates
- Provide a clear description and screenshots (if UI)

---

## Coding Standards

- Python 3.12+
- Type hints where appropriate
- Follow existing project structure and style
- Keep functions small and focused
- Avoid one-letter variable names

---

## Testing

- Add unit/integration tests for new features
- Maintain coverage targets
- Use `pytest` and `httpx` for API tests

---

## Documentation

- Update `README.md` and related docs for significant changes
- Add examples and usage instructions when helpful

---

## Release Process

1. Create a release branch
2. Update version in `pyproject.toml`
3. Tag the release and create GitHub release notes
4. Deploy to production following `DEPLOYMENT.md`

---

**Last Updated:** December 2025
