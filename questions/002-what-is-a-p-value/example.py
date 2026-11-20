"""
Q-002: What is a p-value? Explain it to a non-technical person.
Run: python example.py   (needs numpy, pandas, scipy, statsmodels, matplotlib)

Example 1 (NHS trust): a fictional trust randomly picks 8 of its 16 outpatient clinics
to trial a new text reminder and asks whether missed appointments really fell. We compute
the p-value the literal way (shuffle the labels, every possible way) and the textbook way
(Welch's t-test) and show they agree.
Example 2 (energy supplier): a fictional supplier tests 19 email subject lines against its
usual one. Every variant was given the SAME true booking rate, so any "winner" is noise by
construction. One variant still gets p < 0.05: the p-value promise holds for one planned
test, not for nineteen.
"""
import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportions_ztest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
import viz_style as vs  # noqa: E402

pd.set_option("display.width", 120)

# ---------------------------------------------------------------------------
# Example 1 (NHS trust): did the new text reminder reduce missed appointments?
# did_not_attend_pct = % of booked outpatient appointments missed last quarter.
# The 8 reminder clinics were chosen at random, which is what makes shuffling valid.
# ---------------------------------------------------------------------------
clinics = pd.DataFrame(
    [
        ("Ashby Road", "usual letter", 8.1), ("Brookfield", "usual letter", 7.4),
        ("Castle Vale", "usual letter", 9.0), ("Dunmore", "usual letter", 6.8),
        ("Elm Park", "usual letter", 8.6), ("Fenwick", "usual letter", 7.9),
        ("Greystone", "usual letter", 9.4), ("Holloway", "usual letter", 7.2),
        ("Ivy Lane", "new text reminder", 6.9), ("Juniper", "new text reminder", 6.1),
        ("Kingsmead", "new text reminder", 7.6), ("Larchwood", "new text reminder", 7.1),
        ("Millbrook", "new text reminder", 7.4), ("Northgate", "new text reminder", 6.3),
        ("Oakhill", "new text reminder", 8.5), ("Parkside", "new text reminder", 6.6),
    ],
    columns=["clinic", "group", "did_not_attend_pct"],
)
x = clinics.did_not_attend_pct.to_numpy()
is_reminder = (clinics.group == "new text reminder").to_numpy()
control_mean = x[~is_reminder].mean()
reminder_mean = x[is_reminder].mean()
observed = reminder_mean - control_mean

# The p-value, literally: pretend the reminder did nothing, so the labels are arbitrary.
# Try every way of choosing which 8 of the 16 clinics are "reminder" clinics
# (16 choose 8 = 12,870 ways) and see how often the gap is at least as big as the real one.
null_diffs = np.empty(12870)
for k, idx in enumerate(itertools.combinations(range(16), 8)):
    mask = np.zeros(16, dtype=bool)
    mask[list(idx)] = True
    null_diffs[k] = x[mask].mean() - x[~mask].mean()
as_extreme = np.abs(null_diffs) >= abs(observed) - 1e-9   # two-sided; tolerance for float noise
p_shuffle = as_extreme.mean()

# The textbook shortcut: Welch's t-test (two-sided) and a 95% confidence interval
welch = stats.ttest_ind(x[is_reminder], x[~is_reminder], equal_var=False)
v1 = x[is_reminder].var(ddof=1) / 8
v2 = x[~is_reminder].var(ddof=1) / 8
se = np.sqrt(v1 + v2)
dof = (v1 + v2) ** 2 / (v1 ** 2 / 7 + v2 ** 2 / 7)
t_crit = stats.t.ppf(0.975, dof)
ci_low, ci_high = observed - t_crit * se, observed + t_crit * se

print("== Example 1 (NHS trust): missed appointments by clinic ==")
print(clinics.to_string(index=False))
print(f"\nMean missed-appointment rate, usual letter:      {control_mean:.2f}%")
print(f"Mean missed-appointment rate, new text reminder: {reminder_mean:.2f}%")
print(f"Observed difference (reminder - letter):         {observed:+.2f} percentage points")
print(f"\nShuffles tried: {len(null_diffs):,} | gap at least as big as observed: {int(as_extreme.sum()):,}")
print(f"p-value by shuffling (exact, two-sided): {p_shuffle:.4f}")
print(f"p-value by Welch's t-test (two-sided):   {welch.pvalue:.4f}")
print(f"95% confidence interval for the difference: {ci_low:+.2f} to {ci_high:+.2f} percentage points")

# Visual: the 'nothing is going on' world, with the real result marked
fig, ax = vs.figure()
bins = np.linspace(-1.6, 1.6, 33)
ax.hist([null_diffs[~as_extreme], null_diffs[as_extreme]], bins=bins, stacked=True,
        color=[vs.MUTED, vs.SERIES[1]], edgecolor=vs.SURFACE, lw=0.5)
ax.axvline(observed, color=vs.INK, lw=1.2, ls="--")
ax.text(observed - 0.05, ax.get_ylim()[1] * 0.92, f"Real result\n{observed:+.2f} pts", ha="right",
        va="top", fontsize=8.5, color=vs.INK)
ax.text(0.95, ax.get_ylim()[1] * 0.55,
        f"Orange = shuffles with a gap at least\nas big as the real one (either direction):\n"
        f"{int(as_extreme.sum()):,} of {len(null_diffs):,} = p of {p_shuffle:.3f}",
        ha="left", va="top", fontsize=8.5, color=vs.SERIES[1])
ax.set_xlabel("Difference in missed-appointment rate if the reminder did nothing "
              "(percentage points, reminder minus letter)")
ax.set_ylabel("Number of shuffles")
vs.headline(fig, f"If the reminder did nothing, a gap this big turns up in {p_shuffle:.1%} of shuffles",
            "All 12,870 ways of relabelling 8 of 16 clinics as 'reminder' clinics. That share is the p-value.")
vs.footer(fig, "Made-up data for a fictional NHS trust | Data Interview Questions #002")
vs.save(fig, HERE / "chart_1.png")
print("Saved chart_1.png")

# ---------------------------------------------------------------------------
# Example 2 (energy supplier): 19 subject lines tested against the usual one.
# 5,000 customers per email. The booking counts below were drawn once at random
# with the SAME true booking rate (4.0%) for every email, then written in, so by
# construction no subject line is really better than the control.
# ---------------------------------------------------------------------------
subjects = [
    "CONTROL: Book your smart meter", "Your free smart meter is ready", "Save time on meter readings",
    "No more estimated bills", "Pick a slot that suits you", "Takes about an hour",
    "Your neighbours have booked", "See your energy use live", "Quick question about your meter",
    "Smart meters: your questions answered", "One less thing to do", "Book online in 2 minutes",
    "Your meter is due an upgrade", "Free installation, no catch", "Make your bills accurate",
    "We have engineers near you", "Avoid the winter rush", "Last chance: free smart meter",
    "Track your spending daily", "Join 1,000 local households",
]
bookings = [186, 202, 203, 190, 208, 191, 202, 205, 206, 184,
            200, 210, 206, 214, 194, 195, 184, 231, 193, 203]
n = 5000
emails = pd.DataFrame({"subject_line": subjects, "sent": n, "bookings": bookings})
emails["booking_rate_pct"] = (100 * emails.bookings / n).round(2)

pvals = np.array([proportions_ztest([b, bookings[0]], [n, n])[1] for b in bookings[1:]])
holm = multipletests(pvals, alpha=0.05, method="holm")[1]
tests = emails.iloc[1:].copy()
tests["p_value"] = pvals.round(4)
tests["holm_adjusted_p"] = holm.round(3)
tests = tests.sort_values("p_value")

print("\n== Example 2 (energy supplier): 19 subject lines vs the usual one ==")
print(emails.iloc[[0]].to_string(index=False))
print(tests.to_string(index=False))
winner = tests.iloc[0]
print(f"\nTests run: {len(pvals)} | raw p < 0.05: {int((pvals < 0.05).sum())}"
      f" | Holm-adjusted p < 0.05: {int((holm < 0.05).sum())}")
print(f"'Winner': {winner.subject_line!r}, {winner.booking_rate_pct:.2f}% vs "
      f"{emails.booking_rate_pct[0]:.2f}%, raw p = {winner.p_value:.4f}, "
      f"Holm-adjusted p = {winner.holm_adjusted_p:.3f}")

# How often does a campaign like this produce at least one false 'winner'?
print(f"\nChance of at least one p < 0.05 in 19 independent tests with no real effect: "
      f"{1 - 0.95 ** 19:.1%}")
rng = np.random.default_rng(2026)
sims, hits = 2000, 0
for _ in range(sims):
    b = rng.binomial(n, 0.04, 20)
    p = np.array([proportions_ztest([bi, b[0]], [n, n])[1] for bi in b[1:]])
    hits += bool((p < 0.05).any())
print(f"Simulated: {sims:,} campaigns like this one, all with no real effect: "
      f"{hits / sims:.1%} had at least one 'winner' at p < 0.05")

# The analogy in the README: a fair coin landing heads 8 times in a row
print(f"\nFair coin, 8 heads in a row: {0.5 ** 8:.4f} (about {1000 * 0.5 ** 8:.0f} in 1,000)")
