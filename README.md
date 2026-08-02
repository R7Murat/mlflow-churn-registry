## Design decisions

Real engineering choices made during this project — the "why", not just the "what".

**Aliases, not stages.** MLflow's `Staging`/`Production` stages are
deprecated. This project uses the current standard — **aliases**
(`@champion`, `@challenger`) — which decouple *role* from *version*
and allow zero-downtime model swaps (serving reads `@champion`, we just
move the alias).

**Champion / challenger, not per-environment models.** A model's *role*
(champion) lives in the registry; its *environment* (prod/uat) belongs to
infrastructure. Keeping one model with moving aliases guarantees "what you
tested is what you deploy" — no rebuild between test and prod.

**Self-contained pyfunc.** Preprocessing is embedded in the model object
(via cloudpickle), not referenced through `context.artifacts` file paths.
This avoids a cross-platform bug where Windows-logged artifact manifests
use backslash paths that fail to load inside a Linux container.

**Proxy artifact access.** The tracking server runs with
`--artifacts-destination` (proxy mode), so both the host notebook and the
serving container reach artifacts through the server over HTTP — no
host-specific file paths leak into the registry.

**Governance as data.** Leakage checks run at *training* time and are
recorded as a `leakage_checked` tag. The promotion gate verifies the
*evidence exists* — a model without it cannot become champion.

**Fail-closed gates, cheapest first.** `promote.py` checks tag → metric →
overfitting (cheap to expensive), and rejects on any failure. The previous
champion is preserved as `@previous-champion` for rollback. Every decision
is logged for audit.

**Bootstrap via compose profiles.** Serving sits behind a `serve` profile
so it never starts against an empty registry — the "champion must exist
before serving" order is enforced by infrastructure, not just documentation.

## Model documentation

See [`model_card.md`](model_card.md) for performance, intended use,
limitations, and reproducibility notes. Headline metrics: **ROC-AUC 0.858**,
**PR-AUC 0.682** (imbalanced problem, ~20% churn — accuracy alone is
misleading).

## License

MIT — see [`LICENSE`](LICENSE).

---

*Built as a portfolio project demonstrating production ML engineering
practices: reproducibility, governance, rollback, and evidence.*