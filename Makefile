# vim: set noet sw=4 ts=4 fileencoding=utf-8:

# External utilities
PYTHON=python
PIP=pip
PYTEST=py.test
COVERAGE=coverage
TWINE=twine
PYFLAGS=
DEST_DIR=/

NAME:=$(shell $(PYTHON) $(PYFLAGS) setup.py --name)
VER:=$(shell $(PYTHON) $(PYFLAGS) setup.py --version)
PYVER:=$(shell $(PYTHON) $(PYFLAGS) -c "import sys; print('py%d.%d' % sys.version_info[:2])")

$(DIST_TAR): $(PY_SOURCES) $(SUBDIRS)
	$(PYTHON) $(PYFLAGS) setup.py sdist

$(DIST_WHEEL): $(PY_SOURCES) $(SUBDIRS)
	$(PYTHON) $(PYFLAGS) setup.py bdist_wheel

$(DISTS): $(PY_SOURCES) $(SUBDIRS)
	$(PYTHON) $(PYFLAGS) setup.py sdist bdist_wheel

# Calculate the name of all outputs
DIST_WHEEL=dist/$(NAME)-$(VER)-py3-none-any.whl
DIST_TAR=dist/$(NAME)-$(VER).tar.gz

# Default target
all:
	@echo "make install - Install on local system"
	@echo "make develop - Install symlinks for development"
	@echo "make test - Run tests"
	@echo "make dist - Generate all packages"
	@echo "make clean - Get rid of all generated files"
	@echo "make release - Create and tag a new release"

install: $(SUBDIRS)
	$(PYTHON) $(PYFLAGS) setup.py install --root $(DEST_DIR)

source: $(DIST_TAR)

wheel: $(DIST_WHEEL)

dist: $(DIST_WHEEL)

tar: $(DIST_TAR)

dist: $(DIST_WHEEL) $(DIST_TAR)

develop: tags
	@# These have to be done separately to avoid a cockup...
	$(PIP) install -U setuptools
	$(PIP) install -U pip
	$(PIP) install -e .[test]

test:
	$(COVERAGE) run --rcfile coverage.cfg -m $(PYTEST) tests -v -r sx
	$(COVERAGE) report --rcfile coverage.cfg

clean:
	rm -rf dist/ $(NAME).egg-info/ tags
	for dir in $(SUBDIRS); do \
		$(MAKE) -C $$dir clean; \
	done

release: $(DIST_TAR) $(DIST_WHEEL)
	git tag -s v$(VER) -m "Release v$(VER)"
	git push --tags
	# build sdist and bdist and upload to PyPI
	$(TWINE) upload $(DIST_TAR) $(DIST_WHEEL)

.PHONY: all install develop test source wheel tar dist clean tags release $(SUBDIRS)
