# Concept presentation: outline (Tue, 15 Dec 2026, 11:00, SW301, 10 min)

Also upload the PDF to Moodle (deadline 10 Jan 2027, 23:59). Each slide covers one of the 8 assessment criteria.
Status: adapted to the first results with real data (3 Nov 2026), translated into English (7 Nov 2026).

| # | Slide | Content | Chart / table | Criterion | Time |
|---|---|---|---|---|---|
| 1 | Title | “When and where are trains late?”, Group 37, **Marc Stump, Ayushan Ahilan** | – | Structure | 0:15 |
| 2 | Outline | Background · objective & question · data · methods · expected results · timeline | – | Structure | 0:15 |
| 3 | Background & problem | Punctuality is central for commuters; SBB counts a train as late from 3 min; differences between regions and times of day are rarely studied | – | Background | 1:15 |
| 4 | Objective & research question | Research question + 3 hypotheses: **H1** peak hours increase the risk of delay, but *not equally in all regions* (interaction region × peak). **H2** train type and operator are the most important factors (long-distance > S-Bahn). **H3** precipitation increases the risk, but only slightly. | – | Objective | 1:00 |
| 5 | Data sources | 3 sources via web APIs: actual data (opentransportdata.swiss, CKAN API), service points (31,095 stations), Open-Meteo (hourly weather). Period 14–27 Oct 2026, **13 days** (19 Oct not published by the source) → 2.08 M train stops | table of the 3 sources | Data | 1:15 |
| 6 | Data structure & integration | SQLite schema (stops, stations, weather → analysis), join keys `bpuic` and hour. Funnel: 2.08 M → 1.77 M (measured, plausible) → **400,135 arrivals** at the 100 largest stations with weather | `outputs/slide_chart_integration_funnel.png` | Data | 1:15 |
| 7 | Methods | EDA → classification (logistic regression, random forest, baseline), temporal split (test = last 4 days), measures of fit (precision, recall, F1, ROC-AUC instead of accuracy only because of the 6% minority class); group comparison with separate models + logit with interaction term; bonus: k-means, maps, chi²/ANOVA | – | Methods | 1:45 |
| 8 | Expected results (first findings) | Share late 6.3%; Romandy 8.8% vs. German-speaking 5.8%. **Peak-hour effect only in German-speaking Switzerland** (8.1% vs. 5.0%), hardly in Romandy (9.0% vs. 8.8%), where delays rise over the day. Long-distance trains are late much more often (international 26%, S-Bahn 5%). Rain: 7.8% vs. 5.6%. Expectation for the final model: only moderate predictive power (first ROC-AUC ≈ 0.68) → focus on explanation rather than prediction | `outputs/slide_chart_delay_by_hour.png` | Expected results | 1:00 |
| 9 | Timeline & risks | Data collection ✓, first analysis ✓; refine model + interpretation by end of Dec, submission 10 Jan. Risks/limitations: only 2 autumn weeks (hardly any snow), only 17 stations in Romandy, region at canton level, weather only at the arrival station | – | Structure | 0:45 |
| 10 | Questions | Thank you, sources (opentransportdata.swiss, Open-Meteo.com, CC BY 4.0), GitHub link | – | – | 0:15 |

**Note on H1:** originally H1 was “peak hours increase the risk more strongly in Romandy”. The first data shows the opposite (logit: OR peak 1.67 in German-speaking Switzerland, interaction Romandy × peak OR 0.60 → ≈ 1.0 in Romandy). H1 is therefore phrased without a direction; the result can be discussed in the video as a surprising finding.

**Tips:** speak freely (criterion 7), consistent slide design, axis labels and sources on every chart (criterion 8), split the speaking time evenly between both of us.
