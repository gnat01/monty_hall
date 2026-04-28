# Config Presets

This directory contains ready-to-edit JSON presets for the longer Stage 2
commands.

The idea is simple:

- open a preset
- tweak the values you want
- run it directly with `--config`

These presets are now loaded directly by the CLI.

## Files

### `config/stage2_single_landscape.json`

Repeat-averaged canonical Stage 2 labeled-prior example.

Equivalent command:

```sh
python -B src/monty_hall_heterogeneous.py door-specific-stage2 --door-priors '0.1:1,0.2:1.5,0.8:4,0.3:2,0.05:10' --trials 30000 --repeats 5 --seed 11 --output-prefix outputs/stage2_labeled
```

Direct preset run:

```sh
python -B src/monty_hall_heterogeneous.py --config config/stage2_single_landscape.json
```

### `config/stage2_family_interactive.json`

Small fast family-of-landscapes run for quick iteration.

Equivalent command:

```sh
python -B src/monty_hall_heterogeneous.py door-specific-stage2-collapse --K 5 --landscapes 6 --trials 5000 --repeats 3 --workers 4 --seed 19 --output-prefix outputs/stage2_family_interactive
```

Direct preset run:

```sh
python -B src/monty_hall_heterogeneous.py --config config/stage2_family_interactive.json
```

### `config/stage2_family_medium.json`

Default medium robustness run.

Equivalent command:

```sh
python -B src/monty_hall_heterogeneous.py door-specific-stage2-collapse --K 5 --landscapes 18 --trials 20000 --repeats 4 --seed 19 --output-prefix outputs/stage2_family
```

Direct preset run:

```sh
python -B src/monty_hall_heterogeneous.py --config config/stage2_family_medium.json
```

### `config/stage2_family_heavy.json`

Large offline batch run.

Equivalent command:

```sh
python -B src/monty_hall_heterogeneous.py door-specific-stage2-collapse --K 10 --landscapes 40 --trials 40000 --repeats 30 --workers 8 --seed 19 --output-prefix outputs/stage2_family_K10_l40_tr40000_rep30
```

Direct preset run:

```sh
python -B src/monty_hall_heterogeneous.py --config config/stage2_family_heavy.json
```

## Suggested Workflow

1. Start from the preset closest to the run you want.
2. Edit only the fields you care about.
3. Run it with `python -B src/monty_hall_heterogeneous.py --config ...`
4. If needed, override individual values on the command line.

Example:

```sh
python -B src/monty_hall_heterogeneous.py --config config/stage2_family_medium.json --landscapes 24 --workers 8
```
