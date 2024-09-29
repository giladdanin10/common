import os
import glob

# Specify the directory containing the Python files
directory = r"C:\work\code\common\tools_support\QGIS"

# Change the current working directory to the specified directory
os.chdir(directory)

# Iterate through all Python files in the directory
for python_file in glob.glob("*.py"):
    print(f"Running {python_file}...")
    exec(open(python_file).read())
