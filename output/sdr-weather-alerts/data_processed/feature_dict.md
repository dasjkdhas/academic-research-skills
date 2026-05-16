# Feature Dictionary

Generated at 2026-05-16 10:10:43.722414

Shape after lag dropping: (2313, 68)

Period: 2025-07-13 00:00:00 → 2025-10-26 23:00:00


## Path A vs Path B Day-Type Agreement

- Adjusted Rand Index: **0.336**
- Normalized Mutual Info: **0.484**
- Path A classes (manual): {'exam_week_spring': 0, 'national_holiday': 1, 'obon_break': 2, 'regular_term_fall': 3, 'regular_term_spring': 4, 'summer_break': 5, 'weekend': 6}
- Path B clusters (K-Means, K=5): {0: 39, 1: 26, 2: 1, 3: 2, 4: 47}


## Features by group

- `b00`  (float64)  mean=842.8069606571552
- `b01`  (float64)  mean=210.88261997405965
- `b02`  (float64)  mean=19.730912235192392
- `b04`  (float64)  mean=26.103329009943796
- `b05`  (float64)  mean=60.4452010376135
- `b06`  (float64)  mean=22.707306528318203
- `b07`  (float64)  mean=274.79809770860356
- `b08`  (float64)  mean=9.336165153480326
- `b09`  (float64)  mean=4.156895806312149
- `b10`  (float64)  mean=29.611910938175534
- `b11`  (float64)  mean=41.665045395590155
- `b12`  (float64)  mean=51.08761348897536
- `b13`  (float64)  mean=33.21424556852572
- `b14`  (float64)  mean=3.431906614785992
- `b15`  (float64)  mean=5.340034587116299
- `temperature_2m`  (float64)  mean=26.57302204928664
- `relative_humidity_2m`  (int64)  mean=77.26070038910505
- `dew_point_2m`  (float64)  mean=22.01837440553394
- `apparent_temperature`  (float64)  mean=30.31206225680934
- `precipitation`  (float64)  mean=0.2196714223951578
- `wind_speed_10m`  (float64)  mean=10.786338089061823
- `wind_direction_10m`  (int64)  mean=170.5278858625162
- `surface_pressure`  (float64)  mean=1011.0942498919153
- `cloud_cover`  (int64)  mean=50.27453523562473
- `shortwave_radiation`  (float64)  mean=212.23476005188067
- `wbgt_approx`  (float64)  mean=29.605715312586504
- `heat_alert_level`  (int64)  mean=3.0423692174664936
- `dow`  (int64)  mean=3.063553826199741
- `dow_name`  (str)  mean=n/a
- `day_type`  (str)  mean=n/a
- `is_class_day`  (int64)  mean=0.3320363164721141
- `holiday_name`  (str)  mean=n/a
- `hour`  (int32)  mean=11.470817120622568
- `dow_int`  (int32)  mean=3.063553826199741
- `month`  (int32)  mean=8.553826199740596
- `day_of_year`  (int32)  mean=244.28534370946824
- `week_of_year`  (int64)  mean=35.60311284046693
- `is_weekend`  (int64)  mean=0.29442282749675747
- `hour_sin`  (float64)  mean=0.002650163547961972
- `hour_cos`  (float64)  mean=0.0015300726378123335
- `dow_sin`  (float64)  mean=-0.01115453476932339
- `dow_cos`  (float64)  mean=-0.01441951881879856
- `month_sin`  (float64)  mean=-0.8221888250657637
- `month_cos`  (float64)  mean=-0.1966742689691762
- `dow_hour`  (int32)  mean=317.8261997405966
- `day_type_id_A`  (int64)  mean=4.277561608300908
- `day_type_id_B`  (int64)  mean=1.946822308690013
- `b00_lag1`  (float64)  mean=842.9747081712062
- `b00_lag2`  (float64)  mean=843.1549935149156
- `b00_lag3`  (float64)  mean=843.3456549935149
- `b00_lag6`  (float64)  mean=844.1156506701254
- `b00_lag12`  (float64)  mean=846.5639861651534
- `b00_lag24`  (float64)  mean=848.1947686986598
- `b00_lag48`  (float64)  mean=854.5341547773454
- `b00_lag168`  (float64)  mean=861.9781668828361
- `b00_roll24_mean`  (float64)  mean=846.1241173079695
- `b00_roll24_std`  (float64)  mean=203.5432624799667
- `b00_roll168_mean`  (float64)  mean=857.6353890021204
- `temp_lag24`  (float64)  mean=26.645827929096413
- `temp_lag168`  (float64)  mean=27.173584089926504
- `wbgt_lag1`  (float64)  mean=29.608897245507254
- `cdh_20`  (float64)  mean=6.714699524427151
- `hdh_18`  (float64)  mean=0.04055339386078686
- `heat_alert_ge2`  (int64)  mean=0.8715953307392996
- `heat_alert_ge3`  (int64)  mean=0.7518374405533939
- `heat_alert_ge4`  (int64)  mean=0.4708171206225681
- `y`  (float64)  mean=842.8069606571552
- `y_peak`  (int64)  mean=0.043233895373973194