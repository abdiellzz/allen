"""Fail when the branch changes files outside the paths allowed for the current task."""
from __future__ import annotations

import argparse
import subprocess
import sys

PROFILES = {
    "design": (
        "android/web/",
        "android/app/src/main/res/",
        ".agents/",
        "AGENTS.md",
        "android/AGENTS.md",
    ),
}


def git(*args: str) -> str:
    result = subprocess.run(("git", *args), capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        sys.exit(f"git {' '.join(args)} falló:\n{result.stderr.strip()}")
    return result.stdout


def allowed(path: str, rules: tuple[str, ...]) -> bool:
    return any(path.startswith(rule) if rule.endswith("/") else path == rule for rule in rules)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", default="design", choices=sorted(PROFILES))
    parser.add_argument("--allow", nargs="+", default=[], metavar="RUTA", help="rutas extra para esta tarea")
    parser.add_argument("--only", nargs="+", metavar="RUTA", help="sustituye el perfil por estas rutas")
    parser.add_argument("--base", default="main", help="rama base (por defecto main)")
    args = parser.parse_args()

    rules = tuple(args.only) if args.only else PROFILES[args.profile] + tuple(args.allow)
    base = git("merge-base", args.base, "HEAD").strip()

    print(f"Base: {args.base} (merge-base {base[:10]})")
    print(f"Rutas permitidas: {', '.join(rules)}\n")
    print("$ git diff --stat", args.base)
    print(git("diff", "--stat", base) or "(sin cambios)\n")

    changed = git("diff", "--name-only", base).splitlines()
    untracked = git("ls-files", "--others", "--exclude-standard").splitlines()
    print("$ git diff --name-only", args.base)
    print("\n".join(changed) or "(sin cambios)")
    if untracked:
        print("\nSin seguimiento:\n" + "\n".join(untracked))

    outside = sorted({path for path in changed + untracked if path and not allowed(path, rules)})
    if outside:
        print(f"\nFALLO: {len(outside)} archivo(s) fuera del alcance:")
        for path in outside:
            print("  -", path)
        return 1
    print(f"\nOK: {len(set(changed + untracked))} archivo(s), todos dentro del alcance.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
