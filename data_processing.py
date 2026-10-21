"""Components extracted from the original bus travel-time baseline notebook."""
import numpy as np
import pandas as pd

def clean_and_audit(CSV_PATH, OUT, ROUTES):
    raw = pd.read_csv(CSV_PATH, dtype=str)
    raw.columns = raw.columns.str.strip().str.lower().str.replace(r'\s+', '_', regex=True)
    required = ['year','month','day_of_week','hour_of_day','route_id','direction','route_type',
                'timepoint_stop_id','next_timepoint_stop_id','road_distance',
                'average_travel_time','bus_trip_count']
    missing = sorted(set(required) - set(raw.columns))
    if missing:
        raise ValueError(f'Missing required columns: {missing}')
    raw['source_row'] = np.arange(len(raw)) + 2
    for col in required:
        raw[col] = raw[col].str.strip()
    raw['route_id'] = raw.route_id.str.upper()
    d = raw[raw.route_id.isin(ROUTES)].copy()
    audit = {'source_rows': len(raw), 'selected_route_rows': len(d)}
    source_cols = [c for c in d.columns if c != 'source_row']
    exact = d.duplicated(source_cols)
    audit['exact_duplicates_removed'] = int(exact.sum())
    d.loc[exact].to_csv(OUT/'exact_duplicates.csv', index=False)
    d = d.loc[~exact].copy()
    nums = ['year','month','hour_of_day','road_distance','average_travel_time','bus_trip_count']
    for col in nums:
        d[col] = pd.to_numeric(d[col], errors='coerce')
    for col in ['timepoint_stop_id','next_timepoint_stop_id']:
        d[col] = d[col].str.replace(r'\.0$', '', regex=True)
    d['day_of_week'] = d.day_of_week.str.title()
    d['direction'] = d.direction.str.upper()
    weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    valid = d[required].notna().all(axis=1) & np.isfinite(d[nums]).all(axis=1)
    valid &= d.month.between(1,12) & d.hour_of_day.between(0,23)
    valid &= d.year.between(2000,2100)
    for col in ['year','month','hour_of_day','bus_trip_count']:
        valid &= d[col].eq(d[col].round())
    valid &= d.day_of_week.isin(weekdays) & d.direction.isin(['N','S','E','W'])
    valid &= (d[['road_distance','average_travel_time','bus_trip_count']] > 0).all(axis=1)
    valid &= d.timepoint_stop_id.ne(d.next_timepoint_stop_id)
    for col in ['route_type','timepoint_stop_id','next_timepoint_stop_id']:
        valid &= d[col].ne('')
    d.loc[~valid].to_csv(OUT/'invalid_rows.csv', index=False)
    audit['invalid_rows_removed'] = int((~valid).sum())
    d = d.loc[valid].copy()
    for col in ['year','month','hour_of_day','bus_trip_count']:
        d[col] = d[col].astype(int)
    series_key = ['route_id','direction','route_type','timepoint_stop_id',
                  'next_timepoint_stop_id','day_of_week','hour_of_day']
    key = ['year','month'] + series_key
    ambiguous = d.duplicated(key, keep=False)
    d.loc[ambiguous].to_csv(OUT/'ambiguous_groups.csv', index=False)
    audit['ambiguous_rows_quarantined'] = int(ambiguous.sum())
    audit['ambiguous_groups'] = len(d.loc[ambiguous,key].drop_duplicates())
    d = d.loc[~ambiguous].copy()
    d['period'] = pd.PeriodIndex(year=d.year, month=d.month, freq='M')
    d['month_index'] = d.year*12 + d.month
    # No same-period observed speed, trip count or distance is passed as a model predictor.
    d['low_support'] = d.bus_trip_count < 5
    d['segment_id'] = d.timepoint_stop_id + '>' + d.next_timepoint_stop_id + ':' + d.direction
    assert not d.duplicated(key).any()
    audit['clean_rows'] = len(d)
    audit['low_support_rows_retained'] = int(d.low_support.sum())
    d.sort_values(key).to_csv(OUT/'cleaned_data.csv', index=False)
    print(pd.Series(audit, name='count').to_frame())
    coverage = d.groupby(['period','route_id']).size().unstack(fill_value=0)
    coverage.to_csv(OUT/'coverage.csv')
    print(coverage)
    print(d.groupby('route_id')[['average_travel_time','bus_trip_count']].agg(['min','median','max']))
    segment_coverage = d.groupby(['period','route_id']).segment_id.nunique().unstack(fill_value=0)
    segment_coverage.to_csv(OUT/'segment_coverage.csv')
    shared = d[['segment_id','route_id']].drop_duplicates().groupby('segment_id').route_id.nunique()
    print('Endpoint/direction pairs present on multiple routes:', int((shared > 1).sum()))
    print('These are candidate shared segments, not verified identical road paths.')
    return raw, d, audit, series_key, shared

