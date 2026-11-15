# FDE Interview Tracker

A daily practice tracker for Forward Deployed Engineer interview questions from Aced.

**Live site:** https://fairyfox5700.github.io/fde-interview-tracker/

## Automatic refresh

GitHub Actions fetches the complete public FDE question listing from Aced every day at 05:15 UTC. It validates the result, updates `index.html`, and commits only when the embedded dataset changed. The workflow can also be run manually from the Actions tab.

The updater uses only the Python standard library and fails safely if Aced returns fewer than 100 questions or if pagination is incomplete.

## Features

- Daily-refreshed FDE question dataset
- Expandable interview answers for every current Design, AI, Coding, and Behavioral question
- Question-specific C#-oriented coding solutions and production-focused AI guidance
- Truthful customizable STAR templates for experience-based questions; placeholders are never presented as personal facts
- Architecture Lab with one full source-backed case for each of the 12 current system-design questions
- Exact question coverage is validated against the daily-refreshed tracker dataset
- Hello Interview–style flow: understanding the problem, functional and non-functional requirements, entities, APIs, high-level design, deep dives, and level expectations
- Responsive SVG architecture diagram for every system-design case, with typed components and labeled data flows
- Clear labels separating published facts from adapted or proposed design choices
- Links to the original Microsoft architecture and runnable implementation where available
- Independent Architecture Lab progress saved in the browser
- Daily question set and adjustable goal
- Practice streak and seven-day activity chart
- New → Practicing → Mastered status cycle
- Topic, company, status, and text filters
- Local browser persistence and CSV progress export with clickable source links
- LeetCode Patterns tracker: 87 classic coding-interview problems tagged by company (one-click "Google only" filter) and by algorithmic pattern (Arrays & Hashing, Two Pointers, Sliding Window, Binary Search, Trees, Graphs, DP, Backtracking, and more) to plan focused practice before SWE round 2-3 coding interviews
- No backend or account required

## System design template

`docs/system-design-template.md` is the Hello-Interview-style template each Architecture Lab case is written against (Understanding the Problem, Set Up, 4 workflows in High-Level Design, one Deep Dive per workflow, Mid/Senior/Staff+ level expectations). Use it as the starting point when adding or rewriting a case.

## Local checks

```bash
python -m unittest tests/test_update_questions.py -v
python scripts/update_questions.py --check
```

> Interview reports are community-sourced. Question wording and company attribution may change over time.
