"""Verify the four-person greedy orbits and finite-horizon minimax values."""
import argparse
import csv
from collections import deque
from functools import lru_cache
from itertools import combinations
from pathlib import Path

ZERO = (0, 0, 0, 0)
UNIT = 12
CERT = Path(__file__).resolve().parent / "certificates" / "orbits.csv"


def requests(single):
    for k in (2, 3, 4):
        for group in combinations(range(4), k):
            for r in range(1, 2 if single else k):
                yield group, r


def step(state, group, r, charged):
    values = list(state)
    for i in group:
        values[i] -= UNIT * r // len(group)
    for i in charged:
        values[i] += UNIT
    return tuple(sorted(values))


def orbit(moves):
    distance = {ZERO: 0}
    queue = deque([ZERO])
    while queue:
        state = queue.popleft()
        for group, r in moves:
            # Indices follow increasing discrepancy in a sorted state.
            target = step(state, group, r, group[:r])
            if target not in distance:
                distance[target] = distance[state] + 1
                queue.append(target)
    return distance


def finite_values(moves, horizon):
    @lru_cache(None)
    def safe(state, limit, left):
        if max(-state[0], state[-1]) > limit:
            return False
        if left == 0:
            return True
        for group, r in moves:
            if not any(safe(step(state, group, r, payers), limit, left - 1)
                       for payers in combinations(group, r)):
                return False
        return True

    # The separately verified greedy invariant supplies the upper limit.
    return [next(limit for limit in range(15) if safe(ZERO, limit, h))
            for h in range(horizon + 1)]


def check(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-certificate", action="store_true")
    args = parser.parse_args()
    orbits = []
    expected = ([0, 9, 10, 13, 13, 13, 14], [0, 9, 12, 13, 13, 14, 14])
    for single, profile in zip((True, False), expected):
        moves = tuple(requests(single))
        distances = orbit(moves)
        orbits.append(distances)
        result = finite_values(moves, 6)
        check(result == profile, "unexpected minimax profile")
        bound = max(max(-s[0], s[-1]) for s in distances)
        check(len(distances) == 195 and bound == 14, "unexpected orbit")
        profile_greedy = [max(max(-s[0], s[-1]) for s, d in distances.items() if d <= h)
                          for h in range(7)]
        check(profile_greedy == profile, "greedy and minimax differ")
        print(f"{'single' if single else 'batch'}: requests={len(moves)}, "
              f"orbit={len(distances)}, depth={max(distances.values())}, "
              f"minimax (twelfths)={result}")

    first, second = orbits
    check(first.keys() == second.keys(), "orbit sets differ")
    check(all(tuple(-v for v in reversed(s)) in first for s in first),
          "orbit lacks sign symmetry")
    rows = [["x1", "x2", "x3", "x4", "single_depth", "batch_depth"]]
    rows += [[str(x) for x in (*s, first[s], second[s])] for s in sorted(first)]
    if args.write_certificate:
        with CERT.open("w", newline="", encoding="ascii") as out:
            csv.writer(out, lineterminator="\n").writerows(rows)
    with CERT.open(newline="", encoding="ascii") as inp:
        check(list(csv.reader(inp)) == rows, "certificate differs from computation")
    print("Certificate verified; orbits coincide and are closed under negation.")


if __name__ == "__main__":
    main()
