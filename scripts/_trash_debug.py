#!/usr/bin/env python3
"""Debug script — run from your terminal to verify deletion works."""
import subprocess, os, datetime

TRASH_DIR = os.path.expanduser("~/.Trash")

r_names = subprocess.run(["osascript", "-e", "tell application \"Finder\" to get name of items of trash"], capture_output=True, text=True)
names = [n.strip() for n in r_names.stdout.strip().split(",") if n.strip()]

date_script = """
tell application "Finder"
    set dateList to modification date of items of trash
    set strList to {}
    repeat with d in dateList
        set end of strList to (short date string of d & " " & time string of d)
    end repeat
    return strList
end tell
"""
r_dates = subprocess.run(["osascript", "-e", date_script], capture_output=True, text=True)
date_strs = [d.strip() for d in r_dates.stdout.strip().split(", ") if d.strip()]

now = datetime.datetime.now()
def parse_date(d_str):
    for fmt in ["%d/%m/%Y %H:%M:%S", "%m/%d/%Y %H:%M:%S"]:
        try:
            return datetime.datetime.strptime(d_str, fmt)
        except ValueError:
            pass
    return None

expired = []
for i in range(min(len(names), len(date_strs))):
    dt = parse_date(date_strs[i])
    if dt and (now - dt).total_seconds() / 86400.0 >= 30:
        expired.append(names[i])

print(f"Testing new deletion approach on first 5 expired items:")
print()

for name in expired[:5]:
    path = os.path.join(TRASH_DIR, name)
    print(f"Item    : {name}")
    print(f"Path    : {path}")
    print(f"Exists  : {os.path.exists(path)}")

    subprocess.run(["/usr/bin/chflags", "-R", "nouchg", path], capture_output=True)
    if os.path.isdir(path):
        subprocess.run(["/bin/chmod", "-R", "u+rwX", path], capture_output=True)

    res = subprocess.run(["/bin/rm", "-rf", path], capture_output=True, text=True)
    print(f"/bin/rm returncode: {res.returncode}, stderr: {repr(res.stderr)}")
    print(f"Still exists: {os.path.exists(path)}")
    print()
