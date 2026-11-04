SCENARIO ?= f1_date_format
MODE ?= crash
PARAMS ?=
MODEL ?=
CASE ?= out/scenarios/$(SCENARIO)__$(MODE)
NO_TOOLS ?=
model_opt = $(if $(MODEL),--model $(MODEL),) $(if $(NO_TOOLS),--no-tools,) $(if $(SANDBOX),--sandbox $(SANDBOX),)

SANDBOX ?=
RUN ?=
CRASH ?=
.PHONY: site site-preview ui docker-build docker-run setup data run break diagnose doctor resume history grade attack template smoke test clean suite-build suite judge-calibrate judge scorecard

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

doctor:           ## Step 4 graph, checkpointed: make doctor SCENARIO=f1_date_format MODE=silent [CRASH=hypothesize] [SANDBOX=local]
	uv run etl-doctor run $(CASE)/bundle $(if $(SANDBOX),--sandbox $(SANDBOX),) $(if $(CRASH),--crash-before $(CRASH),)

resume:           ## continue a run from its last checkpoint: make resume RUN=run-...
	uv run etl-doctor resume $(RUN)

history:          ## list a run's checkpoints: make history RUN=run-...
	uv run etl-doctor history $(RUN)

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

K ?= 3
CONCURRENCY ?= 4
suite-build:      ## Step 6: inject every scenario x mode x variant (18 cases) and check each is broken
	uv run python -m evals.suite build

suite:            ## Step 6: run the graph on every case K times (resumable): make suite K=3 [AGENT=no_tools]
	uv run python -m evals.suite run --k $(K) --concurrency $(CONCURRENCY) $(if $(AGENT),--agent $(AGENT),)

judge-calibrate:  ## Step 6: measure the LLM judge on labelled answers before trusting it
	uv run python -m evals.judge calibrate

judge:            ## Step 6: LLM-as-judge on every diagnosis in the suite results
	uv run python -m evals.judge run

scorecard:        ## Step 6: write out/suite/scorecard.md from the results
	uv run python -m evals.scorecard

clean:
	rm -rf out demo_pipeline/data .etl_doctor

ui:               ## web UI on http://127.0.0.1:8000 (ETLDOC_UI_USERS=name:pw to require a login)
	uv run etl-doctor serve

docker-build:     ## the hosting image
	docker build -t etl-doctor .

docker-run:       ## the image locally: needs NVIDIA_API_KEY, E2B_API_KEY and ETLDOC_UI_USERS in the environment
	docker run --rm -p 8000:8000 -v etl-doctor-data:/data -e NVIDIA_API_KEY -e E2B_API_KEY -e ETLDOC_UI_USERS etl-doctor

site:             ## the static replay site in _site/ (what GitHub Pages publishes)
	rm -rf _site && mkdir -p _site && cp -r site/. _site/ && cp src/etl_doctor/web/static/app.js src/etl_doctor/web/static/style.css _site/

site-preview: site ## serve _site/ on http://127.0.0.1:8001
	python3 -m http.server 8001 --bind 127.0.0.1 --directory _site
