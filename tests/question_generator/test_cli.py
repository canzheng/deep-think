import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path


from tools.question_generator.cli import main


FIXTURE_PATH = (
    Path(__file__).resolve().parent / "fixtures" / "minimal_state.json"
)


class CliTest(unittest.TestCase):
    def test_cli_prints_assembled_prompt(self) -> None:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(
                [
                    "--stage",
                    "decision_logic",
                    "--state",
                    str(FIXTURE_PATH),
                    "--include-optional",
                    "structure",
                    "--include-optional",
                    "question_generation",
                ]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("## Stage 7 - Decision Logic", output)
        self.assertIn("## Current State", output)
        self.assertIn("## Active Steering", output)
        self.assertIn("## Required Output", output)


if __name__ == "__main__":
    unittest.main()
