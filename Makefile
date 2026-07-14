.PHONY: install run debug clean lint lint-strict

PYTHON = python3
MAIN = a_maze_ing.py

install:
	$(PYTHON) -m pip install .

run:
	$(PYTHON) $(MAIN) config.txt

debug:
	$(PYTHON) -m pdb $(MAIN) config.txt

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf build
	rm -rf *.egg-info
	rm -rf dist

# used if u want to remove venv
fclean: clean
	rm -rf .venv
	rm -rf venv

lint:
	flake8 . --exclude=.venv
	mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	flake8 . --exclude=.venv
	mypy . --strict