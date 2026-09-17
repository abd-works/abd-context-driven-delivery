"""Fix import paths after harness->installer rename."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {"legacy-no-longer-valid", ".git", "__pycache__", ".agent_bdd_sessions"}


def skip(path: Path) -> bool:
    return any(p in SKIP for p in path.parts)


def fix(text: str) -> str:
    text = text.replace("from installer.", "from installer.")
    text = text.replace("primitives.installer.installation", "primitives.installer.installation")
    text = text.replace("from .installation import", "from .installation import")
    text = text.replace("from .installer import", "from .installer import")
    text = text.replace("import Installer", "import Installer")
    text = text.replace(", Installer", ", Installer")
    text = text.replace('["Installation", "Installer"]', '["Installation", "Installer"]')
    text = text.replace('__all__ = ["Installation", "Installer"]', '__all__ = ["Installation", "Installer"]')
    text = text.replace("installer.installer import Installer", "installer.installer import Installer")
    text = text.replace(".installation.install(", ".installation.install(")
    text = text.replace("def install(self, host", "def install(self, host")
    return text


def main() -> None:
    n = 0
    for path in ROOT.rglob("*.py"):
        if skip(path):
            continue
        try:
            original = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        updated = fix(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            n += 1
    print(f"fixed {n} py files")


if __name__ == "__main__":
    main()
