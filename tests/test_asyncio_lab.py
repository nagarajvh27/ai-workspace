import asyncio

from ai_workspace.asyncio_lab import (
    run_concurrent,
    run_sequential,
)


def test_sequential_io_finishes_first_before_starting_second() -> None:
    results, events = asyncio.run(run_sequential(delay=0))

    assert results == ["first", "second"]
    assert events == [
        "first:start",
        "first:end",
        "second:start",
        "second:end",
    ]


def test_concurrent_io_starts_both_before_either_finishes() -> None:
    results, events = asyncio.run(run_concurrent(delay=0))

    assert results == ["first", "second"]
    assert set(events) == {
        "first:start",
        "first:end",
        "second:start",
        "second:end",
    }

    start_positions = [
        events.index("first:start"),
        events.index("second:start"),
    ]
    end_positions = [
        events.index("first:end"),
        events.index("second:end"),
    ]

    assert max(start_positions) < min(end_positions)
