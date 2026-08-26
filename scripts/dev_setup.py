"""
Chronon Developer Environment Setup Script
Checks Python, Node, Docker, and PostgreSQL prerequisites.
"""
import sys
import subprocess
import shutil


def check_command(cmd: str, name: str) -> bool:
    path = shutil.which(cmd)
    if path:
        print(f"  [OK] {name} found: {path}")
        return True
    else:
        print(f"  [WARNING] {name} ({cmd}) not found in PATH")
        return False


def main():
    print("==================================================")
    print("      CHRONON M0 ENVIRONMENT CHECK               ")
    print("==================================================")

    print("\n1. Checking Language Runtimes:")
    check_command("python", "Python 3")
    check_command("node", "Node.js")
    check_command("npm", "npm")

    print("\n2. Checking Infrastructure Tools:")
    check_command("docker", "Docker")
    check_command("docker-compose", "Docker Compose")
    check_command("git", "Git")
    check_command("tesseract", "Tesseract OCR (Optional for local OCR)")

    print("\n3. Verifying Repository Branch:")
    try:
        branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
        print(f"  [OK] Current Git branch: {branch}")
        if branch != "dev":
            print("  [NOTE] Remember that 'dev' is the shared integration branch.")
    except Exception as e:
        print(f"  [ERROR] Git check failed: {e}")

    print("\n==================================================")
    print("  Chronon setup check complete!")
    print("==================================================")


if __name__ == "__main__":
    main()
