# agent-memory-layers

> Long-term memory for a product line: four layers, write gates, offline consolidation.

A plain-Markdown memory kit. No server, no database, no vector store — one git repo is enough.

## Why

Knowledge bases nobody maintains share one failure: raw records and conclusions live in the
same layer. Retrieval cost grows until nobody bothers.

Four layers fix two things at once — retrieval cost (each layer holds only what belongs in it)
and contamination (raw records stay traceable, every conclusion carries evidence).

| Layer | Holds | Constraint |
|---|---|---|
| ① Facts | tickets, experiment logs, transcripts | append-only; the ground truth for corrections |
| ② Judgments | rules, traps, verified causality | always with evidence; `verified` / `hypothesis` / `stale` |
| ③ Map | a wiki that indexes the rest | must stay **smaller** than what it indexes |
| ④ Injected | the tiny context loaded every session | hard cap; demote when it grows |

Never skip a layer: ② without ① is guesswork, ③ without ② is copying.

## Three rules that matter most

1. **Three-question gate** before writing: will this recur? is it already queryable? can I cite evidence?
2. **Consolidate offline, and emit patches only.** A human reviews `git diff` and merges.
   Without the diff you have lost the only correction gate in the system.
3. **One file per author.** Concurrent writes to a shared file silently overwrite each other;
   merging belongs to the consolidation step.

## Where it came from

Built while consolidating one real product line (a precision metrology instrument), where the
most valuable lessons were all cases of *documentation disagreeing with reality*:

- A repo doc said an algorithm was "not deployed"; production logs showed it had been running for
  three weeks. Comparing data across that date silently compares two different measurement channels.
- An offset blamed on the algorithm dropped 74% when a different probe was fitted — hardware, not math.
- A compensation table treated as "root cause found" was left on by default; the configuration it was
  calibrated for had already changed, and it amplified errors by 3×.

Hence: layer ① must be raw records, not documentation. Docs record intent; records record fact.

## Quick start

```bash
git clone <this repo> memory-kit
cp -r memory-kit/templates/* <your-product-repo>/memory/
```

Then fill `memory/AGENTS.md` (product, environment, red lines, **software version**), write 10–20
seed notes by hand, wire `templates/dreaming/prompt.md` to emit patches, and run one
with/without-memory comparison using the `templates/eval/cases.jsonl` format.

## Docs

- [`docs/why-four-layers.md`](docs/why-four-layers.md) — the method, and why it is not the same thing
  as agent memory
- [`docs/dreaming.md`](docs/dreaming.md) — offline consolidation: patch mode, version sweep, promotion
- [`docs/metrics.md`](docs/metrics.md) — four-arm evaluation and the metrics that actually move

## Not doing

No server, no vector DB, no GUI. Tenant isolation by directory boundary, permissions by your git host.
This kit does not answer business questions; it only makes sure knowledge is not lost because nobody
remembered to write it down.

## License

MIT.
