"""
Rebuild navigation from metadata (runs in CI on push to main and daily):
  - README.md index: "Prep by interview type" + answered questions by topic
  - prep/<track>.md: one page per interview type, with every bank question for that
    track (answered ones linked) plus Data Explained case files tagged with it.

Case files are read from a local checkout of suryanaraynan/data-explained, if one
is given: python tools/build_index.py --case-repo ../data-explained
"""
import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
START, END = "<!-- INDEX:START -->", "<!-- INDEX:END -->"
CASE_URL = "https://github.com/suryanaraynan/data-explained/tree/main/posts"
TOPIC = {"sql": "SQL", "stats": "Statistics", "experimentation": "Experimentation & A/B testing",
         "ml": "Machine learning", "python": "Python", "data-modelling": "Data modelling",
         "data-engineering": "Data engineering & pipelines", "spark-lakehouse": "Spark / lakehouse",
         "llm-rag": "LLM / RAG", "bi": "BI / Power BI", "product-metrics": "Product sense & metrics",
         "behavioural": "Behavioural"}
TRACK_INTRO = {
    "data-analyst": "SQL fluency, metrics, BI and turning numbers into decisions.",
    "data-scientist": "SQL, statistics, experiments, ML and product sense.",
    "data-engineer": "SQL, data modelling, pipelines, Spark/lakehouse and data quality.",
    "ml-engineer": "ML fundamentals, evaluation, Python and LLM/RAG systems.",
    "statistics": "Probability, inference, hypothesis tests and experiment design.",
}

ap = argparse.ArgumentParser()
ap.add_argument("--case-repo", default=None)
args = ap.parse_args()

bank = json.loads((ROOT / "questions.json").read_text())
TRACKS = bank["tracks"]
answered = {m["rank"]: m for m in (json.loads(p.read_text()) for p in (ROOT / "questions").glob("*/meta.json"))}
cases = []
if args.case_repo and Path(args.case_repo, "posts").exists():
    cases = sorted((json.loads(p.read_text()) for p in Path(args.case_repo, "posts").glob("*/meta.json")),
                   key=lambda m: m["number"])


def qlink(q, rel=""):
    m = answered.get(q["rank"])
    return f"[{q['question']}]({rel}questions/{m['slug']}/)" if m else f"{q['question']} *(answer coming)*"


# ---------------- prep pages
(ROOT / "prep").mkdir(exist_ok=True)
summary = []
for track, label in TRACKS.items():
    qs = [q for q in bank["questions"] if track in q["tracks"]]
    done = sum(q["rank"] in answered for q in qs)
    tcases = [c for c in cases if track in c.get("tracks", [])]
    summary.append((track, label, done, len(qs), len(tcases)))
    out = [f"# {label}: interview prep", "", TRACK_INTRO.get(track, ""), "",
           f"**{done} of {len(qs)} questions answered** · **{len(tcases)} case file{'' if len(tcases) == 1 else 's'}** · "
           "Tier 1 = asked most often, so start there.", "",
           "← [All interview types](../README.md#prep-by-interview-type)", ""]
    tier1 = [q for q in qs if q["tier"] == 1]
    out += ["## Start here: most-asked (tier 1)", ""] + [f"- {qlink(q, '../')}" for q in tier1] + [""]
    out += ["## All questions by topic", ""]
    for topic in TOPIC:
        tq = [q for q in qs if q["topic"] == topic]
        if not tq:
            continue
        out += [f"### {TOPIC[topic]}", ""]
        out += [f"- {qlink(q, '../')} · tier {q['tier']}" for q in sorted(tq, key=lambda q: (q["tier"], q["rank"]))]
        out.append("")
    out += ["## Case files for this track", "",
            "Worked, real-world examples with a STAR interview script (`INTERVIEW.md`) in each folder.", ""]
    if tcases:
        out += ["| # | Case file | Concept |", "|---:|---|---|"]
        out += [f"| {c['number']:03d} | [{c['title']}]({CASE_URL}/{c['slug']}/) "
                f"([interview script]({CASE_URL}/{c['slug']}/INTERVIEW.md)) | {c['concept'].replace('-', ' ')} |"
                for c in reversed(tcases)]
    else:
        out.append("*None yet.*")
    (ROOT / "prep" / f"{track}.md").write_text("\n".join(out).rstrip() + "\n")

# ---------------- README index
qs_done = sorted(answered.values(), key=lambda m: m["number"])
counts = Counter(q["topic"] for q in qs_done)
short = {"data-analyst": "DA", "data-scientist": "DS", "data-engineer": "DE", "ml-engineer": "ML", "statistics": "Stats"}
lines = ["### Prep by interview type", "",
         "| Interview | Questions answered | Case files | Prep page |", "|---|---:|---:|---|"]
lines += [f"| {label} | {d} / {n} | {c} | [Open](prep/{t}.md) |" for t, label, d, n, c in summary]
lines += ["", f"### Answered so far: {len(qs_done)}", ""]
for topic in (t for t in TOPIC if counts.get(t)):
    lines += [f"**{TOPIC[topic]}**", "", "| # | Question | Tracks | Tier |", "|---:|---|---|:---:|"]
    for q in (q for q in qs_done if q["topic"] == topic):
        tags = " ".join(f"`{short[t]}`" for t in q.get("tracks", []))
        lines.append(f"| {q['number']:03d} | [{q['question']}](questions/{q['slug']}/) | {tags} | {q['tier']} |")
    lines.append("")
readme = ROOT / "README.md"
head, rest = readme.read_text().split(START, 1)
_, tail = rest.split(END, 1)
readme.write_text(f"{head}{START}\n" + "\n".join(lines).rstrip() + f"\n{END}{tail}")
print(f"Index rebuilt: {len(qs_done)} answered, {len(cases)} case files, {len(TRACKS)} prep pages")
