# Contributing to Sequence Finder

Thank you for your interest in contributing to the DNA/RNA Sequence Pattern Finder! This document provides guidelines and instructions for contributing to this project.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Features](#suggesting-features)
  - [Submitting Code Changes](#submitting-code-changes)
- [Development Setup](#development-setup)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing](#testing)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)

---

## Code of Conduct

This project follows a standard code of conduct:

- **Be respectful**: Treat all contributors with respect and consideration
- **Be collaborative**: Work together towards improving the project
- **Be constructive**: Provide helpful feedback and suggestions
- **Be inclusive**: Welcome contributions from people of all backgrounds

---

## How Can I Contribute?

### Reporting Bugs

If you find a bug, please create an issue on GitHub with the following information:

**Bug Report Template:**
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command '...'
2. With input file '...'
3. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened (including error messages).

**Environment:**
 - OS: [e.g., macOS 14.0, Ubuntu 22.04]
 - Python version: [e.g., 3.9.7]
 - Package versions: [run `pip list | grep -E 'biopython|openpyxl|pandas|matplotlib'`]

**Input files** (if applicable)
- Attach or describe your FASTA file
- Include patterns/parameters used

**Additional context**
Any other relevant information.
```

---

### Suggesting Features

We welcome feature suggestions! Please create an issue with:

**Feature Request Template:**
```markdown
**Feature Description**
Clear description of the proposed feature.

**Use Case**
Explain why this feature would be useful. What problem does it solve?

**Proposed Implementation**
(Optional) How you think this could be implemented.

**Alternatives Considered**
(Optional) Other approaches you've thought about.

**Biological Justification**
(For biology-related features) Why is this important for biological research?
```

---

### Submitting Code Changes

1. **Fork the repository** on GitHub
2. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following the code style guidelines
4. **Test your changes** thoroughly
5. **Commit your changes** with descriptive commit messages
6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Create a Pull Request** on GitHub

---

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/qiandemoni/HSE_sequence_finder.git
cd HSE_sequence_finder
```

### 2. Create Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Development Dependencies (Optional)

```bash
# For code formatting
pip install black

# For linting
pip install pylint

# For type checking
pip install mypy
```

### 5. Test Your Setup

```bash
python3 sequence_finder.py examples/sample_input.fasta test_output.xlsx \
    --patterns "nGAAn" "nTTCn" "nGAAn"
```

---

## Code Style Guidelines

### Python Style

- **PEP 8**: Follow [PEP 8](https://pep8.org/) style guide
- **Line length**: Maximum 100 characters (acceptable: up to 120 for complex expressions)
- **Formatting**: Use `black` for automatic formatting:
  ```bash
  black sequence_finder.py
  ```

### Naming Conventions

- **Functions**: `lowercase_with_underscores`
- **Classes**: `CapitalizedWords`
- **Constants**: `UPPERCASE_WITH_UNDERSCORES`
- **Private methods**: `_leading_underscore`

### Documentation

- **Docstrings**: All public functions/classes must have docstrings
- **Format**: Use Google-style docstrings

**Example:**
```python
def search_pattern(sequence: str, pattern: str, max_mismatches: int = 2) -> List[Dict]:
    """
    Search for pattern matches in a DNA sequence.

    Args:
        sequence: DNA sequence to search (e.g., "ATCGATCG")
        pattern: Pattern with wildcards (e.g., "nGAAn")
        max_mismatches: Maximum allowed mismatches (default: 2)

    Returns:
        List of match dictionaries containing:
            - 'position': Start position (1-based)
            - 'subsequence': Matched sequence
            - 'mismatch_count': Number of mismatches

    Raises:
        ValueError: If pattern contains invalid characters

    Example:
        >>> search_pattern("ATGAAC", "nGAAn", max_mismatches=1)
        [{'position': 2, 'subsequence': 'TGAAC', 'mismatch_count': 0}]
    """
    # Implementation here
    pass
```

### Type Hints

- **Prefer type hints** for function signatures:
  ```python
  def count_mismatches(sequence: str, pattern: str) -> Tuple[int, List[int]]:
      ...
  ```

### Comments

- **Explain WHY, not WHAT**: Code should be self-explanatory; comments explain reasoning
- **Good comment**:
  ```python
  # Use Hamming distance instead of edit distance because insertions/deletions
  # are not biologically relevant for TF binding site matching
  ```
- **Bad comment**:
  ```python
  # Loop through sequence
  for i in range(len(sequence)):
      ...
  ```

---

## Testing

### Manual Testing

Before submitting, test your changes with:

**1. Basic functionality:**
```bash
python3 sequence_finder.py examples/sample_input.fasta output.xlsx \
    --patterns "nGAAn" "nTTCn" "nGAAn"
```

**2. Edge cases:**
```bash
# No matches
python3 sequence_finder.py examples/sample_input.fasta output.xlsx \
    --patterns "ZZZZZ" "ZZZZZ"

# Single pattern
python3 sequence_finder.py examples/sample_input.fasta output.xlsx \
    --patterns "ATCG"

# Large gap sizes
python3 sequence_finder.py examples/sample_input.fasta output.xlsx \
    --patterns "nGAAn" "nTTCn" \
    --gap-sizes 0 1 2 3 4 5 10
```

**3. Analysis module:**
```bash
python3 analyze_results.py output.xlsx analysis.xlsx
python3 analyze_results.py output.xlsx analysis.xlsx --no-charts
```

### Unit Tests (Future Enhancement)

If you're adding complex logic, consider adding unit tests in a `tests/` directory.

---

## Commit Message Guidelines

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting changes (not code logic)
- `refactor`: Code restructuring without changing behavior
- `test`: Adding/updating tests
- `chore`: Maintenance tasks (dependencies, build, etc.)

### Examples

**Good commit messages:**
```
feat(analysis): add 4D cross-tabulation analysis

Added Pattern × Mismatch × Gap × Sequence analysis to
enable sequence-specific parameter optimization.

Closes #42
```

```
fix(search): correct mismatch position tracking for wildcards

Wildcard positions were incorrectly included in mismatch
position list. Now properly skips 'n' characters.

Fixes #38
```

```
docs(README): add troubleshooting section

Added common error messages and solutions based on
user feedback from Issues #12, #15, #23.
```

**Bad commit messages:**
```
Update code
Fix bug
Changes
WIP
```

---

## Pull Request Process

### Before Submitting

1. ✅ **Test your changes** with multiple test cases
2. ✅ **Update documentation** if you changed functionality
3. ✅ **Update CHANGELOG.md** (if exists) with your changes
4. ✅ **Run code formatter**: `black *.py`
5. ✅ **Check for TODO/FIXME comments** you may have left
6. ✅ **Verify examples still work** (see [Testing](#testing))

### PR Description Template

```markdown
## Description
Brief description of what this PR does.

## Motivation
Why is this change needed? What problem does it solve?

## Changes Made
- Added X feature
- Fixed Y bug
- Updated Z documentation

## Testing
- [ ] Tested on Linux/macOS/Windows
- [ ] Ran all examples successfully
- [ ] Added/updated tests (if applicable)
- [ ] Updated documentation

## Related Issues
Fixes #123
Closes #456

## Screenshots (if applicable)
[Add screenshots of new features/changes]

## Checklist
- [ ] Code follows project style guidelines
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
- [ ] Commit messages follow guidelines
```

### Review Process

1. **Automated checks** (if configured): Must pass before review
2. **Code review**: Maintainer will review your code
3. **Feedback**: Address any requested changes
4. **Approval**: Once approved, PR will be merged
5. **Credit**: Your contribution will be acknowledged in release notes

---

## Questions?

- **General questions**: [GitHub Discussions](https://github.com/qiandemoni/HSE_sequence_finder/discussions)
- **Bugs/Features**: [GitHub Issues](https://github.com/qiandemoni/HSE_sequence_finder/issues)
- **Email**: mqiande@ufl.edu

---

## Recognition

All contributors will be acknowledged in:
- `CONTRIBUTORS.md` file (if you make significant contributions)
- GitHub contributors page
- Release notes for the version including your changes

Thank you for contributing to making bioinformatics tools better! 🎉
