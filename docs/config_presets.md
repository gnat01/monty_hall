# Config Presets

This directory contains ready-to-edit JSON presets for the longer Stage 2
commands.

The idea is simple:

- open a preset
- tweak the values you want
- run the matching command

These are not loaded automatically by the current CLI. They are plain reference
files so you do not have to keep reconstructing long command lines.

## Files

### `config/stage2_single_landscape.json`

Repeat-averaged canonical Stage 2 labeled-prior example.

Equivalent command:

```sh
python -B src/monty_hall_heterogeneous.py door-specific-stage2 --door-priors '0.1:1,0.2:1.5,0.8:4,0.3:2,0.05:10' --trials 30000 --repeats 5 --seed 11 --output-prefix outputs/stage2_labeled
```

### `config/stage2_family_interactive.json`

Small fast family-of-landscapes run for quick iteration.

Equivalent command:

```sh
python -B src/monty_hall_heterogeneous.py door-specific-stage2-collapse --K 5 --landscapes 6 --trials 5000 --repeats 3 --workers 4 --seed 19 --output-prefix outputs/stage2_family_interactive
```

### `config/stage2_family_medium.json`

Default medium robustness run.

Equivalent command:

```sh
python -B src/monty_hall_heterogeneous.py door-specific-stage2-collapse --K 5 --landscapes 18 --trials 20000 --repeats 4 --seed 19 --output-prefix outputs/stage2_family
```

### `config/stage2_family_heavy.json`

Large offline batch run.

Equivalent command:

```sh
python -B src/monty_hall_heterogeneous.py door-specific-stage2-collapse --K 10 --landscapes 40 --trials 40000 --repeats 30 --workers 8 --seed 19 --output-prefix outputs/stage2_family_K10_l40_tr40000_rep30
```

## Suggested Workflow

1. Start from the preset closest to the run you want.
2. Edit only the fields you care about.
3. Copy the values into the matching CLI command from `how_to_run.md`.

If we want later, the next step is to add actual `--config` loading to the
Monty Hall CLI the same way we did in the colliding-bandits repo.
