# Reward Structures for Heterogeneous Monty Hall

This note separates the heterogeneous-reward ideas into clean model classes and
suggests how to code them.

The main point: there are two very different notions of heterogeneity.

1. The rewards are heterogeneous, but door labels are exchangeable.
2. Door labels themselves carry different prior reward distributions.

These should be coded separately.

## 1. Exchangeable Reward Multiset

In this model, we are given or sample a multiset of positive rewards

```text
v_1, ..., v_m
```

and place them uniformly at random among `K` doors, with `K-m` zeros.

Door labels carry no information. The player knows the reward multiset or its
distribution, but not the placement.

### Good Reward Distributions

For the positive rewards `v_i`, useful choices are:

```text
fixed        v_i = 1
uniform      v_i ~ Uniform(low, high)
exponential  v_i ~ Exponential(scale)
lognormal    v_i ~ LogNormal(mu, sigma)
pareto       v_i ~ Pareto(alpha)
```

Recommended defaults:

```text
fixed        for verifying the Part I identical-prize case
lognormal    for visibly heterogeneous rewards
exponential  for a simple skewed positive distribution
```

### Clean Theorem to Test

Let

```text
V = sum_i v_i.
```

Under exchangeable placement and uniform switching after `t` reveals,

```text
E[switch after t reveals] = V(K - 1) / [K(K - 1 - t)].
```

So this model is mathematically useful because it demonstrates that
heterogeneous rewards alone do not necessarily complicate the problem.

If the labels are exchangeable and switching is uniform, heterogeneity collapses
to total reward mass `V`.

### Code Shape

Suggested functions:

```python
sample_reward_multiset(m, kind="lognormal", ...)
place_rewards_exchangeably(K, rewards, rng)
simulate_exchangeable_uniform_switch(K, m, reward_dist, r, ...)
```

This should remain separate from the door-specific prior model.

## 2. Door-Specific Prior Model

This is the richer model.

Each door `j` has its own random reward

```text
X_j >= 0.
```

The player knows the prior law of each `X_j`, but not the realized rewards.
Monty observes realized rewards and may reveal only doors with realized reward
zero.

The prior mean of door `j` is

```text
mu_j = E[X_j].
```

But after Monty reveals doors, the relevant object is no longer the original
`mu_j`; it is the posterior vector

```text
mu_j(R) = E[X_j | Monty revealed R and followed policy pi].
```

The identity of revealed zero doors matters.

## 3. Recommended First Prior: Bernoulli-Value Doors

The cleanest first door-specific model is:

```text
X_j = 0    with probability q_j
X_j = v_j  with probability 1 - q_j
```

where

```text
q_j in [0,1]
v_j > 0.
```

Then

```text
mu_j = (1 - q_j) v_j.
```

This is a good first model because:

- It is easy to simulate.
- It has a real atom at zero, so Monty has legal zero-reward doors to reveal.
- The prior mean is transparent.
- The model naturally supports strategic initial choice.
- Posterior updates are simpler than for continuous positive distributions.

### Suggested Priors Over Door Types

A flexible default:

```text
q_j ~ Beta(alpha_q, beta_q)
v_j ~ LogNormal(mu_v, sigma_v)
```

Then

```text
X_j = 0 with probability q_j
X_j = v_j with probability 1 - q_j.
```

Reasonable starting defaults:

```text
q_j ~ Beta(2, 2)
v_j ~ LogNormal(0, 1)
```

Interpretation:

- `q_j` controls how likely door `j` is empty.
- `v_j` controls how valuable door `j` is if nonempty.
- The lognormal makes high-value outliers possible.
- The beta distribution gives a healthy mix of likely-empty and likely-nonempty
  doors.

Alternative defaults:

```text
q_j ~ Beta(5, 2)       many doors likely empty
q_j ~ Beta(2, 5)       many doors likely nonempty
v_j ~ Exponential(1)   simpler positive values
v_j fixed              isolates zero-probability heterogeneity
```

## 4. Alternative Prior: Zero-Inflated Continuous Rewards

A more general model is:

```text
X_j = 0                         with probability q_j
X_j ~ positive_dist(theta_j)     with probability 1 - q_j.
```

For example:

```text
positive_dist = Exponential(scale_j)
scale_j ~ LogNormal(mu_scale, sigma_scale)
```

Then

```text
mu_j = (1 - q_j) E[positive_dist(theta_j)].
```

This is more realistic but harder to reason about. It should probably come
after the Bernoulli-value model.

## 5. Monty Reveal Policies

With door-specific priors, Monty's policy matters. The identity of the revealed
door can carry information.

Start with one policy but design the interface for several.

Possible policies:

```text
uniform_zero      reveal uniformly among legal zero doors
low_mu_zero       reveal legal zero door with lowest prior mean
high_mu_zero      reveal legal zero door with highest prior mean
adversarial       reveal the zero door that minimizes player switch value
helpful           reveal the zero door that maximizes player switch value
```

Recommended first implementation:

```text
uniform_zero
```

Reason: it is neutral, easy to simulate, and a good baseline.

## 6. Player Strategies

Strategies should be explicit.

Suggested initial strategies:

```text
stay
uniform_switch
prior_best_switch
oracle_best_switch
```

Definitions:

```text
stay:
    keep initial door.

uniform_switch:
    switch uniformly among remaining unopened non-initial doors.

prior_best_switch:
    switch to the remaining unopened non-initial door with highest prior mean mu_j.

oracle_best_switch:
    switch to the remaining unopened non-initial door with highest realized reward.
    This is not feasible for the player, but gives an upper bound.
```

Later strategy:

```text
posterior_best_switch:
    compute posterior means after Monty's reveal under a known host policy,
    then switch to the highest posterior mean.
```

This should come later because exact posterior updating can be model-specific.

## 7. Strategic Initial Choice

In the symmetric model, initial choice is irrelevant.

In the door-specific prior model, initial choice is strategic.

The player may choose:

```text
highest_mu_initial:
    choose the door with largest prior mean.

lowest_mu_initial:
    choose the door with smallest prior mean.

random_initial:
    choose uniformly.

switch_preserving_initial:
    choose a low-value door to preserve high-value doors for later switching.
```

The interesting phenomenon:

```text
Choosing a low-prior door can be optimal if the player expects to switch later.
```

This is the "sacrifice initial choice" idea.

## 8. Recommended Code Layout

Create:

```text
src/monty_hall_heterogeneous.py
```

Suggested data classes:

```python
@dataclass(frozen=True)
class DoorPrior:
    zero_prob: float
    reward_value: float

    @property
    def mean(self) -> float:
        return (1.0 - self.zero_prob) * self.reward_value
```

For later continuous models:

```python
@dataclass(frozen=True)
class ZeroInflatedPrior:
    zero_prob: float
    positive_kind: str
    positive_params: dict
```

Core functions:

```python
sample_reward_multiset(...)
place_rewards_exchangeably(...)

sample_door_priors(...)
sample_realized_rewards(priors, rng)

legal_reveals(rewards, initial, opened)
monty_reveal(rewards, priors, initial, opened, policy, rng)

choose_initial(priors, strategy, rng)
choose_switch(priors, rewards, initial, opened, strategy, rng)

simulate_exchangeable(...)
simulate_door_specific(...)
```

## 9. First Implementation Plan

Phase 1: exchangeable rewards.

- Implement reward multiset sampling.
- Verify the total-mass theorem by simulation.
- Compare fixed, exponential, and lognormal rewards.

Phase 2: Bernoulli-value door priors.

- Implement `DoorPrior`.
- Implement `q_j ~ Beta`, `v_j ~ LogNormal`.
- Implement `uniform_zero` Monty.
- Implement initial choice strategies.
- Implement switch strategies: stay, uniform, prior-best, oracle-best.

Phase 3: strategic initial choice.

- Search for small examples where choosing a low-mean initial door dominates
  choosing a high-mean initial door.
- Start with `K=3` or `K=4`.
- Compare random, highest-mean, and lowest-mean initial choices.

Phase 4: posterior updating.

- Only after the simulation model is stable.
- Start with exact enumeration for small `K`.
- Compute posterior means under `uniform_zero` Monty.
- Add `posterior_best_switch`.

## 10. What Distribution Should We Use First?

Recommended first serious model:

```text
K = 8 or 10
q_j ~ Beta(2, 2)
v_j ~ LogNormal(0, 1)
X_j = 0 with probability q_j
X_j = v_j with probability 1 - q_j
Monty policy = uniform_zero
```

Why:

- It creates many legal zero reveals.
- It creates visible reward heterogeneity.
- It has simple prior means.
- It is easy to simulate and explain.
- It supports strategic initial choice.

Recommended first theorem-checking model:

```text
exchangeable reward multiset
v_i ~ LogNormal(0, 1)
uniform switching
```

Why:

- It should collapse to total reward mass `V`.
- It gives a clean sanity check.
- It separates "heterogeneous rewards" from "door-specific information."

## 11. Main Design Principle

Do not mix these two models too early:

```text
exchangeable reward multiset
door-specific priors
```

The first is a clean theorem playground.

The second is where the genuinely new decision theory lives.

They should share helper functions where convenient, but the simulations and
paper sections should keep them conceptually separate.
