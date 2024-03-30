import os, shutil, subprocess

project_directory = "securityscripts"
new_requirements_file = os.path.join(project_directory, "requirements.txt")
try:
    import pipreqs
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
    print(f"Error: {e}")
