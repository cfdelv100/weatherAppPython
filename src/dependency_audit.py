from __future__ import annotations

import ast
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOTS = [PROJECT_ROOT / "src", PROJECT_ROOT / "weather.py"]
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"

OPTIONAL_IMPORTS = {
    "PIL": "pillow",
    "cartopy": "cartopy",
    "matplotlib": "matplotlib",
    "requests": "requests",
}


def parse_requirements(path: Path) -> set[str]:
    requirements: set[str] = set()
    text = None
    for encoding in ("utf-8-sig", "utf-8", "utf-16"):
        try:
            text = path.read_text(encoding=encoding)
            break
        except UnicodeDecodeError:
            continue

    if text is None:
        text = path.read_text(encoding=sys.getdefaultencoding(), errors="replace")

    for raw_line in text.splitlines():
        line = raw_line.strip().lstrip("\ufeff")
        if not line or line.startswith("#"):
            continue
        for separator in ("==", ">=", "<=", "~=", ">", "<", "!="):
            if separator in line:
                line = line.split(separator, 1)[0]
                break
        requirements.add(line.replace("_", "-").lower())
    return requirements


def iter_python_files() -> list[Path]:
    files: list[Path] = []
    for item in SOURCE_ROOTS:
        if item.is_file() and item.suffix == ".py":
            files.append(item)
        elif item.is_dir():
            files.extend(item.rglob("*.py"))
    return files


def collect_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".", 1)[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level > 0 or node.module is None:
                continue
            imports.add(node.module.split(".", 1)[0])

    return imports


def is_stdlib(module_name: str) -> bool:
    if module_name in sys.builtin_module_names:
        return True
    stdlib_names = getattr(sys, "stdlib_module_names", set())
    return module_name in stdlib_names


def normalize_import_name(module_name: str) -> str:
    mapped = OPTIONAL_IMPORTS.get(module_name, module_name)
    return mapped.replace("_", "-").lower()


def analyze_dependencies() -> tuple[set[str], set[str], set[str]]:
    requirements = parse_requirements(REQUIREMENTS_FILE)
    imported_third_party: set[str] = set()

    for source_file in iter_python_files():
        for module_name in collect_imports(source_file):
            if module_name.startswith("_") or is_stdlib(module_name):
                continue
            if module_name == "src":
                continue
            imported_third_party.add(normalize_import_name(module_name))

    missing = imported_third_party - requirements
    unused = requirements - imported_third_party
    return imported_third_party, missing, unused


def print_dependency_report() -> int:
    if not REQUIREMENTS_FILE.exists():
        print(f"Missing requirements file: {REQUIREMENTS_FILE}")
        return 1

    imported_third_party, missing, unused = analyze_dependencies()
    requirements = parse_requirements(REQUIREMENTS_FILE)

    print("Dependency audit")
    print("=================")
    print(f"Imported third-party packages: {len(imported_third_party)}")
    print(f"Packages listed in requirements: {len(requirements)}")

    if missing:
        print("\nMissing from requirements:")
        for package in sorted(missing):
            print(f"- {package}")
    else:
        print("\nMissing from requirements: none")

    if unused:
        print("\nListed but not imported:")
        for package in sorted(unused):
            print(f"- {package}")
    else:
        print("\nListed but not imported: none")

    return 0 if not missing else 2
