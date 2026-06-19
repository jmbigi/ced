from __future__ import annotations

import threading
from pathlib import Path

from hypothesis import assume, given, settings, strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule

from ced.editor.buffer import Buffer, BufferManager


# ── Load testing ────────────────────────────────────────────────────────

def test_large_file_load(tmp_path: Path) -> None:
    """Load a 1MB+ file into EnhancedCodeEditor."""
    large = tmp_path / "large.py"
    large.write_text("x\n" * 200_000)
    from ced.editor.widget import EnhancedCodeEditor
    editor = EnhancedCodeEditor()
    editor.load_file(large)
    assert len(editor.text) > 100_000


def test_many_edits_stress() -> None:
    """10,000 sequential edits — verify stability."""
    from ced.editor.widget import EnhancedCodeEditor
    editor = EnhancedCodeEditor()
    for i in range(10_000):
        editor.text += "a"
    assert len(editor.text) == 10_000


def test_buffer_large_open_close() -> None:
    """Open and close 1000 buffers — verify no crash."""
    bm = BufferManager()
    for i in range(1000):
        bm.add(Path(f"/tmp/{i}.py"))
    assert bm.count == 1000
    for i in range(1000):
        bm.close_active()
    assert bm.count == 0


def test_buffer_rapid_switch() -> None:
    """1000 rapid switch_next/prev operations."""
    bm = BufferManager()
    for i in range(10):
        bm.add(Path(f"/tmp/{i}.py"))
    bm.active_index = 0
    for _ in range(1000):
        bm.switch_next()
        bm.switch_prev()
    assert 0 <= bm.active_index < bm.count


# ── Concurrency testing ─────────────────────────────────────────────────

def test_buffer_manager_concurrent_add() -> None:
    """Multi-threaded add operations — verify consistency."""
    bm = BufferManager()
    errors: list[Exception] = []

    def worker() -> None:
        try:
            for _ in range(100):
                bm.add()
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Errors in threads: {errors}"
    assert bm.count == 400, f"Expected 400 buffers, got {bm.count}"


def test_buffer_manager_concurrent_mixed() -> None:
    """Multi-threaded add + remove — verify index consistency."""
    bm = BufferManager()
    for _ in range(10):
        bm.add()
    errors: list[Exception] = []
    lock = threading.Lock()

    def adder() -> None:
        for _ in range(50):
            with lock:
                try:
                    bm.add()
                    if bm.count > 1:
                        bm.remove(0)
                    bm.switch_next()
                except Exception as e:
                    errors.append(e)

    threads = [threading.Thread(target=adder) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Errors in threads: {errors}"
    assert bm.active_index == -1 or 0 <= bm.active_index < bm.count


# ── Fuzz testing (Hypothesis stateful amplified) ────────────────────────

class BufferManagerFuzz(RuleBasedStateMachine):
    def __init__(self) -> None:
        super().__init__()
        self.bm = BufferManager()
        self.model_count = 0

    @rule()
    def add(self) -> None:
        self.bm.add()
        self.model_count += 1

    @rule()
    def remove_first(self) -> None:
        assume(self.bm.count > 0)
        self.bm.remove(0)
        self.model_count = max(0, self.model_count - 1)

    @rule()
    def remove_last(self) -> None:
        assume(self.bm.count > 0)
        idx = self.bm.count - 1
        self.bm.remove(idx)
        self.model_count = max(0, self.model_count - 1)

    @rule()
    def remove_middle(self) -> None:
        assume(self.bm.count >= 3)
        idx = self.bm.count // 2
        old_active = self.bm.active_index
        self.bm.remove(idx)
        self.model_count = max(0, self.model_count - 1)
        assert self.bm.active_index == -1 or 0 <= self.bm.active_index < self.bm.count

    @rule()
    def switch_next(self) -> None:
        assume(self.bm.count > 0)
        old = self.bm.active_index
        self.bm.switch_next()
        expected = (old + 1) % self.bm.count
        assert self.bm.active_index == expected

    @rule()
    def switch_prev(self) -> None:
        assume(self.bm.count > 0)
        old = self.bm.active_index
        self.bm.switch_prev()
        expected = (old - 1) % self.bm.count
        assert self.bm.active_index == expected

    @rule()
    def count_match(self) -> None:
        assert self.bm.count == self.model_count

    @rule()
    def active_in_range(self) -> None:
        if self.bm.count > 0:
            assert 0 <= self.bm.active_index < self.bm.count
        else:
            assert self.bm.active_buffer is None


TestBufferFuzz = BufferManagerFuzz.TestCase


# ── Config fuzz ─────────────────────────────────────────────────────────

@given(st.integers(min_value=-100, max_value=100))
def test_config_tab_size_fuzz(tab_size: int) -> None:
    """Fuzz EditorConfig with any integer tab_size."""
    from ced.config import EditorConfig
    cfg = EditorConfig(tab_size=tab_size)
    assert cfg.tab_size >= 1  # clamp


@given(st.text())
def test_config_opencode_path_fuzz(path: str) -> None:
    """Fuzz OpenCodeConfig with any string path."""
    from ced.config import OpenCodeConfig
    cfg = OpenCodeConfig(path=path)
    assert isinstance(cfg.path, str)
    assert cfg.path  # never empty after __post_init__


@given(st.sampled_from(["auto", "dark", "light", "invalid"]))
def test_theme_config_mode_fuzz(mode: str) -> None:
    """Fuzz ThemeConfig with valid and invalid modes."""
    from ced.config import ThemeConfig
    try:
        cfg = ThemeConfig(mode=mode)
        assert cfg.mode == mode
    except ValueError:
        pass  # invalid mode raises ValueError


@given(st.dictionaries(st.text(), st.text()))
def test_config_merge_fuzz(data: dict[str, str]) -> None:
    """Fuzz Config._merge with arbitrary dicts — should never crash."""
    from ced.config import Config
    cfg = Config()
    cfg._merge(data)  # should not raise


@given(st.integers(min_value=-5, max_value=5))
def test_buffer_active_index_edge(idx: int) -> None:
    """Set active_index to edge values."""
    bm = BufferManager()
    for i in range(3):
        bm.add(Path(f"/tmp/{i}.py"))
    old = bm.active_index
    bm.active_index = idx
    if 0 <= idx < bm.count:
        assert bm.active_index == idx
    else:
        assert bm.active_index == old
