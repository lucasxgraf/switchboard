# Switchboard — LLM Gateway

Arbeitstitel. Ein selbst gehostetes Gateway vor mehreren LLM-Anbietern. OpenAI-kompatibler Endpunkt, Routing auf das jeweils ausreichende Modell, Cache, Fallback bei Ausfall, Dashboard mit Kosten, Latenz und Qualität.

Diese Datei ist das Briefing für Claude Code und gleichzeitig mein eigener Plan. Sie wird während des Projekts fortgeschrieben.

---

## 1. Warum dieses Projekt

Zwei eigene Anwendungen rufen heute direkt Groq und Gemini: Code-A-Cuisine und Quizly. Beide werden hinter das Gateway gehängt. Damit ist es kein Demo-Projekt, sondern Infrastruktur vor laufenden Anwendungen.

Ziel im Dezember: eine gemessene Aussage der Form "X Prozent weniger Kosten bei gleicher Antwortqualität, gemessen an N Aufgaben", plus ein Dashboard, das jemand in einer Minute versteht.

Was das Projekt beweisen soll:

- Ich kann ein System bauen, das nicht nur funktioniert, sondern dessen Qualität ich messe.
- Ich kann Streaming, Nebenläufigkeit und Fehlerfälle im Backend beherrschen.
- Ich kann ein Frontend bauen, das echte Daten zeigt und nicht nur eine Formularmaske ist.

Was es ausdrücklich nicht ist: eine Neuerfindung. LiteLLM und OpenRouter machen dasselbe und besser. Der Unterschied ist, dass ich jede Entscheidung darin begründen kann. Der Vergleich mit LiteLLM steht im README, nicht im Kleingedruckten.

## 2. Rahmen

- Zeitraum: September bis Ende Dezember 2026, rund 16 Wochen.
- Zeit: 45 bis 60 Minuten an Werktagen. Bewerbungen haben Vorrang, an manchen Tagen passiert nichts.
- API-Kosten: Ziel unter 50 Euro über die gesamte Laufzeit. Siehe Abschnitt 7.
- Deployment auf dem eigenen IONOS-VPS neben den bestehenden Projekten.

## 3. Stack

| Bereich | Wahl | Begründung |
|---|---|---|
| Backend | Django + DRF unter ASGI (Uvicorn) | Django kann ich, ASGI ist neu und für Streaming nötig |
| Worker | django-rq | kenne ich aus Videoflix |
| Datenbank | PostgreSQL | Zeitreihen der Requests, Aggregationen im ORM |
| Cache/Queue | Redis | Rate Limits, Cache-Index, Job-Queue |
| Frontend | React + TypeScript + Tailwind, Vite | Lernziel des Projekts |
| Charts | Recharts | reicht, kein D3-Ausflug |
| Container | Docker Compose | wie bei Videoflix |
| CI | GitHub Actions | Tests, Linting, Build |
| Fehler | Sentry | Backend und Frontend |

### Anbieter

Vier Stück, bewusst unterschiedlich:

| Anbieter | Art | Kosten | Warum dabei |
|---|---|---|---|
| Groq | Cloud, sehr schnelle Inferenz für offene Modelle | Gratis-Kontingent | nutze ich schon in Code-A-Cuisine |
| Google Gemini | Cloud, eigenes API-Format | Gratis-Kontingent | nutze ich schon in Quizly, zweites Format zum Übersetzen |
| Anthropic oder OpenAI | Cloud, hochwertige Stufe | bezahlt | dritte API-Form, dient als Qualitätsreferenz |
| Ollama | lokale Laufzeit auf dem MacBook (M3) | kostenlos | kostenlose Stufe für Routing-Versuche |

**Ollama ist nicht Groq.** Groq ist ein Cloud-Dienst mit eigener Hardware. Ollama ist ein Programm, das offene Modelle (Llama, Mistral, Qwen) lokal auf meinem Rechner ausführt. Ein 7B- oder 8B-Modell läuft auf dem M3 flüssig. Für das Projekt ist Ollama die günstigste Routing-Stufe und macht den Router interessanter: Die Frage "wann reicht ein kleines lokales Modell" ist inhaltlich reizvoller als "wann reicht das billigere von zwei bezahlten Modellen".

Einschränkung: Ollama läuft lokal, nicht auf dem VPS. Im Produktivbetrieb ist diese Stufe deshalb nicht verfügbar, in Eval-Läufen schon. Das gehört so ins README.

Bewusst nicht: FastAPI (Django ist der Punkt, den ich zeigen will), LangChain (versteckt genau das, was ich lernen soll), Kubernetes, Grafana.

## 4. Nichtziele

Damit der Umfang nicht wächst:

- Keine Mandantenverwaltung mit Teams, Rollen und Rechten. Ein Nutzer, mehrere API-Keys.
- Keine Weboberfläche zum Chatten. Das Gateway hat keine eigene Endnutzer-UI.
- Kein Finetuning, keine eigenen Modelle.
- Kein Prompt-Management. Prompts liegen in den aufrufenden Anwendungen.
- Keine Unterstützung für Bilder, Audio oder Tool-Calling in Version 1. Nur Chat Completions, mit und ohne Streaming.

## 5. Architektur in einem Absatz

Ein Client schickt eine Chat-Completion-Anfrage an `/v1/chat/completions` mit einem Gateway-Key. Das Gateway prüft den Key, schlägt im Cache nach, entscheidet über das Zielmodell, ruft den Anbieter, zählt Tokens und Kosten, schreibt einen Request-Datensatz und gibt die Antwort zurück. Bei Streaming werden die Chunks durchgereicht und parallel gepuffert, damit am Ende trotzdem abgerechnet und gecacht werden kann. Fällt ein Anbieter aus, greift eine Fallback-Kette. Die Auswertung läuft asynchron im Worker, damit sie die Antwortzeit nicht belastet.

## 6. Meilensteine

Jeder Meilenstein hat ein hartes Abschlusskriterium. Solange das nicht erfüllt ist, geht es nicht weiter.

### M1 (Woche 1 bis 2) — Durchleiten

- `/v1/chat/completions`, kompatibel zum OpenAI-Format, nicht-streamend und streamend.
- API-Key-Modell, Prüfung per Header.
- Ein Anbieter (Groq), Request und Response werden vollständig protokolliert.
- Docker Compose lokal, Deployment auf dem VPS, Sentry angebunden.
- Code-A-Cuisine schickt seine Anfragen über das Gateway.

**Fertig, wenn:** Code-A-Cuisine läuft in Produktion über das Gateway und ich kann in der Datenbank jeden Aufruf sehen.

API-Kosten in diesem Meilenstein: praktisch null.

### M2 (Woche 3 bis 5) — Robustheit und Abrechnung

- Anbieter-Abstraktion, vier Anbieter hinter einer einheitlichen Schnittstelle.
- Token- und Kostenerfassung pro Anfrage, auch bei Streaming.
- Timeouts, Retries mit exponentiellem Backoff, Fallback-Kette, Circuit Breaker mit Half-Open-Zustand.
- Rate Limit pro Key über Redis, korrektes 429 mit `Retry-After`.
- Quizly umgestellt.

**Fertig, wenn:** Ich schalte einen Anbieter künstlich ab und der Verkehr läuft ohne Fehler beim Client weiter.

### M3 (Woche 6 bis 8) — Eval-Harness

Der wichtigste Abschnitt. Ohne ihn ist das Projekt eine weitere Demo.

- 50 bis 60 Aufgaben über mehrere Kategorien (Extraktion, Klassifikation, Zusammenfassung, Rechnen, längeres Schreiben). Von Hand geschrieben, nicht generiert.
- Runner, der jede Aufgabe gegen jedes Modell laufen lässt und Ergebnis, Kosten, Latenz speichert. Ergebnisse auf der Platte cachen, Schlüssel aus Aufgabe, Modell und Parametern.
- Judge-Modell bewertet die Antworten gegen eine Rubrik.
- 50 Bewertungen von Hand nachlabeln und die Übereinstimmung mit dem Judge messen. Taugt der Judge nicht, ist jede spätere Zahl wertlos.
- Erste rohe Dashboard-Ansicht, weil ich die Ergebnisse ohnehin ansehen muss.

**Fertig, wenn:** Eine Tabelle existiert, die für jedes Modell Qualität, Kosten und Latenz pro Kategorie zeigt, und ich weiß, wie zuverlässig mein Judge ist.

### M4 (Woche 9 bis 12) — Router und Cache

- Exakter Cache über Hash aus Nachrichten, System-Prompt, Modell, Temperatur und weiteren Parametern. Ein Cache, der den System-Prompt ignoriert, liefert Antworten aus fremdem Kontext.
- Semantischer Cache über Embeddings, mit messbarer Fehltrefferquote. Wenn die Quote schlecht ist, bleibt er aus. Das ist ein akzeptables Ergebnis, kein Scheitern.
- Router Variante A: Klassifikation der Anfrage vorab, Zuordnung zu einer Modellstufe.
- Router Variante B: Kaskade. Erst das günstige Modell, ein Prüfer entscheidet über Eskalation.
- Beide gegen dasselbe Eval-Set messen.

**Fertig, wenn:** Eine Tabelle existiert mit einer Zeile pro Ausbaustufe und den Spalten Kosten, Qualität und Latenz. Aus dieser Tabelle kommt die Zahl fürs README.

### M5 (Woche 13 bis 16) — Dashboard und Abschluss

- React-Dashboard: Übersicht (Kosten pro Tag, Modellverteilung, Cache-Trefferquote, Fehlerquote), Request-Explorer mit Filter und Detailansicht, Eval-Vergleich zweier Läufe.
- Tests aufräumen.
- README mit Architekturbild, den Zahlen und der Abgrenzung gegenüber LiteLLM und OpenRouter.
- Demo-Key mit engem Limit, damit Prüfer es selbst ausprobieren können.
- Loom-Video unter drei Minuten.

**Fertig, wenn:** Jemand ohne Vorwissen versteht in einer Minute, was das Ding tut und wie gut es das tut.

## 7. Kosten

Grobe Rechnung für einen vollen Eval-Lauf: 55 Aufgaben mal vier Modelle sind 220 Generierungen, dazu 220 Bewertungen durch den Judge. Drei der vier Modelle laufen über Gratis-Kontingente oder lokal, bezahlt wird nur die Referenzstufe und der Judge. Mit einem günstigen Judge-Modell landet ein Lauf bei etwa einem Dollar, mit der Batch-API bei der Hälfte.

| Posten | Schätzung |
|---|---|
| Produktivverkehr Code-A-Cuisine und Quizly | wenige Cent pro Monat |
| Eval-Läufe M3, etwa 15 Durchläufe | 8 bis 15 Euro |
| Router- und Cache-Versuche M4, etwa 25 Durchläufe | 12 bis 25 Euro |
| Embeddings für den semantischen Cache | unter 5 Euro |
| Puffer | 10 Euro |
| **Summe** | **30 bis 55 Euro über vier Monate** |

Die fünf Hebel, ohne die daraus schnell das Fünffache wird:

1. Eval-Set klein halten. 50 bis 60 Aufgaben reichen für eine belastbare Aussage.
2. Jede Modellantwort auf der Platte cachen. Ein Wiederholungslauf kostet dann nur das, was sich geändert hat.
3. Batch-API für Eval-Läufe. Halber Preis, Ergebnis meist innerhalb von Stunden, und ein Eval-Lauf ist nie eilig.
4. Günstiges Judge-Modell beim Iterieren, das teure nur für den finalen Vergleich.
5. Ollama und die Gratis-Kontingente von Groq und Gemini für alles, was nicht die Referenzstufe ist.

Harte Regel: Kein Skript, das Modelle in einer Schleife aufruft, ohne `--limit` und `--dry-run`. Vor jedem vollen Lauf die geschätzten Kosten ausrechnen lassen.

## 8. Was gemessen wird

- Eigener Overhead des Gateways, p50 und p95, getrennt von der Anbieter-Latenz. Django unter ASGI liegt über den 10 ms, die in Blogposts für Go-Proxies stehen. Ich messe meinen echten Wert und schreibe den hin.
- Kosten pro Anfrage und pro Tag.
- Cache-Trefferquote, exakt und semantisch getrennt.
- Fehltrefferquote des semantischen Caches.
- Qualität pro Modell und Kategorie laut Judge.
- Übereinstimmung Judge gegen meine eigenen 50 Labels.
- Fallback-Auslösungen und Zustandswechsel des Circuit Breakers.

Regel: Die Prozentzahl im README kommt aus dem Eval-Set, nicht aus dem Produktivverkehr. Mein Verkehr ist zu klein und zu einseitig für eine belastbare Aussage. Das steht auch so im README.

## 9. Tests

- Backend: pytest. Anbieter-Abstraktion, Kostenrechnung, Cache-Key-Erzeugung, Rate Limit, Circuit Breaker. Externe Anbieter gemockt, die Suite läuft ohne Netzwerk und ohne API-Kosten.
- Streaming: eigener Test, der prüft, dass gepufferte Antwort und ausgelieferte Chunks übereinstimmen.
- Frontend: Vitest plus Testing Library. Keine Coverage-Jagd, sondern die Datenaufbereitung und zwei bis drei Komponenten.
- CI blockiert den Merge bei roten Tests oder Lint-Fehlern.

## 10. Zusammenarbeit mit Claude Code

Siehe `CLAUDE.md`. Kurzfassung: Claude Code schreibt keinen Code in dieses Repo. Ich tippe jede Zeile selbst, inklusive Docker, CI und Konfiguration. Claude Code plant mit, erklärt, reviewt und widerspricht.

Der Preis dafür sind etwa zwei bis drei zusätzliche Wochen. Falls es im Dezember eng wird, fällt zuerst der Umfang von M5 weg, nicht die Eval aus M3.

## 11. Build in Public

Begleitende LinkedIn-Dokumentation. Regeln zuerst:

- Ein Beitrag nur, wenn es ein Ergebnis gibt. Keine Beiträge über Vorhaben.
- Nichts behaupten, was nicht gemessen ist.
- Jeder Beitrag wird von mir geschrieben, danach durch die `human`-Skill geprüft. Kein Text geht ungeprüft raus.
- Wenn das Projekt pausiert, weil eine Stelle kommt, wird das offen gesagt statt still eingeschlafen.

Neun Zeitpunkte über 16 Wochen, das ist etwa alle zwei Wochen. Zu jedem stellt Claude mir die Fragen, aus denen ich den Beitrag baue.

### Beitrag 1 — Start (Woche 1)

Der schwächste der neun, weil es noch kein Ergebnis gibt. Trotzdem sinnvoll als Auftakt der Reihe.

Fragen: Was ärgert dich an deinem jetzigen Aufbau, bei dem zwei Apps direkt zwei Anbieter rufen? Was willst du in vier Monaten wissen, das du heute nicht weißt? Was ist dein Abbruchkriterium?

### Beitrag 2 — Erster Aufruf in Produktion (Ende M1)

Fragen: Wie lange hat es vom leeren Repo bis zum ersten durchgeleiteten Aufruf gedauert? Was hat unerwartet lange gebraucht? Wie hoch ist der Overhead deines Gateways gemessen, p50 und p95? Was hat dich an ASGI überrascht, verglichen mit dem WSGI-Django, das du kennst?

### Beitrag 3 — Streaming und Abrechnung (M2)

Der erste inhaltlich starke Beitrag. Die Frage "wie rechne ich eine Antwort ab, die ich nur durchreiche" verstehen wenige und viele finden sie interessant.

Fragen: Wie hast du die Chunks gleichzeitig ausgeliefert und gepuffert? Was passiert, wenn der Client die Verbindung mittendrin abbricht, zahlst du dann trotzdem? Wie testest du das ohne Netzwerk?

### Beitrag 4 — Anbieter fällt aus (M2)

Fragen: Wie hast du den Ausfall simuliert? Wie lange dauert es vom ersten Fehler bis zum Umschalten? Warum Circuit Breaker mit Half-Open statt einfachem Retry, was passiert ohne den Zwischenzustand? Zeig den Zustandswechsel im Log.

### Beitrag 5 — Die Cache-Key-Falle (M4, vorziehen falls der Fehler früher auftritt)

Fragen: Was genau geht schief, wenn der System-Prompt nicht in den Cache-Key einfließt? Ist dir das selbst passiert oder hast du es vorher bedacht? Welche Parameter gehören noch rein und welche bewusst nicht?

### Beitrag 6 — Taugt der Judge? (Ende M3)

Der stärkste Beitrag der Reihe. Fast niemand prüft sein Bewertungsmodell.

Fragen: Wie viele deiner 50 Handlabels stimmten mit dem Judge überein? Bei welcher Art Aufgabe lag er daneben? Was hast du am Rubrik-Prompt geändert und wie hat sich die Übereinstimmung verschoben? Würdest du dem Judge jetzt trauen?

### Beitrag 7 — Router A gegen Router B (M4)

Fragen: Welche Variante hat gewonnen, Klassifikation vorab oder Kaskade? Um wie viel, bei welchen Kosten? Wo verliert die Gewinner-Variante trotzdem? Hättest du das vorher so getippt?

### Beitrag 8 — Was ich wieder ausgebaut habe (M4)

Nur schreiben, wenn der semantische Cache tatsächlich rausfliegt. Beiträge über verworfene Bauteile kommen gut an und sind ehrlicher als Erfolgsmeldungen.

Fragen: Wie hoch war die Fehltrefferquote? Ab welcher Schwelle wurde die Trefferquote unbrauchbar niedrig? Was hätte es gekostet, wenn du es trotzdem eingeschaltet gelassen hättest?

### Beitrag 9 — Abschluss (M5)

Fragen: Wie lautet die Zahl, und woraus genau ist sie gerechnet? Was würdest du beim nächsten Mal anders bauen? Was macht LiteLLM besser als du und warum? Was hast du in vier Monaten gelernt, das du vorher nicht konntest?

## 12. Offene Entscheidungen

- Endgültiger Projektname.
- Dritter Cloud-Anbieter: Anthropic oder OpenAI.
- Wie viel React ich vorher kann. Bei wenig Vorerfahrung wird das Dashboard ab M3 parallel aufgebaut statt erst in M5, sonst lerne ich in diesem Projekt kein React.
- Eigene Subdomain auf dem VPS oder Betrieb neben den bestehenden Containern.

## 13. Repo-Struktur

```
switchboard/
  backend/
    config/              Django-Projekt, ASGI-Einstiegspunkt
    apps/
      keys/              API-Keys, Rate Limits
      proxy/             Endpunkt, Streaming, Abrechnung
      providers/         Anbieter-Abstraktion, Fallback, Circuit Breaker
      cache/             exakter und semantischer Cache
      router/            Klassifikation und Kaskade
      evals/             Aufgabenset, Runner, Judge
    tests/
  frontend/              React, Vite, Tailwind
  eval-data/             Aufgaben und Rubriken als JSON, versioniert
  docker/
  docs/
    decisions/           kurze Notiz pro Architekturentscheidung
    posts/               Entwürfe der LinkedIn-Beiträge
  README.md
  CLAUDE.md
  PROJECT_SPEC.md
```

`docs/decisions/` ist wichtiger, als es aussieht. Eine halbe Seite pro Entscheidung, geschrieben am Tag der Entscheidung. Im Dezember weiß ich sonst nicht mehr, warum ich mich gegen den semantischen Cache entschieden habe, und genau danach wird im Gespräch gefragt.
