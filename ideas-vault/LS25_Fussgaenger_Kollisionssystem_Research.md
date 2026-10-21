# LS25 – Fußgänger-Kollisionssystem („Flatsch“)

**Status:** Rekonstruierte Research / Ideen-Vault – pausiert  
**Ursprüngliche Gespräche und Tests:** 15.–19. September 2026  
**Rekonstruiert:** 21. Oktober 2026  
**Projektkontext:** Agriculture Science / Farming Simulator 25; erste Entwicklung von `FS25_DevTools`

> **Quellenhinweis:** Dieses Dokument rekonstruiert die in früheren Unterhaltungen festgehaltenen Ergebnisse. Es ist kein vollständiger Ersatz für originale Logdateien oder den damaligen Source-Stand. Beobachtungen, Konzeptideen und noch offene Fragen sind getrennt. Keine neue Laufzeitvalidierung.

## 1. Ursprüngliche Idee

Ein optionales humoristisches System für Begegnungen von Fahrzeugen und NPC-Fußgängern in LS25:
- Charakteristischer „Flatsch“-Sound bei erkannter Begegnung/Kollision.
- Optional temporäres Decal beziehungsweise Fleck.
- Mögliche spätere zusätzliche Effekte.

Es existiert kein bestätigter produktiver Prototyp; Performance, Darstellung und MP/Dedi sind offen.

## 2. Ursprung der DevTools

Fragestellung: Sind Fußgänger in der GIANTS-Physik über einen Kollisions- oder Raycast-Treffer zugänglich? Dafür wurde zunächst `FS25_DevTools` im Entwicklungszweig `dev-tools` unter `dev_tools/FS25_DevTools/` geschaffen.

Historische Belegung (nicht notwendigerweise heute gültig):

| Taste | Funktion |
|---|---|
| F8 | Raycast-Inspector / Raycast-Dump |
| F9 | Wiederholung Raycast-Test |
| F10 | Fußgänger-Scan |
| F11 | API-Discovery |

Untersucht: `g_currentMission.pedestrianSystem`, `raycastClosest`, `getRigidBodyType`, Nodes, RigidBody-/Collision-/Trigger-Dumps in `log.txt`, HUD-Rückmeldungen.

Die historische F10-Belegung ist **kein Beweis** für einen Zusammenhang mit dem später beobachteten Render-Pass-Debugger.

## 3. Historische Testergebnisse (19. September 2026)

Es wurden **14 `pedestrianNodes`** gefunden, darunter Referenzen auf `playerM_pedestrian` und `playerF_pedestrian`. Für die untersuchten Nodes:

```text
rigidBodyType = 0
collision    = false
trigger      = false
```

**Damals beobachtet:** Keiner der 14 untersuchten Nodes zeigte eine nutzbare Collider-/Trigger-Konfiguration; verwendete Raycasts passierten sichtbare Fußgänger ohne Treffer.

**Grenze:** Das beweist weder, dass sämtliche Engine-Fußgänger stets kollisionslos sind, noch dass intern keine andere native Repräsentation besteht.

Beim inspizierten Child-/Skelettbaum wurden lokale Koordinaten gefunden, aber **keine verifizierte Weltposition eines Fußgänger-Roots**. Der native Instanz-/Bewegungszustand blieb ungeklärt.

## 4. Damaliger Ansatz: positionsbasierte Begegnungserkennung

**Konzept, nicht als funktionierend bestätigt.** Nicht auf einen Collision-Callback verlassen, sondern:
1. Fahrzeuge und stabile Fußgängerinstanzen ermitteln.
2. Verifizierte Weltpositionen und Bewegungen erheben.
3. Nur Kandidaten im Nahbereich eines relevanten Fahrzeugs prüfen.
4. Überlappung beziehungsweise Fahrzeugbewegungspfad berücksichtigen.
5. Doppelauslösung durch Cooldown verhindern.
6. Erst nach verlässlichem Nachweis Sound/Visualeffekt auslösen.

Spätere mögliche Präzisierungen, noch nicht getestet: orientierte Fahrzeuggeometrie statt reinem Mittelpunktabstand; schnelle Bewegungen und Swept-Tests; Spawn-/Despawn-Lifecycle; Scanintervalle und Performancegrenzen.

## 5. Offene Forschungsfragen

1. Wo liegen die tatsächlichen Fußgängerinstanzen in `pedestrianSystem`?
2. Wie findet man den korrekten Welttransform des bewegten NPC-Roots, und funktioniert `getWorldTranslation()` darauf?
3. Wer aktualisiert Positionen, mit welchen Ticks/Streaminggrenzen?
4. Ist die fehlende Kollision ein Designmerkmal oder nur ein Effekt des untersuchten Node-Zugangs?
5. Welche Erkennungsgeometrie und welche Geschwindigkeitsgrenzen sind sinnvoll?
6. Wie realisiert man Audio/Decals einschließlich Lebensdauer und Bereinigung?
7. Welche Instanz besitzt MP-/Dedi-Autorität, und wie verhindert man doppelte Events?
8. Wie wirken sich Spielupdates und andere Mods aus?

## 6. Plan zur späteren Wiederaufnahme

**A.** Alte DevTools-Branch, Scanlogs und Quellstände sichern, historische Messwerte an Originalartefakten prüfen.

**B.** Einem sichtbar bewegten Fußgänger eine konkrete Instanz/Root zuordnen und seine Weltposition an mehreren Orten nachweisen.

**C.** Rein lesenden Positions-/Nähe-Trace aufbauen, keine Physik erzwingen und zunächst keine Effekte.

**D.** Bewegung, hohe Geschwindigkeit, Streaming, Spawn/Despawn und Mehrspieler-Einflüsse prüfen.

**E.** Erst nach reproduzierbarer Erkennung Sound und optional Decal entwickeln.

## 7. Mögliche spätere Claude-Untersuchung: Native Root-/Transform-Verfolgung

**Nur Ideen-Vault, nicht beauftragt.**

Sollte die dokumentierte Lua-/SDK-Oberfläche keine stabile Fußgängerposition liefern, könnte Claude als unabhängiger Zweitgutachter die Kette **Fußgängerinstanz → Bewegungscontroller → Root/Transform → Weltposition → nutzbarer Lua-Zugriff** verfolgen.

Vorgehen: Erst SDK, Lua-Bindings, Instanzverwaltung, Animations-/Transformhierarchie, verfügbare Symbole und diagnostische Logs auswerten. Erst wenn diese Wege nicht genügen, eine rechtlich zulässige, **rein lesende** statische Reverse-Engineering-/Decompilierungsanalyse der relevanten nativen Engine-Bestandteile erwägen. Keine Binary-Patches, Code-Injection oder Engine-Manipulation. Jede Hypothese/Sackgasse samt Beleg dokumentieren und danach den nächsten Pfad prüfen. Eine gefundene native Funktion ist **noch keine** für LS25-Mods nutzbare Lua-Schnittstelle.

Ergebnisziel: belegte Transformkette, genaue Zugriffsgrenzen, kleine passive DevTools-Prüfexperimente und klar beschriebene offene Punkte. Unabhängige Befunde erst anschließend mit den bisherigen Annahmen abgleichen.

## 8. Was ausdrücklich nicht gelöst ist

- Keine bewiesene native Fußgängerkollision oder Collision-Callbacks.
- Keine verifizierte positionsbasierte Kollisions-/Begegnungserkennung.
- Keine bestätigten stabilen Fußgänger-Weltkoordinaten oder Native-Handles.
- Keine implementierten Audio-/Decal-/Multiplayer-Funktionen.
- Keine Garantie, dass die historischen 14 Nodes alle Fußgängerdarstellungen abbilden.

**Nächster belegbarer Meilenstein:** In einer echten Spielsitzung die Weltposition eines bewegten Fußgängers reproduzierbar nachweisen.

**Tags:** LS25, GIANTS, pedestrianSystem, DevTools, raycastClosest, getRigidBodyType, position-based detection, Flatsch, Claude, research.
