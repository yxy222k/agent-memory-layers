# agent-memory-layers (v2)

> Long-term engineering memory for hardware-software & precision instrumentation product lines: **4 Domain Areas × 4 Processing Stages, troubleshooting-driven evolution, and dual-gate offline dreaming**.

A plain-Markdown + Shell memory kit. No server, no database, no vector store — one Git repository is enough. ([中文文档](README.zh.md))

## Why Two Orthogonal Axes

Splitting memory purely by compression level (`transcripts → notes → wiki → injected context`, as in Anthropic's *The components of agent memory*) works well for pure-text tasks, but breaks down in real hardware/optics/instrumentation R&D:

- **First-principles physics equations** and **one specific spectrometer's dark counts** differ in half-life by orders of magnitude.
- **Serial port commands, `.hdf5` schemas, and slide redaction rules** are procedural skills — they should cost `0 tokens` until the moment you connect hardware, save data, or export a report.
- **Troubleshooting records** have no known mechanism while open (they only need reproducibility), yet once resolved they must cascade backward to revise simulation assumptions, add missing calibration checks, and invalidate stale conclusions.

v2 combines **4 Engineering Domains (horizontal)** with **4 Processing Stages (vertical)**:

### Horizontal: 4 Engineering Domains

| Domain | Directory | Holds | Authored & Reviewed By |
|---|---|---|---|
| **① Theory & Models** | `1_theory/` | Physics/math laws, literature maps, simulation assumptions & bounds | Frontier multi-agent exploration (one file per agent) + human review |
| **② Calibration & Assets** | `2_calibration/` | **SOPs**: intake/measurement checklists; **Assets**: per-SN baselines (drift tables, dark counts, overload thresholds) | Human SOPs; execution models follow strict checklists with photo/screenshot evidence |
| **③ Procedural Skills** | `3_skills/` | Device serial/IP setup, CLI/repos, data schemas (`csv/hdf5/pcap/json`), report redaction, office automation | On-demand `SKILL.md` modules; **zero plaintext credentials** |
| **④ Anomalies & Root Cause** | `4_anomalies/` | **Open**: reproducible anomaly snapshots; **Resolved**: root causes, negative results (`refuted`), cascade checklists | Lightweight capture in-session; resolved items trigger offline updates to ① / ② / ③ |

### Vertical: 4 Processing & Loading Stages

| Stage | Location | Hard Constraint |
|---|---|---|
| **④ Injected** | `AGENTS.md` + `MEMORY.md` | Loaded every session; **capped at ≤200 lines / 25KB** (software version, active hardware SNs, safety/redaction red lines, routing index) |
| **③ Navigation** | `1_theory/` + `3_skills/` | Cross-document synthesis wiki & on-demand skills; `1_theory/` must stay smaller than underlying records |
| **② Judgments & Baselines** | `2_calibration/` + `4_anomalies/` | Always carries evidence & `applies_to` bounds; separates `verified` / `hypothesis` / `refuted` / `stale` |
| **① Ground-Truth Facts** | `transcripts/` | Append-only logs & multimodal sidecars pointing to setup photos, GUI screenshots, and `.hdf5`/`.pcap` files |

---

## Four Core Engineering Rules

1. **Low-friction capture, strict promotion**: Open anomalies only require a minimal reproducible snapshot (never force premature mechanism guessing in-session); promoting to `verified` requires mechanism, version/SN bounds, and counterexamples.
2. **Troubleshooting drives cross-layer evolution**: Every `resolved` anomaly triggers a four-way offline audit across `1_theory/`, `2_calibration/`, `3_skills/`, and historical conclusions.
3. **Dual-confirmation offline dreaming**: A 30-second **pre-dream triage** filters out botched lab runs first; consolidation then edits an isolated `git worktree` and emits a real `git diff` for human review (avoiding brittle LLM-generated `.patch` line numbers).
4. **Physical tenant isolation & zero secrets**: Scoped search via `scripts/search.sh --tenant <code_name>`; credentials and internal IPs are referenced strictly via environment variables.

---

## Quick Start

```bash
cp -r templates/* <your-product-repo>/memory/
cp -r scripts <your-product-repo>/memory/scripts
```

See [`examples/interferometry-mini/`](examples/interferometry-mini/README.md) for a complete worked example (1310nm SLD low-current wavelength drift causing interferometric phase jumps, and how its resolution cascades across all layers).

## Docs

- [`docs/architecture.md`](docs/architecture.md) — Dual-axis architecture, two-stage write gates, state machine, and multimodal/security boundaries
- [`docs/dreaming.md`](docs/dreaming.md) — Dual-gate offline consolidation, L4→L1/L2/L3 cascade, and version sweeps
- [`docs/metrics.md`](docs/metrics.md) — 5-arm ablation evaluation and R&D / field-service health metrics

## License

MIT.
