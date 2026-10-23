"""Components extracted from the original bus travel-time baseline notebook."""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error

def train_models(train, val, refit, out, routes, lag_months, seed):
    categorical = ['route_id','direction','route_type','segment_id','day_of_week']
    numeric = ['hour_of_day','month_sin','month_cos','month_index','historical_distance',
               'history_mean','history_count'] + [f'lag_{k}' for k in [lag_months,lag_months+1,lag_months+2]]
    features = categorical + numeric
    assert not set(features) & {'average_travel_time','average_road_speed','bus_trip_count','road_distance'}
    configs = [dict(max_leaf_nodes=15,l2_regularization=10.0),
               dict(max_leaf_nodes=31,l2_regularization=10.0)]
    def make_model(config):
        prep = ColumnTransformer([
            ('category', OneHotEncoder(handle_unknown='ignore',sparse_output=False),categorical),
            ('number', SimpleImputer(strategy='median',add_indicator=True,keep_empty_features=True),numeric)
        ])
        model = HistGradientBoostingRegressor(learning_rate=0.08,max_iter=150,
                 min_samples_leaf=30,early_stopping=False,random_state=seed,**config)
        return Pipeline([('prepare',prep),('model',model)])
    models, selections, validation_rows = {}, {}, []
    for scope in ['pooled'] + routes:
        tr = train if scope == 'pooled' else train[train.route_id.eq(scope)]
        va = val if scope == 'pooled' else val[val.route_id.eq(scope)]
        scores = []
        for i, config in enumerate(configs):
            model = make_model(config)
            model.fit(tr[features],tr.average_travel_time)
            pred = np.maximum(0,model.predict(va[features]))
            score = mean_absolute_error(va.average_travel_time,pred)
            scores.append(score)
            validation_rows.append({'scope':scope,'configuration':i,'validation_MAE':score})
        best = int(np.argmin(scores))
        selections[scope] = best
        fit = refit if scope == 'pooled' else refit[refit.route_id.eq(scope)]
        models[scope] = make_model(configs[best]).fit(fit[features],fit.average_travel_time)
        print(scope,'selected configuration',best,'validation MAE',round(scores[best],3))
    validation_results = pd.DataFrame(validation_rows)
    validation_results.to_csv(out/'validation_results.csv',index=False)
    return models, selections, configs, features, validation_results

