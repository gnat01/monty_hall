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

## Notes

- Part I is the constant-cost baseline with exact threshold `c* = 1/K`.
- Part II keeps the same success law but replaces constant cost with a cost sequence `c_t`.
- The key variable-cost increment is `W(t+1)-W(t) = Delta_t - c_t`.
- Linearly increasing costs can produce interior optima.
- Costs that rise and saturate can restore the late-stage push-through effect.
