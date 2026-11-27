"""
Q-004: Explain the bias-variance trade-off. How do you diagnose overfitting?
Run: python example.py   (needs numpy, pandas, scikit-learn, matplotlib)

Example 1 (logistics): a fictional parcel company predicts how long a van route takes
from its number of stops. We fit polynomials from a straight line (degree 1) to degree 6
and watch training error fall while cross-validated error turns back up. Because the data is simulated, we also know
the true answer, so we can split the test error into bias^2, variance and noise directly.

Example 2 (education): a fictional college predicts weekly quiz scores so it can flag
students who need support. Each student appears six times. We tune a decision tree's depth.
Random K-fold puts the same student in both training and validation folds, so it rewards
the tree that memorises students and picks the deepest one. Grouping the folds by student (the real job: new
students next year) picks a shallow tree, and a fresh cohort confirms grouped CV was right.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold, KFold, cross_validate
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import MinMaxScaler, PolynomialFeatures
from sklearn.tree import DecisionTreeRegressor

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
import viz_style as vs  # noqa: E402

pd.set_option("display.width", 120)
DEPTHS = [1, 2, 3, 4, 5, 6, 8, 10, None]          # None = grow until leaves are pure


def depth_label(d):
    return "full" if d is None else str(d)


def rmse(a, b):
    return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))


# ---------------------------------------------------------------------------
# Example 1 (logistics): Kestrel Parcels (fictional), route duration in minutes.
# True process: each extra stop adds time, but less once drops cluster on the same streets.
# We fit polynomials of degree 1 (a straight line) to 6 (a very bendy curve) to 20 routes.
# ---------------------------------------------------------------------------
NOISE_SD = 15.0   # minutes of traffic and doorstep luck that no model can predict
DEGREES = [1, 2, 3, 4, 5, 6]


def true_duration(stops):
    return 40 + 330 * (1 - np.exp(-stops / 22))


def make_routes(n, rng):
    stops = rng.integers(5, 61, n)
    return stops, true_duration(stops) + rng.normal(0, NOISE_SD, n)


def poly(degree):
    return make_pipeline(MinMaxScaler((-1, 1)), PolynomialFeatures(degree, include_bias=False),
                         LinearRegression())


stops, minutes = make_routes(20, np.random.default_rng(4))
routes = pd.DataFrame({"route": [f"R{i:02d}" for i in range(1, 21)], "stops": stops,
                       "minutes": minutes.round(0)})
X1, y1 = routes[["stops"]].to_numpy(), routes["minutes"].to_numpy()

print("== Example 1 (logistics): Kestrel Parcels route durations ==")
print(routes.to_string(index=False))

cv5 = KFold(5, shuffle=True, random_state=0)
rows1 = []
for d in DEGREES:
    res = cross_validate(poly(d), X1, y1, cv=cv5, scoring="neg_root_mean_squared_error",
                         return_train_score=True)
    rows1.append({"degree": d, "train_rmse": -res["train_score"].mean(),
                  "cv_rmse": -res["test_score"].mean()})
curve1 = pd.DataFrame(rows1)
curve1["gap"] = curve1.cv_rmse - curve1.train_rmse
best1 = curve1.loc[curve1.cv_rmse.idxmin()]
print("\nValidation curve (5-fold CV, RMSE in minutes):")
print(curve1.round(1).to_string(index=False))
print(f"Best degree by CV: {int(best1.degree)} (CV RMSE {best1.cv_rmse:.1f} min)")
print(f"Irreducible noise floor: {NOISE_SD:.1f} min")

# Bias-variance decomposition. Because we wrote the true process, we can refit each degree
# on 300 fresh sets of 20 routes and compare its average prediction (bias) and its spread
# (variance) at every stop count from 5 to 60. Note: the straight line's variance is not the
# smallest, because its tilt depends heavily on which route sizes happen to be sampled.
grid = np.arange(5, 61).reshape(-1, 1)
f_grid = true_duration(grid.ravel())
sim_rng = np.random.default_rng(7)
train_sets = [make_routes(20, sim_rng) for _ in range(300)]
decomp = []
for d in DEGREES:
    preds = np.array([poly(d).fit(s.reshape(-1, 1), y).predict(grid) for s, y in train_sets])
    bias_sq = float(np.mean((preds.mean(axis=0) - f_grid) ** 2))
    variance = float(np.mean(preds.var(axis=0)))
    decomp.append({"degree": d, "bias_sq": bias_sq, "variance": variance, "noise": NOISE_SD ** 2,
                   "expected_mse": bias_sq + variance + NOISE_SD ** 2})
decomp = pd.DataFrame(decomp)
decomp["expected_rmse"] = np.sqrt(decomp.expected_mse)
print("\nBias-variance decomposition (300 training sets of 20 routes; minutes^2):")
print(decomp.round(1).to_string(index=False))

# ---------------------------------------------------------------------------
# Example 2 (education): Westmere College (fictional), weekly quiz score out of 100.
# 40 students x 6 weeks. Each student has a hidden "ability" the features don't capture,
# but their prior grades and attendance are unique enough to act as a fingerprint.
# ---------------------------------------------------------------------------
def make_cohort(n_students, rng, first_id=1):
    rows = []
    for s in range(n_students):
        prior = rng.uniform(4.0, 8.0)          # average GCSE grade on entry
        attend = rng.uniform(70, 99)           # attendance %
        ability = rng.normal(0, 9)             # hidden, student-specific
        for week in range(1, 7):
            hours = max(0.0, rng.normal(3, 1.5))
            score = 10 + 6 * prior + 0.2 * attend + 2.0 * hours + ability + rng.normal(0, 4)
            rows.append({"student_id": first_id + s, "week": week, "prior_gcse": round(prior, 2),
                         "attendance_pct": round(attend, 1), "study_hours": round(hours, 1),
                         "quiz_score": float(np.clip(round(score), 0, 100))})
    return pd.DataFrame(rows)


cohort = make_cohort(40, np.random.default_rng(11))
FEATS = ["prior_gcse", "attendance_pct", "study_hours"]
X2, y2, groups = cohort[FEATS], cohort["quiz_score"], cohort["student_id"]
new_cohort = make_cohort(40, np.random.default_rng(12), first_id=101)   # next year's intake

print("\n== Example 2 (education): Westmere College weekly quiz scores ==")
print(f"Rows: {len(cohort)} ({cohort.student_id.nunique()} students x 6 weeks); first 8 shown")
print(cohort.head(8).to_string(index=False))

random_cv = KFold(5, shuffle=True, random_state=0)
grouped_cv = GroupKFold(5)
rows2 = []
for d in DEPTHS:
    model = DecisionTreeRegressor(max_depth=d, random_state=0)
    r = cross_validate(model, X2, y2, cv=random_cv, scoring="neg_root_mean_squared_error",
                       return_train_score=True)
    g = cross_validate(model, X2, y2, cv=grouped_cv, groups=groups,
                       scoring="neg_root_mean_squared_error")
    fitted = DecisionTreeRegressor(max_depth=d, random_state=0).fit(X2, y2)
    rows2.append({"max_depth": depth_label(d), "train_rmse": -r["train_score"].mean(),
                  "random_cv_rmse": -r["test_score"].mean(),
                  "grouped_cv_rmse": -g["test_score"].mean(),
                  "new_cohort_rmse": rmse(fitted.predict(new_cohort[FEATS]), new_cohort.quiz_score)})
curve2 = pd.DataFrame(rows2)
print("\nRandom K-fold vs grouped-by-student K-fold (RMSE in quiz points):")
print(curve2.round(1).to_string(index=False))
pick_random = curve2.loc[curve2.random_cv_rmse.idxmin()]
pick_grouped = curve2.loc[curve2.grouped_cv_rmse.idxmin()]
print(f"Random K-fold picks depth {pick_random.max_depth}: random-CV RMSE {pick_random.random_cv_rmse:.1f}, "
      f"new-cohort RMSE {pick_random.new_cohort_rmse:.1f}")
print(f"Grouped K-fold picks depth {pick_grouped.max_depth}: grouped-CV RMSE {pick_grouped.grouped_cv_rmse:.1f}, "
      f"new-cohort RMSE {pick_grouped.new_cohort_rmse:.1f}")
print(f"Baseline (predict the training mean for everyone): new-cohort RMSE "
      f"{rmse(np.full(len(new_cohort), y2.mean()), new_cohort.quiz_score):.1f}")

# ---------------------------------------------------------------------------
# Chart: the two validation curves side by side
# ---------------------------------------------------------------------------
fig, (a1, a2) = vs.figure(width=11, height=5.4, ncols=2)
fig.subplots_adjust(top=0.78, bottom=0.17, left=0.06, right=0.97, wspace=0.25)
xs = np.arange(len(DEPTHS))
labels = [depth_label(d) for d in DEPTHS]

x1 = np.arange(len(DEGREES))
a1.plot(x1, curve1.train_rmse, color=vs.MUTED, lw=2, marker="o", ms=4)
a1.plot(x1, curve1.cv_rmse, color=vs.SERIES[0], lw=2.2, marker="o", ms=4)
a1.axhline(NOISE_SD, color=vs.INK_3, lw=1, ls="--")
a1.text(x1[-1], NOISE_SD - 1.0, f"noise floor {NOISE_SD:.0f} min", fontsize=7.5, color=vs.INK_2,
        ha="right", va="top")
bi = int(curve1.cv_rmse.idxmin())
vs.callout(a1, bi, curve1.cv_rmse[bi], f"best: degree {DEGREES[bi]}, {curve1.cv_rmse[bi]:.1f} min",
           dx=25, dy=32, marker_color=vs.SERIES[0])
a1.text(3.5, curve1.train_rmse.iloc[3] + 1.5, "training", fontsize=8, color=vs.INK_2, ha="center", va="bottom")
a1.text(x1[-1] - 0.1, curve1.cv_rmse.iloc[-1], "5-fold CV", fontsize=8, color=vs.SERIES[0], ha="right", va="center")
a1.text(-0.1, curve1.cv_rmse.iloc[0] + 3, "underfit\n(high bias)", fontsize=7.5, color=vs.INK_2, ha="left", va="bottom")
a1.text(x1[-1], curve1.cv_rmse.iloc[-1] + 3, "overfit\n(high variance)", fontsize=7.5, color=vs.INK_2, ha="center", va="bottom")
a1.set_xticks(x1, [str(d) for d in DEGREES])
a1.set_xlabel("polynomial degree (simple → complex)")
a1.set_ylabel("RMSE, minutes")
a1.set_title("Example 1, Kestrel Parcels: CV error is U-shaped", fontsize=9.5, color=vs.INK, loc="left")
a1.set_ylim(0, curve1.cv_rmse.max() * 1.25)

a2.plot(xs, curve2.random_cv_rmse, color=vs.SERIES[1], lw=2.2, marker="o", ms=4)
a2.plot(xs, curve2.grouped_cv_rmse, color=vs.SERIES[0], lw=2.2, marker="o", ms=4)
a2.plot(xs, curve2.new_cohort_rmse, color=vs.INK, lw=1.2, ls=":", marker="s", ms=3)
ri = int(curve2.random_cv_rmse.idxmin())
gi = int(curve2.grouped_cv_rmse.idxmin())
vs.callout(a2, ri, curve2.random_cv_rmse[ri], f"random folds pick depth {labels[ri]}",
           dx=-10, dy=-28, marker_color=vs.SERIES[1], ha="right")
vs.callout(a2, gi, curve2.grouped_cv_rmse[gi], f"grouped folds pick depth {labels[gi]}",
           dx=10, dy=-30, marker_color=vs.SERIES[0])
a2.text(xs[-1], curve2.random_cv_rmse.iloc[-1] - 1.0, "random K-fold", fontsize=8, color=vs.SERIES[1], ha="right", va="top")
a2.text(xs[-1], curve2.grouped_cv_rmse.iloc[-1] + 0.8, "grouped by student", fontsize=8, color=vs.SERIES[0], ha="right", va="bottom")
a2.text(5.5, 11.8, "next year's students (truth)", fontsize=7.5, color=vs.INK, ha="center", va="center")
a2.set_xticks(xs, labels)
a2.set_xlabel("tree max_depth (simple → complex)")
a2.set_ylabel("RMSE, quiz points")
a2.set_title("Example 2, Westmere College: the split decides the answer", fontsize=9.5, color=vs.INK, loc="left")
a2.set_ylim(0, max(curve2.grouped_cv_rmse.max(), curve2.new_cohort_rmse.max()) * 1.15)

vs.headline(fig, "Overfitting shows up as a gap, but only if validation mimics the real job",
            "Training vs cross-validated RMSE as model complexity rises (lower is better)")
vs.footer(fig, "Made-up data for a fictional parcel company and college | Data Interview Questions #004")
vs.save(fig, HERE / "chart_1.png")
print("\nSaved chart_1.png")
