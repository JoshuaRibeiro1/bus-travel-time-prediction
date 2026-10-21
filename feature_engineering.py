"""Components extracted from the original bus travel-time baseline notebook."""
import numpy as np
import pandas as pd

def engineer_features_and_split(d, audit, series_key, OUT, ROUTES, LAG_MONTHS):
    data = d.copy()
    for lag in [LAG_MONTHS, LAG_MONTHS+1, LAG_MONTHS+2]:
        hist = d[series_key + ['month_index','average_travel_time']].copy()
        hist['month_index'] += lag
        hist = hist.rename(columns={'average_travel_time':f'lag_{lag}'})
        data = data.merge(hist, on=series_key+['month_index'], how='left', validate='one_to_one')
    # Shift past expanding statistics forward to the earliest permitted target month.
    parts = []
    for _, g in d.groupby(series_key, sort=False):
        g = g.sort_values('month_index').copy()
        g['history_mean'] = g.average_travel_time.expanding().mean()
        g['historical_distance'] = g.road_distance.expanding().mean()
        g['history_count'] = np.arange(1,len(g)+1)
        g['available_month'] = g.month_index + LAG_MONTHS
        parts.append(g[series_key+['available_month','history_mean','historical_distance','history_count']])
    h = pd.concat(parts, ignore_index=True)
    data = pd.merge_asof(data.sort_values('month_index'), h.sort_values('available_month'),
                         left_on='month_index', right_on='available_month', by=series_key,
                         direction='backward')
    assert (data.available_month.dropna() <= data.loc[data.available_month.notna(),'month_index']).all()
    data['month_sin'] = np.sin(2*np.pi*data.month/12)
    data['month_cos'] = np.cos(2*np.pi*data.month/12)
    data = data.sort_values(['month_index']+series_key).reset_index(drop=True)
    # First months cannot supply supervised examples with any eligible history.
    eligible = data.history_count.notna()
    audit['rows_without_eligible_history'] = int((~eligible).sum())
    data = data.loc[eligible].copy()
    months = sorted(data.month_index.unique())
    if len(months) < 10:
        raise ValueError('Need at least 10 usable target months for these held-out splits.')
    test_months = months[-3:]
    first_test = min(test_months)
    refit_end = first_test-LAG_MONTHS
    val_months = [refit_end-2, refit_end-1]
    train_end = min(val_months)-LAG_MONTHS
    train = data[data.month_index <= train_end].copy()
    val = data[data.month_index.isin(val_months)].copy()
    refit = data[data.month_index <= refit_end].copy()
    test = data[data.month_index.isin(test_months)].copy()
    for name, frame in [('train',train),('validation',val),('refit',refit),('test',test)]:
        assert len(frame) and set(ROUTES).issubset(frame.route_id.unique()), name
        print(name, str(frame.period.min()), 'to', str(frame.period.max()), 'rows:', len(frame))
    assert train.month_index.max() <= val.month_index.min()-LAG_MONTHS
    assert refit.month_index.max() <= test.month_index.min()-LAG_MONTHS
    print('Test rows with exact lag:', round(test[f'lag_{LAG_MONTHS}'].notna().mean()*100,2),'%')
    data.to_csv(OUT/'modeling_data.csv', index=False)
    return data, audit, train, val, refit, test

