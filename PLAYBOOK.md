# Playbook for scheduled runs

This file is the instruction set for the scheduled Claude run that answers about **two interview questions a week**, on irregular days when nothing else goes out (no [Data Explained](https://github.com/suryanaraynan/data-explained) case file, no project milestone). Together that keeps Surya active on 5–6 days a week. Each run starts with no memory, so everything it needs is here.

**Questions are committed straight to `main`** (Surya chose this; they're short, and he reads them as a daily flashcard). That makes accuracy the whole job: never publish anything you haven't checked.

## 0. Decide whether today is a question day

```bash
pip install -q --break-system-packages -r requirements.txt
python tools/next_question.py --today <today in Europe/London, YYYY-MM-DD>
```

- `"post": false` → **stop**. Finish with the `reason` in one line. No commit, no message.
- `"post": true` → answer exactly the `question` it returns, using its `number`, `rank`, `topic`, `roles`, `tier` and `evidence`.
- If it says the bank is exhausted: research the next most-asked questions (web search, frequency-ranked sources only), append them to `questions.json` with tier and evidence, commit that, and finish. Answer one tomorrow.

## 1. Check your facts before writing

- For anything version- or vendor-specific (SQL dialect support, Spark/Delta behaviour, Power BI/DAX, LLM tooling), **verify with a web search** and prefer official docs. If dialects differ, say so.
- Never invent statistics, company names or quotes. The "How often it's asked" line uses only the `evidence` from `questions.json`; link to `questions.json` rather than restating sources you haven't opened.

## 2. Write the example: `questions/<NNN>-<slug>/example.py`

- Include one for every technical question; behavioural questions skip it. It must run **offline** in under 30 seconds with `requirements.txt` (DuckDB for SQL, pandas/sklearn/scipy otherwise). No API keys or network.
- Use a **small, made-up, real-world-flavoured** table (8–20 rows) from a fictional organisation, and rotate domains: council, NHS trust, retailer, bank, transport operator, energy supplier, HR, subscriptions. Deliberately include the edge case the question is really about (ties, NULLs, duplicates, imbalance, skew).
- Print every number the README quotes.
- Add a visual (`chart_1.png`) **only where it helps**, e.g. a comparison table, a distribution, a confusion matrix, a before/after. Use `tools/viz_style.py` (`table_png`, `figure`, `headline`, `callout`, …). The headline states the takeaway; add a subtitle and a footer "Made-up data for a fictional <org> | Data Interview Questions #NNN". Open the PNG and check it for overlaps and clipping.
- Run it and fix it until it runs cleanly.

## 3. Write `questions/<NNN>-<slug>/README.md`

Follow `questions/_template/README.md` exactly. `questions/001-top-earner-per-department/` is the reference example for depth, tone and length (about 600–900 words).

- **The 30-second answer is spoken English** in quotation marks. It answers the question directly, then names the one decision or trade-off that shows judgement.
- **The deeper answer:** 3–5 bullets on what separates a strong answer: clarifying questions, why not the obvious alternative, edge cases, performance.
- **Common wrong answers:** 3–5 concrete traps.
- **Follow-ups:** 3–4 likely next questions, each answered in 1–3 sentences.
- **Explain it to a non-technical person:** 2–3 sentences, an everyday analogy, zero jargon.
- **Related:** link a Data Explained case file only if it genuinely uses the idea. Check the posts list at https://github.com/suryanaraynan/data-explained/tree/main/posts.
- For **behavioural** questions, replace the example section with: what the interviewer is really assessing, a STAR skeleton, a worked example answer framed around a portfolio project (never a fake job), and the mistakes to avoid.
- UK English. No hype words, no emojis.

## 4. Write `questions/<NNN>-<slug>/meta.json`

```json
{"number": N, "rank": R, "date": "YYYY-MM-DD", "slug": "<NNN>-<short-kebab>",
 "question": "<question exactly as in questions.json>", "short_title": "<under 60 characters>",
 "topic": "<topic>", "roles": [...], "tier": T}
```

## 5. Commit to main and notify

- Change **only** `questions/<NNN>-<slug>/`. CI rebuilds the README index.
- `git add questions/<NNN>-<slug> && git commit -m "Q-<NNN>: <short_title>"`, then `git -c push.negotiate=true push origin main`.
- Send **one** SendUserMessage as a flashcard:
  ```
  Interview flashcard #NNN (<Topic>, Tier T)
  Q: <question>

  Try answering out loud first. Then:
  <the 30-second answer, without the quotation marks>

  Full answer: https://github.com/suryanaraynan/data-interview-questions/tree/main/questions/<NNN>-<slug>
  ```

## Final checks before pushing

- [ ] `python questions/<slug>/example.py` runs cleanly; every number in the README appears in its output
- [ ] Vendor- or dialect-specific claims verified
- [ ] All template sections present, about 600–900 words
- [ ] Any visual checked by eye
- [ ] Only `questions/<NNN>-<slug>/` changed
