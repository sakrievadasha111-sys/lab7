from random import Random
from time import perf_counter

rng = Random(42)

def make_rows(n):
    return [
        {"id": f"SK-{i:06d}", "debit": rng.random() * 100}
        for i in range(n)
    ]

def find_by_scan(rows, target):
    for row in rows:
        if row["id"] == target:
            return row
    return None

def time_queries(lookup, queries, passes=1):
    results = []

    for _ in range(3):
        start = perf_counter()

        for _ in range(passes):
            for target in queries:
                lookup(target)

        elapsed = (perf_counter() - start) / passes
        results.append(elapsed * 1000)

    return sum(results) / len(results)

print("N; Перебор; Индекс; Ускорение; Построение")

for n in (100, 1000, 10000, 100000):
    rows = make_rows(n)

    build_times = []

    for _ in range(3):
        start = perf_counter()
        index = {row["id"]: row for row in rows}
        build_times.append((perf_counter() - start) * 1000)

    build_ms = sum(build_times) / len(build_times)

    queries = [
        rows[rng.randrange(n)]["id"]
        for _ in range(1000)
    ]

    scan_ms = time_queries(
        lambda target: find_by_scan(rows, target),
        queries
    )

    index_ms = time_queries(
        lambda target: index[target],
        queries,
        passes=50
    )

    print(
        f"{n}; {scan_ms:.3f}; {index_ms:.3f}; "
        f"{scan_ms / index_ms:.1f}; {build_ms:.3f}"
    )

    