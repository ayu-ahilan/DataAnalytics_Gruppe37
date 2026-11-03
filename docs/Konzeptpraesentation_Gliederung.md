# Konzeptpräsentation: Gliederung (Di, 15.12.2026, 11:00, SW301, 10 Min.)

PDF zusätzlich auf Moodle hochladen. Jede Folie deckt eines der 8 Bewertungskriterien ab.
Stand: angepasst an die ersten Ergebnisse mit echten Daten (03.11.2026).

| # | Folie | Inhalt | Grafik / Tabelle | Kriterium | Zeit |
|---|---|---|---|---|---|
| 1 | Titel | «Wann und wo ist der Zug zu spät?», Gruppe 37, **Marc Stump, Ayushan Ahilan** | – | Struktur | 0:15 |
| 2 | Gliederung | Hintergrund · Ziel & Frage · Daten · Methoden · Erwartete Resultate · Zeitplan | – | Struktur | 0:15 |
| 3 | Hintergrund & Problem | Pünktlichkeit ist zentral für Pendler; SBB zählt einen Zug ab 3 Min. als verspätet; Unterschiede zwischen Regionen und Tageszeiten sind wenig untersucht | – | Hintergrund | 1:15 |
| 4 | Ziel & Forschungsfrage | Forschungsfrage + 3 Hypothesen: **H1** Die Stosszeit erhöht das Verspätungsrisiko, aber *nicht in allen Regionen gleich stark* (Interaktion Region × Stosszeit). **H2** Zugtyp und Betreiber sind die wichtigsten Faktoren (Fernverkehr > S-Bahn). **H3** Niederschlag erhöht das Risiko, aber nur schwach. | – | Ziel | 1:00 |
| 5 | Datenquellen | 3 Quellen via Web-API: Ist-Daten (opentransportdata.swiss, CKAN-API), Service Points (31'095 Haltestellen), Open-Meteo (stündliches Wetter). Zeitraum 14.–27.10.2026, **13 Tage** (19.10. von der Quelle nicht publiziert) → 2,08 Mio. Zug-Halte | Tabelle der 3 Quellen | Daten | 1:15 |
| 6 | Datenstruktur & Integration | SQLite-Schema (halte, stationen, wetter → analyse), Join-Schlüssel `bpuic` und Stunde. Trichter: 2,08 Mio. → 1,77 Mio. (gemessen, plausibel) → **400'135 Ankünfte** an den 100 grössten Bahnhöfen mit Wetter | `outputs/02_integration_trichter.png` | Daten | 1:15 |
| 7 | Methoden | EDA → Klassifikation (Log. Regression, Random Forest, Baseline), zeitlicher Split (Test = letzte 4 Tage), Gütemasse (Precision, Recall, F1, ROC-AUC statt nur Accuracy wegen 6 % Minderheitsklasse); Gruppenvergleich mit separaten Modellen + Logit mit Interaktionsterm; Bonus: k-Means, Karten, Chi²/ANOVA | evtl. Ablauf-Schema | Methoden | 1:45 |
| 8 | Erwartete Resultate (erste Ergebnisse) | Anteil verspätet 6,3 %; Romandie 8,8 % vs. Deutschschweiz 5,8 %. **Stosszeit-Effekt nur in der Deutschschweiz** (8,1 % vs. 5,0 %), in der Romandie kaum (9,0 % vs. 8,8 %), dort steigen Verspätungen über den Tag an. Fernverkehr deutlich häufiger verspätet (international 26 %, S-Bahn 5 %). Regen: 7,8 % vs. 5,6 %. Erwartung für das finale Modell: nur mässige Vorhersagegüte (erste ROC-AUC ≈ 0,68) → Fokus auf Erklärung statt Vorhersage | `outputs/03_verspaetung_tagesverlauf.png` | Erwartete Resultate | 1:00 |
| 9 | Zeitplan & Risiken | Datensammlung ✓, erste Analyse ✓; Feinschliff Modell + Interpretation bis Ende Dez., Abgabe 10.01. Risiken/Limitationen: nur 2 Herbstwochen (kaum Schnee), nur 17 Bahnhöfe in der Romandie, Region auf Kantonsebene, Wetter nur am Ankunftsbahnhof | – | Struktur | 0:45 |
| 10 | Fragen | Danke, Quellen (opentransportdata.swiss, Open-Meteo.com, CC BY 4.0) | – | – | 0:15 |

**Hinweis zu H1:** Ursprünglich war H1 «Stosszeit erhöht das Risiko stärker in der Romandie». Die ersten Daten zeigen das Gegenteil (Logit: OR Stosszeit 1,67 in der Deutschschweiz, Interaktion Romandie × Stosszeit OR 0,60 → in der Romandie ≈ 1,0). Darum ist H1 jetzt ungerichtet formuliert; das Ergebnis kann man im Video als überraschenden Befund diskutieren.

**Tipps:** frei sprechen (Kriterium 7), einheitliches Folien-Design, Achsenbeschriftungen und Quellenangaben auf jeder Grafik (Kriterium 8), Redezeit gleichmässig auf beide verteilen.
