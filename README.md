# Data Interview Questions

**The most-asked technical interview questions for data analyst, data scientist and data engineer roles. Each one is answered so you can say it out loud, with a runnable example.**

Every question has:

| Section | What you get |
|---|---|
| The 30-second answer | What to say first, in spoken English |
| The deeper answer | What turns a correct answer into a strong one |
| Two worked examples | Two industries, where the second adds a twist that changes the right choice. Runnable, with real output |
| Common wrong answers | The traps interviewers are listening for |
| Follow-ups | The next questions they'll ask, with short answers |
| Explain it to a non-technical person | Because half of every data job is this |

## How questions are chosen

Questions are ranked by how often they appear across frequency-ranked public sources: candidate-reported answer counts, frequency-ordered question lists, and analyses of real interviews. The full ranked bank and its sources are in [`questions.json`](questions.json). Tier 1 questions appear across several sources or at the top of a ranked list, and they're answered first.

Role coverage: **Analyst** (SQL, metrics, BI), **Scientist** (stats, experiments, ML), **Engineer** (modelling, pipelines, Spark/lakehouse), plus **LLM/RAG** and **behavioural** questions.

## Questions

<!-- INDEX:START -->
### Prep by interview type

| Interview | Questions answered | Case files | Prep page |
|---|---:|---:|---|
| Data Analyst (DA) | 3 / 60 | 0 | [Open](prep/data-analyst.md) |
| Data Scientist (DS) | 4 / 76 | 0 | [Open](prep/data-scientist.md) |
| Data Engineer (DE) | 2 / 51 | 0 | [Open](prep/data-engineer.md) |
| ML / AI Engineer (ML) | 1 / 40 | 0 | [Open](prep/ml-engineer.md) |
| Statistics & Experimentation (Stats) | 1 / 22 | 0 | [Open](prep/statistics.md) |

### Answered so far: 4

**SQL**

| # | Question | Tracks | Tier |
|---:|---|---|:---:|
| 001 | [Find the highest-paid employee in each department. Then the top 3. What changes with ties?](questions/001-top-earner-per-department/) | `DA` `DS` `DE` | 1 |
| 003 | [INNER JOIN vs LEFT JOIN: when do you use each, and what goes wrong with LEFT JOIN filters?](questions/003-inner-vs-left-join/) | `DA` `DS` `DE` | 1 |

**Statistics**

| # | Question | Tracks | Tier |
|---:|---|---|:---:|
| 002 | [What is a p-value? Explain it to a non-technical person.](questions/002-what-is-a-p-value/) | `DA` `DS` `Stats` | 1 |

**Machine learning**

| # | Question | Tracks | Tier |
|---:|---|---|:---:|
| 004 | [Explain the bias-variance trade-off. How do you diagnose overfitting?](questions/004-bias-variance-trade-off/) | `DS` `ML` | 1 |
<!-- INDEX:END -->

## Run an example

```bash
pip install -r requirements.txt
python questions/<folder>/example.py
```

Deeper, end-to-end versions of these ideas live in **[Data Explained](https://github.com/suryanaraynan/data-explained)**: real-world case files explained for technical and non-technical readers.

*Drafted with AI assistance; I review every answer, and every example runs in CI.*
