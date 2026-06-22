from __future__ import annotations

from typing import TYPE_CHECKING, Generator

import pytest

from ced.app import Ced

if TYPE_CHECKING:
    from syrupy import SnapshotAssertion
    from _pytest.config import Config

    from tests.debug_ui_events import DebugUIEventHandler


def pytest_addoption(parser: pytest.Parser) -> None:
    """Añadir flag --debug-ui-events para observabilidad de UI.

    Niveles: minimal, standard (default), verbose, full
    """
    parser.addoption(
        "--debug-ui-events",
        action="store",
        default=None,
        nargs="?",
        const="standard",
        choices=["minimal", "standard", "verbose", "full"],
        help="UI event observability level (RR-81)",
    )


@pytest.fixture
def app_cls() -> type[Ced]:
    return Ced


@pytest.fixture
def snapshot_text(snapshot: SnapshotAssertion):
    return snapshot


@pytest.fixture(autouse=True)
def debug_ui_events(
    request: pytest.FixtureRequest,
    worker_id: str,
) -> Generator[DebugUIEventHandler | None, None, None]:
    """Inyectar DebugUIEventHandler automáticamente si --debug-ui-events está activo.

    El fixture es autouse, pero solo crea el handler si --debug-ui-events
    fue pasado. Los tests pueden usarlo opcionalmente:

        def test_algo(debug_ui_events):
            if debug_ui_events:
                debug_ui_events.key_press("ctrl+n")
    """
    from tests.debug_ui_events import create_handler_from_config

    config: Config = request.config
    handler = create_handler_from_config(config, request.node.name, worker_id)
    if handler is None:
        yield None
        return

    handler.start()
    yield handler
    handler.stop()
    handler.write_log()
