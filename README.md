# Five dishes or six?

A three-page computational research note on a four-person bill-splitting game. Four people start at zero. Each item is split equally among whichever people shared it. The allocator assigns the leftover cents to distinct participants immediately. The question is how far anyone's total payments can ever drift from their exact shares.

[Read the paper (PDF)](paper.pdf) · [Editable HTML](paper.html) · [195-state certificate](certificates/orbits.csv)

**The worst discrepancy is 7/6 cents in both games.** With one leftover cent per item, an adaptive adversary needs six items to force it. Allowing several leftover cents reduces this to five. The same greedy rule is optimal at every horizon: assign the cents to those participants who have previously paid least relative to their exact shares. The two rules lead to the same reachable greedy states but different distances to them.

| Number of items | 0 | 1 | 2 | 3 | 4 | 5 | ≥6 |
|---|---:|---:|---:|---:|---:|---:|---:|
| One leftover cent | 0 | 3/4 | 5/6 | 13/12 | 13/12 | 13/12 | 7/6 |
| Any legal remainder | 0 | 3/4 | 1 | 13/12 | 13/12 | 7/6 | 7/6 |

Values are minimax cumulative discrepancies in cents, measured at the worst prefix. Participants can change on every item. The result is for equal shares and irrevocable item-by-item, floor-or-ceiling rounding.

## Reproduce

From this directory, run with Python 3.8 or newer. No packages or network access are required.

```sh
python3 verify.py
python3 check_certificate.py
```

The first command enumerates the greedy orbits using integer arithmetic, solves the finite-horizon game against every legal allocation, and compares its results with the certificate. The second checks the certificate from scratch using rational arithmetic and all eligible tie choices. Its predecessor and edge checks certify the shortest distances from zero. To regenerate the CSV, use `python3 verify.py --write-certificate`.

The certificate's first four columns are sorted discrepancies in **twelfths of a cent**. The last two columns count items. The PDF was built from the editable HTML using `python3 build_pdf.py` (optional typesetting dependencies: ReportLab, lxml, and DejaVu fonts installed under `/usr/share/fonts/truetype/dejavu`).

## Attribution and scope

[Fagin and Williams (1983)](https://doi.org/10.1147/rd.272.0133), p. 136, already report the four-person positive extremum of 7/6 for single-driver greedy. [Ajtai et al. (1998)](https://doi.org/10.1006/jagm.1998.0953) study scheduling under adaptive and random inputs. This note gives a reproducible small-instance comparison of the two games, their full minimax horizon profiles, and explicit forcing examples. The literature check does not establish priority for the refinements.

This research note and its verification software were prepared with OpenAI Codex. This is a public-facing preprint, without a claim of peer review or institutional affiliation.
