.DEFAULT_GOAL := help

UV ?= uv

.PHONY: help install lint format typecheck test train clean

help: ## Show the available targets
	@echo SafeSite Vision - available targets:
	@echo   install    Install all dependency groups (uv sync --all-groups)
	@echo   lint       ruff check + ruff format --check
	@echo   format     ruff check --fix + ruff format
	@echo   typecheck  mypy on src
	@echo   test       pytest with coverage
	@echo   train      run the baseline training script
	@echo   clean      remove caches and build artefacts

install: ## Install all dependency groups
	$(UV) sync --all-groups

lint: ## Check formatting and lint rules
	$(UV) run ruff check .
	$(UV) run ruff format --check .

format: ## Apply formatting and safe lint fixes
	$(UV) run ruff check --fix .
	$(UV) run ruff format .

typecheck: ## Run mypy
	$(UV) run mypy src

test: ## Run the test suite with coverage
	$(UV) run pytest --cov=safesite --cov-report=term-missing --cov-report=xml

train: ## Train the baseline model
	$(UV) run python scripts/train.py --config configs/train_baseline.yaml

clean: ## Remove caches and build artefacts
	$(UV) run python -c "import shutil, pathlib; targets=['.pytest_cache','.mypy_cache','.ruff_cache','.coverage','htmlcov','dist','build','.hypothesis']; [shutil.rmtree(t, ignore_errors=True) for t in targets]; [p.unlink() for p in pathlib.Path('.').glob('coverage.xml')]"
