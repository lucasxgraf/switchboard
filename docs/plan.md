# Switchboard — Umsetzungsplan

## Context

Du startest bei Null: `switchboard/` enthält heute nur `CLAUDE.md` und `PROJECT_SPEC.md` plus zwei leere Ordner `backend/` und `frontend/`, und der Ordner ist **untracked im `~/Claude`-Workspace-Repo** — es gibt kein eigenes Git-Repo, keine History, keine CI.

Das Projekt ist ein Lernvehikel und Portfolio-Stück: ein selbst gehostetes LLM-Gateway vor vier Anbietern, mit gemessener Aussage über Kosten und Qualität. Der Zweck ist nicht das Gateway — den gibt es als LiteLLM besser. Der Zweck ist, dass du im Vorstellungsgespräch jede Zeile verteidigen kannst.

Daraus folgt die Struktur dieses Plans:

- **Du schreibst jede Zeile selbst.** Ich plane, erkläre, reviewe, widerspreche. Ich lege keine Datei in diesem Repo an.
- **TDD ist der Standardweg**, aber nicht überall — Abschnitt 3 sagt ehrlich, wo er greift und wo nicht.
- **Config- und Admin-Schritte sind terminiert**, nicht "irgendwann" (Abschnitt 5).
- Der Plan ist auf **~50-Minuten-Sessions** geschnitten. Jede Aufgabe nennt ihren Session-Bedarf.

### Vier Entscheidungen, die jetzt feststehen

| Offener Punkt (Spec §12) | Entscheidung |
|---|---|
| Repo | Eigenes Git-Repo, GitHub **public ab Tag 1** |
| Dritter Cloud-Anbieter | **Anthropic** (eigenes API-Format, Batch API, Judge) |
| React / Dashboard | Fast keine Vorerfahrung → **Dashboard-Spur ab M3 parallel**, eine feste Session pro Woche |
| Deployment | **Eigene Subdomain, eigener Compose-Stack** neben den bestehenden Containern |

Offen bleibt nur der endgültige Projektname. Arbeitstitel „Switchboard" trägt bis M5; entscheide ihn spätestens beim README in W16.

---

## 0. Harte Regel: Ich sehe keine Secrets

**Ich lese niemals `.env` oder eine andere Datei, die echte Zugangsdaten enthält.** Nicht mit dem Read-Werkzeug, nicht mit `cat`, `grep`, `head`, `tail`, `less`, `source`, nicht über ein Skript, das den Inhalt ausgibt. Aus keinem Grund, auch nicht zum Debuggen, auch nicht, wenn du mich ausdrücklich darum bittest.

Betroffen sind: `.env`, `.env.local`, `.env.production`, `.env.test`, die Produktions-`.env` auf dem VPS, SSH-Schlüssel, Sentry-DSN-Dateien, Anbieter-Zugangsdaten in beliebiger Form.

**Erlaubt und nötig:** `.env.example`. Die Datei enthält nur Platzhalter, sie ist die Dokumentation dessen, was das Projekt braucht, und ich lese und pflege sie mit dir.

### Wenn ein Wert gebraucht wird

Ich nenne dir den **Variablennamen** und **wofür** er gebraucht wird. Du trägst den Wert selbst ein. Beispiel: „Für M2-03 brauchst du `ANTHROPIC_API_KEY` in `.env`, plus den Platzhalter in `.env.example`." Ich frage nie nach dem Wert und ich prüfe ihn nie.

### Befehle, die ich deshalb nicht ausführe

Ein paar davon würde man im Docker-Setup arglos aufrufen — sie lösen `.env` auf und schreiben die Werte in die Ausgabe:

| Befehl | Warum |
|---|---|
| `docker compose config` | Setzt `.env`-Werte in die Ausgabe ein. **Die Falle in M1-08** |
| `env`, `printenv`, `set` | Gibt die gesamte Umgebung aus |
| `docker compose exec app env` | dito, im Container |
| `docker inspect <container>` | Enthält den Umgebungsblock |
| `cat .env`, `grep … .env` | offensichtlich |

Wenn ich einen davon brauche, sage ich dir, was du ausführen sollst, und du zeigst mir nur den Teil der Ausgabe, der keine Werte enthält. `docker compose config` kannst du selbst laufen lassen — schau dir das Ergebnis allein an.

### Beim Review

Du zeigst mir Diffs, Logs und Fehlermeldungen. Redigiere Zugangsdaten vorher. Wenn mir trotzdem einer auffällt, sage ich es sofort und lese nicht weiter — und dann geht es nicht um den Fehler, sondern um **Rotation**: Key beim Anbieter widerrufen, neu erzeugen, überall eintragen. Ein Key, der einmal in einem Commit, einem Log oder einem Chatverlauf stand, ist verbrannt, auch wenn du den Commit zurücknimmst.

### Was daraus für den Code folgt

- `.env` steht ab dem allerersten Commit in `.gitignore` (M0-01). Prüfe es **vor** dem ersten Push, nicht danach
- Keine Zugangsdaten in Sentry: Header und Anfrageinhalte filtern (M1-09)
- Keine Zugangsdaten in `RequestLog` oder in Fehlermeldungen des Gateways
- API-Keys deiner eigenen Nutzer liegen gehasht in der Datenbank, nie im Klartext (M1-02) — dieselbe Logik, eine Ebene tiefer

---

## 1. Mein Widerspruch zur Spec: die Meilenstein-Termine

Die Spec setzt M1 auf Woche 1–2. Das geht nicht auf. 45–60 Minuten an Werktagen sind rund **4 Stunden netto pro Woche**, und die Spec sagt selbst, dass an manchen Tagen nichts passiert — realistisch **3,5 Stunden**. M1 enthält aber Django-ASGI-Gerüst, Key-Modell mit Hashing, Authentifizierung, Groq-Adapter, streamenden und nicht-streamenden Endpunkt, Logging-Modell, Testwerkzeuge, CI, Dockerfile, Compose, VPS-Einrichtung, DNS, TLS, Sentry und die Umstellung von Code-A-Cuisine. Das sind 16–20 Stunden Arbeit.

Wenn du an den Terminen der Spec festhältst, passiert eines von zwei Dingen: du schreibst M1 ohne Tests fertig (dann ist das Portfolio-Argument weg), oder du bist in Woche 3 im Rückstand und schleppst ihn bis Dezember mit.

Deshalb verschiebe ich die Grenzen. Die Regel aus Spec §10 bleibt: **Wenn es eng wird, fällt M5 zusammen, nie die Eval aus M3.**

| | Spec | Dieser Plan | Kalender 2026 |
|---|---|---|---|
| **M0** Fundament | — | W1 | Mi 09.09. – Fr 11.09. |
| **M1** Durchleiten | W1–2 | **W2–W4** | 14.09. – 02.10. |
| **M2** Robustheit | W3–5 | **W5–W7** | 05.10. – 23.10. |
| **M3** Eval-Harness | W6–8 | **W8–W10** | 26.10. – 13.11. |
| **M4** Router & Cache | W9–12 | **W11–W14** | 16.11. – 11.12. |
| **M5** Dashboard & Abschluss | W13–16 | **W15–W16 + Puffer** | 14.12. – 23.12. |

M5 ist nur deshalb kurz, weil die Dashboard-Spur ab W8 nebenherläuft. In W15 baust du kein React mehr von Null, du setzt zusammen, was seit sieben Wochen wächst.

Jeder Meilenstein hat **Kern** und **Kür**. Kür fällt zuerst, ohne Diskussion.

---

## 2. Arbeitsweise: der Rhythmus, an den du dich hältst

### Die Session

Eine Session sind 45–60 Minuten. Sie beginnt damit, dass du diesen Plan aufschlägst und die nächste offene Aufgabe nimmst — nicht damit, dass du überlegst, worauf du Lust hast.

Ablauf jeder Session:

1. **Plan** — ich sage dir vorher in einem kurzen Absatz: was gebaut wird, welche Dateien betroffen sind, welche Entscheidung offen ist.
2. **Du setzt um**, test-first wo Abschnitt 3 das vorsieht.
3. **Review** — du zeigst mir das Ergebnis (`git diff`), ich lese streng: Korrektheit, Fehlerpfade, Tests, Lesbarkeit.
4. **Nachbessern.**
5. **Commit** — nur wenn Definition of Done erfüllt ist.

Wenn eine Session endet, ohne dass die Aufgabe fertig ist: WIP-Commit auf den Feature-Branch, nicht auf `main`. Der Feature-Branch darf hässlich sein, `main` nicht.

### Git-Workflow

`main` ist geschützt. Branch Protection mit Required Status Checks wird in W2 eingerichtet (siehe M1-05), und ab da geht nichts mehr direkt auf `main`.

```
main
 └── feat/m1-03-api-key-model     ← ein Branch pro Aufgabe
      ├── wip: key hashing sketch  ← Zwischenstände erlaubt
      └── ...
     → Pull Request → CI grün → Squash Merge
```

Das kostet dich pro Aufgabe zwei Minuten und bringt dir drei Dinge: eine lesbare History für den Portfolio-Blick, eine CI, die tatsächlich blockiert statt nur zu meckern, und geübten PR-Workflow.

Commit-Nachrichten auf Englisch, Imperativ, mit Kontext im Body wenn nötig:

```
Add API key hashing with per-key salt

Keys are stored as sha256(salt + key), never in plain text.
The prefix (first 8 chars) is kept for identification in the UI.
```

### Definition of Done (Spec §"Definition of Done", hier operationalisiert)

Eine Aufgabe ist fertig, wenn **alle sechs** Punkte stimmen:

1. Code geschrieben, Type Hints vollständig
2. Tests grün: `pytest` (Backend) bzw. `vitest run` (Frontend)
3. Lint sauber: `ruff check .` und `ruff format --check .`
4. Typen sauber: `mypy backend/`
5. Dokumentation angepasst: README-Abschnitt, `.env.example`, oder ADR in `docs/decisions/` — je nachdem was betroffen ist
6. Commit gesetzt, PR gemerged, CI grün

Nicht fünf von sechs. Sechs.

### Wenn du feststeckst

CLAUDE.md regelt das: Ich frage erst, was du probiert hast und was du erwartet hättest. Dann zeige ich dir, wo du nachsiehst. Dann nenne ich die wahrscheinlichste Ursache ohne den Code. Erst dann die Lösung.

Du kannst das abkürzen mit dem Satz „keine Zeit für den Weg". Ich frage dann einmal nach und überspringe die Stufen.

---

## 3. TDD in diesem Projekt

Du willst nach TDD arbeiten. Gut — aber TDD auf ein ganzes Projekt zu stülpen erzeugt entweder Theater (Tests für `settings.py`) oder Frust (du willst Docker test-first bauen und es geht nicht). Deshalb hier die ehrliche Aufteilung.

### 3.1 Der Zyklus

Für jede Aufgabe in Zone A und B:

```
RED     Test schreiben, der das gewünschte Verhalten beschreibt.
        Test laufen lassen. Er muss FEHLSCHLAGEN.
        Wenn er sofort grün ist, testet er nichts.

GREEN   Die einfachste Implementierung, die den Test grün macht.
        Nicht die schöne. Die einfachste.

REFACTOR Aufräumen bei durchgehend grünen Tests.
        Type Hints, Benennung, Duplikate.

CHECK   ruff check . && ruff format --check . && mypy backend/

COMMIT  Erst jetzt.
```

Die Regel, die den Unterschied macht: **Du darfst keine Produktivzeile schreiben, für die kein fehlschlagender Test existiert.** Das fühlt sich in Woche 2 lästig an und in Woche 10 wie eine Versicherung.

### 3.2 Zone A — echtes TDD, keine Ausnahme

Reine Logik mit klarem Ein- und Ausgang. Hier ist TDD schneller als Nachtesten, weil du die Schnittstelle beim Testschreiben entwirfst.

| Bauteil | Meilenstein | Warum TDD hier trägt |
|---|---|---|
| API-Key-Hashing und -Prüfung | M1 | Sicherheitsrelevant, reine Funktion |
| Kostenrechnung (Tokens → Betrag) | M2 | Zahlenlogik, Rundungsfehler sind unsichtbar ohne Test |
| Provider-Adapter: Request-Übersetzung | M2 | Drei Formate, drei Testklassen, sehr klarer Vertrag |
| Provider-Adapter: Response-Übersetzung | M2 | dito, plus Fehlerfälle |
| Token-Zählung aus Stream-Chunks | M2 | Der schwierigste Teil des Projekts. Ohne Test rätst du. |
| Rate-Limiter | M2 | Zeit- und Zustandslogik |
| Circuit Breaker | M2 | Eine Zustandsmaschine — das Lehrbuchbeispiel für TDD |
| Fallback-Kette | M2 | Reihenfolge und Abbruchbedingungen |
| Cache-Key-Erzeugung | M4 | Die Falle aus Build-in-Public-Beitrag 5 lebt genau hier |
| Router-Klassifikation | M4 | Ein-/Ausgabe-Abbildung |
| Kaskaden-Eskalationslogik | M4 | Entscheidungsregeln |
| Judge-Antwort-Parsing | M3 | Fremde Ausgabe parsen — ohne Test nur Hoffnung |
| Agreement-Metrik (Judge vs. Handlabels) | M3 | Statistik, muss stimmen |
| Frontend-Datenaufbereitung | M3–M5 | Aggregation, Formatierung, Zeitzonen |

### 3.3 Zone B — Test-first, aber gröber

HTTP-Endpunkte und Django-Views. Du schreibst zuerst den API-Test (Statuscode, Antwortform, Fehlerfall), dann die View. Das geht mit `pytest-django` und dem DRF-Testclient sauber, ist aber kein Micro-TDD — ein Test deckt mehrere Zeilen ab.

- `/v1/chat/completions` nicht-streamend: Test prüft Statuscode, Antwortstruktur, dass ein `RequestLog` entstand
- `/v1/chat/completions` streamend: Test konsumiert den Stream und prüft Chunk-Folge plus finalen Log-Eintrag
- Auth: fehlender Header, falscher Key, deaktivierter Key, gültiger Key — vier Tests, vier Statuscodes
- Rate Limit: 429 mit `Retry-After`-Header
- Dashboard-API-Endpunkte in M3–M5

### 3.4 Zone C — kein TDD, stattdessen Nachweis

Hier wäre ein Test-First-Zwang Selbstbetrug. Der Nachweis ist manuell und wird dokumentiert.

| Bauteil | Nachweis stattdessen |
|---|---|
| Django-Projekt-Setup, Settings-Split | `python manage.py check --deploy` läuft sauber |
| Migrationen | `makemigrations --check --dry-run` in CI: keine ausstehenden Migrationen |
| Dockerfile, docker-compose | Container startet, Healthcheck grün |
| GitHub-Actions-Workflow | Der Lauf ist grün, danach ein absichtlich roter Test → Lauf ist rot |
| nginx/Caddy, DNS, TLS | `curl -v https://…` zeigt gültiges Zertifikat |
| Sentry-Anbindung | Absichtlicher Fehler erscheint im Sentry-Dashboard |
| Tailwind-Layout, Farben, Abstände | Browser. Ein Screenshot in der PR-Beschreibung. |
| VPS-Administration | Deploy-Skript läuft zweimal hintereinander ohne Handgriff |

Für Zone C gilt ein anderer Rhythmus: erst manuell nachweisen, **dann** einen Smoke-Test schreiben, der die Regression fängt (z. B. ein Test, der prüft, dass die ASGI-App importierbar ist und `/healthz` 200 liefert).

### 3.5 Mock-Strategie — die harte Regel umgesetzt

CLAUDE.md: *„Die Suite läuft ohne Netzwerk und ohne API-Kosten. Das ist eine harte Regel, kein Richtwert."*

So setzt du das um, **ohne eine einzige neue Abhängigkeit**:

- **HTTP-Anbieter:** `httpx.MockTransport`. Das ist in `httpx` eingebaut. Du übergibst dem Client einen Transport, der aus einer Handler-Funktion Antworten erzeugt — inklusive Streaming, Timeouts, 429, 500, kaputtes JSON. Kein `responses`, kein `vcrpy`, kein `pytest-httpx`. Der Client bekommt seinen Transport von außen injiziert; in Produktion der echte, im Test der Mock. Das erzwingt nebenbei eine testbare Architektur.
- **Zeit:** keine `freezegun`. Du injizierst eine `clock`-Funktion (Standard: `time.monotonic`) in Circuit Breaker und Rate-Limiter. Im Test übergibst du eine Funktion, deren Rückgabewert du steuerst. Lehrreicher und billiger als eine Bibliothek, die Zeit global patcht.
- **Redis:** der **echte** Redis aus Docker Compose. Redis ist keine externe API, sondern deine Infrastruktur — die Regel meint kostenpflichtige Anbieter. Ein Rate-Limiter gegen `fakeredis` testet nicht, was in Produktion läuft (Ablaufsemantik, atomare Operationen). Eigene Datenbanknummer für Tests, `flushdb` im Fixture.
- **Postgres:** der echte aus Compose, `pytest-django` mit `--reuse-db` für Tempo.
- **Ollama:** nie im Test. Der Adapter wird gegen `MockTransport` getestet, genau wie die anderen. Wenn die Laufzeit nicht erreicht wird, muss der Code sauber ausfallen — **dafür gibt es einen Test** (Connection Refused → definierter Fehler, kein Stacktrace).

### 3.6 Der Streaming-Test, den die Spec verlangt

Spec §9: *„eigener Test, der prüft, dass gepufferte Antwort und ausgelieferte Chunks übereinstimmen."*

Das ist der wichtigste Test des Projekts, weil er das schwierigste Bauteil absichert. Aufbau:

1. `MockTransport` liefert eine feste Folge von SSE-Chunks.
2. Der Test ruft den streamenden Endpunkt und sammelt alles, was beim Client ankommt.
3. Der Test liest den `RequestLog`-Eintrag, der nach Abschluss geschrieben wurde.
4. Assertion: Der zusammengesetzte Text aus den ausgelieferten Chunks ist **identisch** mit dem gepufferten Text im Log. Und die Token-Zahlen stimmen mit dem Usage-Chunk überein.

Dazu die Fehlerfälle als eigene Tests: Abbruch nach dem dritten Chunk, Anbieter liefert kaputtes JSON mittendrin, Anbieter beendet den Stream ohne Usage-Chunk.

---

## 4. Abhängigkeiten — vorab begründet

CLAUDE.md verlangt für jede Abhängigkeit eine Begründung. Hier sind alle, die ich vorschlage. Alles, was nicht in dieser Liste steht, ist eine neue Entscheidung und braucht eine Rückfrage.

### Backend

| Paket | Warum nicht Standardbibliothek |
|---|---|
| `django` | Gesetzt |
| `djangorestframework` | Gesetzt. Serializer und Testclient |
| `uvicorn[standard]` | ASGI-Server. Ohne ihn kein Streaming |
| `psycopg[binary]` | Postgres-Treiber, async-fähig |
| `redis` | Rate Limits, Cache-Index |
| `django-rq` | Kennst du aus Videoflix. **Aber:** Django 6 bringt ein eigenes Background-Tasks-Framework mit. Prüfe das in W6 und halte die Wahl in ADR-0011 fest — eventuell sparst du eine Abhängigkeit |
| `httpx` | **Die zentrale Wahl.** `requests` kann kein async, `urllib` kein sauberes Streaming mit Timeouts. `httpx` kann sync und async, HTTP/2, Streaming, und bringt `MockTransport` für die Tests mit. Eine Abhängigkeit, die drei ersetzt |
| `sentry-sdk` | Von der Spec gesetzt |
| `python-dotenv` | Nur für lokale Entwicklung. In Produktion kommen die Werte aus der Container-Umgebung |

**Ausdrücklich nicht:** `openai`, `anthropic`, `google-generativeai`, `groq`. Keine Anbieter-SDKs. Du sprichst die REST-APIs direkt über `httpx` an. Begründung: Die Übersetzung zwischen drei Anfrageformaten **ist** der Lerninhalt dieses Projekts. Ein SDK versteckt genau das, was du im Vorstellungsgespräch erklären sollst — und es ist derselbe Grund, aus dem LangChain draußen bleibt. Nebeneffekt: vier Abhängigkeiten weniger und keine SDK-Breaking-Changes über vier Monate.

### Backend-Werkzeuge (dev)

`pytest`, `pytest-django`, `pytest-asyncio`, `mypy`, `django-stubs`, `ruff`.

`ruff` ersetzt `black`, `isort` und `flake8` in einem Werkzeug. Ein Konfigurationsblock in `pyproject.toml` statt drei Dateien.

### Frontend

`react`, `react-dom`, `typescript`, `vite`, `tailwindcss` + `@tailwindcss/vite`, `recharts`, `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `jsdom`, `msw`.

`msw` (Mock Service Worker) ist die einzige, die eine Begründung braucht: Sie fängt `fetch` auf Netzwerkebene ab, statt dass du deine eigenen API-Funktionen mockst. Damit testest du die echte Datenverarbeitung inklusive Fehlerbehandlung, und die Suite bleibt ohne Netzwerk — dieselbe harte Regel wie im Backend.

**Hinweis zu Tailwind:** Aktuelle Tailwind-Versionen konfigurieren sich CSS-first über `@import "tailwindcss"` und `@theme`, nicht mehr über `tailwind.config.js`. Wenn du auf ein Tutorial mit `tailwind.config.js` und `content: [...]` stößt, ist es für die ältere Generation geschrieben. Prüfe die Version, bevor du dich ärgerst.

### Laufzeit-Versionen

Lokal hast du **Python 3.14.3**. Das ist frisch. Django 6 unterstützt es, aber bei C-Erweiterungen (`psycopg`) kann es Wheel-Lücken geben, und du willst in Woche 1 keine Compiler-Fehler debuggen.

Empfehlung: **Python 3.13 als Projekt-Version**, lokal über `pyenv` oder einen zweiten python.org-Installer, im Docker-Image `python:3.13-slim`. Entscheidend ist nicht die Zahl, sondern dass **lokal und Container identisch** sind. Halte das in ADR-0002 fest, mit `.python-version` im Repo.

Wenn du auf 3.14 bestehst: probiere in M0-02 sofort `pip install psycopg[binary]`. Läuft es durch, bleib dabei und schreib es in den ADR.

Paketverwaltung: `pip` + `venv` + `requirements.txt` / `requirements-dev.txt`. Kein `uv`, kein `poetry` — beides ist nicht installiert, beides wäre eine neue Baustelle in Woche 1, und `pip` reicht für ein Projekt dieser Größe. Versionen pinnen (`django==6.0.4`, nicht `django`), sonst bricht dir CI irgendwann grundlos weg.

---

## 5. Config- und Admin-Kalender

Das ist der Teil, den du explizit wolltest: wann du was einrichten musst, damit es fertig ist, bevor du es brauchst. Zwei Dinge haben Vorlaufzeit — DNS-Propagierung und die Freischaltung eines Zahlungsmittels bei Anthropic. Die stehen deshalb früher, als du sie brauchst.

| Woche | Admin-Schritt | Wo | Ergebnis / Prüfung |
|---|---|---|---|
| **W1** | Git-Repo initialisieren | lokal | `git init`, `.gitignore` (Python, Node, macOS, `.env`), erster Commit |
| **W1** | `Dev/` im Workspace-Repo ausschließen | `~/Claude/.gitignore` | Workspace-Repo verfolgt `switchboard/` nicht mehr |
| **W1** | GitHub-Repo anlegen, **public** | `gh repo create` | Remote gesetzt, Push erfolgreich |
| **W1** | Groq-API-Key erzeugen | console.groq.com | Key in lokaler `.env`, Platzhalter in `.env.example` |
| **W1** | Sentry-Account + zwei Projekte | sentry.io | DSN Backend und Frontend notiert (Anbindung erst W3/W4) |
| **W1** | Python 3.13 installieren, venv | lokal | `python --version` im venv zeigt 3.13.x |
| **W2** | Postgres + Redis lokal | `docker/compose.yml` | Beide Container laufen, `manage.py migrate` geht durch |
| **W2** | Branch Protection auf `main` | GitHub → Settings → Rules | Direkter Push auf `main` wird abgelehnt |
| **W2** | Required Status Check „CI" | GitHub → Rules | PR mit rotem Test lässt sich nicht mergen |
| **W3** | **DNS-Eintrag anlegen** | Cloudflare | A-Record `gateway.lucasgraf.com` → VPS-IP. **Jetzt, nicht in W4** — Propagierung und TLS-Ausstellung brauchen Zeit |
| **W3** | Sentry im Backend verdrahten | `settings/production.py` | Absichtlicher Fehler erscheint im Dashboard |
| **W4** | VPS vorbereiten | IONOS per SSH | Verzeichnis, Docker-Netz, Reverse-Proxy-Eintrag für die Subdomain |
| **W4** | Deploy-Secrets in GitHub | Settings → Secrets → Actions | `SSH_HOST`, `SSH_USER`, `SSH_KEY`, `GHCR_TOKEN` o. ä. |
| **W4** | TLS prüfen | Browser + `curl -v` | Gültiges Zertifikat, kein Mixed Content |
| **W4** | Produktions-Gateway-Key erzeugen | Django-Admin auf dem VPS | Key einmalig sichtbar, danach nur noch der Hash |
| **W4** | Code-A-Cuisine umstellen | Vercel → Environment Variables | Base-URL und Key gesetzt, Redeploy, Aufrufe erscheinen im `RequestLog` |
| **W5** | Gemini-API-Key | aistudio.google.com | Key in `.env`, Platzhalter in `.env.example` |
| **W5** | **Anthropic Console + Zahlungsmittel** | console.anthropic.com | Guthaben aufgeladen |
| **W5** | **Ausgabenlimit setzen** | Anthropic Console → Limits | Harte Monatsgrenze **20 €** plus Mail-Warnung bei 10 €. Nicht optional. Ein Skript mit Schleifenfehler kostet dich sonst dein Eval-Budget an einem Nachmittag |
| **W5** | Ollama installieren + Modell ziehen | lokal (MacBook M3) | `ollama pull llama3.1:8b` (~5 GB). `ollama list` zeigt es. **Nie auf dem VPS** |
| **W7** | Quizly umstellen | Vercel / VPS | Aufrufe erscheinen im `RequestLog` |
| **W8** | Node-Toolchain fürs Frontend | `frontend/` | `npm run dev` liefert eine Seite |
| **W9** | Anthropic Batch API prüfen | Doku + ein Testaufruf | Ein einzelner Batch-Job läuft durch, bevor du 220 Aufgaben hineinwirfst |
| **W11** | Cache-Datenbanknummer in Redis trennen | `.env` | Rate-Limit-DB und Cache-DB sind verschiedene Nummern |
| **W15** | Demo-Key mit engem Limit | Django-Admin | Eigener Key, 20 Anfragen/Tag, eigenes Budget |
| **W16** | README, Architekturbild, Loom | Repo + Loom | Öffentlich verlinkbar |

### `.env.example` — laufende Pflicht

Jedes Mal, wenn ein Key oder eine Einstellung dazukommt, kommt im **selben Commit** der Platzhalter in `.env.example`. Nicht später. Die Datei ist die einzige Dokumentation, die dir sagt, was das Projekt zum Laufen braucht — und in vier Monaten die einzige, der du glaubst.

`.env` steht ab dem ersten Commit in `.gitignore`. Prüfe das, bevor du zum ersten Mal pushst, nicht danach.

Die Arbeitsteilung dabei ist die aus Abschnitt 0: **Ich sage dir den Variablennamen und wofür er da ist, du trägst den Wert ein.** Ich sehe die `.env` nie. Jeder Eintrag in der Tabelle oben, der „Key in `.env`" sagt, meint: du machst das allein.

---

## 6. Repo-Struktur

Die Spec gibt sie vor. Zwei Anmerkungen dazu, bevor du sie anlegst:

```
switchboard/
  backend/
    config/                Django-Projekt, ASGI-Einstiegspunkt, Settings-Split
      settings/
        base.py  dev.py  production.py  test.py
      asgi.py  urls.py
    apps/
      keys/                API-Keys, Rate Limits
      proxy/               Endpunkt, Streaming, Abrechnung
      providers/           Anbieter-Abstraktion, Fallback, Circuit Breaker
      caching/             exakter und semantischer Cache
      router/              Klassifikation und Kaskade
      evals/               Aufgabenset, Runner, Judge
    tests/
    manage.py  pyproject.toml  requirements.txt  requirements-dev.txt
  frontend/                React, Vite, Tailwind
  eval-data/               Aufgaben und Rubriken als JSON, versioniert
  docker/
  docs/
    decisions/             ADR pro Architekturentscheidung
    posts/                 Entwürfe der LinkedIn-Beiträge
  .github/workflows/ci.yml
  README.md  CLAUDE.md  PROJECT_SPEC.md
  .env.example  .gitignore  .python-version
```

**Erste Anmerkung:** Die Spec nennt die App `cache/`. Nenn sie **`caching/`**. `cache` kollidiert mit `django.core.cache`, und du wirst irgendwann eine halbe Session damit verlieren, dass ein Import den falschen Namen trifft. Eine Umbenennung im November ist teurer als eine Entscheidung heute.

**Zweite Anmerkung:** Settings-Split ab Tag 1, nicht nachträglich. `base.py` mit allem Gemeinsamen, `dev.py`/`production.py`/`test.py` mit den Unterschieden. Nachträglich aufzuteilen bedeutet, jede Einstellung einzeln zu prüfen — jetzt kostet es zehn Minuten.

---

## 7. M0 — Fundament (W1, Mi 09.09. – Fr 11.09., 3 Sessions)

Ziel: Am Freitagabend existiert ein öffentliches Repo mit einem grünen CI-Lauf, und du hast einen Test geschrieben, der etwas Echtes prüft.

### M0-01 — Repo und Werkzeugkette (1 Session)

Der Ordner liegt untracked im Workspace-Repo. Erst trennen, dann bauen.

- `Dev/` (oder gezielt `Dev/projects/switchboard/`) in `~/Claude/.gitignore` eintragen und dort committen
- In `switchboard/`: `git init`, `.gitignore` (Python, Node, macOS, `.env`, `.venv`, `__pycache__`, `dist`)
- Python 3.13 installieren, `.python-version` anlegen, `python -m venv .venv`
- `gh repo create --public --source=. --remote=origin`, erster Push
- `CLAUDE.md` und `PROJECT_SPEC.md` sind bereits da und werden mitgenommen — sie gehören ins Repo, sie sind Teil der Geschichte

**Kontrolle:** `git log` im Workspace-Repo zeigt keine switchboard-Dateien. Das GitHub-Repo ist im Browser erreichbar.

**ADR-0001** anlegen: warum eigenes Repo statt Workspace-Unterordner. Vier Zeilen reichen, aber schreib sie.
**ADR-0002** anlegen: Python-Version, `pip` statt `uv`/`poetry`, Versionen gepinnt.

### M0-02 — Django-Gerüst und der erste Test (1–2 Sessions)

Jetzt beginnt TDD, und zwar an einer Stelle, wo es Sinn ergibt.

- `pip install django djangorestframework uvicorn[standard] psycopg[binary] httpx python-dotenv`
- `pip install -r requirements-dev.txt`: pytest, pytest-django, pytest-asyncio, mypy, django-stubs, ruff
- `django-admin startproject config backend/` mit Settings-Split
- `pyproject.toml`: ruff-Konfiguration, mypy-Konfiguration (streng: `disallow_untyped_defs`), pytest-Konfiguration (`DJANGO_SETTINGS_MODULE=config.settings.test`)

**Der erste Test (RED → GREEN):** ein Health-Endpunkt.

RED: Test schreiben, der `GET /healthz` aufruft und 200 plus `{"status": "ok"}` erwartet. Er schlägt fehl (404). Dann die View schreiben. Das ist bewusst trivial — der Punkt ist, dass deine Testinfrastruktur nachweislich funktioniert, bevor du echte Logik darauf legst.

**Kontrolle:** `pytest` grün, `ruff check .` sauber, `mypy backend/` sauber.

### M0-03 — CI, die wirklich blockiert (1 Session)

- `.github/workflows/ci.yml`: Python-Setup, Abhängigkeiten aus Cache, `ruff check`, `ruff format --check`, `mypy`, `pytest`
- Postgres und Redis als Service-Container im Workflow
- Branch Protection auf `main`, Required Status Check „CI"

**Der Nachweis (Zone C):** Mach in einem Branch absichtlich einen Test rot. Öffne einen PR. Der Merge-Button muss gesperrt sein. Erst wenn du das gesehen hast, ist die CI eingerichtet — nicht wenn der Workflow einmal grün war.

**→ Build in Public, Beitrag 1** (Spec §11). Fragen, die ich dir am Freitag stellen werde: Was ärgert dich an deinem jetzigen Aufbau, bei dem zwei Apps direkt zwei Anbieter rufen? Was willst du in vier Monaten wissen, das du heute nicht weißt? Was ist dein Abbruchkriterium?

---

## 8. M1 — Durchleiten (W2–W4, 14.09. – 02.10., ~15 Sessions)

**Abschlusskriterium (unverändert aus der Spec):** Code-A-Cuisine läuft in Produktion über das Gateway, und du siehst jeden Aufruf in der Datenbank.

### Woche 2 — Schlüssel und Daten

**M1-01 · Datenmodell entwerfen (1 Session, kein Code)**

Bevor du Modelle tippst, entscheide die Felder. Zwei Punkte, an denen man sich in vier Monaten ärgert:

- **Kosten als Ganzzahl in Mikro-Cent**, nicht als `FloatField`. Gleitkomma-Addition über 10.000 Zeilen driftet, und du willst später Summen bilden, denen du traust. `DecimalField` wäre die Alternative — wäg ab und halt es fest.
- **Latenz zweimal messen**: Gesamtdauer und Anbieter-Dauer, getrennt. Die Differenz ist dein eigener Overhead, und den brauchst du für Spec §8 und für Beitrag 2. Wenn du das erst nachträglich einbaust, hast du keine Vergleichswerte aus den ersten Wochen.

`ApiKey`: Name, Präfix, Hash, aktiv, erstellt, Rate-Limit, Monatsbudget, zuletzt benutzt.
`RequestLog`: Key, Zeitstempel, angefragtes Modell, benutztes Modell, Anbieter, Prompt-/Completion-Tokens, Kosten, Gateway-Latenz, Anbieter-Latenz, Status, Fehlercode, Cache-Treffer, Streaming ja/nein, Fallback-Tiefe, Request-ID.

Felder wie `cache_hit` und `fallback_depth` legst du **jetzt** an, obwohl sie erst in M2/M4 gefüllt werden. Eine Migration heute ist billig; eine Migration im November, nachdem sie auf dem VPS lief, fällt unter die Regel „Migrationen nie nachträglich ändern".

**ADR-0003:** Kostenrepräsentation und Latenzmessung.

**M1-02 · API-Key-Modell, test-first (2 Sessions)** — Zone A

RED zuerst, in dieser Reihenfolge:

1. Ein erzeugter Key ist nirgends im Klartext gespeichert
2. Ein gültiger Key wird erkannt
3. Ein falscher Key wird abgelehnt
4. Ein deaktivierter Key wird abgelehnt
5. Der Präfix bleibt lesbar (für die spätere Anzeige)

Dann implementieren. Beim Hashing: kein einfaches `sha256(key)` ohne Salz, und kein `bcrypt` (zu langsam für einen Aufruf pro Request). Überleg dir, was hier angemessen ist, und begründe es in **ADR-0004**. Das ist eine Frage, die im Vorstellungsgespräch kommt.

**M1-03 · Authentifizierung (1–2 Sessions)** — Zone B

Vier Tests, vier Ausgänge: kein Header → 401, kaputter Header → 401, unbekannter Key → 401, gültiger Key → Request kommt durch und `request.api_key` ist gesetzt. OpenAI-kompatibel heißt: `Authorization: Bearer sk-…`.

Entscheidung: DRF-Authentication-Klasse oder ASGI-Middleware. Beides geht, die Nachteile sind unterschiedlich (Middleware läuft vor DRF, sieht aber die View nicht). Ich lege dir beide hin, du entscheidest.

**M1-04 · Django-Admin nutzbar machen (1 Session)** — Zone C

Du brauchst ihn in W4, um den Produktions-Key zu erzeugen. `ApiKey` registrieren, Klartext-Key **einmalig** nach dem Anlegen anzeigen, danach nie wieder. `RequestLog` schreibgeschützt mit sinnvollen Listenspalten und Filtern.

### Woche 3 — Durchleiten und Streaming

**M1-05 · Groq-Adapter, nicht-streamend (2 Sessions)** — Zone A

Erst der Test mit `httpx.MockTransport`: eine feste Groq-Antwort rein, geprüfte Ausgabe raus. Dann der Adapter. Groq ist OpenAI-kompatibel, also ist die Übersetzung hier fast eine Identität — genau deshalb ist es der richtige erste Adapter. Die echte Übersetzungsarbeit kommt in M2 mit Gemini und Anthropic, und dann hast du das Muster schon.

Der Transport wird von außen übergeben. Das ist keine Abstraktion auf Vorrat, sondern die Voraussetzung für jeden Test in diesem Projekt.

Fehlerfälle als eigene Tests: Timeout, 429, 500, ungültiger Key, kaputtes JSON. Fünf Tests, fünf definierte Ausgänge. Das ist die CLAUDE.md-Regel „für jeden Fehlerpfad ein Test", und du erfüllst sie ab dem ersten Adapter, nicht rückwirkend.

**M1-06 · `/v1/chat/completions` nicht-streamend (2 Sessions)** — Zone B

**Die Stolperfalle, auf die du zulaufen wirst:** Du kennst Django unter WSGI. Unter ASGI in einer `async def`-View wirft jeder synchrone ORM-Zugriff `SynchronousOnlyOperation`. Du brauchst die async-ORM-Methoden (`acreate`, `aget`, `asave`) oder `sync_to_async`. Das ist die Überraschung, nach der Build-in-Public-Beitrag 2 fragt — notier dir, wann du zum ersten Mal darauf stößt, für den Beitrag.

Test-first: Request rein, OpenAI-förmige Antwort raus, ein `RequestLog` entstand, Latenzen sind gefüllt.

**M1-07 · `/v1/chat/completions` streamend (3 Sessions)** — Zone A + B, das Herzstück

Hier liegt die schwierigste Logik des Meilensteins. Der Test aus Abschnitt 3.6 ist Pflicht.

Die Aufgabe: Chunks vom Anbieter kommen an, gehen sofort an den Client raus **und** werden gleichzeitig gepuffert, damit du am Ende abrechnen und protokollieren kannst. Ein Async-Generator, der beides tut.

Zwei Dinge, die dich Zeit kosten werden, wenn du sie nicht vorher weißt:

- Groq und OpenAI liefern die Token-Zahlen im Stream **nur**, wenn du `stream_options: {"include_usage": true}` mitschickst. Ohne das kommt kein Usage-Chunk, und deine Abrechnung ist leer. Prüfe die aktuelle Doku, das Feld hat sich schon einmal geändert.
- Wenn der Client die Verbindung abbricht, läuft dein Generator ins Leere. Wo fängst du das ab, und rechnest du dann ab? Das ist eine echte Entscheidung mit zwei vertretbaren Antworten — halte sie in **ADR-0005** fest, und merk sie dir für Beitrag 3.

**ADR-0006:** ASGI-Server, Worker-Modell, warum Uvicorn.

### Woche 4 — Deployment und der erste echte Aufruf

**M1-08 · Docker lokal (1–2 Sessions)** — Zone C

Dockerfile (Multi-Stage, Python 3.13-slim, non-root User), `docker/compose.yml` mit App, Postgres, Redis. Healthcheck auf `/healthz`.

Nachweis: `docker compose up` von Null, Migrationen laufen, `curl` gegen den Container liefert eine Antwort.

**M1-09 · Sentry (0,5 Sessions)** — Zone C

DSN aus der Umgebung, nur in `production.py`. Nachweis: absichtlicher Fehler landet im Dashboard. Achte darauf, dass keine API-Keys in den Sentry-Kontext geraten — Anfrageinhalte und Header filtern.

**M1-10 · VPS-Deployment (2–3 Sessions)** — Zone C

DNS steht seit W3. Jetzt: Verzeichnis auf dem VPS, Compose-Stack, Reverse-Proxy-Eintrag für `gateway.lucasgraf.com`, TLS. Deploy per GitHub Actions auf `main` oder per Skript über SSH — beides vertretbar, entscheide nach Aufwand.

**ADR-0007:** Deployment-Topologie. Eigener Stack, eigene Postgres- und Redis-Instanz, warum nicht geteilt.

Nachweis: Deploy zweimal hintereinander ohne Handgriff. Ein Deploy, der beim zweiten Mal manuelle Eingriffe braucht, ist kein Deploy.

**M1-11 · Code-A-Cuisine umstellen (1–2 Sessions)**

Base-URL und Gateway-Key in die Vercel-Umgebung, Redeploy, echten Aufruf machen, im `RequestLog` nachsehen.

**Der Rückweg muss vorher stehen.** Bevor du umstellst: wie kommst du in zwei Minuten zurück auf den direkten Groq-Aufruf, wenn das Gateway um 22 Uhr ausfällt? Ein Umgebungsschalter reicht, aber er muss existieren, bevor du ihn brauchst.

**Meilenstein-Abschluss:**
- README aktualisieren (Spec: am Ende jedes Meilensteins, nicht im Dezember)
- Overhead messen: p50 und p95 deiner eigenen Latenz, getrennt von der Anbieter-Latenz. Diese Zahl brauchst du für Beitrag 2 und fürs README

**→ Build in Public, Beitrag 2.** Fragen: Wie lange vom leeren Repo bis zum ersten durchgeleiteten Aufruf? Was hat unerwartet lange gebraucht? Wie hoch ist dein Overhead, p50 und p95? Was hat dich an ASGI überrascht, verglichen mit dem WSGI-Django, das du kennst?

---

## 9. M2 — Robustheit und Abrechnung (W5–W7, 05.10. – 23.10., ~15 Sessions)

**Abschlusskriterium:** Du schaltest einen Anbieter künstlich ab, und der Verkehr läuft ohne Fehler beim Client weiter.

### Woche 5 — Anbieter-Abstraktion

**M2-01 · Die Schnittstelle schneiden (1 Session, kein Code)**

Du hast einen Adapter (Groq). Jetzt kommen drei dazu. CLAUDE.md sagt: „Erst der zweite Anwendungsfall rechtfertigt eine Basisklasse" — der ist jetzt da, du darfst abstrahieren.

Die Frage ist nur, **wo** der Schnitt liegt. Zu weit oben und Gemini passt nicht rein; zu weit unten und du duplizierst. Ich lege dir zwei Varianten hin (Protokoll mit vier Methoden vs. abstrakte Basisklasse mit Template-Methode), mit Nachteilen. **ADR-0008.**

**M2-02 · Gemini-Adapter (2 Sessions)** — Zone A

Das erste wirklich fremde Format: andere Rollenbezeichnungen, System-Prompt an anderer Stelle, andere Antwortstruktur, andere Fehlercodes. Test-first, `MockTransport`, dieselben fünf Fehlerpfade wie bei Groq.

Hier merkst du, ob dein Schnitt aus M2-01 taugt. Wenn du die Basisklasse anpassen musst: gut, das ist der Sinn des zweiten Anwendungsfalls. Notier es im ADR.

**M2-03 · Anthropic-Adapter (2 Sessions)** — Zone A

Drittes Format. Achte auf: System-Prompt als eigenes Feld statt als Nachricht, `max_tokens` ist Pflicht, eigenes Stream-Ereignisformat.

**M2-04 · Ollama-Adapter (1 Session)** — Zone A

Lokal, kostenlos. **Der wichtigste Test hier ist der Fehlerfall:** Laufzeit nicht erreichbar → definierter Fehler, kein Stacktrace, kein hängender Request. CLAUDE.md ist da eindeutig: kein Test und kein Deployment darf von Ollama abhängen. Der Adapter wird wie alle anderen gegen `MockTransport` getestet.

### Woche 6 — Abrechnung und Grenzen

**M2-05 · Kostenrechnung (2 Sessions)** — Zone A, striktes TDD

Preise gehören **in Daten, nicht in Code**. Eine JSON- oder YAML-Datei pro Modell mit Preis pro Million Eingabe- und Ausgabe-Tokens, versioniert. Wenn ein Anbieter die Preise ändert, änderst du eine Datei, keinen Code — und du kannst rückwirkend nachvollziehen, mit welchem Preis eine alte Zeile gerechnet wurde. **ADR-0009.**

Tests: bekannte Token-Zahlen → bekannter Betrag. Rundung an der Grenze. Unbekanntes Modell → definierter Fehler, kein stilles Null. Kostenloser Anbieter → null, aber protokolliert.

**M2-06 · Token-Zählung im Stream (2 Sessions)** — Zone A, der zweitschwerste Teil

Der Puffer aus M1-07 existiert. Jetzt: Usage-Chunk finden, auswerten, in Kosten umrechnen, in den Log schreiben. Und die Fälle, in denen der Usage-Chunk fehlt (Anbieter liefert ihn nicht, Stream bricht ab) — was steht dann im Log? Ein definierter Zustand, kein `null`, über das du im Dashboard stolperst.

**→ Build in Public, Beitrag 3.** Fragen: Wie hast du die Chunks gleichzeitig ausgeliefert und gepuffert? Was passiert, wenn der Client mittendrin abbricht, zahlst du dann trotzdem? Wie testest du das ohne Netzwerk?

**M2-07 · Rate Limit über Redis (2 Sessions)** — Zone A

Erst der Algorithmus: fixes Fenster (einfach, aber Burst an der Fenstergrenze) oder Sliding Window (fairer, aufwendiger). **ADR-0010** mit der Wahl.

Tests gegen echten Redis, eigene Datenbanknummer, injizierte Uhr. Fälle: unter dem Limit, genau am Limit, über dem Limit, Fenster läuft ab. Und: 429 muss einen korrekten `Retry-After`-Header haben — ein 429 ohne diesen Header ist für den Client wertlos.

### Woche 7 — Ausfallsicherheit

**M2-08 · Timeouts und Retries (1–2 Sessions)** — Zone A

Exponentieller Backoff mit Jitter. Der Jitter ist nicht Zierrat: ohne ihn laufen alle wartenden Requests gleichzeitig wieder los und erschlagen den Anbieter im Moment seiner Erholung.

Wichtiger Test: **nicht jeder Fehler darf wiederholt werden.** Ein 429 ja, ein 500 ja, ein 401 nein (der Key wird beim dritten Versuch nicht gültiger), ein 400 nein. Ein Retry auf einen nicht-idempotenten Fehler kostet dich echtes Geld.

**M2-09 · Circuit Breaker (2 Sessions)** — Zone A, das TDD-Musterbeispiel

Drei Zustände: Closed, Open, Half-Open. Tests entlang der Zustandsübergänge, mit injizierter Uhr:

- Closed, Fehler unter Schwelle → bleibt Closed
- Closed, Schwelle erreicht → Open
- Open, Anfrage kommt → sofort abgelehnt, kein Anbieteraufruf
- Open, Zeit abgelaufen → Half-Open
- Half-Open, Probeanfrage erfolgreich → Closed
- Half-Open, Probeanfrage fehlgeschlagen → wieder Open

Der Half-Open-Zustand ist der Punkt, nach dem Beitrag 4 fragt: Ohne ihn schickst du beim Ablauf des Timers den vollen Verkehr auf einen Anbieter, der sich vielleicht noch nicht erholt hat. **ADR-0011** mit Schwellenwerten und Begründung.

**M2-10 · Fallback-Kette (1–2 Sessions)** — Zone A

Reihenfolge, Abbruchbedingung, Protokollierung der Fallback-Tiefe. Test: erster Anbieter offen, zweiter antwortet, Client merkt nichts, Log zeigt Tiefe 1.

**M2-11 · Quizly umstellen (1 Session)**

Wie M1-11, inklusive Rückweg.

**Abschlussnachweis:** Groq-Key im Container absichtlich ungültig machen. Verkehr läuft weiter. Log zeigt den Zustandswechsel des Breakers.

**→ Build in Public, Beitrag 4.** Fragen: Wie hast du den Ausfall simuliert? Wie lange vom ersten Fehler bis zum Umschalten? Warum Half-Open statt einfachem Retry, was passiert ohne den Zwischenzustand? Zeig den Zustandswechsel im Log.

README aktualisieren.

---

## 10. M3 — Eval-Harness (W8–W10, 26.10. – 13.11., ~15 Sessions)

Der wichtigste Meilenstein. Spec: *„Ohne ihn ist das Projekt eine weitere Demo."* Wenn du in Verzug bist, kürzt du woanders.

**Ab hier läuft die Dashboard-Spur parallel: eine feste Session pro Woche, freitags.**

### Woche 8 — Aufgabenset und Runner

**M3-01 · Eval-Set schreiben (3 Sessions, verteilt)**

50–60 Aufgaben, **von Hand**, in `eval-data/` als JSON, versioniert. Kategorien: Extraktion, Klassifikation, Zusammenfassung, Rechnen, längeres Schreiben.

Warum von Hand: Ein generiertes Eval-Set misst, wie gut ein Modell zu einem anderen Modell passt. Deine Aufgaben sollen aus deinen echten Anwendungsfällen kommen — Code-A-Cuisine und Quizly geben dir realistische Vorlagen.

Pro Aufgabe: ID, Kategorie, Prompt, optional erwartete Ausgabe, Bewertungskriterien. Das Format legst du einmal fest und änderst es nicht mehr, sonst sind alte Ergebnisse unbrauchbar. **ADR-0012.**

Das sind ~15 Aufgaben pro Session. Zieh es über die Woche, nicht an einem Stück — das Set wird besser, wenn du zwischendurch darüber nachdenkst.

**M3-02 · Runner mit Platten-Cache (2 Sessions)** — Zone A

Der Runner ruft jede Aufgabe gegen jedes Modell und speichert Ergebnis, Kosten, Latenz.

**Der Cache-Schlüssel ist die kritische Stelle.** Er besteht aus Aufgabe, Modell **und allen Parametern** (Temperatur, max_tokens, System-Prompt). Wenn du einen Parameter vergisst, bekommst du beim nächsten Lauf still das alte Ergebnis unter neuen Bedingungen — und merkst es erst, wenn deine Zahlen unerklärlich sind. Das ist dieselbe Falle wie beim Response-Cache in M4, nur früher und leiser.

**Pflicht laut CLAUDE.md:** `--limit` und `--dry-run`. `--dry-run` gibt aus, wie viele Aufrufe anstünden und was sie schätzungsweise kosten, ohne einen einzigen zu machen. Du baust das **zuerst**, nicht später.

Test-first: Cache-Treffer macht keinen Aufruf. Cache-Verfehlung macht genau einen. Geänderter Parameter erzeugt einen neuen Schlüssel.

**M3-03 · Frontend-Setup (1 Session)** — Dashboard-Spur, Zone C

Vite + React + TypeScript + Tailwind, Vitest + Testing Library + msw. Eine Seite, die „läuft" zeigt. Ein Test, der eine Komponente rendert.

Mehr nicht. Das Ziel dieser Session ist eine funktionierende Werkzeugkette, keine Oberfläche.

### Woche 9 — Judge

**M3-04 · Judge und Rubrik (2 Sessions)** — Zone A

Ein Modell bewertet Antworten gegen eine Rubrik. Die Rubrik liegt versioniert in `eval-data/`, nicht im Code.

Test-first für das Parsing: Was passiert bei einer Bewertung außerhalb der Skala? Bei Fließtext statt Zahl? Bei abgeschnittener Antwort? Das Modell wird alle drei Fälle irgendwann liefern.

Günstiges Judge-Modell beim Iterieren (Spec §7, Hebel 4). Das teure nur für den finalen Vergleich.

**M3-05 · Erster echter Eval-Lauf (1 Session)**

**Vor diesem Lauf: `--dry-run`, Kosten ausrechnen, mir zeigen.** Das ist der erste Punkt im Projekt, an dem echtes Geld fließt. Grobe Erwartung aus Spec §7: rund ein Dollar für einen vollen Lauf, mit Batch-API die Hälfte.

Erst `--limit 5`. Ergebnisse ansehen. Dann der volle Lauf.

**M3-06 · Dashboard: erste Datenansicht (1 Session)** — Dashboard-Spur

Eine Tabelle mit echten Eval-Ergebnissen. Kein Styling, keine Charts. Der Punkt ist der Datenfluss vom Backend bis in die Komponente — und dass du siehst, wie React sich anfühlt, wenn echte Daten kommen.

### Woche 10 — Taugt der Judge?

**M3-07 · 50 Antworten von Hand labeln (2 Sessions)**

Stumpfe Arbeit, und der Abschnitt, der das Projekt von den anderen trennt. Ohne diese Zahl ist jede spätere Qualitätsaussage eine Behauptung.

Wichtig: **Labele blind.** Wenn du beim Labeln die Judge-Bewertung siehst, misst du deine eigene Zustimmungsneigung, nicht die Übereinstimmung.

**M3-08 · Agreement messen (1 Session)** — Zone A

Übereinstimmung zwischen deinen Labels und dem Judge. Rohe Übereinstimmung reicht als erste Zahl; wenn du es sauber willst, nimm Cohens Kappa — das korrigiert um Zufallstreffer und ist die Zahl, nach der im Vorstellungsgespräch gefragt wird.

Test-first: bekannte Eingaben → bekannte Metrik. Randfälle: völlige Übereinstimmung, völlige Uneinigkeit.

**M3-09 · Rubrik nachschärfen (1–2 Sessions)**

Wenn die Übereinstimmung schlecht ist: Wo genau liegt der Judge daneben? Bei welcher Kategorie? Rubrik anpassen, erneut messen, **Veränderung dokumentieren**. Genau danach fragt Beitrag 6.

**M3-10 · Dashboard: Eval-Tabelle (1 Session)** — Dashboard-Spur

Qualität, Kosten, Latenz pro Modell und Kategorie. Recharts einführen, ein Diagramm.

**Abschlusskriterium:** Die Tabelle existiert, und du weißt, wie zuverlässig dein Judge ist.

**ADR-0013:** Judge-Modell, Rubrik-Version, gemessene Übereinstimmung.

**→ Build in Public, Beitrag 6** — laut Spec der stärkste der Reihe. Fragen: Wie viele deiner 50 Handlabels stimmten mit dem Judge überein? Bei welcher Art Aufgabe lag er daneben? Was hast du am Rubrik-Prompt geändert und wie hat sich die Übereinstimmung verschoben? Würdest du dem Judge jetzt trauen?

README aktualisieren.

---

## 11. M4 — Router und Cache (W11–W14, 16.11. – 11.12., ~20 Sessions)

**Abschlusskriterium:** Eine Tabelle mit einer Zeile pro Ausbaustufe und den Spalten Kosten, Qualität, Latenz. Aus ihr kommt die Zahl fürs README.

### Woche 11 — Exakter Cache

**M4-01 · Cache-Key (1–2 Sessions)** — Zone A, striktes TDD

**Die Falle, um die es in Beitrag 5 geht.** Schreib die Tests, bevor du den Key baust:

- Gleiche Nachrichten, gleiches Modell, gleiche Parameter → gleicher Key
- **Anderer System-Prompt → anderer Key.** Wenn dieser Test fehlt und der System-Prompt nicht im Key steckt, liefert Code-A-Cuisine irgendwann eine Antwort aus Quizlys Kontext. Der Fehler ist still und im Log kaum zu sehen
- Andere Temperatur → anderer Key
- Andere Reihenfolge der Nachrichten → anderer Key
- `max_tokens` anders → **anderer Key?** Das ist eine echte Entscheidung. Begründe sie

**ADR-0014:** welche Parameter in den Key gehören und welche bewusst nicht.

**→ Build in Public, Beitrag 5.** Fragen: Was genau geht schief, wenn der System-Prompt nicht in den Key einfließt? Ist es dir passiert oder hast du es vorher bedacht? Welche Parameter gehören noch rein und welche bewusst nicht?

Wenn dir der Fehler schon in M3-02 beim Runner-Cache passiert ist: zieh den Beitrag vor. Ein echter selbst erlebter Fehler liest sich besser als ein bedachter.

**M4-02 · Exakter Cache anschließen (2 Sessions)** — Zone A + B

Nachschlagen vor dem Anbieteraufruf, schreiben danach. Ablaufzeit. `cache_hit` im Log füllen.

Die unangenehme Frage: **Cachest du auch Streaming-Antworten?** Ein Cache-Treffer auf einen Stream muss die gepufferte Antwort wieder als Chunks ausliefern, sonst verhält sich das Gateway bei Treffer anders als bei Verfehlung. Test dafür.

**M4-03 · Dashboard: Cache-Trefferquote (1 Session)** — Dashboard-Spur

### Woche 12 — Semantischer Cache

**M4-04 · Embeddings und Ähnlichkeitssuche (2–3 Sessions)** — Zone A

Ähnliche Anfragen finden. Schwellenwert konfigurierbar.

**Bevor du baust, definiere das Abschaltkriterium.** Ab welcher Fehltrefferquote fliegt der semantische Cache raus? Schreib die Zahl **jetzt** auf, nicht nachdem du die Ergebnisse gesehen hast — sonst redest du dir das Ergebnis schön. Die Spec sagt ausdrücklich: Abschalten ist ein akzeptables Ergebnis, kein Scheitern.

**M4-05 · Fehltrefferquote messen (2 Sessions)**

Gegen das Eval-Set. Wie oft liefert der semantische Cache eine Antwort, die inhaltlich nicht passt? Über mehrere Schwellenwerte messen und die Kurve ansehen.

**ADR-0015:** Schwelle, gemessene Quote, Entscheidung ein/aus.

**M4-06 · Dashboard: Fehltrefferquote (1 Session)** — Dashboard-Spur

### Woche 13 — Router A

**M4-07 · Klassifikation vorab (2–3 Sessions)** — Zone A

Ein kleines Modell klassifiziert die Anfrage, das Ergebnis bestimmt die Modellstufe. Test-first: bekannte Anfrage → bekannte Stufe. Unklarer Fall → definierte Vorgabe (welche? Entscheidung).

**M4-08 · Router A gegen das Eval-Set messen (1 Session)**

`--dry-run` zuerst.

**M4-09 · Dashboard: Modellverteilung (1 Session)** — Dashboard-Spur

**→ Build in Public, Beitrag 8** — nur falls der semantische Cache tatsächlich rausfliegt. Fragen: Wie hoch war die Fehltrefferquote? Ab welcher Schwelle wurde die Trefferquote unbrauchbar? Was hätte es gekostet, ihn trotzdem eingeschaltet zu lassen?

### Woche 14 — Router B und der Vergleich

**M4-10 · Kaskade (2–3 Sessions)** — Zone A

Erst das günstige Modell, ein Prüfer entscheidet über Eskalation. Test-first: Antwort gut genug → keine Eskalation. Antwort zu schwach → Eskalation, und die Kosten **beider** Aufrufe werden protokolliert. Der zweite Punkt ist der, an dem eine Kaskade in der Praxis teurer wird als gedacht.

**M4-11 · A gegen B messen (1–2 Sessions)**

Beide gegen dasselbe Eval-Set. `--dry-run`, Kosten zeigen, dann laufen lassen.

**M4-12 · Die Ergebnistabelle (1 Session)**

Eine Zeile pro Ausbaustufe: Baseline (immer das teure Modell), nur Cache, Router A, Router B, Router + Cache. Spalten: Kosten, Qualität, Latenz.

**Aus dieser Tabelle kommt die Zahl fürs README.** Sie kommt aus dem Eval-Set, nicht aus dem Produktivverkehr — und dass sie das tut, steht mit im README (Spec §8).

**ADR-0016:** Router A gegen B, Ergebnis, Entscheidung.

**→ Build in Public, Beitrag 7.** Fragen: Welche Variante hat gewonnen? Um wie viel, bei welchen Kosten? Wo verliert die Gewinner-Variante trotzdem? Hättest du das vorher so getippt?

README aktualisieren.

---

## 12. M5 — Dashboard und Abschluss (W15–W16, 14.12. – 23.12., ~10 Sessions)

**Abschlusskriterium:** Jemand ohne Vorwissen versteht in einer Minute, was das Ding tut und wie gut es das tut.

Weil die Dashboard-Spur seit W8 läuft, hast du hier Komponenten, Datenfluss und Vitest-Setup schon stehen. Du baust zusammen, nicht neu.

### Woche 15 — Dashboard fertig

**M5-01 · Übersichtsseite (2 Sessions)** — Kern
Kosten pro Tag, Modellverteilung, Cache-Trefferquote, Fehlerquote. Recharts.

**M5-02 · Request-Explorer (2 Sessions)** — Kern
Liste mit Filter, Detailansicht eines Requests. Paginierung serverseitig — die Tabelle wird groß.

**M5-03 · Eval-Vergleich zweier Läufe (1–2 Sessions)** — **Kür, fällt zuerst**

**M5-04 · Demo-Key (0,5 Sessions)** — Kern
Eigener Key mit engem Limit, damit Prüfer es selbst ausprobieren können. Eigenes Budget, damit ein Fremder dir keine Rechnung macht.

### Woche 16 — Abschluss

**M5-05 · Tests aufräumen (1 Session)**
Suite ohne Netzwerk und ohne Kosten laufen lassen — die harte Regel prüfen, nicht annehmen. Übersprungene Tests durchgehen: wieder aktivieren oder löschen.

**M5-06 · README (2 Sessions)** — der wichtigste Text des Projekts

Enthält: Architekturbild, die gemessene Zahl mit ihrer Herkunft, dein gemessener Overhead (p50/p95), die Abgrenzung gegenüber LiteLLM und OpenRouter, die Einschränkung dass Ollama nur lokal läuft und in Produktion nicht verfügbar ist, und die Notiz dass die Prozentzahl aus dem Eval-Set kommt und nicht aus dem Produktivverkehr.

Die Abgrenzung ist keine Pflichtübung. Spec §1: *„LiteLLM und OpenRouter machen dasselbe und besser."* Das ehrlich zu schreiben, wirkt in einem Vorstellungsgespräch stärker als jede Erfolgsmeldung — es zeigt, dass du dein eigenes Projekt einordnen kannst.

**M5-07 · Loom-Video unter drei Minuten (1 Session)**
Skript vorher schreiben. Drei Minuten sind kurz.

**→ Build in Public, Beitrag 9.** Fragen: Wie lautet die Zahl, und woraus genau ist sie gerechnet? Was würdest du beim nächsten Mal anders bauen? Was macht LiteLLM besser als du und warum? Was hast du in vier Monaten gelernt, das du vorher nicht konntest?

---

## 13. Architekturentscheidungen — die Liste

CLAUDE.md: *„Bei jeder Architekturentscheidung eine kurze Notiz in `docs/decisions/`."* Diese fallen planmäßig an. Ich erinnere dich, wenn eine Entscheidung fällt und keine Notiz entsteht.

Format je ADR: Datum, Entscheidung, betrachtete Alternativen, Begründung. Eine halbe Seite. Am **Tag der Entscheidung** geschrieben, nicht nachträglich rekonstruiert.

| ADR | Woche | Thema |
|---|---|---|
| 0001 | W1 | Eigenes Repo statt Workspace-Unterordner |
| 0002 | W1 | Python-Version, pip statt uv/poetry, Pinning |
| 0003 | W2 | Kostenrepräsentation (Ganzzahl) und getrennte Latenzmessung |
| 0004 | W2 | API-Key-Speicherung: Hash-Verfahren |
| 0005 | W3 | Streaming: Pufferung und Verhalten bei Client-Abbruch |
| 0006 | W3 | ASGI-Server und Worker-Modell |
| 0007 | W4 | Deployment-Topologie auf dem VPS |
| 0008 | W5 | Provider-Abstraktion: wo der Schnitt liegt |
| 0009 | W6 | Preise als Daten, nicht als Code |
| 0010 | W6 | Rate-Limit-Algorithmus |
| 0011 | W7 | Circuit-Breaker-Parameter; django-rq vs. Django-6-Tasks |
| 0012 | W8 | Eval-Set: Kategorien und Format |
| 0013 | W10 | Judge-Modell, Rubrik, gemessene Übereinstimmung |
| 0014 | W11 | Cache-Key: welche Parameter, welche nicht |
| 0015 | W12 | Semantischer Cache: Schwelle und Abschaltkriterium |
| 0016 | W14 | Router A gegen B: Ergebnis und Entscheidung |

Dazu jeder ungeplante ADR: Wenn du eine Entscheidung triffst, die nicht in dieser Liste steht, bekommt sie trotzdem eine Notiz.

---

## 14. Kostenkontrolle

CLAUDE.md ist hier streng, und die Regeln sind operativ, nicht dekorativ:

1. **Kein Skript, das Modelle in einer Schleife aufruft, ohne `--limit` und `--dry-run`.** Beides wird gebaut, bevor der erste echte Lauf startet — in M3-02, nicht danach.
2. **Vor jedem vollen Lauf** rechne ich dir die geschätzten Kosten aus, und du bestätigst.
3. **Jede Modellantwort landet auf der Platte.** Ein Wiederholungslauf kostet nur, was sich geändert hat.
4. **Batch-API für Eval-Läufe.** Halber Preis, Ergebnis in Stunden — und ein Eval-Lauf ist nie eilig. Ein Testjob in W9, bevor du 220 Aufgaben hineinwirfst.
5. **Ausgabenlimit in der Anthropic-Console: 20 € hart, Warnung bei 10 €.** Das ist die einzige Absicherung, die auch dann greift, wenn du um Mitternacht einen Schleifenfehler baust.

Budgetrahmen laut Spec: 30–55 € über vier Monate. Trag nach jedem Eval-Lauf die tatsächlichen Kosten in eine Zeile in `docs/decisions/` oder ein Log — dann siehst du in W12, ob du im Rahmen liegst, statt es zu hoffen.

---

## 15. Risiken

| Risiko | Woran du es merkst | Was du dann tust |
|---|---|---|
| **ASGI kostet mehr Zeit als gedacht** | Woche 3 endet ohne funktionierendes Streaming | M1 um eine Woche verlängern, M2 kürzen. Streaming ist Kern, es fällt nicht |
| **Verzug bis W10** | M3 ist Mitte November nicht fertig | M5 auf Übersicht + README + Loom eindampfen. Eval nie kürzen |
| **Bewerbungen fressen Wochen** | Zwei Wochen ohne Commit | Offen posten (Spec §11: „wird offen gesagt statt still eingeschlafen"), Umfang von M4 auf einen Router reduzieren |
| **TDD wird lästig und fällt weg** | Du schreibst Tests nach dem Code | Das ist der teuerste Fehler im Plan. Wenn du merkst, dass es passiert: sag es mir. Zone-A-Aufgaben ohne Test-first sind nicht fertig |
| **Python 3.14 macht Ärger** | `pip install psycopg` bricht mit Compiler-Fehler ab | Auf 3.13 wechseln, `.python-version` und Dockerfile anpassen, ADR-0002 ergänzen |
| **Semantischer Cache funktioniert nicht** | Fehltrefferquote über deiner vorher definierten Schwelle | Ausbauen und Beitrag 8 schreiben. Das ist ein Ergebnis, kein Scheitern |
| **Gateway fällt aus, echte Apps hängen** | Code-A-Cuisine antwortet nicht mehr | Umgebungsschalter zurück auf Direktaufruf. Der Schalter muss vor der Umstellung existieren, nicht danach |
| **React bleibt fremd** | W10, das Dashboard ist noch eine Tabelle | Genau dafür ist die Spur da. Halte die wöchentliche Session, auch wenn Backend drängt — sie ist dein Werkstudenten-Argument |

---

## 16. Verifikation

### Nach jeder Aufgabe

```bash
# Backend
pytest                              # grün
ruff check . && ruff format --check .
mypy backend/
python manage.py makemigrations --check --dry-run   # keine ausstehenden Migrationen

# Frontend (ab W8)
npx vitest run
npx tsc --noEmit
```

Dann PR öffnen, CI abwarten, squash-mergen.

### Nach jedem Meilenstein

**M1:** Echter Aufruf von Code-A-Cuisine aus, dann in der Produktions-Datenbank die Zeile suchen. Overhead p50/p95 aus den Log-Daten berechnen.

**M2:** Groq-Key im Container ungültig setzen. `curl` gegen das Gateway. Antwort kommt trotzdem. Log zeigt Fallback-Tiefe und den Zustandswechsel des Breakers. **Erst danach** ist M2 fertig.

**M3:** Eval-Tabelle existiert. Agreement-Zahl existiert. `pytest` läuft mit deaktiviertem Netzwerk durch — probier es aus, verlass dich nicht darauf.

**M4:** Ergebnistabelle mit einer Zeile pro Ausbaustufe. Cache-Key-Tests decken den System-Prompt ab.

**M5:** Fremde Person auf die README-Seite setzen und eine Minute geben. Wenn sie danach nicht sagen kann, was das Ding tut, ist M5 nicht fertig.

### Der Test, der nie fehlschlagen darf

```bash
# Netzwerk aus, Suite muss trotzdem grün sein
pytest
```

Wenn dieser Lauf jemals rot wird, hat sich ein echter Anbieteraufruf in die Tests geschlichen. Das ist die harte Regel aus CLAUDE.md, und sie ist die einzige, deren Verletzung dich Geld kostet.

---

## 17. Was ich in jeder Session mache

Damit klar ist, was du von mir erwarten kannst:

- **Vor der Aufgabe:** kurzer Plan — was gebaut wird, welche Dateien, welche Entscheidung offen ist
- **Während:** Muster erklären, wenn du danach fragst (kurz, als Erklärung gekennzeichnet, nicht zum Kopieren). Fehlermeldungen mit dir auseinandernehmen statt sie zu lösen
- **Nach der Aufgabe:** strenger Review. Korrektheit, Fehlerpfade, fehlende Tests, Lesbarkeit. Das ist laut CLAUDE.md der wertvollste Teil unserer Zusammenarbeit, und ich behandle ihn so
- **Ungefragt:** Ich sage dir sofort, wenn ich einen Fehler in deinem Code sehe, auch wenn du gerade nach etwas anderem gefragt hast
- **Erinnerungen:** ADR fehlt, Build-in-Public-Zeitpunkt erreicht, `.env.example` nicht gepflegt, Definition of Done nicht erfüllt
- **Widerspruch:** Wenn du etwas verlangst, das schlecht ist, sage ich es und begründe es

**Ich schreibe keinen Code in dieses Repo.** Wenn du mich darum bittest, frage ich einmal nach und weise auf diesen Abschnitt hin. Wenn du dann bestätigst, mache ich es — und es kommt in `docs/decisions/`, damit du im Dezember weißt, welche Stellen nicht von dir sind.

**Ich sehe keine Secrets.** Abschnitt 0. Diese Regel hat keine Ausnahme und keinen Bestätigungsweg — anders als die Code-Regel kannst du sie nicht überstimmen. Wenn du mich bittest, in die `.env` zu schauen, lehne ich ab und sage dir stattdessen, welchen Variablennamen du brauchst.
