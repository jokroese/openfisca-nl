all: test

uninstall:
	uv pip freeze | grep -v "^-e" | sed "s/@.*//" | xargs uv pip uninstall -y

clean:
	rm -rf build dist
	find . -name '*.pyc' -exec rm \{\} \;
	find . -type d -name '__pycache__' -exec rm -r {} +

deps:
	uv pip install --upgrade build twine

install:
	@# Install OpenFisca-Extension-Template for development.
	@# `make install` installs the editable version of openfisca-nl.
	@# This allows contributors to test as they code.
	uv pip install --editable .[dev] --upgrade

build: clean deps
	@# Install OpenFisca-Extension-Template for deployment and publishing.
	@# `make build` allows us to be be sure tests are run against the packaged version
	@# of OpenFisca-Extension-Template, the same we put in the hands of users and reusers.
	uv build
	uv pip uninstall --yes openfisca-nl
	find dist -name "*.whl" -exec uv pip install --force-reinstall {}[dev] \;

format:
	@# Do not analyse .gitignored files.
	@# `make` needs `$$` to output `$`. Ref: http://stackoverflow.com/questions/2382764.
	uv run ruff format `git ls-files | grep "\.py$$"`
	uv run isort `git ls-files | grep "\.py$$"`

lint:
	@# Do not analyse .gitignored files.
	@# `make` needs `$$` to output `$`. Ref: http://stackoverflow.com/questions/2382764.
	uv run isort --check `git ls-files | grep "\.py$$"`
	uv run ruff check `git ls-files | grep "\.py$$"`
	uv run yamllint `git ls-files | grep "\.yaml$$"`

test: clean
	uv run openfisca test --country-package openfisca_nl openfisca_nl/tests

serve-local: build
	uv run openfisca serve --country-package openfisca_nl
