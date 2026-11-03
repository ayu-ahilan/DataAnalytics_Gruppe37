# Dokumentation der KI-Nutzung (Gruppe 37)

> Pflichtteil der Abgabe: Folien und Video müssen zeigen, welche KI-Tools wie genutzt wurden, welche Vor- und Nachteile es gab und wo etwas nicht funktioniert hat. Diese Datei laufend ergänzen.

## Eingesetzte Tools
| Tool | Wofür | Wer / Wann |
|---|---|---|
| Claude im Browser (claude.ai, Cowork) | Moodle-Anforderungen zusammengefasst, Themenfindung, Projektstruktur, erster Entwurf aller Skripte und Notebooks, Recherche zu den Datenquellen | Ayushan, 03.11.2026 |
| Claude Code (Desktop-App, direkt im Projektordner) | Datensammlung ausgeführt und überwacht, Notebooks mit echten Daten ausgeführt, Interpretationen geschrieben, Präsentationsgliederung angepasst, Konzeptfolien erstellt und geprüft, GitHub-Repo angelegt | Ayushan, 03.11.2026 |

*(Weitere Tools, z. B. GitHub Copilot, hier eintragen, falls sie später genutzt werden.)*

## Was die KI gemacht hat
**Phase 1 – Entwurf (Claude im Browser)**
- Aus den Moodle-Anforderungen ein Thema vorgeschlagen, das alle Mindestanforderungen und mehrere Bonuspunkte abdeckt.
- Datenquellen recherchiert (CKAN-API von opentransportdata.swiss, Open-Meteo), Spaltenformate aus der Dokumentation (Cookbook «Actual data») übernommen.
- Code für Datensammlung, SQLite-Schema, Integration, EDA, Modelle, Clustering und Tests geschrieben.
- Den Code mit **synthetischen Testdaten** im Format der echten Quellen durchlaufen lassen, um Fehler zu finden (die Testdaten sind nicht Teil der Analyse).

**Phase 2 – Ausführung mit echten Daten (Claude Code)**
- `run_collection.py` gestartet, Abbrüche erkannt und den Lauf fortgesetzt; die fehlende Tagesdatei (19.10.) als Lücke der Quelle identifiziert.
- Notebooks 02–05 ausgeführt, Ergebnisse auf Plausibilität geprüft und die Abschnitte «Erkenntnisse» / «Interpretation» mit den echten Zahlen geschrieben.
- Hypothese H1 in der Präsentationsgliederung an die Ergebnisse angepasst.
- Konzeptpräsentation (10 Folien, Sprechernotizen) erstellt, zwei Grafiken im Folien-Design neu gezeichnet und die Folien gerendert, um Layoutfehler zu finden und zu korrigieren.
- Git-Repository angelegt (Daten ausgeschlossen) und auf GitHub veröffentlicht.

## Vorteile
- Sehr schneller Start: lauffähige Projektstruktur in kurzer Zeit.
- Hilfreich beim Recherchieren der API-Endpunkte und beim Umgang mit Sonderfällen (z. B. 7-/9-stellige BPUIC, SLOID, Zeitumstellung).
- Gute Vorschläge für Methoden (zeitlicher Train/Test-Split, Permutation Importance, Effektstärken bei grossen Stichproben).
- Claude Code arbeitet direkt im Projektordner: Es konnte Skripte selbst ausführen, Fehler im Log sehen und die Ergebnisse direkt in der Datenbank kontrollieren, statt nur Code vorzuschlagen.
- Die Präsentation entstand direkt aus den echten Ergebnissen; die Zahlen auf den Folien stammen aus den Notebooks.

## Nachteile / Grenzen
- Die KI im Browser konnte die echten APIs aus ihrer Umgebung nicht abrufen → Code wurde zuerst nur mit synthetischen Daten getestet; erst Claude Code hat ihn mit echten Daten laufen lassen.
- Die Zuordnung zur Sprachregion ist eine Vereinfachung (Kanton + Ausnahmeliste), die wir selbst prüfen müssen.
- Gefahr, Code zu übernehmen, ohne ihn zu verstehen → wir müssen jeden Schritt selbst erklären können (wird bei der Bewertung geprüft).
- Die KI schreibt auch Interpretationen sehr überzeugt, die nicht stimmen (Beispiel Genf, siehe unten) → jede Aussage gegen die Zahlen prüfen.
- Die Arbeit verteilte sich auf mehrere KI-Sessions; Informationen aus einer Session mussten manuell in die nächste kopiert werden.

## Wo etwas nicht funktioniert hat
- **Datensammlung (03.11.2026, mit Claude Code):**
  - Der erste Lauf brach nach 3 Tagen ab; ein zweiter Lauf wurde beendet, als die Claude-Session geschlossen wurde, die ihn gestartet hatte. Dank «bereits geladene Tage überspringen» konnte jeweils einfach neu gestartet werden.
  - Die CKAN-API von opentransportdata.swiss antwortete zeitweise mit **403 Forbidden** (vermutlich Drosselung nach mehreren GB Downloads). Das Skript wiederholt Anfragen automatisch; der Block wurde bewusst nicht umgangen.
  - Für den **19.10.2026** ist auf der Plattform keine Tagesdatei publiziert (32 statt 33 Tage im Zeitraum 01.10.–02.11.). Ergebnis: 13 statt 14 Betriebstage (14.–27.10. ohne 19.10.), 2'078'429 Zug-Halte.
  - Wetter: 100 Bahnhöfe × 360 Stunden = 36'000 Werte. Die doppelte Stunde der Zeitumstellung (25.10.) wird beim Laden entfernt.
- **Notebooks mit echten Daten (03.11.2026):** Die Notebooks 02–05 liefen ohne Code-Änderung durch. Die KI-Annahmen zu Spaltennamen und Formaten stimmten also. Die Interpretationstexte hat Claude aus den Ergebnissen geschrieben; eine Aussage («Genf ist besonders unpünktlich») war falsch und wurde nach Kontrolle der Daten korrigiert → KI-Interpretationen immer gegen die Zahlen prüfen.
- Die Hypothese H1 aus dem ersten Entwurf («Stosszeit erhöht das Risiko stärker in der Romandie») wird von den Daten **nicht** gestützt: Der Stosszeit-Effekt zeigt sich nur in der Deutschschweiz.
