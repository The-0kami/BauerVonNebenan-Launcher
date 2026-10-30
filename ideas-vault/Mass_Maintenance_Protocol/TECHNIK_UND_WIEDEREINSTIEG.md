# Technische Notizen und Wiedereinstieg

**Kein Implementierungsauftrag. Diese Datei konserviert nur den pausierten Plan.**

## Angedachte Zustände (Konzept, keine implementierten Enum-Namen)

```text
IDLE
  -> CONFIRMATION_1 ... CONFIRMATION_5 (nur Auslöser)
  -> VALIDATION (Farmzuordnung, Rechte, Kandidaten)
  -> ANNOUNCE_GLOBAL (nach finaler Zustimmung)
  -> WARNING_SEQUENCE / MUSIC_INTRO
  -> MAINTENANCE_WAVE / MUSIC_MAIN
  -> COMPLETE_OR_ABORT / MUSIC_OUTRO
  -> CLEANUP / IDLE
```

Die Reihenfolge von VALIDATION und der letzten Bestätigung ist für eine spätere technische Umsetzung festzulegen; **vor dem globalen Start darf nichts unbeabsichtigt ausgeführt werden**.

## Auftragsumfang und Farmgrenzen

- Farm-ID aus dem berechtigten anfordernden Spieler bestimmen und bei Serverfreigabe validieren.
- Nur **eigene Farmfahrzeuge** auswählen, nicht blind alle Objekte auf der Karte; Berechtigungs-/Miet-/Leihfälle offen.
- Andere Farmen dürfen weder automatisch verändert noch mit deren Fahrzeugen in den Wartungsauftrag aufgenommen werden.
- MMP soll bewusst ausgelöst werden, niemals als Standard-AutoService.
- Bei nicht verfügbaren Services/Bays ohne Endlosschleife und ohne Aussetzen von Reservierungs-/Occupancy-Sicherheiten reagieren.

## Verknüpfung mit APS / LEGS / ASS

- APS: bestehende Fahr-/Parkaufträge und mögliche Übergaben; darf nicht durch MMP überschrieben werden, ohne Konfliktregeln.
- LEGS: verfügbare Provider-/Bay-Kapazitäten und zeitbegrenzte Reservierungen; `UNKNOWN` bedeutet **nicht** freie Bay.
- ASS: vorhandene WASH-/REPAIR-/REFUEL-Dienste und native Gebäudetrigger; jeder abgeschlossene Service muss am tatsächlich beobachteten Ergebnis gemessen werden.
- Eine **ausführende Warteschlange** mit Nachrücken ist bisher **nicht produktiv implementiert**. MMP braucht daher ein **eigenes, serverautorisiertes** Scheduling-/Konfliktkonzept oder eine bewusste Beschränkung.
- Voice- und Musiksystem des Packs kann als Referenz dienen. Server entscheidet über Zustände; nur Clients stellen HUD, Warnungen und Musik dar.

## Multiplayer/Netzwerk: vor Umsetzung klären

1. Welche Farm-/Spielerrollen dürfen das Protokoll auslösen?
2. Können Clients bei Late Join den MMP-Zustand sauber übernehmen?
3. Was passiert bei Disconnect des Auslösers / bei Serverneustart?
4. Gibt es laufende AD-/APS-Aufträge oder gesperrte Hebebühnen?
5. Wie werden Servicegebäude, Bay-Leases, Kapazität und Fahrzeugauswahl priorisiert?
6. Wie werden Warnungen/Audio pro Client dargestellt, ohne private Meldungen falsch zuzuordnen?
7. Wie wird Zeit-/Musiksynchronisation robust gegenüber Latenz und nicht installierten Soundpacks?
8. Was passiert bei Abbruch, Fehlern, unbekannten Servicezuständen und Lade-/Speicherereignissen?

## Wiedereinstiegs-Checkliste

- [ ] Nutzer bestätigt, dass MMP reaktiviert werden soll.
- [ ] Tatsächliche Musikmaster, Suno-Stems, Extend-Versionen und eventuelle Audacity/Codex-Projekte in `assets/` übernehmen und Hashes inventarisieren.
- [ ] Trackrechte für eine öffentliche FS25-Moddistribution anhand konkreter Quellen prüfen.
- [ ] Aktuellen APS-/LEGS-/ASS-Quellstand lesen und bestehende Service-APIs gegen geplante Orchestrierung abgleichen.
- [ ] Scope/Bestätigungen/Message-Texte DE + EN finalisieren.
- [ ] Minimales Scheduling mit Farmgrenzen, Berechtigungen und Wiederherstellung spezifizieren.
- [ ] Musikphasen anhand **echter** Hörproben markieren und testen.
- [ ] Testmatrix für SP, Hosted MP, Dedicated Server, Late Join, Disconnect und Parallelaufträge definieren.
- [ ] Keine automatische Integration in Pack-Release ohne neue gesonderte Freigabe.
