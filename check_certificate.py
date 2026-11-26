"""Check the CSV independently, using exact fractions and all legal tie choices."""
import csv
from fractions import Fraction
from itertools import combinations
from pathlib import Path

path = Path(__file__).resolve().parent / "certificates" / "orbits.csv"
with path.open(newline="", encoding="ascii") as source:
    rows = list(csv.reader(source))[1:]

depth = {}
for row in rows:
    a, b, c, d, one, batch = map(int, row)
    state = tuple(Fraction(n, 12) for n in (a, b, c, d))
    if sum(state) or tuple(sorted(state)) != state or state in depth:
        raise ValueError("Invalid or duplicate state")
    depth[state] = (one, batch)

origin = (0, 0, 0, 0)
if len(depth) != 195 or depth.get(origin) != (0, 0):
    raise ValueError("Invalid state table")
for mode in (0, 1):
    successors = {origin}
    for state, distances in depth.items():
        for k in (2, 3, 4):
            for people in combinations(range(4), k):
                for r in (range(1, k) if mode else (1,)):
                    for payers in combinations(people, r):
                        others = set(people).difference(payers)
                        if max(state[i] for i in payers) > min(state[i] for i in others):
                            continue
                        target = list(state)
                        for i in people:
                            target[i] += int(i in payers) - Fraction(r, k)
                        target = tuple(sorted(target))
                        if target not in depth or depth[target][mode] > distances[mode] + 1:
                            raise ValueError("Missing successor or invalid distance")
                        if depth[target][mode] == distances[mode] + 1:
                            successors.add(target)
    if successors != set(depth) or any(d[mode] <= 0 for s, d in depth.items() if s != origin):
        raise ValueError("Not all distances have a descending predecessor chain")
if max(abs(x) for s in depth for x in s) != Fraction(7, 6):
    raise ValueError("Wrong extremum")
print("Independent rational-arithmetic check passed for both 195-state orbits.")
