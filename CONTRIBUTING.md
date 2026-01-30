# Contributing to Email Summarizer Agent

First off, thanks for taking the time to contribute! 🎉

The following is a set of guidelines for contributing to this project. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## How Can I Contribute?

### Reporting Bugs
This section guides you through submitting a bug report.
* **Use a clear and descriptive title** for the issue to identify the problem.
* **Describe the exact steps which reproduce the problem** in as much detail as possible.
* **Provide typical emails** (redacted) that failed to parse, if applicable.

### Suggesting Enhancements
* **Use a clear and descriptive title** for the issue.
* **Provide a specific example** of how the new feature would look or work.
* **Explain why this enhancement would be useful** to most users.

## Pull Requests

1. **Fork the repo** and create your branch from `main`.
2. **Install dependencies** in a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Format your code**. We try to follow PEP 8.
4. **Test your changes** locally.
5. **Ensure no secrets** (like `credentials.json` or `token.json`) are committed.
6. **Submit that PR!**

## Development Setup

1. Follow the [Setup Guide](README.md#setup-guide) in README.
2. Use `.env.example` as a template for your local `.env`.

## Styleguides

### Git Commit Messages
* Use the present tense ("Add feature" not "Added feature").
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...").
* Limit the first line to 72 characters or less.
