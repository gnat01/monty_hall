# Stage 2 Labeling Landscapes

## Why This Note Exists

Stage 2 is now live: doors are labeled, each door has its own prior, and the
simple Stage 1 collapse to total reward mass `V` is gone.

That creates an immediate problem:

- “random labeled landscapes” is too broad
- if we do not characterize the landscapes, the partial-collapse story is vague
- we need a language for saying which kinds of labeled environments behave
  similarly and which do not

So this note proposes a first taxonomy for Stage 2 landscapes.

## What A Labeled Landscape Is

A Stage 2 labeled landscape is the full door-by-door specification

- `(p_1, v_1), (p_2, v_2), ..., (p_K, v_K)`

where:

- `p_j` = probability door `j` pays out
- `v_j` = reward magnitude if door `j` pays out
- `mu_j = p_j v_j` = prior mean of door `j`

This means a landscape is not just “a set of means”. It has at least three
layers:

1. payout probabilities `p_j`
2. payout sizes `v_j`
3. resulting prior means `mu_j`

Two landscapes can have very similar prior means and still differ in their
underlying `p_j` / `v_j` structure.

## First-Pass Summary Statistics

These are the most useful initial descriptors.

### 1. Best Mean

- `best_mean = max_j mu_j`

This captures how attractive the best labeled door is in absolute terms.

### 2. Total Mean Mass

- `mean_mass = sum_j mu_j`

This is the labeled analogue of “total reward mass”, but it no longer governs
the dynamics by itself.

### 3. Top-Door Concentration

- `concentration = max_j mu_j / sum_j mu_j`

This measures how dominant the best door is relative to the whole landscape.

Interpretation:

- high concentration = one door dominates
- low concentration = value is spread broadly

### 4. Gap Between Top Doors

- `gap_12 = mu_(1) - mu_(2)`

or alternatively

- `gap_ratio = mu_(1) / mu_(2)`

This tells us whether there is one clearly best door or several near-best
alternatives.

### 5. Effective Number Of Good Doors

Let

- `w_j = mu_j / sum_k mu_k`

Then define

- `n_eff = 1 / sum_j w_j^2`

Interpretation:

- small `n_eff` = sharply concentrated landscape
- large `n_eff` = diffuse landscape with several relevant doors

### 6. Reward Heterogeneity

Spread of the `v_j` values, for example:

- `sd(v_j)`
- coefficient of variation of `v_j`

This distinguishes flat reward magnitudes from “jackpot” landscapes.

### 7. Probability Heterogeneity

Spread of the `p_j` values, for example:

- `sd(p_j)`
- coefficient of variation of `p_j`

This distinguishes uniform reliability from highly uneven reliability.

### 8. Alignment Between `p_j` And `v_j`

This is important.

We need to know whether:

- high-reward doors also tend to have high payout probability

or whether:

- high rewards come from rare-event doors

A simple first descriptor is:

- correlation between `p_j` and `v_j`

Interpretation:

- positive alignment = big rewards also likely rewards
- negative alignment = rare jackpots

## Candidate Landscape Classes

These are not yet formal, but they are a good working taxonomy.

### A. Peaked

Properties:

- one door has much larger `mu_j` than the rest
- large `gap_12`
- high concentration
- low `n_eff`

Expectation:

- `highest_mu` behaves distinctly
- `random` and `lowest_mu` may cluster more closely
- partial-collapse class structure may be strongest here

### B. Diffuse

Properties:

- several doors have similar `mu_j`
- small top gap
- lower concentration
- larger `n_eff`

Expectation:

- initial choice matters less
- switching rules may separate less dramatically
- partial collapse may weaken or become trivial

### C. Two-Tier

Properties:

- a small band of good doors
- then a weaker bulk

Expectation:

- may behave between peaked and diffuse
- likely a good regime for “several near-best alternatives”

### D. Rare-Jackpot

Properties:

- some doors have large `v_j`
- but very small `p_j`
- often negative or weak `p-v` alignment

Expectation:

- `mu_j` alone may hide important structure
- prior-best switching may be more fragile
- oracle gap may widen

### E. Aligned High-Value

Properties:

- high `v_j` and high `p_j` occur together
- strong positive `p-v` alignment

Expectation:

- best doors are obvious in prior mean
- `prior_best_switch` may perform strongly

### F. Misaligned

Properties:

- high `v_j` paired with low `p_j`
- high `p_j` paired with middling `v_j`

Expectation:

- more tension between “safe” and “jackpot” doors
- richer Stage 2 behavior

## Why This Matters For Collapse

Stage 1 collapse worked because the landscape was exchangeable.

Stage 2 is different:

- labels matter
- initial choice matters
- the survival set after reveals matters

So we should not expect one universal scalar collapse.

But we may still get:

- class-dependent collapses
- conditional collapses after controlling for landscape type

For example, the current Stage 2 evidence suggests:

- in some peaked landscapes, `random` and `lowest_mu` look very similar after
  normalization by `oracle_best_switch`
- `highest_mu` remains distinct, especially early in reveal depth

That suggests the right question is not:

- “does Stage 2 collapse?”

but rather:

- “within which landscape classes does a partial collapse emerge?”

## Practical Next Step

For each sampled labeled landscape, compute and store at least:

- `best_mean`
- `mean_mass`
- `concentration`
- `gap_12`
- `n_eff`
- `sd(p_j)`
- `sd(v_j)`
- `corr(p_j, v_j)`

Then:

1. bin landscapes by coarse class
2. rerun the partial-collapse plots within each class
3. check whether the class-dependent structure sharpens

## Current Working Hypothesis

The strongest current hypothesis is:

- partial collapse is real in Stage 2
- but only after conditioning on broad structural properties of the labeled
  landscape

Most likely the first successful conditioning variables will be:

- concentration
- top gap
- effective number of good doors

Those are probably the key coarse descriptors.
