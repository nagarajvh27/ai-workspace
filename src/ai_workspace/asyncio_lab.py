"""Standalone asyncio I/O-wait lab that is not wired into production."""

import asyncio
from time import perf_counter


async def simulated_io(
    name: str,
    delay: float,
    events: list[str],
) -> str:
    events.append(f"{name}:start")
    await asyncio.sleep(delay)
    events.append(f"{name}:end")
    return name


async def run_sequential(
    delay: float = 0.1,
) -> tuple[list[str], list[str]]:
    events: list[str] = []
    results = [
        await simulated_io("first", delay, events),
        await simulated_io("second", delay, events),
    ]
    return results, events


async def run_concurrent(
    delay: float = 0.1,
) -> tuple[list[str], list[str]]:
    events: list[str] = []
    results = await asyncio.gather(
        simulated_io("first", delay, events),
        simulated_io("second", delay, events),
    )
    return list(results), events


async def main() -> None:
    sequential_start = perf_counter()
    sequential_results, sequential_events = await run_sequential()
    sequential_elapsed = perf_counter() - sequential_start

    concurrent_start = perf_counter()
    concurrent_results, concurrent_events = await run_concurrent()
    concurrent_elapsed = perf_counter() - concurrent_start

    print(
        "Sequential simulated I/O:",
        f"{sequential_elapsed:.3f}s",
        sequential_results,
        sequential_events,
    )
    print(
        "Concurrent simulated I/O:",
        f"{concurrent_elapsed:.3f}s",
        concurrent_results,
        concurrent_events,
    )


if __name__ == "__main__":
    asyncio.run(main())
