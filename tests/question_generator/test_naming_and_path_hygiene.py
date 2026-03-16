import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ACTIVE_USER_FACING_FILES = [
    REPO_ROOT / "README.md",
    REPO_ROOT / "environment.yml",
    REPO_ROOT / "prompt" / "question-generator" / "README.md",
    REPO_ROOT / "skills" / "deep-think" / "SKILL.md",
    REPO_ROOT / "skills" / "deep-think" / "references" / "commands.md",
    REPO_ROOT / "skills" / "deep-think" / "openclaw" / "SKILL.md",
]
DISALLOWED_MACHINE_LOCAL_PATTERNS = (
    "/" + "Users/",
    "/" + "home/",
)


class NamingAndPathHygieneTest(unittest.TestCase):
    def _read_active_file(self, path: Path) -> str:
        self.assertTrue(path.is_file(), f"Expected active file to exist: {path}")
        return path.read_text(encoding="utf-8")

    def test_active_user_facing_files_exist_under_deep_think_skill_surface(self) -> None:
        for path in ACTIVE_USER_FACING_FILES:
            with self.subTest(path=path):
                self.assertTrue(path.is_file(), f"Expected active file to exist: {path}")

    def test_active_user_facing_files_do_not_leak_machine_local_absolute_paths(self) -> None:
        for path in ACTIVE_USER_FACING_FILES:
            content = self._read_active_file(path)
            for disallowed in DISALLOWED_MACHINE_LOCAL_PATTERNS:
                with self.subTest(path=path, disallowed=disallowed):
                    self.assertNotIn(disallowed, content)

    def test_active_user_facing_files_use_deep_think_external_name(self) -> None:
        for path in ACTIVE_USER_FACING_FILES:
            content = self._read_active_file(path)
            with self.subTest(path=path):
                self.assertNotIn("truth-seek", content)


if __name__ == "__main__":
    unittest.main()
