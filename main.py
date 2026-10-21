"""Run the original notebook workflow as a modular Python pipeline."""
import argparse
from pathlib import Path
from src.data_processing import clean_and_audit
from src.feature_engineering import engineer_features_and_split
from src.training import train_models
from src.evaluation import evaluate_models
from src.visualization import create_charts
from src.reporting import save_report

ROUTES = ['M101', 'M102', 'M103']
SEED = 42
LAG_MONTHS = 2


def main():
    parser = argparse.ArgumentParser(description='MTA bus travel-time baseline')
    parser.add_argument('--csv', required=True, type=Path, help='Source segment-speed CSV')
    parser.add_argument('--out', default='bus_baseline_outputs', type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    raw, cleaned, audit, series_key, shared = clean_and_audit(args.csv, args.out, ROUTES)
    data, audit, train, val, refit, test = engineer_features_and_split(cleaned, audit, series_key, args.out, ROUTES, LAG_MONTHS)
    models, selections, configs, features, validation = train_models(train, val, refit, args.out, ROUTES, LAG_MONTHS, SEED)
    predictions, metrics, by_route, by_month, improvement = evaluate_models(test, refit, models, features, shared, selections, args.out, ROUTES, LAG_MONTHS)
    create_charts(metrics, by_route, by_month, args.out)
    archive = save_report(raw, cleaned, audit, args.csv, selections, configs, features, test, refit, improvement, metrics, args.out, LAG_MONTHS)
    print('Output archive:', archive)


if __name__ == '__main__':
    main()
