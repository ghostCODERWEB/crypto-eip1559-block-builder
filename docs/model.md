# Model specification

## Purpose

Simulate nonce-constrained fee-priority packing, base-fee updates, fee burning and validator tips.

## Economic and protocol assumptions

EIP-1559 integer base-fee formula with elasticity 2 and change denominator 8. Gas estimates are treated as exact usage; no balance validation, refunds, blob fees or MEV. Greedy tip packing is not the optimal block knapsack.

## Execution

`analyze` starts a fresh model from the provided configuration. Events, where present, are replayed in input order. Event timestamps must be nonnegative integers in nondecreasing order. Inputs are not modified by analysis. Invalid transitions raise `ValueError` or `KeyError`; the single-run server responds 400 and does not persist a failed result.

## Exactness

Integer engines use Python arbitrary-precision integers. Decimal engines use the precision declared in their local context. Decimal strings avoid conversion from already-rounded binary float inputs. Statistical engines deliberately use floating point. Rounding policy appears in the implementation; there is no assumption of real-token decimals.

## Reproducibility

The example and checked expected output are the golden fixture. Scenario runs deep-copy the baseline before every case. Stochastic statistics use an explicit seed. Snapshots retain all supplied inputs, so avoid personal or confidential data in publicly shared examples.

## Validation scope

Domain tests exercise economic constraints and replay transitions. Workflow tests cover scenario independence, patch paths, history persistence and pagination. HTTP tests exercise loopback routes, session tokens and rejection behavior. This evidence does not establish protocol equivalence or production security.

## Extending the engine

Add each transition with an explicit precondition, conservation or accounting rule, and rejection test. Document any external trust assumption. Before connecting real chain data, introduce chain IDs, finality policy, identity verification and provenance metadata.
