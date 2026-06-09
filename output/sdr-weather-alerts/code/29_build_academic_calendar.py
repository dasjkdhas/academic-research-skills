"""Build precise academic calendar JFY2025 from Yamaguchi U PDF + re-run RQ3 + RQ4.

Key periods extracted from the PDF:
  前期授業: 2025-04-09 ~ 2025-08-05 (with makeup days)
  夏季休業: 2025-08-06 ~ 2025-09-30
  後期授業: 2025-10-01 ~ 2026-02-05
  冬季休業: 2025-12-27 ~ 2026-01-05
  春季休業1: 2025-04-01 ~ 2025-04-08
  春季休業2: 2026-02-06 ~ 2026-03-31

Special days (relevant to Tokiwa/Ube engineering campus):
  4/3 入学式, 6/1 創立記念日 (university-wide)
  8/9 オープンキャンパス (常盤 = Tokiwa), 8/22-25 代替日
  9/26 秋季卒業式, 3/16 博士学位授与式, 3/24 卒業式

Exam-related closures:
  1/16 大学入学共通テスト準備
  2/24 前期日程準備, 2/25-26 前期日程実施
  3/11 後期日程準備, 3/12-13 後期日程実施
"""
import os, json
import numpy as np, pandas as pd

PROC = "/home/user/academic-research-skills/output/sdr-weather-alerts/data_processed"

# --- Japanese national holidays JFY2025 ---
HOLIDAYS = {
 "2025-04-29": "昭和の日", "2025-05-03": "憲法記念日", "2025-05-04": "みどりの日",
 "2025-05-05": "こどもの日", "2025-05-06": "振替休日",
 "2025-07-21": "海の日", "2025-08-11": "山の日",
 "2025-09-15": "敬老の日", "2025-09-23": "秋分の日",
 "2025-10-13": "スポーツの日", "2025-11-03": "文化の日",
 "2025-11-23": "勤労感謝の日", "2025-11-24": "振替休日",
 "2026-01-01": "元日", "2026-01-12": "成人の日",
 "2026-02-11": "建国記念の日", "2026-02-23": "天皇誕生日",
 "2026-03-20": "春分の日",
}

# --- Special university days ---
EVENT_DAYS = {
 "2025-04-03": "入学式",
 "2025-06-01": "創立記念日",
 "2025-08-08": "オープンキャンパス(吉田・小串)",   # 常盤 not listed -> still mild effect
 "2025-08-09": "オープンキャンパス(常盤)",          # Tokiwa = our campus!
 "2025-08-22": "オープンキャンパス代替日",
 "2025-08-23": "オープンキャンパス代替日",
 "2025-08-25": "オープンキャンパス代替日",
 "2025-09-26": "秋季卒業式・大学院入学式",
 "2026-03-16": "学位記授与式(博士)",
 "2026-03-24": "卒業式・大学院修了式",
}

# --- Exam-related closures (臨時休業) ---
EXAM_CLOSURE = {
 "2026-01-16": "共通テスト準備",
 "2026-02-24": "前期日程準備",
 "2026-02-25": "前期日程実施",
 "2026-02-26": "前期日程実施",
 "2026-03-11": "後期日程準備",
 "2026-03-12": "後期日程実施",
 "2026-03-13": "後期日程実施",
}

# --- Vacation periods (date ranges, both inclusive) ---
VACATIONS = [
 ("2025-04-01", "2025-04-08", "春季休業"),
 ("2025-08-06", "2025-09-30", "夏季休業"),
 ("2025-12-27", "2026-01-05", "冬季休業"),
 ("2026-02-06", "2026-03-31", "春季休業(後期後)"),
]

# --- Class terms (when classes are held) ---
TERMS = [
 ("2025-04-09", "2025-08-05", "前期"),
 ("2025-10-01", "2026-02-05", "後期"),
]

# Build full daily calendar
dates = pd.date_range("2025-04-01", "2026-03-31", freq="D")
rows = []
for d in dates:
    ds = d.strftime("%Y-%m-%d")
    dow = d.dayofweek  # 0=Mon, 6=Sun
    is_weekend = dow >= 5
    is_holiday = ds in HOLIDAYS
    is_event   = ds in EVENT_DAYS
    is_exam    = ds in EXAM_CLOSURE
    # vacation?
    vac_name = None
    for s, e, name in VACATIONS:
        if pd.Timestamp(s) <= d <= pd.Timestamp(e):
            vac_name = name; break
    # term
    term = None
    for s, e, name in TERMS:
        if pd.Timestamp(s) <= d <= pd.Timestamp(e):
            term = name; break

    # Priority for day_type (mutually exclusive label):
    # 1. exam_closure  2. event_day  3. vacation  4. holiday  5. weekend  6. class_day  7. other
    if is_exam:
        dtype = "試験期"
    elif is_event:
        dtype = "活動日"
    elif vac_name:
        dtype = "休業"
    elif is_holiday:
        dtype = "節假日"
    elif is_weekend:
        dtype = "週末"
    elif term:
        dtype = "上課日"
    else:
        dtype = "その他"

    rows.append({
        "date": ds, "dow": dow,
        "is_weekend": int(is_weekend), "is_holiday": int(is_holiday),
        "is_event": int(is_event), "is_exam_closure": int(is_exam),
        "vacation": vac_name or "", "term": term or "",
        "event_name": EVENT_DAYS.get(ds, ""),
        "day_type": dtype,
    })

cal = pd.DataFrame(rows)
cal.to_csv(f"{PROC}/academic_calendar_JFY2025.csv", index=False)
print(f"Calendar built: {len(cal)} days")
print("\nday_type distribution:")
print(cal["day_type"].value_counts().to_string())
print("\nFirst 14 days:")
print(cal.head(14).to_string(index=False))
