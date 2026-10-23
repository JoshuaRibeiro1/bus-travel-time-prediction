# MTA segment-speed input data

The original raw dataset is **not committed** to this repository. The pipeline currently filters for routes `M101`, `M102`, and `M103`. The source CSV may include other routes.

## Data source

- **2025 onward:** [MTA Bus Route Segment Speeds: Beginning 2025](https://data.ny.gov/d/kufs-yh3x)
- **Historical extension, optional:** [MTA Bus Route Segment Speeds: 2023–2024](https://data.ny.gov/d/58t6-89vi)

The CSV supplied with this project review is `MTA_Bus_Route_Segment_Speeds__Beginning_2025_20261023.csv`, with **189,933 records** covering **January 2025–August 2026** for M101/M102/M103. The filename includes the export date, not the end of the observations. The file's raw data have not been modified.

## Prepare the CSV

1. Download the CSV from the 2025+ source, or use the CSV already supplied in the project conversation.
2. Create the `data` folder locally if it does not exist.
3. Rename the file to `mta_segment_speeds.csv` and place it here: `data/mta_segment_speeds.csv`.
4. Run from the repository root:

```bash
python main.py --csv data/mta_segment_speeds.csv --out bus_baseline_outputs
```

You may use the original filename instead; specify that exact path with `--csv`. Don't commit large raw CSV exports to GitHub; `.gitignore` excludes them. GitHub does not fetch ignored input files automatically.

## Required columns

The pipeline normalizes spaces in headers to underscores and lowercases them. It requires these source fields:

- `Year`, `Month`, `Day of Week`, `Hour of Day`
- `Route ID`, `Direction`, `Route Type`
- `Timepoint Stop ID`, `Next Timepoint Stop ID`
- `Road Distance`, `Average Travel Time`, `Bus Trip Count`

The provided export contains these fields. See `src/data_processing.py` for validation rules.

## Before combining years

Do not blindly append 2023–2024 to 2025+ data. Check column definitions, stop identifiers, route variants, temporal coverage, units, and overlapping records first. Keep provenance of each input export. Historical data-publication delay is not verified in the current code; its two-month delay is a modeling assumption.
