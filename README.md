# Running the code

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

## Run

```powershell
python run_all.py --list
python run_all.py
```

To run one experiment group:

```powershell
python run_all.py --section s1
python run_all.py --section s2
python run_all.py --section s3
python run_all.py --section s4
```

Experiments use synthetic reflectances by default. To download Foster hyperspectral
data before running:

```powershell
python -m src.fetch_foster --n 8
```

Results are written to `results/`. Set output and device options before running:

```powershell
$env:RESULTS_DIR = ".\results"
$env:DEVICE = "cpu"
python run_all.py
```

## Run with Docker

```powershell
docker build -t color-vision .
docker run --rm -v "${PWD}/results:/work/results" color-vision
```
