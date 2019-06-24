import subprocess
import sys

# inspired by https://github.com/Axelrod-Python/Axelrod/pull/878/files

modules = ["doctag/tagindex.py", "doctag/filetagindex.py"]

exit_codes = []
for module in modules:
    rc = subprocess.call(["mypy", "--ignore-missing-imports", module])
    exit_codes.append(rc)

sys.exit(max(exit_codes))
