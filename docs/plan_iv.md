# Part IV Plan

## Goal

Extend the Monty Hall program from identical or exchangeable rewards to the case:

- `K` doors
- `m > 1` prize doors
- prize values `v_1, ..., v_m` need not be equal

The conceptual split remains the same as in Part III:

1. exchangeable unequal prizes
2. labeled unequal prizes

The coding should follow that split strictly.

## Stage 1: Exchangeable Unequal-Prize Model

This is the clean baseline and should be coded first.

### Model

- There are `K` doors.
- Exactly `m` doors carry positive rewards.
- Positive rewards are `v_1, ..., v_m`.
- The remaining `K-m` doors carry reward `0`.
- The multiset
  - `\{v_1, ..., v_m, 0, ..., 0\}`
  is placed uniformly at random among door labels.
- The player chooses an initial door uniformly.
- Monty reveals only zero-reward doors.
- After `t` reveals, the player may stay or switch uniformly among remaining non-initial unopened doors.

### Theory To Verify

Let

- `V = sum_i v_i`

Then the exchangeable theorem says:

- stay value: `V / K`
- switch value after `t` reveals:
  - `V (K-1) / [K (K-1-t)]`

So unequal prizes enter only through total reward mass `V`.

### Coding Objective

Implement the smallest extension of the current Part III exchangeable code so that:

- `m > 1` and unequal rewards are explicit
- empirical simulation can be compared directly against the formula above
- plots show theory vs simulation across reward distributions and reveal depths

### Why First

This gives a theorem-verification baseline.
It checks that the new `m > 1`, unequal-prize regime is understood before any label information is introduced.

## Stage 2: Labeled Unequal-Prize Model

This is the genuinely new problem and should come only after Stage 1 is stable.

### Model

For each door `j`, use a Bernoulli-value prior:

- `X_j = v_j` with probability `p_j`
- `X_j = 0` with probability `1 - p_j`

So the prior mean is:

- `mu_j = p_j v_j`

This is the multiple-prize unequal-value analogue of the Part III door-specific model.

### Strategies

Initial-door strategies:

- `random`
- `highest_mu`
- `lowest_mu`

Switch strategies:

- `stay`
- `uniform_switch`
- `prior_best_switch`
- `oracle_best_switch`

Monty reveal policies:

- `uniform_zero`
- `low_mu_zero`
- `high_mu_zero`

## Stage 3: Main Questions Once Stage 2 Exists

After the labeled model is coded, the main questions are:

1. When does `prior_best_switch` beat `uniform_switch` by a large margin?
2. Can low-value initial choices preserve a better switch set when there are several high-value prize candidates rather than one standout door?
3. How sensitive is switch value to Monty's legal reveal policy?
4. Is there any useful reduced state, or does the problem become genuinely high-dimensional in the posterior reward vector?

## Recommended Coding Order

1. Extend the exchangeable model first.
2. Verify empirically:
   - stay = `V / K`
   - switch after `t` reveals = `V (K-1) / [K (K-1-t)]`
3. Only then extend the labeled Bernoulli-value model.
4. Only after that study sacrifice-choice effects and Monty-policy sensitivity.

## Guiding Principle

The exchangeable unequal-prize case is mostly a scalar rescaling of Part I and Part III.
The labeled unequal-prize case is the real Part IV theory problem.

So the code should treat them as separate layers, not merge them prematurely.
