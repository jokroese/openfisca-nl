# OpenFisca-NL: Dutch Rules-as-Code Model

OpenFisca-NL is a rules-as-code implementation of the Dutch tax and benefit system, based on official legislation published by the Belastingdienst (Dutch Tax Authority) and the Rijksoverheid (Dutch Government).

## Scope

This package currently models the following components of the Dutch tax system:

- **Box 1 Income Tax (Inkomstenbelasting)**
  - Progressive tax brackets for wages and self-employment income
  - Tax brackets for 2023, 2024, and 2025

- **Tax Credits (Heffingskortingen)**
  - General tax credit (algemene heffingskorting)
  - Labor tax credit (arbeidskorting)

- **Self-Employment (Zelfstandigen)**
  - Self-employed deduction (zelfstandigenaftrek) - only applied if `urencriterium_voldaan` is true for the year
  - SME profit exemption (mkb-winstvrijstelling)
  - Hours criterion (urencriterium) requirement

- **Social Security Contributions**
  - Simplified model of AOW, WLZ, and other contributions

- **Property Tax (OZB)**
  - Simplified municipal property tax model

## Disclaimer

This package implements official Dutch rules in code form, based on publicly available legislation. It is **not affiliated with the Dutch government** and should **not be relied upon for personal tax filing**. Always consult official sources or a qualified tax advisor for tax advice.

## How the Model Works

All modeling happens within the `openfisca_nl` folder:

- The **parameters** folder contains tax rates, brackets, and thresholds from official sources
- The **variables** folder contains the formulas that calculate taxes and benefits
- The **reforms** folder (optional) contains experimental policy modifications

The files that are outside from the `openfisca_nl` folder are
used to set up the development environment.

## Packaging your Country Package for Distribution

Country packages are Python distributions. You can choose to distribute your
package automatically via the predefined continuous deployment system on GitHub
Actions, or manually.

### Automatic continuous deployment on GitHub

This repository is configured with a continuous deployment system to automate
the distribution of your package via `pip`.

#### Setting up continuous deployment

To activate the continuous deployment:

1. Create an account on [PyPI](https://pypi.org/) if you don't already have
   one.
2. Generate a token in your PyPI account. This token will allow GitHub Actions
   to securely upload new versions of your package to PyPI.
3. Add this token to your GitHub repository's secrets under the name
   `PYPI_TOKEN`.

Once set up, changes to the `main` branch will trigger an automated workflow to
build and publish your package to PyPI, making it available for `pip`
installation.

### Manual distribution

If you prefer to manually manage the release and distribution of your package,
follow the guidelines provided by the
[Python Packaging Authority](https://python-packaging-user-guide.readthedocs.io/tutorials/distributing-packages/#packaging-your-project).

This involves detailed steps on preparing your package, creating distribution
files, and uploading them to PyPI.

## Install Instructions for Users and Contributors

This package requires
[Python 3.11](https://www.python.org/downloads/release/python-3110/) or higher. More
recent versions should work, but are not tested.

All platforms that can execute Python are supported, which includes GNU/Linux,
macOS and Microsoft Windows.

### Setting up with uv

This project uses [uv](https://docs.astral.sh/uv/), a fast Python package installer and resolver. 

First, install `uv`:

```sh
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

`uv` automatically manages virtual environments and Python versions for you, so you don't need to manually create or activate a venv.

:tada: You are now ready to install this OpenFisca Country Package!

Two install procedures are available. Pick procedure A or B below depending on
how you plan to use this Country Package.

### A. Minimal Installation (uv pip install)

Follow this installation if you wish to:

- run calculations on a large population;
- create tax & benefits simulations;
- write an extension to this legislation (e.g. city specific tax & benefits);
- serve your Country Package with the OpenFisca Web API.

For more advanced uses, head to the
[Advanced Installation](#advanced-installation-git-clone).

#### Install this Country Package with uv

Check the prerequisites:

```sh
python --version  # should print "Python 3.11.xx" or higher
uv --version      # should print the uv version
```

Install the Country Package:

```sh
uv pip install openfisca-nl
```

:warning: Please beware that installing the Country Package is
dependent on its maintainers publishing said package.

:tada: This OpenFisca Country Package is now installed and ready!

#### Next Steps

- To learn how to use OpenFisca, follow our
  [tutorials](https://openfisca.org/doc/).
- To serve this Country Package, serve the
  [OpenFisca Web API](#serve-your-country-package-with-the-openFisca-web-api).

Depending on what you want to do with OpenFisca, you may want to install yet
other packages in your venv:

- To install extensions or write on top of this Country Package, head to the
  [Extensions documentation](https://openfisca.org/doc/contribute/extensions.html).
- To plot simulation results, try [matplotlib](http://matplotlib.org/).
- To manage data, check out [pandas](http://pandas.pydata.org/).

### B. Advanced Installation (Git Clone)

Follow this tutorial if you wish to:

- create or change this Country Package's legislation;
- contribute to the source code.

#### Clone this Country Package with Git

First, make sure [Git](https://www.git-scm.com/) and [uv](https://docs.astral.sh/uv/) are installed on your machine.

Set your working directory to the location where you want this OpenFisca
Country Package cloned.

Check the prerequisites:

```sh
python --version  # should print "Python 3.11.xx" or higher
uv --version      # should print the uv version
```

Clone this Country Package on your machine:

```sh
git clone https://github.com/jokroese/openfisca-nl.git
cd openfisca-nl
uv sync --all-extras
```

You can make sure that everything is working by running the provided tests:

```sh
uv run poe test
```

> [Learn more about tests](https://openfisca.org/doc/coding-the-legislation/writing_yaml_tests.html)

:tada: This OpenFisca Country Package is now installed and ready!

#### Next Steps

- To write new legislation, read the
  [Coding the legislation](https://openfisca.org/doc/coding-the-legislation/index.html)
  section to know how to write legislation.
- To contribute to the code, read our
  [Contribution Guidebook](https://openfisca.org/doc/contribute/index.html).

### Development Commands

The project uses [Poe the Poet](https://github.com/nat-n/poethepoet) for task running. Use these convenient commands:

```sh
# Run tests
uv run poe test

# Format code
uv run poe format

# Lint code
uv run poe lint

# Build package
uv build

# Serve API locally
uv run poe serve
```

### C. Contributing

Follow this tutorial if you wish to:

- contribute to the source code.

_Note: This tutorial assumes you have already followed the instructions laid
out in section [B. Advanced Installation](#b-advanced-installation-git-clone)._

In order to ensure all published versions of this template work as expected,
new contributions are tested in an isolated manner on Github Actions.

Follow these steps to set up an isolated environment for testing your
contributions as Github Actions does.

#### Set up an isolated environment

First, make sure [Tox](https://tox.wiki/en/4.23.0/) is installed on your
machine.

We recommend using [uv tool](https://docs.astral.sh/uv/guides/tools/) or [pipx](https://pypi.org/project/pipx/) to install `tox`,
to avoid mixing isolated-testing dependencies with your development environment.

```sh
# With uv (recommended)
uv tool install tox

# Or with pipx
pipx install tox
```

#### Testing your contribution in an isolated environment

You can make sure that your contributions will work as expected by running:

```sh
tox
```

You can also run these in parallel:

```sh
tox -p
```

:tada: Your contribution to OpenFisca Country Package is now ready for prime
time!

#### Next Steps

- Open a pull request to the `main` branch of this repository.
- Announce your changes as described in [CONTRIBUTING](CONTRIBUTING.md).

## Serve this Country Package with the OpenFisca Web API

If you are considering building a web application, you can use the packaged
OpenFisca Web API with your Country Package.

To serve the Openfisca Web API locally, run:

```sh
uv run poe serve --port 5000
```

Or use the full command:

```sh
uv run openfisca serve --port 5000 --country-package openfisca_nl
```

To read more about the `openfisca serve` command, check out its
[documentation](https://openfisca.org/doc/openfisca-python-api/openfisca_serve.html).

You can make sure that your instance of the API is working by requesting:

```sh
curl "http://localhost:5000/spec"
```

This endpoint returns the [Open API specification](https://www.openapis.org/)
of your API.

:tada: This OpenFisca Country Package is now served by the OpenFisca Web API!
To learn more, go to the
[OpenFisca Web API documentation](https://openfisca.org/doc/openfisca-web-api/index.html).

You can test your new Web API by sending it example JSON data located in the
`situation_examples` folder.

```sh
curl -X POST -H "Content-Type: application/json" \
  -d @./openfisca_nl/situation_examples/couple.json \
  http://localhost:5000/calculate
```
