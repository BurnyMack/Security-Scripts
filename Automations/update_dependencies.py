#!/usr/bin/env python3
"""
Regenerate the repo-wide requirements.txt from actual imports via pipreqs.

Usage:
    python Automations/update_dependencies.py

Run from the repo root — scans the current directory (".") recursively.

Requirements:
    pipreqs (installed automatically if missing)
"""

import os
import shutil
import subprocess
import sys

project_directory = "."
new_requirements_file = os.path.join(project_directory, "requirements.txt")

try:
    import pipreqs  # noqa: F401
except ImportError:
    print("pipreqs is not installed. Installing it...")
    subprocess.run(["pip", "install", "pipreqs"], check=True)
    print("pipreqs has been installed.")

try:
    subprocess.run(["pipreqs", "--force", project_directory], check=True)
    print("Created new requirements.txt file with the latest dependencies.")
    generated_requirements_file = os.path.join(project_directory, "requirements.txt")
    shutil.move(generated_requirements_file, new_requirements_file)
    print("Renamed the generated requirements.txt file.")
except subprocess.CalledProcessError as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
