import subprocess
import sys
from pathlib import Path


SCRIPTS = [
    "formal_bound_builder.py",
    "prompt_builder.py",
    "synthetic_response_generator.py",
    "reason_guard_checker.py",
]


def run_script(script_name: str) -> None:
    script_path = Path(script_name)

    if not script_path.exists():
        raise FileNotFoundError(f"Required script not found: {script_path.resolve()}")

    print("=" * 80)
    print(f"Running {script_name}")
    print("=" * 80)

    completed = subprocess.run(
        [sys.executable, script_name],
        check=False,
        text=True,
    )

    if completed.returncode != 0:
        raise RuntimeError(f"{script_name} failed with exit code {completed.returncode}")


def main() -> None:
    for script in SCRIPTS:
        run_script(script)

    print("=" * 80)
    print("Pipeline completed successfully.")
    print("Check the outputs/ folder.")
    print("=" * 80)


if __name__ == "__main__":
    main()