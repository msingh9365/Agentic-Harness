SCENARIO ?= f1_date_format
MODE ?= crash
PARAMS ?=
MODEL ?=
CASE ?= out/scenarios/$(SCENARIO)__$(MODE)
NO_TOOLS ?=
model_opt = $(if $(MODEL),--model $(MODEL),) $(if $(NO_TOOLS),--no-tools,)

.PHONY: setup data run break diagnose grade smoke test clean

setup:            ## install dependencies into .venv
	uv sync

data:             ## generate clean demo source data
	uv run python -m demo_pipeline.generate

run: data         ## run the healthy pipeline + quality checks
	uv run python -m demo_pipeline.pipeline.run --data demo_pipeline/data/clean --db out/clean.duckdb
	WAREHOUSE=out/clean.duckdb DATA_DIR=demo_pipeline/data/clean uv run pytest -q -p no:cacheprovider demo_pipeline/tests

break:            ## build a broken bundle: make break SCENARIO=f4_type_drift MODE=silent PARAMS="-p style=currency_symbol"
	uv run python -m evals.inject $(SCENARIO) --mode $(MODE) $(PARAMS)

diagnose:         ## agent with tools on a bundle: make diagnose SCENARIO=f1_date_format MODE=silent [MODEL=...] [NO_TOOLS=1]
	uv run etl-doctor diagnose $(CASE)/bundle $(model_opt)

grade:            ## diagnose + score against ground truth
	uv run python -m evals.grade $(CASE) $(model_opt)

smoke:            ## compare candidate models on structured output + tool calling (needs NVIDIA_API_KEY)
	uv run python scripts/smoke_llm.py

test:             ## run the repo's test suite
	uv run pytest -q

clean:
	rm -rf out demo_pipeline/data
