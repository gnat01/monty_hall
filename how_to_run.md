# How To Run

Run all commands from the project root:

```sh
cd /Users/gn/work/learn/python/monty_hall
```

Use `MPLCONFIGDIR=.mplconfig` with plotting commands so Matplotlib writes its
font cache inside the project.

## Tests

Run the full Python test suite:

```sh
MPLCONFIGDIR=.mplconfig python -B -m unittest discover -s src
```

## Part I: Generalized Monty Hall

Run the generalized simulator:

```sh
python -B src/monty_hall_generalised.py --K 10 --m 3 --r 4 --experiments 1000 --chances 500 --seed 1 --plot
```

Run the conditional-switching simulator:

```sh
python -B src/monty_hall_clean_conditional_switching.py --K 8 --m 2 --r 3 --experiments 1000 --chances 500 --seed 2 --switch-probability 0.35 --plot
```

Generated simulator plots are written to:

```text
outputs/
```

Build the Part I paper:

```sh
cd monty_hall_paper
make
```

Main output:

```text
monty_hall_paper/monty.pdf
```

## Part II: Variable Reveal Costs

The variable-cost code is:

```text
src/monty_hall_variable_costs.py
```

Run a linearly increasing cost example:

```sh
python -B src/monty_hall_variable_costs.py --K 50 --m 1 --kind linear --base 0.0 --slope 0.001
```

Run a smooth saturating cost example:

```sh
python -B src/monty_hall_variable_costs.py --K 50 --m 1 --kind saturating --base 0.004 --saturation 0.026 --tau 8
```

Run a linear-plus-cap cost example and export the value table:

```sh
python -B src/monty_hall_variable_costs.py --K 50 --m 1 --kind linear_saturating --base 0.004 --slope 0.0018 --saturation 0.022 --csv outputs/variable_cost_table.csv
```

The CSV columns are:

```text
t, S_t, C_t, W_t, next_cost, delta_t
```

Build the Part II paper:

```sh
cd monty_hall_paper_ii
make
```

Main output:

```text
monty_hall_paper_ii/monty_ii.pdf
```

The Part II plotting script is:

```text
monty_hall_paper_ii/generate_plots.py
```

It generates:

```text
fig_cost_shapes.png
fig_linear_regimes.png
fig_linear_phase.png
fig_saturation_pushthrough.png
fig_saturating_phase.png
```

## Part III: Heterogeneous Rewards

The heterogeneous-reward code is:

```text
src/monty_hall_heterogeneous.py
```

Run the exchangeable reward-multiset model:

```sh
python -B src/monty_hall_heterogeneous.py exchangeable --K 12 --m 4 --r 4 --reward-dist lognormal --trials 100000 --seed 3
```

Run the exchangeable unequal-prize Stage IV baseline with explicit reward values:

```sh
python -B src/monty_hall_heterogeneous.py exchangeable --K 12 --m 4 --r 4 --reward-values 1,2,5,9 --trials 100000 --seed 3
```

Run the door-specific Bernoulli-value prior model:

```sh
python -B src/monty_hall_heterogeneous.py door-specific --K 10 --r 2 --trials 100000 --seed 4 --initial lowest_mu --monty uniform_zero --plot
```

Search for a sacrifice-initial-choice example:

```sh
python -B src/monty_hall_heterogeneous.py find-sacrifice --K 4 --r 1 --tries 100 --trials 20000 --seed 5
```

Build the Part III paper:

```sh
cd monty_hall_paper_iii
make
```

Main output:

```text
monty_hall_paper_iii/monty_iii.pdf
```

The Part III plotting script is:

```text
monty_hall_paper_iii/generate_plots.py
```

It generates:

```text
fig_exchangeable_collapse.png
fig_prior_landscape.png
fig_strategy_comparison.png
fig_sacrifice_choice.png
fig_monty_policy_effect.png
```

## Part IV: Multiple Unequal Prize Values

The working paper is:

```text
monty_hall_paper_iv/monty_iv.tex
```

The Stage 1 coding target is the exchangeable unequal-prize case:

- explicit positive reward vector `v_1, ..., v_m`
- uniform random placement over doors
- theory should collapse to total reward mass `V = sum_i v_i`

The exchangeable CLI now supports:

- `--reward-values 1,2,5,9`

which must contain exactly `m` strictly positive values.

## Clean Build Artifacts

Clean Part I LaTeX artifacts:

```sh
cd monty_hall_paper
make clean
```

Clean Part II LaTeX artifacts:

```sh
cd monty_hall_paper_ii
make clean
```

Clean Part III LaTeX artifacts:

```sh
cd monty_hall_paper_iii
make clean
```

## Notes

- Part I is the constant-cost baseline with exact threshold `c* = 1/K`.
- Part II keeps the same success law but replaces constant cost with a cost sequence `c_t`.
- The key variable-cost increment is `W(t+1)-W(t) = Delta_t - c_t`.
- Linearly increasing costs can produce interior optima.
- Costs that rise and saturate can restore the late-stage push-through effect.
- Part III separates exchangeable heterogeneous rewards from door-specific priors.
- Exchangeable heterogeneous rewards collapse to total reward mass under uniform switching.
- Door-specific priors make switching rules, Monty policy, and initial choice matter.
