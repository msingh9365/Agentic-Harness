SCENARIO ?= f1_date_format
MODE ?= crash
PARAMS ?=

.PHONY: setup data run break test clean

setup:            ## install dependencies into .venv
	uv sync

data:             ## generate clean demo source data
	uv run python -m demo_pipeline.generate

run: data         ## run the healthy pipeline + quality checks
	uv run python -m demo_pipeline.pipeline.run --data demo_pipeline/data/clean --db out/clean.duckdb
	WAREHOUSE=out/clean.duckdb DATA_DIR=demo_pipeline/data/clean uv run pytest -q -p no:cacheprovider demo_pipeline/tests

break:            ## build a broken bundle: make break SCENARIO=f4_type_drift MODE=silent PARAMS="-p style=currency_symbol"
	uv run python -m evals.inject $(SCENARIO) --mode $(MODE) $(PARAMS)

test:             ## run the repo's test suite
	uv run pytest -q

clean:
	rm -rf out demo_pipeline/data
