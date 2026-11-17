"""
Decide whether to post an interview question today and pick which one.

    python tools/next_question.py --today 2026-11-18

Rhythm: about 2 questions a week, on irregular days, never on a day when something
else went out. Together with 2-3 Data Explained case files and a weekly project
milestone, that keeps Surya visibly active on 5-6 days a week.
  - Skip if a case file went out today (a post/<today>-* branch on data-explained, or a
    posts/<today>-* folder merged to its main), or Surya pushed project work today
    (the latest commit on a project repo's default branch is dated today, or a
    milestone/<today>-* branch exists).
  - At most one question a day, and at most 2 in any 7 days.
  - Never on consecutive days. Otherwise post with a probability that rises with the
    days since the last question; always post once 3 days have passed.
  - Pick the highest-ranked unanswered question in questions.json (tier 1 first),
    skipping any whose topic matches the last question posted.
"""
import argparse
import json
import subprocess
import tempfile
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASE_REPO = "https://github.com/suryanaraynan/data-explained"
PROJECT_REPOS = ["https://github.com/suryanaraynan/workplace-rights-rag"]  # add new project repos here
POST_PROBABILITY = {2: 0.5}  # days since last question -> chance to post
MAX_GAP_DAYS, MAX_PER_7_DAYS = 3, 2


def sh(*args, cwd=None):
    r = subprocess.run(list(args), cwd=cwd, capture_output=True, text=True, timeout=300)
    return r.returncode, r.stdout


def other_activity_today(today: str):
    code, out = sh("git", "ls-remote", CASE_REPO, "refs/heads/post/*")
    if code != 0:
        return None, "could not reach data-explained"
    if any(line.split("\t")[-1].startswith(f"refs/heads/post/{today}-") for line in out.splitlines()):
        return True, "case-file branch opened today"
    with tempfile.TemporaryDirectory() as tmp:
        code, _ = sh("git", "clone", "-q", "--depth", "1", "--filter=blob:none", "--no-checkout", CASE_REPO, tmp)
        if code == 0:
            _, tree = sh("git", "ls-tree", "--name-only", "HEAD", "posts/", cwd=tmp)
            if any(p.startswith(f"posts/{today}-") for p in tree.split()):
                return True, "case file merged today"
    for repo in PROJECT_REPOS:
        name = repo.rsplit("/", 1)[-1]
        code, out = sh("git", "ls-remote", repo, "refs/heads/milestone/*")
        if code == 0 and any(line.split("\t")[-1].startswith(f"refs/heads/milestone/{today}-")
                             for line in out.splitlines()):
            return True, f"project milestone opened today ({name})"
        with tempfile.TemporaryDirectory() as tmp:
            if sh("git", "clone", "-q", "--depth", "1", "--filter=blob:none", "--no-checkout", repo, tmp)[0] == 0:
                _, when = sh("git", "log", "-1", "--format=%cs", cwd=tmp)
                if when.strip() == today:
                    return True, f"project work pushed today ({name})"
    return False, "nothing else posted today"


def rhythm(done, today: str, rng):
    """Return (post?, reason) from the question history alone."""
    d = date.fromisoformat(today)
    dates = [date.fromisoformat(m["date"]) for m in done]
    if not dates:
        return True, "first question"
    recent = [x for x in dates if d - timedelta(days=6) <= x < d]
    if len(recent) >= MAX_PER_7_DAYS:
        return False, f"{len(recent)} questions in the last 7 days"
    gap = (d - max(dates)).days
    if gap >= MAX_GAP_DAYS:
        return True, f"{gap} days since last question"
    if gap <= 1:
        return False, "question posted yesterday"
    p, roll = POST_PROBABILITY[gap], rng.random()
    return (roll < p), f"{gap} days since last question; roll {roll:.2f} vs {p}"


def done_questions():
    metas = [json.loads(p.read_text()) for p in (ROOT / "questions").glob("*/meta.json")]
    return sorted(metas, key=lambda m: m["number"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--today", default=date.today().isoformat())
    ap.add_argument("--ignore-case-files", action="store_true", help="for manual/test runs")
    ap.add_argument("--seed", type=int, default=None)
    args = ap.parse_args()
    rng = random.Random(args.seed)

    done = done_questions()
    if any(m["date"] == args.today for m in done):
        print(json.dumps({"post": False, "reason": "already posted a question today"}))
        return
    if not args.ignore_case_files:
        clash, why = other_activity_today(args.today)
        if clash is None:
            print(json.dumps({"post": False, "reason": why}))
            return
        if clash:
            print(json.dumps({"post": False, "reason": f"{why}: questions take the other days"}))
            return
    ok, why = rhythm(done, args.today, rng)
    if not ok:
        print(json.dumps({"post": False, "reason": why}))
        return

    bank = json.loads((ROOT / "questions.json").read_text())
    used = {m["rank"] for m in done}
    last_topic = done[-1]["topic"] if done else None
    todo = sorted((q for q in bank["questions"] if q["rank"] not in used),
                  key=lambda q: (q["tier"], q["rank"]))
    if not todo:
        print(json.dumps({"post": False, "reason": "BANK EXHAUSTED: research and add new questions to questions.json"}))
        return
    pick = next((q for q in todo if q["topic"] != last_topic), todo[0])
    print(json.dumps({
        "post": True,
        "number": (done[-1]["number"] + 1) if done else 1,
        "date": args.today,
        **pick,
        "recent_topics": [m["topic"] for m in done[-5:]],
        "remaining_in_bank": len(todo) - 1,
    }, indent=2))


if __name__ == "__main__":
    main()
