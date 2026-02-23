import subprocess
import os

env = os.environ.copy()
env["PYTHONPATH"] = r"c:\Users\Yass0\OneDrive\Desktop\TASK14"

result = subprocess.run(
    ["python", "-m", "uniguru.core.engine"],
    env=env,
    capture_output=True,
    text=True
)

with open("engine_log.txt", "w") as f:
    f.write("STDOUT:\n")
    f.write(result.stdout)
    f.write("\nSTDERR:\n")
    f.write(result.stderr)
print("Done writing engine_log.txt")
