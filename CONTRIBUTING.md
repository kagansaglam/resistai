# Contributing to ResistAI

Thank you for your interest in ResistAI. Bug reports, questions, feature requests and pull requests are welcome.

## Reporting problems and asking questions

Open an issue at <https://github.com/kagansaglam/resistai/issues>. For a bug report please include:

- what you ran (command or API call) and what you expected,
- the error message or output,
- your operating system and Python version.

## Contributing code

1. Fork the repository and create a branch from `main`.
2. Install the dependencies: `pip install -r requirements.txt pytest`.
3. Make your change and add or update a test in `tests/`.
4. Run the tests: `python -m pytest tests -v`.
5. Open a pull request describing the change and why it is useful.

## Scope notes

- Druggability scores are structural proxies computed by fpocket on predicted structures. Changes that alter how scores or tiers are computed should explain the effect on the results in `results/`.
- The web front end and the REST API live in separate repositories (`resistai-web` and `resistai-api`); please open issues about them in those repositories.

## Code of conduct

Please be respectful and constructive. Harassment or discriminatory behaviour is not tolerated.
