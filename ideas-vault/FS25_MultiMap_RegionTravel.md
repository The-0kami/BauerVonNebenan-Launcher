# FS25 Multi-Map Region Travel

> **Status:** Ideen-Vault / vorerst pausiert  
> **Stand:** September 2026  
> **Ziel:** Den aktuellen Denk- und Forschungsstand festhalten, damit das Projekt später ohne Neustart bei null wieder aufgenommen werden kann.

---

## 1. Grundidee

Die ursprüngliche Idee war, den Landwirtschafts-Simulator 25 um eine Art **Regionen-Reisesystem** zu erweitern.

Dabei sollen mehrere eigenständige Maps wie Teile einer größeren Welt wirken. Ein Spieler fährt beispielsweise an einer Straße am Kartenrand in einen definierten Trigger und kann anschließend in eine andere Region wechseln.

Wichtig: Es war **nie** geplant, mehrere Maps nahtlos gleichzeitig in einer laufenden LS-Welt zu laden. Das wäre mit dem verfügbaren Modding-Zugriff sehr wahrscheinlich unrealistisch.

Das gewünschte Nutzergefühl wäre eher:

```text
Map / Region A
    ↓
Straße am Kartenrand
    ↓
Travel Trigger
    ↓
Ladevorgang / Serverwechsel
    ↓
Map / Region B
```

Die Maps bleiben technisch getrennt, sollen sich für die Spieler aber wie Regionen derselben Welt anfühlen.

---

## 2. Warum das Projekt pausiert wurde

Die Servergruppe fand die Idee technisch interessant, sah aktuell aber keinen ausreichend großen spielerischen Mehrwert, der den Entwicklungsaufwand rechtfertigt.

Das Projekt wurde deshalb **nicht als technisch unmöglich verworfen**, sondern bewusst archiviert.

Die wichtigste Erkenntnis vor dem Pausieren war:

> Bevor irgendeine Infrastruktur für Save-Synchronisation, FTP, Fahrzeugtransfer oder einen zentralen Orchestrator gebaut wird, muss zuerst bewiesen werden, dass ein LS25-Client zuverlässig von Server A auf Server B gebracht werden kann.

Der **Serverwechsel ist der Gatekeeper des gesamten Projekts**.

---

# 3. Ursprünglich betrachtete Ansätze

## 3.1 Laufenden Dedicated Server auf einen anderen Save umschalten

Erster Gedanke:

```text
1. aktuellen Save synchronisieren
2. Server vorbereiten
3. Server herunterfahren
4. Savegame wechseln
5. Server neu starten
```

Problem:

- Ein Dedicated Server arbeitet mit einem bestimmten geladenen Savegame.
- Ein sauberer Save-Wechsel zur Laufzeit scheint nicht als normale Modding-Funktion vorgesehen zu sein.
- Bei einem gemieteten Server besteht häufig nur Zugriff über das Dedicated-Server-Webinterface und FTP.
- Für Start/Stop/Save-Auswahl ist keine für dieses Projekt bekannte, dokumentierte API vorhanden.

Eine Browser-Automatisierung des Webportals wäre theoretisch möglich, wurde aber als unnötig komplex und fragil betrachtet.

**Status:** Nicht ausgeschlossen, aber nicht bevorzugt.

---

## 3.2 Zwei dauerhaft laufende Server

Der deutlich interessantere Ansatz wurde schließlich:

```text
Region A → Dedicated Server A
Region B → Dedicated Server B
```

Damit müsste beim Reisen kein Dedicated Server neu gestartet oder auf einen anderen Save umgeschaltet werden.

Der Spieler würde stattdessen den Multiplayer-Server wechseln.

Vorteile:

- Beide Regionen können dauerhaft geladen bleiben.
- Kein Savegame-Wechsel im laufenden Dedicated Server notwendig.
- Jede Map behält ihre eigenen lokalen Daten.
- Globaler Zustand kann separat synchronisiert werden.

Nachteil:

- Es wird ein zweiter Server benötigt.
- Der Client muss möglichst automatisch von Server A zu Server B wechseln können.
- Gemeinsame Daten müssen zwischen den Welten synchronisiert werden.

**Status:** Bevorzugte Architektur, falls automatischer Serverwechsel möglich ist.

---

# 4. Wichtigster offener Punkt: automatischer Serverwechsel

## 4.1 Ziel

Gesucht wird ein Ablauf ungefähr wie:

```text
Spieler ist auf Server A
        ↓
Grenztrigger wird ausgelöst
        ↓
Zielregion wird gespeichert
        ↓
Client verlässt Server A
        ↓
Client verbindet sich automatisch mit Server B
        ↓
Map B lädt
```

Ein Neustart von LS wäre akzeptabel, aber ein Wechsel innerhalb desselben LS-Prozesses wäre deutlich eleganter.

---

## 4.2 CLI / Startparameter

Es wurde überlegt, ob LS25 mit einem Startparameter direkt angewiesen werden kann, einen bestimmten Multiplayer-Server zu betreten, beispielsweise hypothetisch:

```text
-join <server>
-connect <address>
-serverAddress <address>
```

Zum Zeitpunkt der Recherche wurde **kein verlässlich dokumentierter Startparameter für einen direkten Multiplayer-Join gefunden**.

Das bedeutet nicht, dass intern keine entsprechende Möglichkeit existiert.

**Status:** Ungeklärt / kein bestätigter CLI-Auto-Join.

---

## 4.3 Join über interne Lua-/GUI-Funktionen

Ein wichtiger Recherchehinweis war die GIANTS-Klasse:

```text
JoinGameScreen
```

Sie gehört zum Multiplayer-Join-UI von LS.

Die zentrale Forschungsfrage lautet daher:

> Welche Funktion wird intern aufgerufen, wenn ein Spieler im Multiplayer-Menü einen Server auswählt und auf „Beitreten“ klickt?

Gesuchter Call-Flow ungefähr:

```text
JoinGameScreen
      ↓
Server auswählen
      ↓
Join Button
      ↓
interne Join-Funktion
      ↓
Connection / Network Manager
```

Wenn diese Join-Funktion aus Lua erreichbar ist, könnte ein Serverwechsel eventuell ohne vollständigen Client-Neustart möglich sein.

**Wichtig:** Es wurde noch keine konkrete funktionierende `joinServer(...)`-Funktion bestätigt.

---

# 5. Mod-Lifecycle und das Hauptmenü-Problem

Eine normale LS-Mod ist vor allem während einer geladenen Spielsession aktiv.

LS registriert bzw. lädt Mod-Inhalte bereits im Startprozess, aber missions-/spielbezogener Modcode hängt am geladenen Spiel bzw. Server.

Dadurch entstand folgende wichtige Frage:

> Bleibt ein von einer Mod installierter globaler Lua-Hook nach dem Verlassen des aktuellen Servers im Hauptmenü bestehen?

Möglicher Ablauf:

```text
Server A geladen
    ↓
RegionTravel-Mod installiert Hook auf JoinGameScreen
    ↓
Spieler löst Travel aus
    ↓
Server A wird verlassen
    ↓
Hauptmenü
    ↓
Hook existiert weiterhin?
```

Wenn **ja**, könnte die Mod bereits während Server A einen Hook vorbereiten, der anschließend im Hauptmenü automatisch Server B betritt.

Wenn **nein**, wird sehr wahrscheinlich ein externer Client-Agent bzw. der Bauer-von-Nebenan-Launcher benötigt.

**Status:** Muss experimentell getestet werden.

---

# 6. Vorgeschlagener erster Proof of Concept

Bevor irgendein anderes Subsystem entwickelt wird, sollte eine kleine Debug-/Tracer-Mod gebaut werden.

Arbeitstitel:

```text
FS25_RuntimeTracer
```

Sie soll **keine Multi-Map-Funktionalität** enthalten.

Sie dient ausschließlich dazu, LS25 beim Join/Leave zu beobachten.

## Test A – Überlebt ein Hook den Server-Unload?

1. Server/Save laden.
2. Mod installiert einen globalen Test-Hook oder eine globale Variable.
3. Im Log erscheint z. B.:

```text
[RegionTrace] Hook installed
```

4. Server normal verlassen.
5. Multiplayer-Menü öffnen.
6. Prüfen, ob der Hook noch feuert.

Gewünschter Nachweis:

```text
[RegionTrace] Hook survived session unload
```

### Ergebnisinterpretation

**Hook bleibt aktiv:**

Sehr gute Ausgangslage. Ein Serverwechsel könnte möglicherweise komplett innerhalb des laufenden LS-Prozesses umgesetzt werden.

**Hook verschwindet:**

Dann sollte der nächste Ansatz über einen externen Client-Agent bzw. Launcher laufen.

---

## Test B – Join-Call-Flow beobachten

Gezielt relevante Multiplayer-/GUI-Funktionen wrappen und protokollieren.

Prinzip:

```lua
local oldFunction = SomeJoinFunction

SomeJoinFunction = function(self, ...)
    print("[RegionTrace] SomeJoinFunction called")
    return oldFunction(self, ...)
end
```

Dabei nicht wahllos hunderte Funktionen hooken, sondern schrittweise von `JoinGameScreen` in Richtung Netzwerk-Layer arbeiten.

Gesucht werden unter anderem:

- ausgewählter Server
- Join-Callback
- Server-ID / Session-Informationen
- Disconnect-Callback
- Zeitpunkt des Session-Unloads
- Connection-Erstellung

Ziel des Tests:

> Einen normalen manuellen Join durchführen und danach exakt wissen, welche interne Funktion diesen Join tatsächlich auslöst.

---

# 7. Debug-Möglichkeiten in LS25

LS25 besitzt eine Entwicklerkonsole und ein `log.txt`, wodurch das Projekt nicht vollständig blind reverse-engineered werden muss.

Für die spätere Forschung relevant:

- Developer Controls / Console
- `log.txt`
- `print(...)`
- `Logging.info(...)`
- Lua-Funktionswrapper / Overwrites
- GIANTS Developer Network / Scripting-Dokumentation

Dadurch sollte sich zumindest der Lua-/GUI-Call-Flow vergleichsweise gut instrumentieren lassen.

Ein nativer Binary-Debugger sollte erst dann in Betracht gezogen werden, wenn der relevante Join-Code nicht über die Lua-Schicht erreichbar ist.

---

# 8. Langfristige Architektur – falls Serverwechsel funktioniert

Erst **nach erfolgreichem Serverwechsel-PoC** würde folgende Architektur relevant:

```text
                  GHOSTRIG / ORCHESTRATOR
                 ┌──────────────────────┐
                 │ Global World State   │
                 │ Sync / Conflict Mgmt │
                 │ Transfer Registry    │
                 └──────────┬───────────┘
                            │
                 ┌──────────┴──────────┐
                 ↓                     ↓
           Dedicated A           Dedicated B
             Map A                  Map B
```

Die LS-Server wären dann praktisch zwei Simulationsinstanzen derselben übergeordneten Welt.

---

# 9. FTP als möglicher Nachrichtenbus

Da gemietete Dedicated Server oft FTP-Zugriff bieten, entstand folgende Idee:

Jede Server-Mod schreibt regelmäßig ein kleines Statuspaket in einen eigenen Mod-/Settings-Bereich.

Beispiel:

```xml
<syncPacket revision="1842" source="serverA">
    <farm id="1">
        <money>425000</money>
    </farm>
</syncPacket>
```

Ein externer Orchestrator auf Ghostrig könnte periodisch:

```text
Server A per FTP abfragen
        ↓
Paket validieren
        ↓
Global State aktualisieren
        ↓
Paket per FTP auf Server B übertragen
```

Die Server-B-Mod würde neue Pakete erkennen und Änderungen über LS-Runtime-APIs anwenden.

### Wichtig

**Keine laufenden Savegame-XML-Dateien direkt per FTP überschreiben.**

Das könnte zu Race Conditions führen, wenn LS gleichzeitig speichert.

Stattdessen eigene Kommunikationsdateien verwenden, beispielsweise:

```text
modSettings/
└── FS25_RegionLink/
    ├── state.xml
    ├── incoming.xml
    ├── response.xml
    └── processed.xml
```

FTP wäre in diesem Modell nur der Transportweg bzw. Nachrichtenbus.

---

# 10. Periodischer Sync

Als erste Größenordnung wurde diskutiert:

- LS-Mod sammelt etwa alle 30 Sekunden relevante Daten.
- Ghostrig pollt deutlich langsamer als nötig, z. B. alle 30–60 Sekunden.
- Jede Nachricht besitzt Revision / ID / Timestamp.
- Bereits verarbeitete Revisionen werden ignoriert.

Beispiel:

```text
revision = 1842
lastAppliedRevision = 1841
→ anwenden

revision = 1842
lastAppliedRevision = 1842
→ ignorieren
```

Damit entstehen keine Doppelbuchungen durch wiederholte FTP-Übertragungen.

---

# 11. Global vs. regional

Ein entscheidendes Designprinzip:

> Nicht komplette Savegames synchronisieren.

Stattdessen zwischen globalem und regionalem Zustand unterscheiden.

## Möglicherweise global

- Farm / Farm-Zugehörigkeit
- Geld
- bestimmte Statistiken
- globale Zeit / Datum (optional)
- Fahrzeugbesitz
- Fahrzeug-Transferstatus
- Reise-/Regionstatus

## Regional

- Felder
- Boden-/Crop-Zustand
- Farmlands
- lokale Produktionen
- lokale Placeables
- mapgebundene Trigger
- Map-spezifische Objekte
- Fahrzeuge, die physisch in dieser Region stehen

---

# 12. Gemeinsame Farm und Geldproblem

Die einfachste technische Lösung wäre gewesen, jedem Spieler eine eigene Farm zu geben.

Das wurde jedoch als spielerisch unbefriedigend betrachtet, weil dadurch gemeinsamer Fuhrpark und gemeinsames Wirtschaften stark eingeschränkt würden.

Bevorzugtes Ziel bleibt daher:

```text
Eine Farm
├── gemeinsames Geld
├── gemeinsame Spieler
├── global registrierter Fuhrpark
├── Region A Besitz
└── Region B Besitz
```

## Problem mit absolutem Geld-Sync

Beispiel:

```text
Server A: 500.000
Server B: 500.000
```

Spieler A gibt auf Server A 200.000 aus.

Spieler B verdient auf Server B 300.000.

Wenn einfach der „neueste Kontostand“ übernommen wird, geht eine Änderung verloren.

Deshalb entstand die Idee eines zentralen **Transaction Ledgers**.

Statt:

```text
money = 300000
```

würden Änderungen als Deltas behandelt:

```text
TX-1041  -200000  Fahrzeugkauf
TX-1042  +300000  Ernteverkauf
```

Der Orchestrator berechnet daraus den autoritativen Kontostand.

### Unvermeidbarer Konflikt bei periodischem Sync

Wenn beide Server lokal 100.000 anzeigen und gleichzeitig je 80.000 und 70.000 ausgeben, können beide Käufe lokal akzeptiert werden, obwohl global nicht genügend Geld vorhanden war.

Eine vollständig saubere Lösung würde Echtzeit-Reservierungen vor Käufen erfordern.

Für einen privaten Server wäre vermutlich **eventual consistency** ausreichend:

- kurzfristige Abweichungen zulassen
- zentralen Wert später korrigieren

Das ist jedoch erst ein späteres Problem.

---

# 13. Fahrzeugtransfer

Langfristige Idee:

Jedes transferierbare Fahrzeug erhält eine globale ID, zum Beispiel:

```text
BVN-000143
```

Global Registry:

```text
Vehicle: BVN-000143
OwnerFarm: 1
Region: MAP_A
Status: ACTIVE
```

Beim Grenzübertritt:

```text
Map A
  ↓
Fahrzeugzustand exportieren
  ↓
Fahrzeug auf A entfernen / transferieren
  ↓
Orchestrator aktualisiert Region
  ↓
Map B
  ↓
Fahrzeug am Entry Point erzeugen
```

Damit existiert dasselbe Fahrzeug niemals gleichzeitig auf beiden Karten.

Zu übertragende Werte könnten später umfassen:

- Fahrzeugtyp / XML-Datei
- Konfigurationen
- Lackierung
- Verschleiß / Schaden
- Betriebsstunden
- Kraftstoff
- Fill Units / Ladung
- angehängte Geräte

### Reihenfolge

Fahrzeugtransfer ausdrücklich **nicht als ersten Prototyp bauen**.

Empfohlene Reihenfolge:

1. Serverwechsel
2. einfacher globaler Wert (z. B. Geld)
3. Farmstatus
4. einzelnes Fahrzeug
5. Anhänger / Implements
6. Füllstände / Ladung
7. komplexere Weltzustände

---

# 14. Live Editing / Runtime APIs

Mods wie Easy Development Controls und ähnliche Entwicklerwerkzeuge zeigen grundsätzlich, dass viele Werte während einer laufenden Session über Lua geändert werden können.

Daraus entstand folgende Einteilung:

## Wahrscheinlich gut live setzbar

- Geld
- Zeit / Zeitskalierung
- verschiedene Farmwerte
- Teleportation
- einige Fahrzeugwerte
- Fill Levels

## Wahrscheinlich über Spawn / Despawn lösbar

- Fahrzeuge
- Paletten
- Ballen
- bestimmte dynamische Objekte

## Eher map-/loadgebunden

- komplexe Placeable-Strukturen
- Map-Grundzustand
- bestimmte Farmland-/Terrain-Daten

Langfristig sollte der Orchestrator daher **nicht Savegame-Dateien blind patchen**, sondern nach Möglichkeit kleine Commands an die laufende Server-Mod senden, die LS selbst über seine Runtime-APIs ausführt.

---

# 15. Rolle des Bauer-von-Nebenan Launchers

Falls ein Serverwechsel innerhalb desselben LS-Prozesses nicht möglich ist, könnte der bestehende Launcher als Client-Agent dienen.

Möglicher Ablauf:

```text
Grenztrigger auf Server A
        ↓
pendingTravel wird lokal gespeichert
        ↓
LS wird beendet
        ↓
Launcher erkennt Travel Request
        ↓
Launcher startet LS erneut
        ↓
Client soll Server B betreten
```

Das Problem bleibt auch dort der Auto-Join.

Der Launcher löst daher den zentralen Forschungsblocker nicht automatisch, könnte aber später die äußere Orchestrierung übernehmen.

---

# 16. Forschungsfragen bei Wiederaufnahme

Diese Fragen sollten in genau dieser Reihenfolge beantwortet werden:

### P0 – Muss funktionieren

- Welche interne Funktion führt den Multiplayer-Join tatsächlich aus?
- Kann diese Funktion aus Lua aufgerufen werden?
- Welche Daten benötigt sie, um einen konkreten Server auszuwählen?
- Bleibt ein Lua-Hook nach Verlassen eines Servers im Hauptmenü bestehen?
- Kann ein Client Server A verlassen und ohne manuellen Menüweg Server B betreten?

### P1 – Danach

- Wie kann eine Server-Mod zuverlässig kleine State-Pakete schreiben/lesen?
- Welche Verzeichnisse sind auf dem gemieteten Server per FTP erreichbar?
- Kann der Ghostrig zuverlässig per FTP als Nachrichtenbus arbeiten?
- Welche Farmwerte können live gesetzt werden?

### P2 – Später

- Fahrzeugzustand vollständig erfassen
- Fahrzeuge sicher despawnen/spawnen
- Fahrzeug-IDs global verwalten
- Anhängerketten / Implements übertragen
- Konfliktauflösung für Geld und parallele Aktionen

---

# 17. Klare Stop-Regel

Bevor das Projekt wieder groß wird:

> **Keinen Orchestrator, keinen FTP-Sync und keinen Fahrzeugtransfer entwickeln, bevor der automatische Serverwechsel als Proof of Concept funktioniert.**

Minimaler Erfolgstest:

```text
Server A
→ Trigger / Debug-Befehl
→ Server A verlassen
→ Server B wird ohne manuelles Durchklicken betreten
```

Erst wenn dieser Ablauf reproduzierbar funktioniert, lohnt sich die restliche Infrastruktur.

---

# 18. Kurzfassung für Future Us

Die Idee ist technisch nicht als unmöglich verworfen.

Die favorisierte Architektur ist inzwischen **nicht** „ein Server lädt mehrere Maps“, sondern:

```text
mehrere dauerhaft laufende LS-Server
+ zentrale Synchronisation
+ automatischer Client-Serverwechsel
```

Die größte offene Frage ist ausschließlich der Client-Wechsel.

Wenn das Projekt irgendwann wieder aufgenommen wird:

1. `FS25_RuntimeTracer` bauen.
2. `JoinGameScreen` und angrenzende Join-Funktionen instrumentieren.
3. Prüfen, ob Hooks den Session-Unload überleben.
4. Einen Server-A → Server-B Proof of Concept bauen.
5. **Erst danach** über Ghostrig, FTP, Ledger und Fahrzeugtransfer weiterarbeiten.

---

## Referenzbegriffe für spätere Recherche

- `JoinGameScreen`
- `g_currentMission`
- Multiplayer connection / disconnect
- mission/session unload lifecycle
- `Utils.overwrittenFunction`
- Developer Console
- `log.txt`
- GIANTS Developer Network FS25 scripting documentation
- Easy Development Controls
- vehicle loading / spawning APIs

---

*Dieses Dokument beschreibt einen Forschungsstand und enthält bewusst auch Hypothesen. Nicht als Nachweis verstehen, dass die beschriebenen internen LS25-Funktionen bereits erfolgreich getestet wurden.*
