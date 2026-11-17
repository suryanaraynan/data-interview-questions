"""Rebuild the question index in README.md from questions/*/meta.json (runs on push to main)."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
START, END = "<!-- INDEX:START -->", "<!-- INDEX:END -->"
LABEL = {"sql": "SQL", "stats": "Statistics", "experimentation": "Experimentation", "ml": "Machine learning",
         "python": "Python", "data-modelling": "Data modelling", "data-engineering": "Data engineering",
         "spark-lakehouse": "Spark / lakehouse", "llm-rag": "LLM / RAG", "bi": "BI / Power BI",
         "product-metrics": "Product & metrics", "behavioural": "Behavioural"}
qs = sorted((json.loads(p.read_text()) for p in (ROOT / "questions").glob("*/meta.json")),
            key=lambda m: m["number"])
counts = Counter(q["topic"] for q in qs)
lines = [f"**{len(qs)} question{'' if len(qs) == 1 else 's'} answered** · "
         + " · ".join(f"{LABEL.get(t, t)}: {n}" for t, n in counts.most_common()), ""]
for topic in sorted(counts, key=lambda t: list(LABEL).index(t) if t in LABEL else 99):
    lines += [f"### {LABEL.get(topic, topic)}", "", "| # | Question | Roles | Tier |", "|---:|---|---|:---:|"]
    for q in (q for q in qs if q["topic"] == topic):
        roles = ", ".join(r.title() for r in q["roles"])
        lines.append(f"| {q['number']:03d} | [{q['question']}](questions/{q['slug']}/) | {roles} | {q['tier']} |")
    lines.append("")
readme = ROOT / "README.md"
head, rest = readme.read_text().split(START, 1)
_, tail = rest.split(END, 1)
readme.write_text(f"{head}{START}\n" + "\n".join(lines).rstrip() + f"\n{END}{tail}")
print(f"Index rebuilt: {len(qs)} questions")
