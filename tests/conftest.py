from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ced.app import Ced

if TYPE_CHECKING:
    from syrupy import SnapshotAssertion


@pytest.fixture
def app_cls() -> type[Ced]:
    return Ced


@pytest.fixture
def snapshot_svg(snapshot: SnapshotAssertion):
    return snapshot


@pytest.fixture
def snapshot_text(snapshot: SnapshotAssertion):
    return snapshot
