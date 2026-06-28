import re
import json
import hashlib
from pathlib import Path
import pandas as pd

BASE = Path(r"C:\Users\XCKF\.openclaw\workspace-kg-prototype")
light_xlsx = BASE / "data" / "光领域公司.xlsx"
main_xlsx = BASE / "data" / "company-info_with_url.xlsx"
db_csv = BASE / "data" / "neo4j" / "neo4j_enterprise_nodes.csv"
out_lost = BASE / "data" / "lost_list.txt"
out_report = BASE / "data" / "light_compare_report.json"


def clean_name(s: str) -> str:
    s = "" if s is None else str(s)
    s = s.strip()
    s = re.sub(r"\s+", "", s)
    s = s.replace('（人工核对）', '')
    return s

# 读取光领域对象池：默认取 Sheet1 第一列
light_df = pd.read_excel(light_xlsx, sheet_name='Sheet1')
light_names_raw = [x for x in light_df.iloc[:,0].tolist() if pd.notna(x) and str(x).strip()]
light_names = sorted(dict.fromkeys([clean_name(x) for x in light_names_raw]))

main_df = pd.read_excel(main_xlsx)
main_names_raw = [x for x in main_df['公司名称'].tolist() if pd.notna(x) and str(x).strip()]
main_name_map = {}
for x in main_names_raw:
    main_name_map.setdefault(clean_name(x), str(x).strip())
main_names = set(main_name_map.keys())

db_df = pd.read_csv(db_csv)
db_names_raw = [x for x in db_df['name'].tolist() if pd.notna(x) and str(x).strip()]
db_name_map = {}
for x in db_names_raw:
    db_name_map.setdefault(clean_name(x), str(x).strip())
db_names = set(db_name_map.keys())

missing_in_excel = [n for n in light_names if n not in main_names]
missing_in_db_but_in_excel = [n for n in light_names if n in main_names and n not in db_names]
existing_both = [n for n in light_names if n in main_names and n in db_names]

out_lost.write_text("\n".join(main_name_map.get(n, n) for n in missing_in_excel), encoding='utf-8')
report = {
    'light_pool_count': len(light_names),
    'main_excel_count': len(main_names),
    'db_csv_count': len(db_names),
    'missing_in_excel_count': len(missing_in_excel),
    'missing_in_db_but_in_excel_count': len(missing_in_db_but_in_excel),
    'existing_both_count': len(existing_both),
    'missing_in_excel': [n for n in missing_in_excel],
    'missing_in_db_but_in_excel': [main_name_map[n] for n in missing_in_db_but_in_excel],
}
out_report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False))
