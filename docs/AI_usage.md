# Documentation of AI usage (Group 37)

> Mandatory part of the submission: slides and video must show which AI tools were used and how, which advantages and disadvantages we found, and where something did not work. Keep this file up to date.

## Tools used
| Tool | Used for | Who / when |
|---|---|---|
| Claude in the browser (claude.ai, Cowork) | summarising the Moodle requirements, finding a topic, project structure, first draft of all scripts and notebooks, research on the data sources | Ayushan, 3 Nov 2026 |
| Claude Code (desktop app, working directly in the project folder) | running and monitoring the data collection, running the notebooks with real data, writing the interpretations, adapting the presentation outline, creating and checking the concept slides, setting up the Git repository, translating all deliverables into English | Ayushan, 3–7 Nov 2026 |

*(Add further tools here, e.g. GitHub Copilot, if they are used later.)*

## What the AI did
**Phase 1 – draft (Claude in the browser)**
- Proposed a topic based on the Moodle requirements that covers all minimum requirements and several bonus points.
- Researched the data sources (CKAN API of opentransportdata.swiss, Open-Meteo) and took the column formats from the documentation (cookbook “Actual data”).
- Wrote the code for data collection, SQLite schema, integration, EDA, models, clustering and tests.
- Ran the code with **synthetic test data** in the format of the real sources to find errors (the test data is not part of the analysis).

**Phase 2 – execution with real data (Claude Code)**
- Started `run_collection.py`, detected interruptions and resumed the run; identified the missing daily file (19 Oct) as a gap in the source.
- Ran notebooks 02–05, checked the results for plausibility and wrote the “Findings” / “Interpretation” sections with the real numbers.
- Adapted hypothesis H1 in the presentation outline to the results.
- Created the concept presentation (10 slides, speaker notes), redrew two charts in the slide design and rendered the slides to find and fix layout problems.
- Set up the Git repository (data excluded).

**Phase 3 – translation into English (Claude Code)**
- After the lecturers confirmed that all deliverables must be in English, translated the slides, speaker notes, charts, notebooks, code comments, README and documents.
- Renamed the database tables and columns to English (e.g. `halte` → `stops`, `verspaetet` → `late`) and re-ran all notebooks, so that the outputs are in English as well.

## Advantages
- Very fast start: a working project structure in a short time.
- Helpful for researching the API endpoints and for handling special cases (e.g. 7-/9-digit BPUIC, SLOID, daylight saving time change).
- Good suggestions for methods (temporal train/test split, permutation importance, effect sizes for large samples).
- Claude Code works directly in the project folder: it could run scripts itself, see errors in the log and check the results directly in the database instead of only suggesting code.
- The presentation was created directly from the real results; the numbers on the slides come from the notebooks.
- The translation including the database renaming took only a short time and was verified by re-running all notebooks.

## Disadvantages / limitations
- The AI in the browser could not access the real APIs from its environment → the code was first only tested with synthetic data; only Claude Code ran it with real data.
- The assignment to language regions is a simplification (canton + exception list) that we have to check ourselves.
- Risk of adopting code without understanding it → we must be able to explain every step ourselves (this is part of the assessment).
- The AI also writes interpretations very confidently that are wrong (example Geneva, see below) → every statement must be checked against the numbers.
- The work was spread over several AI sessions; information from one session had to be copied manually into the next one.
- The AI first wrote everything in German because we communicated with it in German; the language requirement of the course had to be clarified by us with the lecturers.

## Where something did not work
- **Data collection (3 Nov 2026, with Claude Code):**
  - The first run stopped after 3 days; a second run was terminated when the Claude session that had started it was closed. Thanks to “skip days that are already loaded”, the run could simply be restarted each time.
  - The CKAN API of opentransportdata.swiss temporarily answered with **403 Forbidden** (probably throttling after several GB of downloads). The script retries requests automatically; the block was deliberately not circumvented. The API was still blocked when notebook 01 was re-run on 7 Nov 2026, which is why its first cell shows “API not reachable”.
  - No daily file was published on the platform for **19 Oct 2026** (32 instead of 33 days in the period 1 Oct – 2 Nov). Result: 13 instead of 14 operating days (14–27 Oct without 19 Oct), 2,078,429 train stops.
  - Weather: 100 stations × 360 hours = 36,000 values. The duplicate hour of the daylight saving time change (25 Oct) is removed while loading.
- **Notebooks with real data (3 Nov 2026):** notebooks 02–05 ran without code changes, so the AI's assumptions about column names and formats were correct. Claude wrote the interpretation texts based on the results; one statement (“Geneva is particularly unpunctual”) was wrong and was corrected after checking the data → always check AI interpretations against the numbers.
- Hypothesis H1 of the first draft (“peak hours increase the risk more strongly in Romandy”) is **not** supported by the data: the peak-hour effect only appears in German-speaking Switzerland.
- **Translation (7 Nov 2026):** after renaming the categories (e.g. “Andere” → “Other”), the order of the one-hot-encoded columns changed, so the random forest results shifted slightly (e.g. recall 0.41 → 0.39, ROC-AUC 0.68 unchanged). The logit model, the tests and the clustering produced identical results.
