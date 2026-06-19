from __future__ import annotations

import sys
import subprocess
from unittest.mock import patch

from ced.__main__ import main


def test_main_runs_app() -> None:
    with patch("ced.__main__.Ced") as mock_ced:
        instance = mock_ced.return_value
        main()
        mock_ced.assert_called_once()
        instance.run.assert_called_once()


def test_main_name_main_block() -> None:
    result = subprocess.run(
        [sys.executable, "-c", "import ced.__main__"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
