"""Build the E2B sandbox template that ETL Doctor's tools run in.

    uv run python sandbox/build_template.py

The template is a VM image: Python + the libraries edtools needs, pinned to the same
versions as the host (uv.lock) so a tool behaves the same locally and in the sandbox.
Packages are installed here, at build time, on E2B's builders. At run time the sandbox
has no internet access, so nothing can be installed (or downloaded, or exfiltrated) then.

The edtools code itself is NOT baked in: the executor uploads it when a sandbox starts,
so the host and the sandbox always run the same version of the tools.
"""

from importlib.metadata import version

from e2b import Template

ALIAS = "etl-doctor-v2"

template = (
    Template()
    .from_python_image("3.12")
    # v1: tools only. v2 (Step 5): also what the demo pipeline and its quality tests need,
    # because validating a fix means re-running the pipeline inside the sandbox.
    # Must cover the pipeline's real runtime deps: v2 first shipped without pyarrow (used by
    # polars' to_arrow() in load.py), and every fix failed validation until it was added.
    .pip_install([f"{p}=={version(p)}" for p in ["polars", "duckdb", "pyarrow", "pyyaml", "typer", "pytest"]])
    .run_cmd("mkdir -p /workspace /opt/edtools && chown -R user:user /workspace /opt/edtools", user="root")
)

if __name__ == "__main__":
    info = Template.build(template, alias=ALIAS, cpu_count=2, memory_mb=2048, on_build_logs=lambda e: print(e))
    print(f"built template {ALIAS}: {info}")
