"""Components extracted from the original bus travel-time baseline notebook."""
import hashlib
import json
import shutil
from pathlib import Path
import pandas as pd
import sklearn

def save_report(raw, d, audit, csv_path, selections, configs, features, test, refit, improvement, metrics, out, lag_months):
    metadata = {'audit':audit,'source_sha256':hashlib.sha256(Path(csv_path).read_bytes()).hexdigest(),
        'lag_months':lag_months,'selected_configurations':selections,'configurations':configs,
        'features':features,'test_months':[str(x) for x in sorted(test.period.unique())],
        'refit_last_month':str(refit.period.max()),'sklearn_version':sklearn.__version__,
        'pandas_version':pd.__version__, 'pooled_MAE_reduction_percent':float(improvement),
        'publication_timing':'Retrospective two-month availability assumption; actual release dates unverified.'}
    (out/'run_metadata.json').write_text(json.dumps(metadata,indent=2))
    summary = (f"Source rows: {len(raw):,}; cleaned rows: {len(d):,}.\n"
               f"Ambiguous rows quarantined: {audit['ambiguous_rows_quarantined']:,}.\n"
               f"Test period: {test.period.min()} to {test.period.max()}; {len(test):,} rows.\n\n"
               +metrics.to_string(index=False)+f"\n\nPooled reduction vs separate: {improvement:.2f}%.\n"
               +"Descriptive retrospective results; no causal claim. Actual publication timing unverified.\n")
    (out/'RESULTS.txt').write_text(summary)
    archive = shutil.make_archive(str(out.parent / 'bus_baseline_results'), 'zip', out)
    print(summary)
    print('Saved:',archive)
    return archive

