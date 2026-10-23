"""Components extracted from the original bus travel-time baseline notebook."""
import numpy as np
import pandas as pd
import joblib

def evaluate_models(test, refit, models, features, shared, selections, out, routes, lag_months):
    p = test.copy()
    route_means = refit.groupby('route_id').average_travel_time.mean()
    fallback = p.route_id.map(route_means).fillna(refit.average_travel_time.mean())
    p['Historical mean'] = p.history_mean.fillna(fallback)
    p['Historical lag'] = p[f'lag_{lag_months}'].fillna(p['Historical mean'])
    p['Pooled boosting'] = np.maximum(0,models['pooled'].predict(p[features]))
    p['Separate boosting'] = np.nan
    for route in routes:
        mask = p.route_id.eq(route)
        p.loc[mask,'Separate boosting'] = np.maximum(0,models[route].predict(p.loc[mask,features]))
    names = ['Historical mean','Historical lag','Separate boosting','Pooled boosting']
    assert p[names].notna().all().all()
    def score_table(frame, group):
        rows = []
        groups = [('ALL',frame)] if group is None else frame.groupby(group,observed=True)
        for label,g in groups:
            y = g.average_travel_time.to_numpy()
            for name in names:
                err = y-g[name].to_numpy()
                rows.append({'group':str(label),'model':name,'rows':len(g),
                  'MAE_minutes':np.mean(np.abs(err)), 'RMSE_minutes':np.sqrt(np.mean(err**2)),
                  'trip_weighted_MAE':np.average(np.abs(err),weights=g.bus_trip_count)})
        return pd.DataFrame(rows)
    metrics = score_table(p,None)
    by_route = score_table(p,'route_id')
    by_month = score_table(p,'period')
    p['candidate_shared_segment'] = p.segment_id.map(shared).fillna(0).gt(1)
    for name,table in [('metrics',metrics),('metrics_by_route',by_route),('metrics_by_month',by_month),
                       ('metrics_by_support',score_table(p,'low_support')),
                       ('metrics_by_shared_segment',score_table(p,'candidate_shared_segment'))]:
        table.to_csv(out/f'{name}.csv',index=False)
    print(metrics.round(4)); print(by_route.round(4)); print(by_month.round(4))
    maes = metrics.set_index('model').MAE_minutes
    improvement = 100*(maes['Separate boosting']-maes['Pooled boosting'])/maes['Separate boosting']
    print(f'Pooled MAE reduction relative to separate boosting: {improvement:.2f}% (negative means worse)')
    print('Best approach on this held-out period:',maes.idxmin())
    p.to_csv(out/'test_predictions.csv',index=False)
    joblib.dump({'models':models,'features':features,'lag_months':lag_months,
                 'selected_configs':selections},out/'fitted_models.joblib')
    return p, metrics, by_route, by_month, improvement

