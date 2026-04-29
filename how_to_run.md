# How To Run

## Quick Index

- Part I baseline simulator:
  `src/monty_hall_generalised.py`
- Part I conditional switching:
  `src/monty_hall_clean_conditional_switching.py`
- Part II variable costs:
  `src/monty_hall_variable_costs.py`
- Part III / IV heterogeneous rewards:
  `src/monty_hall_heterogeneous.py`
- Legacy fixed-parameter scripts:
  `src/monty_hall_clean.py`
  `src/monty_hall_and_others.py`
- Paper figure generators:
  `monty_hall_paper/generate_plots.py`
  `monty_hall_paper/generate_plots_with_multik.py`
  `monty_hall_paper_ii/generate_plots.py`
  `monty_hall_paper_iii/generate_plots.py`

Run all commands from the project root:

```sh
cd /Users/gn/work/learn/python/monty_hall
```

Use `MPLCONFIGDIR=.mplconfig` with plotting commands so Matplotlib writes its
font cache inside the project.

Preset JSONs for the longer Stage 2 runs live in:

```text
config/
```

And their explanations are in:

```text
docs/config_presets.md
```

You can run them directly with:

```sh
python -B src/monty_hall_heterogeneous.py --config config/stage2_family_medium.json
```

Any flags you add after `--config` override the preset.

## Tests

Run the full Python test suite:

```sh
MPLCONFIGDIR=.mplconfig python -B -m unittest discover -s src
```

## Part I: Generalized Monty Hall

Help:

```sh
python -B src/monty_hall_generalised.py --help
python -B src/monty_hall_clean_conditional_switching.py --help
```

Run the generalized simulator:

```sh
python -B src/monty_hall_generalised.py --K 10 --m 3 --r 4 --experiments 1000 --chances 500 --seed 1 --plot
```

Flags for `monty_hall_generalised.py`:

- `--K`, `--k`
  number of doors
  default: `3`
- `--m`
  number of prize doors
  default: `1`
- `--r`
  number of losing doors opened
  default: `1`
- `--experiments`
  outer simulation runs
  default: `10000`
- `--chances`
  trials per experiment
  default: `100`
- `--seed`
  RNG seed
  default: unset
- `--plot`
  save the theory-vs-empirical plot
- `--demo`
  run the original demonstration cases

Run the conditional-switching simulator:

```sh
python -B src/monty_hall_clean_conditional_switching.py --K 8 --m 2 --r 3 --experiments 1000 --chances 500 --seed 2 --switch-probability 0.35 --plot
```

Flags for `monty_hall_clean_conditional_switching.py`:

- `--K`, `--k`
  number of doors
  default: `5`
- `--m`
  number of prize doors
  default: `1`
- `--r`
  number of losing doors opened
  default: `1`
- `--experiments`
  outer simulation runs
  default: `1000`
- `--chances`
  trials per experiment
  default: `100`
- `--switch-probability`
  probability of switching in the conditional strategy
  if omitted, the script uses its built-in default rule
- `--seed`
  RNG seed
  default: unset
- `--plot`
  save the histogram plot

Generated simulator plots are written to:

```text
outputs/
```

### Legacy Fixed-Parameter Part I Scripts

These older scripts do not expose a configurable CLI. They run with built-in
settings and write outputs to `outputs/`.

Run the clean fixed-parameter simulator:

```sh
python -B src/monty_hall_clean.py
```

Built-in settings:

- `n_experiments = 1000`
- `n_chances = 1000`
- `num_doors = 4`

Main output:

- `outputs/clean_switch_vs_stay.png`

Run the exploratory mixed script:

```sh
python -B src/monty_hall_and_others.py
```

This script runs:

- a toy path plot
- a membership-key demo
- a Rademacher sampling demo
- a classical Monty Hall switch-vs-stay simulation

Main outputs:

- `outputs/and_others_path_plot.png`
- `outputs/and_others_monty_hist.png`

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

Help:

```sh
python -B src/monty_hall_variable_costs.py --help
```

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

Flags for `monty_hall_variable_costs.py`:

- `--K`, `--k`
  number of doors
  default: `50`
- `--m`
  number of prize doors
  default: `1`
- `--kind`
  one of:
  `constant`, `linear`, `saturating`, `linear_saturating`
  default: `linear`
- `--base`
  base reveal cost level
  default: `0.002`
- `--slope`
  linear slope parameter
  default: `0.0004`
- `--saturation`
  saturation cap parameter
  default: unset
- `--tau`
  saturation timescale parameter
  default: unset
- `--csv`
  optional output CSV path

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

General help:

```sh
python -B src/monty_hall_heterogeneous.py --help
```

Subcommand help:

```sh
python -B src/monty_hall_heterogeneous.py exchangeable --help
python -B src/monty_hall_heterogeneous.py door-specific --help
python -B src/monty_hall_heterogeneous.py find-sacrifice --help
python -B src/monty_hall_heterogeneous.py exchangeable-stage1 --help
python -B src/monty_hall_heterogeneous.py door-specific-stage2 --help
python -B src/monty_hall_heterogeneous.py door-specific-stage2-collapse --help
```

Global option:

- `--config PATH`
  optional JSON preset file
  CLI flags written after `--config` override the preset values

Run the exchangeable reward-multiset model:

```sh
python -B src/monty_hall_heterogeneous.py exchangeable --K 12 --m 4 --r 4 --reward-dist lognormal --trials 100000 --seed 3
```

Flags for `exchangeable`:

- `--K`, `--k`
  number of doors
  default: `10`
- `--m`
  number of positive-reward prize doors
  default: `3`
- `--r`
  number of zero-door reveals
  default: `2`
- `--reward-dist`
  one of:
  `fixed`, `uniform`, `exponential`, `lognormal`, `pareto`
  default: `lognormal`
- `--reward-values`
  optional explicit comma-separated unequal positive prize values
  if set, must have length `m`
- `--trials`
  Monte Carlo trials
  default: `100000`
- `--seed`
  RNG seed
  default: unset

Run the exchangeable unequal-prize Stage IV baseline with explicit reward values:

```sh
python -B src/monty_hall_heterogeneous.py exchangeable --K 12 --m 4 --r 4 --reward-values 1,2,5,9 --trials 100000 --seed 3
```

Run the full Stage IV exchangeable analysis with tables and collapse plots:

```sh
python -B src/monty_hall_heterogeneous.py exchangeable-stage1 --K 12 --m 4 --reward-vectors '1,2,5,9;4,4,4,5;8,4,3,2' --trials 100000 --seed 3 --output-prefix outputs/stage1_exchangeable
```

Run the door-specific Bernoulli-value prior model:

```sh
python -B src/monty_hall_heterogeneous.py door-specific --K 10 --r 2 --trials 100000 --seed 4 --initial lowest_mu --monty uniform_zero --plot
```

Flags for `door-specific`:

- `--K`, `--k`
  number of doors
  default: `10`
- `--r`
  reveal count
  default: `2`
- `--trials`
  Monte Carlo trials
  default: `100000`
- `--seed`
  RNG seed
  default: unset
- `--initial`
  one of:
  `random`, `highest_mu`, `lowest_mu`
  default: `random`
- `--monty`
  one of:
  `uniform_zero`, `low_mu_zero`, `high_mu_zero`
  default: `uniform_zero`
- `--plot`
  save the bar plot for that run
- `--door-priors`
  optional explicit comma-separated `p:v` pairs
  where `p` is prize probability and `v` is reward value

Run the same model with explicit labeled priors, where each pair is `p:v` and
means `prize probability : reward value`:

```sh
python -B src/monty_hall_heterogeneous.py door-specific --K 5 --r 2 --trials 100000 --seed 4 --initial random --monty uniform_zero --door-priors '0.1:1,0.2:1.5,0.8:4,0.3:2,0.05:10' --plot
```

Search for a sacrifice-initial-choice example:

```sh
python -B src/monty_hall_heterogeneous.py find-sacrifice --K 4 --r 1 --tries 100 --trials 20000 --seed 5
```

Flags for `find-sacrifice`:

- `--K`, `--k`
  number of doors
  default: `4`
- `--r`
  reveal count
  default: `1`
- `--tries`
  number of randomly sampled prior landscapes
  default: `200`
- `--trials`
  Monte Carlo trials per evaluation
  default: `20000`
- `--seed`
  RNG seed
  default: unset

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

The Stage 1 analysis command writes:

- `..._curve_table.csv`
- `..._theory_vs_empirical.png`
- `..._collapse_table.csv`
- `..._same_v_collapse.png`
- `..._normalized_collapse.png`

Flags for `exchangeable-stage1`:

- `--K`, `--k`
  required
  number of doors
- `--m`
  required
  number of positive-reward prize doors
- `--reward-vectors`
  required
  semicolon-separated reward vectors, each vector comma-separated
  example:
  `'1,2,5,9;4,4,4,5;8,4,3,2'`
- `--trials`
  Monte Carlo trials per reveal-depth run
  default: `100000`
- `--seed`
  RNG seed
  default: unset
- `--output-prefix`
  output prefix
  default: `outputs/stage1_exchangeable`

Build the Part IV paper:

```sh
cd monty_hall_paper_iv
make
```

Main output:

```text
monty_hall_paper_iv/monty_iv.pdf
```

The Part IV paper now directly includes the Stage 1 figures from `outputs/`:

- `stage1_exchangeable_theory_vs_empirical.png`
- `stage1_exchangeable_same_v_collapse.png`
- `stage1_exchangeable_normalized_collapse.png`

So the standard Part IV workflow is:

```sh
python -B src/monty_hall_heterogeneous.py exchangeable-stage1 --K 12 --m 4 --reward-vectors '1,2,5,9;4,4,4,5;8,4,3,2' --trials 100000 --seed 3 --output-prefix outputs/stage1_exchangeable
cd monty_hall_paper_iv
make
```

Run the Stage 2 labeled unequal-prize analysis:

```sh
python -B src/monty_hall_heterogeneous.py door-specific-stage2 --door-priors '0.1:1,0.2:1.5,0.8:4,0.3:2,0.05:10' --trials 30000 --repeats 5 --seed 11 --output-prefix outputs/stage2_labeled
```

The Stage 2 analysis command writes:

- `..._priors.csv`
- `..._strategy_repeats.csv`
- `..._strategy_table.csv`
- `..._prior_landscape.png`
- `..._strategy_panel.png`
- `..._monty_panel.png`
- `..._policy_gain_heatmap.png`
- `..._partial_collapse.png`

The `..._strategy_table.csv` file is repeat-averaged. The optional
`..._strategy_repeats.csv` file contains the raw per-seed runs that feed the
average.

Flags for `door-specific-stage2`:

- `--door-priors`
  required
  comma-separated `p:v` pairs
  example:
  `'0.1:1,0.2:1.5,0.8:4,0.3:2,0.05:10'`
- `--r-values`
  optional comma-separated reveal counts
  default: `0..K-2`
  where `K` is inferred from the number of door priors
- `--trials`
  Monte Carlo trials per repeat
  default: `100000`
- `--repeats`
  number of independent RNG runs to average
  default: `1`
- `--seed`
  RNG seed
  default: unset
- `--output-prefix`
  output prefix
  default: `outputs/stage2_door_specific`

Run the stronger family-of-landscapes partial-collapse experiment:

```sh
python -B src/monty_hall_heterogeneous.py door-specific-stage2-collapse --K 5 --landscapes 18 --trials 20000 --repeats 4 --seed 19 --output-prefix outputs/stage2_family
```

This writes:

- `..._landscapes.csv`
- `..._collapse_table.csv`
- `..._partial_collapse_family.png`

The Part IV paper uses this robustness figure as well:

- `stage2_family_partial_collapse_family.png`

The family command also supports:

- `--workers 1`
  run sequentially
- `--workers 0`
  or omit the flag to auto-use available CPU cores
- `--workers N`
  force a specific number of worker processes

The landscape sweep parallelizes over landscapes. The inner trial work is also
NumPy-vectorized, so this command is now much faster than the original pure
Python version.

Flags for `door-specific-stage2-collapse`:

- `--K`, `--k`
  number of doors
  default: `5`
- `--r-values`
  optional comma-separated reveal counts
  default: `0..K-2`
- `--landscapes`
  number of sampled labeled prior landscapes
  default: `18`
- `--trials`
  Monte Carlo trials per repeat per landscape slice
  default: `40000`
- `--repeats`
  repeat count per landscape
  default: `4`
- `--seed`
  RNG seed
  default: unset
- `--q-alpha`
  Beta-shape parameter for zero-prob sampling
  default: `2.0`
- `--q-beta`
  Beta-shape parameter for zero-prob sampling
  default: `2.0`
- `--log-mu`
  lognormal location for reward-value sampling
  default: `0.0`
- `--log-sigma`
  lognormal scale for reward-value sampling
  default: `1.0`
- `--workers`
  worker processes
  `0` means auto
  default: `0`
- `--output-prefix`
  output prefix
  default: `outputs/stage2_family`

## Stage 2 Presets

### Interactive

Use this when you want a quick look and do not want to wait:

```sh
python -B src/monty_hall_heterogeneous.py door-specific-stage2-collapse --K 5 --landscapes 6 --trials 5000 --repeats 3 --workers 4 --seed 19 --output-prefix outputs/stage2_family_interactive
```

### Medium

Use this for a decent robustness pass without turning it into a long batch job:

```sh
python -B src/monty_hall_heterogeneous.py door-specific-stage2-collapse --K 5 --landscapes 18 --trials 20000 --repeats 4 --seed 19 --output-prefix outputs/stage2_family
```

### Heavy

Use this when you want the stronger offline run:

```sh
python -B src/monty_hall_heterogeneous.py door-specific-stage2-collapse --K 10 --landscapes 40 --trials 40000 --repeats 30 --workers 8 --seed 19 --output-prefix outputs/stage2_family_K10_l40_tr40000_rep30
```

### Canonical Repeat-Averaged Single Landscape

Use this when you want the Stage 2 paper example, averaged over several RNG
seeds for one fixed labeled prior landscape:

```sh
python -B src/monty_hall_heterogeneous.py door-specific-stage2 --door-priors '0.1:1,0.2:1.5,0.8:4,0.3:2,0.05:10' --trials 30000 --repeats 5 --seed 11 --output-prefix outputs/stage2_labeled
```

The Part IV paper now also uses these Stage 2 labeled-prior figures:

- `stage2_labeled_prior_landscape.png`
- `stage2_labeled_strategy_panel.png`
- `stage2_labeled_policy_gain_heatmap.png`
- `stage2_labeled_partial_collapse.png`

So the standard full Part IV workflow is:

```sh
python -B src/monty_hall_heterogeneous.py exchangeable-stage1 --K 12 --m 4 --reward-vectors '1,2,5,9;4,4,4,5;8,4,3,2' --trials 100000 --seed 3 --output-prefix outputs/stage1_exchangeable
python -B src/monty_hall_heterogeneous.py door-specific-stage2 --door-priors '0.1:1,0.2:1.5,0.8:4,0.3:2,0.05:10' --trials 30000 --repeats 5 --seed 11 --output-prefix outputs/stage2_labeled
python -B src/monty_hall_heterogeneous.py door-specific-stage2-collapse --K 5 --landscapes 18 --trials 20000 --repeats 4 --seed 19 --output-prefix outputs/stage2_family
cd monty_hall_paper_iv
make
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

Clean Part III LaTeX artifacts:

```sh
cd monty_hall_paper_iii
make clean
```

Clean Part IV LaTeX artifacts:

```sh
cd monty_hall_paper_iv
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
- Part IV Stage 1 shows that unequal prize vectors with the same total reward mass `V` collapse empirically under exchangeability.
- Part IV Stage 2 shows that once door labels carry priors, initial choice and switch rule interact strongly and the scalar collapse disappears.
- Part IV Stage 2 also includes a weaker partial-collapse diagnostic, normalized by the oracle switch value, to explore whether any class-dependent rescaling survives after label symmetry is broken.
- The repeat-averaged and family-of-landscapes Stage 2 runs are the robust versions of that partial-collapse test.
- The family Stage 2 command is now both NumPy-vectorized and parallelized over landscapes, so `--workers` is the main runtime control knob after `landscapes`, `trials`, and `repeats`.
