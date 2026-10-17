SCENARIO ?= f1_date_format
MODE ?= crash
PARAMS ?=
MODEL ?=
CASE ?= out/scenarios/$(SCENARIO)__$(MODE)
NO_TOOLS ?=
model_opt = $(if $(MODEL),--model $(MODEL),) $(if $(NO_TOOLS),--no-tools,) $(if $(SANDBOX),--sandbox $(SANDBOX),)

SANDBOX ?=
.PHONY: setup data run break diagnose grade attack template smoke test clean

setup:            ## install dependencies into .venv
	uv sync

data:             ## generate clean demo source data
	uv run python -m demo_pipeline.generate

run: data         ## run the healthy pipeline + quality checks
	uv run python -m demo_pipeline.pipeline.run --data demo_pipeline/data/clean --db out/clean.duckdb
	WAREHOUSE=out/clean.duckdb DATA_DIR=demo_pipeline/data/clean uv run pytest -q -p no:cacheprovider demo_pipeline/tests

break:            ## build a broken bundle: make break SCENARIO=f4_type_drift MODE=silent PARAMS="-p style=currency_symbol"
	uv run python -m evals.inject $(SCENARIO) --mode $(MODE) $(PARAMS)

diagnose:         ## agent, tools in E2B: make diagnose SCENARIO=f1_date_format MODE=silent [MODEL=...] [NO_TOOLS=1] [SANDBOX=local]
	uv run etl-doctor diagnose $(CASE)/bundle $(model_opt)

grade:            ## diagnose + score against ground truth
	uv run python -m evals.grade $(CASE) $(model_opt)

attack:           ## prompt-injection drill on a case (planted log line), tools in E2B
	uv run python -m evals.attack $(CASE)

template:         ## (re)build the E2B sandbox template (needs E2B_API_KEY)
	uv run python sandbox/build_template.py

smoke:            ## compare candidate models on structured output + tool calling (needs NVIDIA_API_KEY)
	uv run python scripts/smoke_llm.py

test:             ## run the repo's test suite
	uv run pytest -q

clean:
	rm -rf out demo_pipeline/data
