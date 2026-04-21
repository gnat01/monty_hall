# Heterogeneous Rewards: Notes for a Possible Part III

This is the next natural generalisation after variable reveal costs.

The baseline papers treat all prizes as identical. A door either has reward `1`
or reward `0`. If there are `m` prize doors, the only relevant state variable is
the number of prize doors remaining. That symmetry is what gives the clean
formula

```text
S(t) = m(K - 1) / [K(K - 1 - t)].
```

With nonidentical rewards, the model can either remain surprisingly clean or
become much richer, depending on what the player knows and how switching is
allowed.

## 1. Exchangeable Random Placement, Uniform Switching

Suppose there are rewards

```text
v_1, ..., v_m
```

and `K-m` zero-reward doors. The rewards are placed uniformly at random among
the `K` doors. The player chooses an initial door uniformly. Monty reveals only
zero-reward doors. After `t` reveals, the player switches uniformly among the
remaining non-initial closed doors.

Let

```text
V = v_1 + ... + v_m.
```

Then the expected reward from staying is

```text
E[stay] = V / K.
```

The expected reward from switching after `t` reveals is

```text
E[switch after t reveals] = V(K - 1) / [K(K - 1 - t)].
```

So in the fully exchangeable uniform-switching model, heterogeneous rewards
collapse to total reward mass `V`.

This is the direct analogue of the identical-prize formula, where `V=m`.

## 2. Why Heterogeneity Sometimes Does Nothing

In the exchangeable model, every unrevealed non-initial door is symmetric. Monty
has only revealed zeros, and the player does not know which remaining door has
which positive reward.

Therefore, if the player switches uniformly, the only quantity that matters is
the total expected reward mass left among the switch options.

The individual values

```text
v_1, ..., v_m
```

do not matter separately.

This gives a clean first theorem for a possible Part III:

```text
Under exchangeable random placement and uniform switching,
heterogeneous rewards enter only through total reward mass V.
```

This is mathematically neat, but not yet the most interesting case.

## 3. Door-Specific Priors

The richer version begins when doors are not exchangeable.

Suppose each door `j` has a known prior expected reward

```text
mu_j.
```

Monty reveals zero-reward doors. Now the identity of the revealed doors matters,
not just the number of reveals.

If the player initially chose door `i` and Monty revealed set `R`, then the
remaining switch set is

```text
A = {doors except i and except revealed doors}.
```

For uniform switching, the switch value is roughly

```text
average posterior reward over A.
```

For optimal switching, the switch value is

```text
max posterior reward over A.
```

So the state is no longer one-dimensional in `t`; it is a posterior distribution
over remaining doors.

## 4. Strategic Initial Choice

With identical rewards and symmetric doors, the initial choice is irrelevant.
With heterogeneous priors, it becomes strategic.

There are two competing effects:

- Choosing a high-prior door gives a good stay option.
- Choosing a low-prior door preserves high-prior doors for the switch set.

This suggests a possible "sacrifice choice" phenomenon:

```text
Choose a door you do not especially want, so that Monty helps concentrate
probability or value among the doors you may later switch to.
```

This feels genuinely interesting. It is counterintuitive and directly tied to
the Monty mechanism.

## 5. Optimal Switching Versus Uniform Switching

In the existing papers, switching is uniform among remaining non-initial doors.
With heterogeneous rewards, that may be too restrictive.

There are at least three switching rules:

1. Uniform switching among all remaining non-initial doors.
2. Switch to the door with highest posterior expected reward.
3. Randomized switching according to posterior weights.

Under symmetry, these often collapse to the same expected value. Under
heterogeneity, they can differ sharply.

This could create a hierarchy:

```text
stay value <= uniform switch value <= optimal switch value
```

though the first inequality need not always hold if the initial door was chosen
strategically.

## 6. Host Behavior Becomes Important

In the symmetric model, Monty's choice among available zero doors does not
matter. All zero doors are equivalent.

With heterogeneous priors, Monty's reveal policy matters.

Examples:

- Monty reveals the lowest-prior zero door.
- Monty reveals the highest-prior zero door.
- Monty reveals randomly among zeros.
- Monty is adversarial and tries to minimize player value.
- Monty is helpful and tries to maximize player value.

The revealed set can carry information even though every revealed door has
zero reward. This turns the problem into a signaling/Bayesian-updating problem.

## 7. Possible Theorems

### Theorem A: Exchangeable Heterogeneous Rewards Collapse to Total Mass

Assume rewards `v_1,...,v_m,0,...,0` are randomly permuted among `K` doors.
Monty reveals `t` zero-reward doors. The player switches uniformly among the
remaining non-initial closed doors. Then

```text
E[switch after t reveals] = V(K - 1) / [K(K - 1 - t)],
```

where `V=sum_i v_i`.

This is a clean, easy theorem.

### Theorem B: Exact Constant-Cost Threshold Becomes `V/(Km)`

Under the same exchangeable model with uniform switching and reveal cost `c`,
the net value is

```text
W(t) = V(K - 1) / [K(K - 1 - t)] - c t.
```

The full-reveal endpoint has value

```text
V(K - 1)/(Km) - c(K - m - 1)
```

and the no-reveal endpoint has value

```text
V/K.
```

The endpoint comparison gives

```text
c* = V / (K m)
```

when the number of zero doors available for revelation is `K-m-1`.

This matches Part I in the identical unit-reward case, because then `V=m` and
therefore `V/(Km)=1/K`.

### Theorem C: Sacrifice Initial Choice Can Be Optimal

With door-specific priors and optimal switching, it may be optimal to choose a
low-prior initial door in order to keep high-prior doors available for later
switching.

This would be the most conceptually interesting theorem.

We should look for a minimal example, probably with `K=3` or `K=4`.

## 8. Possible Minimal Example for Strategic Initial Choice

Take `K=3`, one prize, and prior probabilities

```text
p_1 > p_2 > p_3.
```

If the player chooses door `1`, then the best stay option is strong, but
switching after Monty reveals a zero may leave one of `{2,3}`.

If the player chooses door `3`, then doors `{1,2}` remain available for the
switch set. Monty's reveal may eliminate a zero from this higher-value pair.

The question:

```text
Can choosing door 3 dominate choosing door 1 when the player intends to switch?
```

Likely yes under some priors and host rules.

This is worth analyzing explicitly.

## 9. Relation to Variable Costs

Heterogeneous rewards and variable costs can combine naturally.

The objective becomes

```text
expected reward after t reveals - cumulative reveal cost.
```

If expected reward depends on the actual revealed set, then the stopping problem
is no longer deterministic in `t`. It becomes an adaptive stopping problem:

```text
after each reveal, update posterior values and decide whether to continue.
```

This would be a genuinely more advanced Part III or Part IV topic.

## 10. Suggested Paper Structure

Possible title:

```text
Eliminative Information in a Generalized Monty Hall Problem III:
Heterogeneous Rewards and Strategic Initial Choice
```

Possible structure:

1. Recall Part I and Part II.
2. Introduce heterogeneous rewards.
3. Prove exchangeable rewards collapse to total reward mass.
4. Show why this means heterogeneity alone is not enough; asymmetry is needed.
5. Introduce door-specific priors.
6. Analyze a minimal strategic-initial-choice example.
7. Discuss host policies and posterior updating.
8. Simulate richer cases.

## Main Takeaway

Nonidentical rewards are not automatically complicated. If placement is
exchangeable and switching is uniform, only total reward mass matters.

The real action begins when heterogeneity is tied to door identity, priors, host
behavior, or optimal non-uniform switching. Then the model moves from a scalar
stopping problem to a posterior-state decision problem.

That feels substantial enough to warrant a separate Part III.
