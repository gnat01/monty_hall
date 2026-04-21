# Extensions and Discussion Notes

The current paper studies a deliberately clean model:

- `K` doors.
- `m` prize doors.
- The player chooses one initial door uniformly.
- Monty reveals `t` losing doors, never opening the initial door or a prize.
- Each reveal costs a constant `c`.
- After `t` reveals, the player switches uniformly among the remaining non-initial closed doors.

Under those assumptions,

```text
S(t) = m(K - 1) / [K(K - 1 - t)]
```

and the optimal stopping problem

```text
max_t S(t) - c t
```

has the exact endpoint threshold

```text
c* = 1 / K.
```

The reason is structural: Monty's information is eliminative. Each reveal removes a certified loser, so the remaining switch set becomes more concentrated. Marginal value increases rather than decreases.

## 1. Non-Uniform Priors Over Doors

The clean model assumes every door is equally likely to contain a prize before the initial choice. A natural extension is to assign prior probabilities

```text
p_1, ..., p_K
```

with either one prize or multiple prizes.

For one prize, if the player initially chooses door `i`, and Monty reveals a set `R` of losing doors, then switching uniformly is no longer obviously optimal. The posterior prize mass is concentrated on the unrevealed, non-initial doors:

```text
P(prize behind j | R, i) ∝ p_j
```

for unopened `j != i`.

Possible directions:

- Study optimal switching to the highest-posterior remaining door.
- Study uniform switching despite non-uniform priors.
- Ask whether marginal value remains increasing.
- Identify conditions on the prior under which endpoint optimality survives.

Likely outcome: the `1/K` threshold will not survive exactly, because symmetry is what makes the endpoint comparison collapse so cleanly.

## 2. Biased or Stochastic Host

The current host always reveals a losing door and is otherwise effectively neutral. But host behavior could carry additional information.

Examples:

- Monty prefers lower-numbered doors.
- Monty opens doors according to known weights.
- Monty sometimes makes mistakes and reveals a prize.
- Monty is adversarial but constrained not to reveal prizes.

If Monty's choice among available losing doors is biased, the identity of the revealed door matters, not just the number of reveals. The state becomes a posterior distribution over remaining doors.

This moves the problem from a one-dimensional stopping problem in `t` to a Bayesian filtering problem.

Questions:

- Does eliminative information still produce increasing marginal value in expectation?
- Can biased reveals create interior optima?
- How much host randomness is needed to destroy the endpoint threshold?

## 3. Variable Reveal Costs

Instead of a constant cost `c`, let the cost of the `i`th reveal be

```text
c_i.
```

The objective becomes

```text
S(t) - sum_{i=0}^{t-1} c_i.
```

This is probably the cleanest next mathematical extension.

Because `Delta_t = S(t+1)-S(t)` is increasing, the decision compares increasing benefits with the cost sequence.

Cases:

- If costs are constant, we recover the endpoint theorem.
- If costs are increasing fast enough, interior optima can appear.
- If costs are decreasing, full revelation becomes even more attractive.
- If costs are random but known only at decision time, this becomes a genuine optimal stopping problem.

This extension is attractive because it keeps the same Monty Hall probability formula while enriching the stopping structure.

## 4. Partial Switching Policies

The conditional-switching script explores a simple randomized policy:

```text
switch with probability p, otherwise stay.
```

For fixed `p`, the success probability is just the mixture

```text
(1-p) * P(stay) + p * P(switch after t reveals).
```

So under the current symmetric model, randomized switching is not strategically necessary: if switching is better than staying, choose `p=1`; otherwise choose `p=0`.

But randomized policies may become meaningful under:

- risk-sensitive utility,
- repeated play with budget constraints,
- uncertain or estimated model parameters,
- adversarial host behavior,
- psychological or behavioral constraints.

This is a useful extension to discuss, but it is not mathematically essential in the baseline model.

## 5. Multiple Prizes and Alternative Rewards

The current formula already handles `m` prize doors with identical prize value. The surprising fact is that the critical cost remains

```text
c* = 1/K
```

whenever at least one reveal is possible.

This cancellation relies on identical unit prizes.

Extensions:

- Prizes have different values.
- The player gets reward equal to the value behind the final door.
- There are prize categories rather than identical prizes.
- The initial choice may have value even if switching also has value.

With heterogeneous prizes, Monty's reveal may change the expected value of switching in a way that depends on which losing doors were removed. The clean threshold likely disappears, but the eliminative-information idea remains.

## 6. Choosing the Initial Door Strategically

In the symmetric model, the initial choice is irrelevant. With non-uniform priors or heterogeneous values, the first choice becomes strategic.

There are two competing effects:

- Choosing a high-prior door improves the value of staying.
- Choosing a low-prior door may leave more posterior mass available for switching.

This could create an interesting "sacrifice choice" phenomenon: choose a door you do not want, in order to let Monty concentrate probability elsewhere.

This is likely one of the most interesting conceptual extensions.

## 7. Budget-Constrained Reveals

Instead of cost per reveal, suppose the player has a hard budget:

```text
t <= B.
```

Then the optimal policy is trivial in the baseline model: use the full budget, because `S(t)` is increasing.

But the budget version becomes more interesting if:

- there are multiple independent Monty games,
- reveal budgets must be allocated across games,
- games have different `K`, `m`, and prize values.

Then the increasing marginal value creates an allocation problem with complementarity: it may be better to fully reveal one game than partially reveal many.

This could be a nice bridge to knapsack-style or portfolio-style decision problems.

## 8. Many Games and Allocation of Information

Suppose there are several Monty instances indexed by `a`, each with parameters

```text
K_a, m_a, V_a.
```

The player has total reveal budget `B` and chooses how many reveals `t_a` to buy in each game.

Objective:

```text
sum_a V_a S_a(t_a)
subject to sum_a t_a <= B.
```

Because each `S_a(t)` has increasing marginal returns, this is not a standard concave resource allocation problem. It has complementarities and may favor lumpy allocations.

This is potentially a strong extension because it turns the Monty toy model into a clean example of non-convex information allocation.

## 9. Unknown Number of Prizes

Let `m` itself be uncertain, with a prior over possible values.

Monty's ability to reveal losing doors gives information about `m`, especially if the process stops because no more losing doors are available.

Questions:

- How does the posterior over `m` evolve with each reveal?
- Does increasing marginal value survive after integrating over `m`?
- Can the player learn whether the environment is prize-rich or prize-poor?

This extension is more complex, but it is conceptually natural.

## 10. Strategic or Adversarial Monty

The current Monty is helpful only in the sense that he follows rules. A strategic Monty could choose reveals to minimize the player's eventual success, subject to not revealing prizes.

In the symmetric baseline, adversarial choice among losing doors does not matter because all unrevealed non-initial doors are exchangeable.

But with non-uniform priors or heterogeneous prizes, adversarial Monty becomes important.

Possible variants:

- Monty wants the player to lose.
- Monty wants the player to switch.
- Monty wants to maximize suspense.
- Monty has imperfect information.

This connects the model to signaling and game theory.

## 11. Continuous or Large-`K` Limits

The exact threshold

```text
c*(K) = 1/K
```

suggests scaling cost as

```text
c = lambda / K.
```

Then the phase transition occurs at

```text
lambda = 1.
```

In the one-prize case, if `x = t/(K-1)`, then approximately

```text
S(t) ≈ 1 / [K(1-x)]
```

until very close to full revelation, where the probability jumps to order one. This singular behavior is what makes the transition sharp.

Possible direction:

- Develop an asymptotic description of the value function.
- Study the boundary layer near full revelation.
- Compare finite-`K` and large-`K` transition widths.

## 12. Relation to Pandora's Box and Search Theory

This is more of a framing extension than a model extension.

The baseline paper already contrasts the model with Pandora's box. That comparison can be deepened:

- Pandora reveals values.
- Monty removes impossibilities.
- Pandora often has diminishing marginal value.
- Monty has increasing marginal value.
- Pandora-style index rules rely on separability and reservation values.
- Monty-style eliminative information can generate complementarity.

The slogan:

```text
Eliminative information is not sampled information.
```

This feels like the most portable conceptual contribution.

## Most Promising Next Directions

If we want clean math:

1. Variable reveal costs `c_i`.
2. Multiple games with a shared reveal budget.
3. Non-uniform priors with optimal initial choice.

If we want conceptual punch:

1. Emphasize eliminative information versus revelatory information.
2. Use the model as a counterexample to naive diminishing-returns intuition.
3. Show that randomized conditional switching is a mixture in the baseline but becomes relevant once symmetry is broken.

If we want a stronger paper:

1. Keep the exact `c*=1/K` theorem as the centerpiece.
2. Add one extension with a second theorem, probably variable costs or budget allocation.
3. Keep simulations as illustrations, not evidence.

## Cautionary Notes

The clean threshold depends on several assumptions:

- symmetric doors,
- identical prize values,
- constant linear reveal cost,
- host never reveals a prize,
- switch is uniform among remaining non-initial doors,
- the game is a single isolated decision problem.

Relaxing any of these can be interesting, but we should not expect `1/K` to survive unchanged. The robust idea is not the exact threshold; the robust idea is that eliminative information can have increasing marginal value.
