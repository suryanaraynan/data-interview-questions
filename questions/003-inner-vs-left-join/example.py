"""
Q-003: INNER JOIN vs LEFT JOIN: when do you use each, and what goes wrong with LEFT JOIN filters?
Run: python example.py   (needs duckdb, pandas, matplotlib)

Example 1 (subscriptions): a fictional meal-kit company wants October orders per subscriber,
INCLUDING subscribers who ordered nothing. A filter on the orders table placed in WHERE
quietly turns the LEFT JOIN back into an INNER JOIN; the same filter in ON keeps everyone.
Example 2 (transport operator): a fictional bus company wants November faults for North depot
routes. The twist is the opposite mistake: a filter on the KEPT table (depot) put in ON does
not remove any routes. Plus the anti-join (routes with no faults) and the NOT IN / NULL trap.
"""
import sys
from pathlib import Path

import duckdb
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
import viz_style as vs  # noqa: E402

pd.set_option("display.width", 120)
con = duckdb.connect()

# ---------------------------------------------------------------------------
# Example 1 (subscriptions): made-up data for a fictional meal-kit company
# ---------------------------------------------------------------------------
subscribers = pd.DataFrame(
    [
        (101, "Amara", "Family"), (102, "Bilal", "Couple"), (103, "Cara", "Family"),
        (104, "Dan", "Couple"), (105, "Esi", "Single"), (106, "Finn", "Single"),
        (107, "Gita", "Family"), (108, "Hugo", "Couple"), (109, "Ivy", "Single"),
        (110, "Jude", "Family"),
    ],
    columns=["subscriber_id", "name", "plan"],
)
orders = pd.DataFrame(
    [
        (1, 101, "2026-09-12", 42.0), (2, 101, "2026-10-03", 44.0), (3, 101, "2026-10-17", 44.0),
        (4, 102, "2026-10-09", 31.0),
        (5, 103, "2026-09-20", 46.0),                      # Cara: September only
        (6, 105, "2026-10-01", 22.0), (7, 105, "2026-10-14", 22.0), (8, 105, "2026-10-28", 24.0),
        (9, 106, "2026-09-05", 21.0),                      # Finn: September only
        (10, 107, "2026-09-25", 45.0), (11, 107, "2026-10-22", 47.0),
        (12, 109, "2026-10-30", 23.0),
        # Dan (104), Hugo (108) and Jude (110) have never ordered
    ],
    columns=["order_id", "subscriber_id", "order_date", "amount"],
)
orders["order_date"] = pd.to_datetime(orders["order_date"]).dt.date
con.register("subscribers", subscribers)
con.register("orders", orders)

OCT = "o.order_date >= DATE '2026-10-01' AND o.order_date < DATE '2026-11-01'"
SELECT = """
    SELECT s.subscriber_id, s.name,
           COUNT(o.order_id)          AS oct_orders,
           COALESCE(SUM(o.amount), 0) AS oct_spend
"""
queries = {
    "A. INNER JOIN, October filter": f"""{SELECT}
        FROM subscribers s
        INNER JOIN orders o ON o.subscriber_id = s.subscriber_id AND {OCT}
        GROUP BY s.subscriber_id, s.name ORDER BY s.subscriber_id""",
    "B. LEFT JOIN, October filter in WHERE": f"""{SELECT}
        FROM subscribers s
        LEFT JOIN orders o ON o.subscriber_id = s.subscriber_id
        WHERE {OCT}
        GROUP BY s.subscriber_id, s.name ORDER BY s.subscriber_id""",
    "C. LEFT JOIN, WHERE (October OR no order)": f"""{SELECT}
        FROM subscribers s
        LEFT JOIN orders o ON o.subscriber_id = s.subscriber_id
        WHERE ({OCT}) OR o.order_id IS NULL
        GROUP BY s.subscriber_id, s.name ORDER BY s.subscriber_id""",
    "D. LEFT JOIN, October filter in ON": f"""{SELECT}
        FROM subscribers s
        LEFT JOIN orders o ON o.subscriber_id = s.subscriber_id AND {OCT}
        GROUP BY s.subscriber_id, s.name ORDER BY s.subscriber_id""",
}

print("=" * 78)
print("Example 1 (subscriptions): October orders per subscriber, zeros included")
print("=" * 78)
print(f"Subscribers: {len(subscribers)} | orders: {len(orders)} "
      f"| October orders: {sum(pd.Timestamp(d).month == 10 for d in orders.order_date)}")
summary = []
results = {}
for label, sql in queries.items():
    df = con.sql(sql).df()
    results[label] = df
    zero = int((df.oct_orders == 0).sum())
    missing = sorted(set(subscribers.name) - set(df.name))
    summary.append((label, len(df), zero, ", ".join(missing) if missing else "none"))
    print(f"\n== {label} ==")
    print(df.to_string(index=False))
    print(f"-> subscribers returned: {len(df)} | with 0 October orders: {zero} "
          f"| missing: {', '.join(missing) if missing else 'none'}")

# The COUNT(*) trap: on query D, COUNT(*) counts the NULL-padded row as 1
count_trap = con.sql(f"""
    SELECT s.name, COUNT(*) AS count_star, COUNT(o.order_id) AS count_order_id
    FROM subscribers s
    LEFT JOIN orders o ON o.subscriber_id = s.subscriber_id AND {OCT}
    GROUP BY s.name HAVING COUNT(o.order_id) = 0 ORDER BY s.name
""").df()
print("\n== COUNT(*) vs COUNT(o.order_id) for subscribers with no October orders ==")
print(count_trap.to_string(index=False))

d = results["D. LEFT JOIN, October filter in ON"]
a = results["A. INNER JOIN, October filter"]
print(f"\nOctober revenue: A £{a.oct_spend.sum():.2f} | D £{d.oct_spend.sum():.2f} | "
      f"win-back list from D: {', '.join(d[d.oct_orders == 0].name)}")

# Visual: the four queries side by side
short = {"A": "A. INNER JOIN", "B": "B. LEFT JOIN, date in WHERE",
         "C": "C. WHERE date OR id IS NULL", "D": "D. LEFT JOIN, date in ON"}
chart = pd.DataFrame([(short[r[0][0]],) + r[1:] for r in summary],
                     columns=["Query", "Subscribers returned", "Shown with 0 orders", "Silently missing"])
vs.table_png(
    chart, HERE / "chart_1.png",
    title="Where the October filter goes decides who disappears",
    subtitle="10 subscribers; 5 placed no October order. Only the filter in ON keeps all of them.\n"
             "Filtering the optional table in WHERE turns the LEFT JOIN back into an INNER JOIN.",
    footer_text="Made-up data for a fictional meal-kit company | Data Interview Questions #003",
    highlight_rows=[3], col_width=2.6,
)
print("Saved chart_1.png")

# ---------------------------------------------------------------------------
# Example 2 (transport operator): made-up data for a fictional bus company.
# Twist: the filter is on the KEPT table (routes.depot). In ON it filters nothing.
# ---------------------------------------------------------------------------
routes = pd.DataFrame(
    [
        ("N1", "North"), ("N2", "North"), ("N3", "North"), ("N4", "North"),
        ("S1", "South"), ("S2", "South"), ("S3", "South"), ("S4", "South"),
    ],
    columns=["route_id", "depot"],
)
faults = pd.DataFrame(
    [
        (1, "N1", "2026-11-03"), (2, "N1", "2026-11-12"), (3, "N1", "2026-10-21"),
        (4, "N2", "2026-10-08"),                              # N2: October only
        (5, "N3", "2026-11-18"),
        (6, "S1", "2026-11-02"), (7, "S1", "2026-11-09"), (8, "S1", "2026-11-20"),
        (9, "S2", "2026-11-15"),
        (10, "S4", "2026-10-30"),
        (11, None, "2026-11-11"),                             # logged without a route
        # N4 and S3 have no faults at all
    ],
    columns=["fault_id", "route_id", "reported_on"],
)
faults["reported_on"] = pd.to_datetime(faults["reported_on"]).dt.date
con.register("routes", routes)
con.register("faults", faults)

NOV = "f.reported_on >= DATE '2026-11-01' AND f.reported_on < DATE '2026-12-01'"
wrong = con.sql(f"""
    SELECT r.route_id, r.depot, COUNT(f.fault_id) AS nov_faults
    FROM routes r
    LEFT JOIN faults f ON f.route_id = r.route_id AND {NOV} AND r.depot = 'North'
    GROUP BY r.route_id, r.depot ORDER BY r.route_id
""").df()
right = con.sql(f"""
    SELECT r.route_id, r.depot, COUNT(f.fault_id) AS nov_faults
    FROM routes r
    LEFT JOIN faults f ON f.route_id = r.route_id AND {NOV}
    WHERE r.depot = 'North'
    GROUP BY r.route_id, r.depot ORDER BY r.route_id
""").df()
s1_true = int(((faults.route_id == "S1")
               & (pd.to_datetime(faults.reported_on).dt.month == 11)).sum())

print("\n" + "=" * 78)
print("Example 2 (transport): November faults for North depot routes")
print("=" * 78)
print(f"Routes: {len(routes)} | faults: {len(faults)} "
      f"| faults with no route_id: {int(faults.route_id.isna().sum())}")
print("\n== WRONG: depot filter in ON (it filters the join, not the routes) ==")
print(wrong.to_string(index=False))
print(f"-> rows: {len(wrong)} | South routes included: {int((wrong.depot == 'South').sum())} "
      f"| S1 shown with {int(wrong.loc[wrong.route_id == 'S1', 'nov_faults'].iloc[0])} faults "
      f"(true November count: {s1_true})")
print("\n== RIGHT: date filter in ON (optional table), depot filter in WHERE (kept table) ==")
print(right.to_string(index=False))
print(f"-> rows: {len(right)} | North November faults: {int(right.nov_faults.sum())}")

# Anti-join: North routes with NO November faults. Here a WHERE filter on the optional
# table is exactly right, because IS NULL on its key is how you keep the non-matches.
anti = con.sql(f"""
    SELECT r.route_id
    FROM routes r
    LEFT JOIN faults f ON f.route_id = r.route_id AND {NOV}
    WHERE r.depot = 'North' AND f.fault_id IS NULL
    ORDER BY r.route_id
""").df()
anti_wrong = con.sql(f"""
    SELECT r.route_id
    FROM routes r
    LEFT JOIN faults f ON f.route_id = r.route_id AND {NOV} AND r.depot = 'North'
    WHERE f.fault_id IS NULL
    ORDER BY r.route_id
""").df()
not_exists = con.sql(f"""
    SELECT r.route_id FROM routes r
    WHERE r.depot = 'North'
      AND NOT EXISTS (SELECT 1 FROM faults f WHERE f.route_id = r.route_id AND {NOV})
    ORDER BY r.route_id
""").df()
not_in = con.sql(f"""
    SELECT r.route_id FROM routes r
    WHERE r.depot = 'North'
      AND r.route_id NOT IN (SELECT f.route_id FROM faults f WHERE {NOV})
    ORDER BY r.route_id
""").df()
print("\n== Anti-join: North routes with no November faults ==")
print(f"LEFT JOIN ... WHERE f.fault_id IS NULL : {list(anti.route_id)}")
print(f"Same, depot filter wrongly in ON       : {list(anti_wrong.route_id)} "
      f"({len(anti_wrong)} 'fault-free' routes)")
print(f"NOT EXISTS                             : {list(not_exists.route_id)}")
print(f"NOT IN (subquery has a NULL route_id)  : {list(not_in.route_id)} "
      f"({len(not_in)} rows)")
