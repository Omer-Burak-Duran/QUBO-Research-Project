# Large Final Benchmark Session 20260506

This is the concrete run sequence for the large final-report benchmark suite.
All commands should be run from the repository root with the Python interpreter in `.venv`.

## Output Root

Use one shared output folder:

```powershell
data/results/session-20260506-large
```

Each command creates a timestamped run folder under that session directory.

## 1. Preflight

```powershell
& ".\.venv\Scripts\python.exe" -m pytest
```

Do not continue to the benchmark commands if tests fail.

## 2. Smoke Campaign

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/large_final_report_smoke_campaign.yaml --output-dir data/results/session-20260506-large
```

This validates the large campaign schema on three representative problem cases before the full campaign.

## 3. Main Statevector Campaign

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/large_final_report_benchmark_campaign.yaml --output-dir data/results/session-20260506-large
```

This is the primary large benchmark with 31 problem cases and statevector solver comparisons.

## 4. Backend Campaign

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli run-benchmark-campaign --config configs/experiments/large_final_report_backend_campaign.yaml --output-dir data/results/session-20260506-large
```

This compares statevector, shot-based, and noisy QAOA/VQE behavior on representative cases up to 10 variables.

## 5. QAOA Initialization Studies

Run each one-problem initialization study:

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli compare-initializations --config configs/experiments/large_final_report_qaoa_init_maxcut_er8_seed11.yaml --output-dir data/results/session-20260506-large
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli compare-initializations --config configs/experiments/large_final_report_qaoa_init_maxcut_weighted_er8_seed17.yaml --output-dir data/results/session-20260506-large
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli compare-initializations --config configs/experiments/large_final_report_qaoa_init_maxcut_weighted_er10_seed17.yaml --output-dir data/results/session-20260506-large
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli compare-initializations --config configs/experiments/large_final_report_qaoa_init_mvc_er8_seed11.yaml --output-dir data/results/session-20260506-large
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli compare-initializations --config configs/experiments/large_final_report_qaoa_init_mvc_er10_seed11.yaml --output-dir data/results/session-20260506-large
```

The MVC initialization outputs should be interpreted with feasibility in mind; the main campaign remains the feasibility-adjusted source for constrained optimality ratios.

## 6. Landscape And Gradient Studies

Run each one-problem landscape study:

```powershell
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli analyze-landscape --config configs/experiments/large_final_report_landscape_maxcut_er8_seed11.yaml --output-dir data/results/session-20260506-large
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli analyze-landscape --config configs/experiments/large_final_report_landscape_maxcut_weighted_er8_seed17.yaml --output-dir data/results/session-20260506-large
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli analyze-landscape --config configs/experiments/large_final_report_landscape_mvc_er8_seed11.yaml --output-dir data/results/session-20260506-large
& ".\.venv\Scripts\python.exe" -m qubo_vqa.cli analyze-landscape --config configs/experiments/large_final_report_landscape_mvc_cycle8.yaml --output-dir data/results/session-20260506-large
```

The current landscape command supports QAOA `p = 1` grids for one problem at a time.

## Priority If Runtime Becomes Long

Keep this order:

1. main statevector campaign;
2. backend campaign;
3. MaxCut initialization studies;
4. MaxCut landscape studies;
5. MVC initialization and landscape studies.

The main statevector campaign produces the most important report tables.
