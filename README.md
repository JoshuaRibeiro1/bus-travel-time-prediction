# Dataset location

Place the original filtered MTA segment-speed CSV in this folder, for example `data/mta_segment_speeds.csv`.

The dataset is **not distributed** with this repository. The notebook requires these columns:

`year`, `month`, `day_of_week`, `hour_of_day`, `route_id`, `direction`, `route_type`, `timepoint_stop_id`, `next_timepoint_stop_id`, `road_distance`, `average_travel_time`, `bus_trip_count`.

The analysis filters to M101, M102, and M103. Do not commit raw data or generated files without confirming permission to redistribute them.
