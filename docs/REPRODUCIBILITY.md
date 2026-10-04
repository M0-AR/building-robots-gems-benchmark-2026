# Reproducibility (best practice, verified 2026)

Design follows open-navigation workload benchmark + CSAR 2026 + SwarmRob:
one-command Docker, HIL-style isolation (`gems-benchmark` vs `gems-verify`
services), logs in `results/`, analysis scripted, no manual steps.

## Zero-to-hero
```bash
pip install -r requirements.txt        # or: docker compose up --build
python scripts/fetch_live_data.py      # live gate, cached, never blocks
python scripts/run_all.py              # 5 exps → results/*.json + figures/*.png
python scripts/verify.py               # 12 strict checks, exit 0 required
pytest -q                              # 10 unit tests
```

## Determinism
- Fixed seeds (ADC RNG seeded by voltage bin), fixed grids, Euler dt=0.5ms.
- Verified 2026-10-04: 10/10 tests pass, 12/12 verify checks pass.
- Figures regenerated every run (no checked-in binaries trusted).

## Sharing publicly
- Push this folder to GitHub; CI should run `make test run verify`.
- Large artifacts: keep `results/*.json` in git, figures regenerable.
- Cite: GEMS hardware page, DelftX program, Gaiceanu cascade-PI, thomasthelliez
  protocol framework, open-navigation/CSAR/SwarmRob reproducibility pattern.
  Full URL log in SOURCES.md.
