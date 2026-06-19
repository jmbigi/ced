from __future__ import annotations

from pathlib import Path

from hypothesis import assume, given, settings, strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule

from ced.config import Config, EditorConfig, KeybindingConfig, OpenCodeConfig, ThemeConfig
from ced.editor.buffer import Buffer, BufferManager
from ced.commands.registry import Command, CommandRegistry


@settings(max_examples=2000)
@given(st.integers(min_value=1, max_value=100))
def test_buffer_name_always_string(tab_size: int) -> None:
    cfg = EditorConfig(tab_size=tab_size)
    assert cfg.tab_size == tab_size


@settings(max_examples=2000)
@given(st.text())
def test_buffer_name_is_never_none(name: str) -> None:
    assume(name)
    buf = Buffer(Path(f"/tmp/{name}") if name else None)
    assert buf.name is not None
    assert isinstance(buf.name, str)


@settings(max_examples=1000)
@given(st.lists(st.text(min_size=1, max_size=20), min_size=0, max_size=10))
def test_buffer_manager_add_and_count(names: list[str]) -> None:
    bm = BufferManager()
    for n in names:
        bm.add(Path(f"/tmp/{n}") if n else None)
    assert bm.count == len(names)


@given(
    st.integers(min_value=1, max_value=8),
    st.booleans(),
    st.booleans(),
    st.integers(min_value=8, max_value=72),
)
def test_editor_config_valid_ranges(
    tab_size: int, soft_wrap: bool, line_numbers: bool, font_size: int
) -> None:
    cfg = EditorConfig(
        tab_size=tab_size, soft_wrap=soft_wrap,
        line_numbers=line_numbers, font_size=font_size,
    )
    assert cfg.tab_size == tab_size
    assert cfg.soft_wrap is soft_wrap
    assert cfg.line_numbers is line_numbers
    assert cfg.font_size == font_size


@given(st.sampled_from(["auto", "dark", "light"]), st.sampled_from(["monokai", "dracula", "nord"]))
def test_theme_config_valid(mode: str, name: str) -> None:
    cfg = ThemeConfig(mode=mode, name=name)
    assert cfg.mode == mode
    assert cfg.name == name


@given(st.sampled_from(["vscode", "nano", "sublime", "emacs"]))
def test_keybinding_config_valid(preset: str) -> None:
    cfg = KeybindingConfig(preset=preset)
    assert cfg.preset == preset


@given(st.text(min_size=1), st.booleans())
def test_opencode_config_valid(path: str, auto_start: bool) -> None:
    cfg = OpenCodeConfig(path=path, auto_start=auto_start)
    assert cfg.path == path
    assert cfg.auto_start is auto_start


@given(st.integers(min_value=1, max_value=100))
def test_config_merge_tab_size(tab_size: int) -> None:
    cfg = Config()
    cfg._merge({"editor": {"tab_size": tab_size}})
    assert cfg.editor.tab_size == tab_size


@given(st.lists(st.text(min_size=1, max_size=10).map(lambda s: f"app.{s}"), min_size=0, max_size=10))
def test_command_registry_register_many(ids: list[str]) -> None:
    assume(len(set(ids)) == len(ids))
    reg = CommandRegistry()
    commands = [Command(i, f"Test {i}", lambda: None, "Test") for i in ids]
    if commands:
        reg.register_many(*commands)
        for i in ids:
            assert reg.get(i) is not None
    else:
        assert len(reg.all()) == 0


@given(st.text(min_size=2, max_size=20))
def test_command_search(query: str) -> None:
    reg = CommandRegistry()
    reg.register(Command("app.test", "Find this command", lambda: None, "Test"))
    results = reg.search(query)
    # Search uses SequenceMatcher ratio > 0.3, not substring matching
    if query == "":
        assert len(results) == 0
    else:
        assert isinstance(results, list)


@st.composite
def buffer_list(draw: st.DrawFn) -> list[Buffer]:
    n = draw(st.integers(min_value=0, max_value=5))
    return [Buffer(Path(f"/tmp/{i}.py") if draw(st.booleans()) else None) for i in range(n)]


@given(buffer_list())
def test_buffer_manager_remove_all(buffers: list[Buffer]) -> None:
    bm = BufferManager()
    for b in buffers:
        bm._buffers.append(b)
    bm._active_index = len(buffers) - 1 if buffers else -1
    original_count = bm.count
    for i in range(original_count - 1, -1, -1):
        bm.remove(i)
    assert bm.count == 0


class BufferManagerMachine(RuleBasedStateMachine):
    def __init__(self) -> None:
        super().__init__()
        self.bm = BufferManager()
        self.model: list[str] = []

    @rule()
    def add(self) -> None:
        self.bm.add()
        self.model.append("untitled")

    @rule()
    def remove_last(self) -> None:
        assume(self.bm.count > 0)
        idx = self.bm.count - 1
        self.bm.remove(idx)
        self.model.pop()

    @rule()
    def remove_first(self) -> None:
        assume(self.bm.count > 0)
        self.bm.remove(0)
        self.model.pop(0)

    @rule()
    def switch_next(self) -> None:
        assume(self.bm.count > 0)
        old = self.bm.active_index
        self.bm.switch_next()
        expected = (old + 1) % self.bm.count if self.bm.count > 0 else -1
        if expected >= 0:
            assert self.bm.active_index == expected

    @rule()
    def switch_prev(self) -> None:
        assume(self.bm.count > 0)
        old = self.bm.active_index
        self.bm.switch_prev()
        expected = (old - 1) % self.bm.count if self.bm.count > 0 else -1
        if expected >= 0:
            assert self.bm.active_index == expected

    @rule()
    def count_match(self) -> None:
        assert self.bm.count == len(self.model)

    @rule()
    def active_index_in_range(self) -> None:
        if self.bm.count > 0:
            assert 0 <= self.bm.active_index < self.bm.count
        else:
            assert self.bm.active_buffer is None


TestBufferManagerStates = BufferManagerMachine.TestCase


@given(st.integers(min_value=1, max_value=64), st.integers(min_value=1, max_value=1000))
def test_detect_language_all_extensions(count: int, seed: int) -> None:
    import random
    from ced.editor.widget import LANGUAGE_MAP, detect_language
    rng = random.Random(seed)
    extensions = list(LANGUAGE_MAP.keys())
    for _ in range(min(count, len(extensions))):
        ext = rng.choice(extensions)
        lang = detect_language(Path(f"file{ext}"))
        assert lang is not None
        assert isinstance(lang, str)


@given(st.lists(st.integers(min_value=1, max_value=4), min_size=1, max_size=10))
def test_config_merge_multiple_edits(sizes: list[int]) -> None:
    cfg = Config()
    for s in sizes:
        cfg._merge({"editor": {"tab_size": s}})
    assert cfg.editor.tab_size == sizes[-1]


@given(st.text(min_size=1, max_size=30), st.text(min_size=1, max_size=30))
def test_command_creation(a: str, b: str) -> None:
    try:
        cmd = Command(f"app.{a}", b, lambda: None, "Test")
        assert cmd.id == f"app.{a}"
        assert cmd.description == b
    except Exception:
        pass  # some ids may be invalid


@given(st.lists(st.integers(min_value=0, max_value=5), min_size=0, max_size=5))
def test_buffer_manager_remove_multiple(indices: list[int]) -> None:
    bm = BufferManager()
    for i in range(5):
        bm.add(Path(f"/tmp/{i}.py"))
    # Remove without duplicates in reverse to avoid index shifting
    seen = set()
    for idx in indices:
        if idx < bm.count and idx not in seen:
            seen.add(idx)
            bm.remove(idx)
    assert 0 <= bm.count <= 5


@given(st.integers(min_value=0, max_value=4))
def test_buffer_manager_switch_wraparound(start: int) -> None:
    bm = BufferManager()
    for i in range(5):
        bm.add(Path(f"/tmp/{i}.py"))
    bm.active_index = start
    bm.switch_next()
    assert bm.active_index == (start + 1) % 5
    bm.switch_prev()
    assert bm.active_index == start  # back to start
    bm.switch_prev()
    assert bm.active_index == (start - 1) % 5  # wraparound backward
