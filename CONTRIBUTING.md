# Contributing to inundation

Thank you for your interest in contributing to the `inundation` package! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)
- [Security Vulnerabilities](#security-vulnerabilities)
- [Questions](#questions)

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to fernando.romerogalvan@gmail.com.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- A GitHub account

### Setting Up Your Development Environment

1. **Fork the repository**

   Click the "Fork" button on [GitHub](https://github.com/ferg-dwr/inundation) to create your own copy of the project.

2. **Clone your fork**

   ```bash
   git clone https://github.com/YOUR-USERNAME/inundation.git
   cd inundation
   ```

3. **Add the upstream remote**

   ```bash
   git remote add upstream https://github.com/ferg-dwr/inundation.git
   ```

4. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. **Install the package with development dependencies**

   ```bash
   pip install -e ".[dev]"
   ```

6. **Set up pre-commit hooks** (recommended)

   Pre-commit hooks automatically run code quality checks before each commit:

   ```bash
   pip install pre-commit
   pre-commit install
   ```

7. **Verify your setup**

   ```bash
   pytest tests/ -v -m "not integration"
   ```

   All tests should pass.

## Development Workflow

This project uses a **Git Flow-inspired workflow** with `main` and `develop` branches:

- `main` - Stable releases (tagged with semantic versions)
- `develop` - Active development branch
- `feature/issue-N-description` - Feature branches (where N is the issue number)
- `fix/description` - Hotfix branches

### Workflow Steps

1. **Sync your fork with upstream**

   ```bash
   git checkout develop
   git fetch upstream
   git merge upstream/develop
   git push origin develop
   ```

2. **Create a feature branch from develop**

   ```bash
   git checkout -b feature/issue-N-short-description
   ```

   Use a descriptive name that includes the issue number you're working on.

3. **Make your changes** (see [Making Changes](#making-changes))

4. **Test your changes** (see [Testing](#testing))

5. **Commit your changes** with clear messages (see [Commit Messages](#commit-messages))

6. **Push to your fork**

   ```bash
   git push origin feature/issue-N-short-description
   ```

7. **Open a Pull Request** (see [Submitting Changes](#submitting-changes))

## Making Changes

### Working on an Issue

1. Check the [issue tracker](https://github.com/ferg-dwr/inundation/issues) for open issues
2. Comment on an issue to indicate you're working on it
3. If you have an idea that's not yet an issue, open one to discuss first

### Best Practices

- **Keep changes focused** - One PR should address one concern
- **Write tests** - New features should include tests
- **Update documentation** - Keep README, docstrings, and CHANGELOG up to date
- **Follow existing patterns** - Match the code style of surrounding code
- **Ask questions** - If you're unsure, open an issue or draft PR to discuss

## Testing

### Running Tests

```bash
# Run all unit tests (default - fast)
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=inundation --cov-report=html

# Skip slow integration tests (default in CI)
pytest tests/ -m "not integration"

# Run only integration tests (requires network access)
pytest tests/ -m integration

# Run a specific test file
pytest tests/test_cache.py -v

# Run a specific test
pytest tests/test_cache.py::TestCacheManagement::test_show_cache -v
```

### Test Categories

The project has three types of tests:

1. **Unit tests** (`tests/test_*.py`) - Fast, mocked tests with no external dependencies
2. **Scientific correctness tests** (`tests/test_scientific_correctness.py`) - Verify calculation logic with known inputs/outputs
3. **Integration tests** (`tests/test_integration.py`) - Hit live external APIs (CDEC, CNRA)

By default, only unit and scientific tests run in PR CI. Integration tests run on a weekly schedule.

### Writing Tests

- Place new tests in the appropriate file under `tests/`
- For tests that hit external APIs, use mocks with fixtures from `tests/fixtures/`
- See `tests/test_api_edge_cases.py` for examples of mocked API tests
- Test naming: `test_<what_youre_testing>` (e.g., `test_cache_clears_old_entries`)

## Code Style

This project uses several tools to maintain consistent code style:

### Tools

- **Ruff** - Linting and import sorting
- **Black** - Code formatting
- **MyPy** - Static type checking

### Running Style Checks Locally

```bash
# Check linting (no auto-fix)
ruff check .

# Auto-fix linting issues
ruff check . --fix

# Format code
black .

# Check formatting without changing
black --check .

# Type check
mypy src/inundation
```

### Pre-commit Hooks

If you've set up pre-commit hooks (recommended), these will run automatically before each commit:

```bash
# Run pre-commit on all files manually
pre-commit run --all-files

# Run pre-commit on staged files only
pre-commit run
```

### Style Guidelines

- **Type hints** - Add type hints to all new functions
- **Docstrings** - Use NumPy-style docstrings for public functions
- **Line length** - 100 characters max
- **Imports** - Use Ruff/isort sorting rules
- **Comments** - Explain *why*, not *what*

## Submitting Changes

### Commit Messages

Use clear, descriptive commit messages following this format:

```
<type>: <short summary>

<longer description if needed>

<reference to issue or PR if applicable>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Adding or updating tests
- `refactor:` - Code refactoring without changing behavior
- `chore:` - Maintenance tasks (dependencies, build, etc.)
- `ci:` - CI/CD changes

**Examples:**

```
feat: add request-aware caching with metadata

Implements per-request cache keys so different API calls
get separate cache files. Includes metadata tracking.

Resolves #6
```

```
fix: handle empty CDEC responses gracefully

Previously crashed on empty responses; now returns
an empty DataFrame.

Resolves #15
```

### Pull Request Process

1. **Update your branch** with the latest develop:

   ```bash
   git fetch upstream
   git rebase upstream/develop
   ```

2. **Run all checks locally** before pushing:

   ```bash
   pytest tests/ -m "not integration"
   ruff check .
   black --check .
   mypy src/inundation
   ```

3. **Push to your fork**:

   ```bash
   git push origin feature/your-branch-name
   ```

4. **Open a Pull Request** on GitHub:
   - Target the `develop` branch
   - Use a clear, descriptive title
   - Reference the issue you're addressing (e.g., "Resolves #N")
   - Describe what changed and why
   - Include screenshots for UI/visualization changes

5. **PR Description Template:**

   ```markdown
   ## Summary
   Brief description of what this PR does.

   ## Changes
   - Bullet list of changes
   - Files modified, features added, etc.

   ## Testing
   How you tested the changes.

   ## Related Issue
   Resolves #N
   ```

6. **Respond to feedback** - Maintainers may request changes. Update your branch and push again.

7. **CI must pass** - All automated checks must pass before merging.

### Merge Strategy

Maintainers typically merge PRs using "Squash and merge" to keep history clean. Your local commits don't need to be perfect.

## Reporting Issues

### Bug Reports

If you find a bug, please open an issue with:

- **Description** - What happened vs. what you expected
- **Reproduction steps** - How to reproduce the bug
- **Environment** - Python version, OS, package version
- **Code sample** - Minimal example that demonstrates the issue
- **Error message** - Full traceback if applicable

### Feature Requests

For new features, open an issue describing:

- **Use case** - Why is this needed?
- **Proposed solution** - How might it work?
- **Alternatives** - What have you considered?

### Good Issue Examples

Look at existing issues for examples of well-formatted reports.

## Security Vulnerabilities

**Do not open public issues for security vulnerabilities.** See [SECURITY.md](SECURITY.md) for our security reporting process.

## Questions

- For general questions, open a [GitHub Discussion](https://github.com/ferg-dwr/inundation/discussions) (if enabled) or an issue
- For sensitive matters, contact fernando.romerogalvan@gmail.com

## Recognition

Contributors are recognized in:

- The project's `NOTICE.md` file
- Release notes for significant contributions
- GitHub's automatic contributor tracking

Thank you for helping make `inundation` better!

## License

By contributing, you agree that your contributions will be licensed under the [Apache License 2.0](LICENSE.md), the same license as the project.