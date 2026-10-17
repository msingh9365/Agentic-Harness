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

ALIAS = "etl-doctor-v1"

template = (
    Template()
    .from_python_image("3.12")
    .pip_install([f"polars=={version('polars')}", f"duckdb=={version('duckdb')}"])
    .run_cmd("mkdir -p /workspace /opt/edtools && chown -R user:user /workspace /opt/edtools", user="root")
)

if __name__ == "__main__":
    info = Template.build(template, alias=ALIAS, cpu_count=2, memory_mb=2048, on_build_logs=lambda e: print(e))
    print(f"built template {ALIAS}: {info}")
