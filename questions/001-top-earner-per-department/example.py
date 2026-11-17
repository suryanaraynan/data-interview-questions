"""
Q-001: Highest-paid employee per department, top 3, and what ties do.
Run: python example.py   (needs duckdb, pandas, matplotlib)

Data: a small, made-up staff table for a fictional council, with ties on purpose.
"""
import sys
from pathlib import Path

import duckdb
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
import viz_style as vs  # noqa: E402

staff = pd.DataFrame(
    [
        ("Aisha", "Planning", 52000), ("Ben", "Planning", 52000), ("Chloe", "Planning", 47000),
        ("Dev", "Planning", 45000), ("Ella", "Planning", 41000),
        ("Femi", "Housing", 49000), ("Grace", "Housing", 46000), ("Hari", "Housing", 46000),
        ("Isla", "Housing", 43000),
        ("Jon", "Finance", 58000), ("Kemi", "Finance", 51000),
    ],
    columns=["name", "department", "salary"],
)
con = duckdb.connect()
con.register("staff", staff)

# 1) Highest-paid per department, the version most people write first
top1 = con.sql("""
    SELECT department, name, salary
    FROM (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS rn
        FROM staff
    )
    WHERE rn = 1
    ORDER BY department
""").df()

# 2) The three ranking functions side by side: this is where ties matter
compare = con.sql("""
    SELECT department, name, salary,
           ROW_NUMBER() OVER w AS row_number,
           RANK()       OVER w AS rank,
           DENSE_RANK() OVER w AS dense_rank
    FROM staff
    WINDOW w AS (PARTITION BY department ORDER BY salary DESC)
    ORDER BY department, salary DESC, name
""").df()

# 3) "Top 3 salaries per department": DENSE_RANK keeps everyone on a tied salary
top3 = con.sql("""
    SELECT department, name, salary, dense_rank
    FROM (
        SELECT *, DENSE_RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dense_rank
        FROM staff
    )
    WHERE dense_rank <= 3
    ORDER BY department, salary DESC, name
""").df()

pd.set_option("display.width", 120)
print("== 1) ROW_NUMBER = 1 (one row per department, ties broken arbitrarily) ==")
print(top1.to_string(index=False))
print("\n== 2) ROW_NUMBER vs RANK vs DENSE_RANK ==")
print(compare.to_string(index=False))
print("\n== 3) Top 3 distinct salaries per department (DENSE_RANK <= 3) ==")
print(top3.to_string(index=False))
print(f"\nPlanning rows returned by ROW_NUMBER = 1: {int((top1.department == 'Planning').sum())}"
      f" | by RANK = 1: {int(((compare.department == 'Planning') & (compare['rank'] == 1)).sum())}")

# Visual: the comparison table for Planning and Housing, ties highlighted
show = compare[compare.department.isin(["Planning", "Housing"])].reset_index(drop=True)
show.columns = ["Department", "Name", "Salary (£)", "ROW_NUMBER", "RANK", "DENSE_RANK"]
ties = [i for i, s in enumerate(show["Salary (£)"])
        if ((show["Salary (£)"] == s) & (show["Department"] == show.loc[i, "Department"])).sum() > 1]
vs.table_png(
    show, HERE / "chart_1.png",
    title="Same data, three answers: ties are where ranking functions differ",
    subtitle="Highlighted rows share a salary. RANK skips a number after a tie, DENSE_RANK doesn't,\nand ROW_NUMBER breaks the tie arbitrarily.",
    footer_text="Made-up staff data for a fictional council | Data Interview Questions #001",
    highlight_rows=ties, col_formats={"Salary (£)": "{:,}"}, col_width=1.25,
)
print("Saved chart_1.png")
