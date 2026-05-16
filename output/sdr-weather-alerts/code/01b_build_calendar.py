"""Step 1b: Build synthetic calendar.csv for Yamaguchi University academic year.

Yamaguchi University standard academic calendar (令和7年度 = 2025-04 to 2026-03):
  前期 (Spring term)      : 2025-04-09 → 2025-08-04
  前期試験 (final exams)   : 2025-07-28 → 2025-08-04 (overlapped — exams during last week)
  夏季休業 (Summer break)  : 2025-08-05 → 2025-09-30
  後期 (Fall term)         : 2025-10-01 → 2026-02-15
  後期試験 (final exams)   : 2026-02-02 → 2026-02-15

Japanese national holidays 2025 (mid-year onwards):
  2025-07-21 (Mon) 海の日 Marine Day
  2025-08-11 (Mon) 山の日 Mountain Day
  2025-09-15 (Mon) 敬老の日 Respect for the Aged Day
  2025-09-23 (Tue) 秋分の日 Autumnal Equinox Day
  2025-10-13 (Mon) スポーツの日 Sports Day
"""
import os
import pandas as pd

OUT_DIR = "/home/user/academic-research-skills/output/sdr-weather-alerts/data_processed"
os.makedirs(OUT_DIR, exist_ok=True)

START = "2025-07-06"
END   = "2025-10-31"

# Term windows
SPRING_TERM   = ("2025-04-09", "2025-07-27")   # regular spring classes
EXAM_WEEK_S   = ("2025-07-28", "2025-08-04")   # spring final exams
SUMMER_BREAK  = ("2025-08-05", "2025-09-30")
FALL_TERM     = ("2025-10-01", "2026-02-01")   # regular fall classes

# 2025 Japanese national holidays in our window
HOLIDAYS = {
    "2025-07-21": "Marine Day",
    "2025-08-11": "Mountain Day",
    "2025-09-15": "Respect for the Aged Day",
    "2025-09-23": "Autumnal Equinox Day",
    "2025-10-13": "Sports Day",
}

# Note: Aug 13-15 is unofficial "Obon" holiday — most universities close
OBON = pd.date_range("2025-08-13", "2025-08-15")

dates = pd.date_range(START, END, freq="D")
records = []
for d in dates:
    d_str = d.strftime("%Y-%m-%d")
    dow = d.dayofweek  # 0=Mon, 6=Sun

    # Holiday tags (priority order)
    if d_str in HOLIDAYS:
        day_type     = "national_holiday"
        is_class_day = False
        holiday_name = HOLIDAYS[d_str]
    elif d in OBON:
        day_type     = "obon_break"
        is_class_day = False
        holiday_name = "Obon"
    elif dow >= 5:
        day_type     = "weekend"
        is_class_day = False
        holiday_name = ""
    elif pd.Timestamp(SPRING_TERM[0]) <= d <= pd.Timestamp(SPRING_TERM[1]):
        day_type     = "regular_term_spring"
        is_class_day = True
        holiday_name = ""
    elif pd.Timestamp(EXAM_WEEK_S[0]) <= d <= pd.Timestamp(EXAM_WEEK_S[1]):
        day_type     = "exam_week_spring"
        is_class_day = True
        holiday_name = ""
    elif pd.Timestamp(SUMMER_BREAK[0]) <= d <= pd.Timestamp(SUMMER_BREAK[1]):
        day_type     = "summer_break"
        is_class_day = False
        holiday_name = ""
    elif pd.Timestamp(FALL_TERM[0]) <= d <= pd.Timestamp(FALL_TERM[1]):
        day_type     = "regular_term_fall"
        is_class_day = True
        holiday_name = ""
    else:
        day_type     = "other"
        is_class_day = False
        holiday_name = ""

    records.append({
        "date": d_str,
        "dow":  dow,
        "dow_name": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][dow],
        "day_type": day_type,
        "is_class_day": is_class_day,
        "holiday_name": holiday_name,
    })

cal = pd.DataFrame(records)
cal["date"] = pd.to_datetime(cal["date"])
cal.set_index("date", inplace=True)

print("Calendar built:", cal.shape)
print("\nday_type distribution:")
print(cal["day_type"].value_counts().sort_index())
print("\nClass days vs non-class days:")
print(cal["is_class_day"].value_counts())

csv_path = os.path.join(OUT_DIR, "calendar.csv")
cal.to_csv(csv_path)
print(f"\n💾 saved → {csv_path}")

# Also print preview
print("\nFirst 10 days:")
print(cal.head(10))
print("\nMid-period days (Aug 11-15 Obon):")
print(cal.loc["2025-08-09":"2025-08-16"])
print("\nFall term start:")
print(cal.loc["2025-09-28":"2025-10-05"])
