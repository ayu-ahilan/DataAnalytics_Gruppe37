# Concept presentation: outline (Tue, 15 Dec 2026, 11:00–12:45, SW301, 10 min)

Also upload the slides as PDF to Moodle (deadline 10 Jan 2027, 23:59). Each slide covers one of the 8 assessment criteria.
Status: updated to the six-week data (24 Nov 2026).

| # | Slide | Content | Chart / table | Speaker | Time |
|---|---|---|---|---|---|
| 1 | Title | “When and where are trains late?”, Group 37, **Marc Stump, Ayushan Ahilan** | – | Ayushan | 0:15 |
| 2 | Outline | Background · question · data · methods · expected results · timeline | – | Ayushan | 0:15 |
| 3 | Background & problem | Punctuality is reported as one average; differences between regions and times of day are rarely studied; open actual data shows every stop; SBB threshold 3 min | – | Ayushan | 1:15 |
| 4 | Objective & research question | Research question + H1 (peak effect differs between regions), H2 (train type and operator matter most), H3 (rain matters slightly) | – | Ayushan | 1:00 |
| 5 | Data sources | 3 sources via web APIs; 5 Oct – 15 Nov 2026, six full weeks; 6.73 M train stops, 31,095 stations, 103,200 hourly weather values | table of the 3 sources | Ayushan | 1:00 |
| 6 | Data structure & integration | SQLite schema (stops, stations, weather → analysis), join keys `bpuic` and hour, funnel 6.73 M → 1.30 M arrivals, knock-on delay via `LAG` | `outputs/slide_chart_integration_funnel.png` | Marc | 1:15 |
| 7 | Methods | EDA → classification (logistic regression, random forest, gradient boosting vs. baseline, rolling CV over 6 weeks) → measures of fit (precision, recall, F1, ROC-AUC, PR-AUC, tuned threshold) → group comparison (models per group, permutation importance, logit with interaction, cluster-robust SE, knock-on delay); bonus: map, k-means, chi²/ANOVA/correlation, GitHub | – | Marc | 1:45 |
| 8 | Expected results (first findings) | 6.1% late; German-speaking 5.5% vs. Romandy 8.6%; peak-hour odds ratio 1.79 vs. 1.19; Romandy stays high in the evening; 81% of late arrivals were already late at the previous stop; ROC-AUC 0.73 (0.95 with the previous delay) | `outputs/slide_chart_delay_by_hour.png` | Marc | 1:30 |
| 9 | Timeline & risks | Data, integration, EDA and models done; December: final slides, video, appendix; risks: six autumn weeks, 18 stations in Romandy, region via canton, weather only at arrival station, causes of disruptions unknown | – | Ayushan | 0:45 |
| 10 | Questions | Thank you, sources, GitHub link | – | both | 0:15 |

Total ≈ 9:15 (Ayushan ≈ 4:30, Marc ≈ 4:30).

**Note on H1:** originally H1 was “peak hours increase the risk more strongly in Romandy”. The data shows the opposite; H1 was rephrased without a direction (documented in `docs/AI_usage.md`).

**Tips:** speak freely (criterion 7), consistent slide design, axis labels and sources on every chart (criterion 8), balanced speaking time.
