# Mass Maintenance Protocol – Konzeptstand

**Status: Zurückgestellt, kein Produktivfeature.**

## Sinn und Grundidee

Ein bewusst vom Spieler aktiviertes, überzeichnetes Massenwartungsereignis innerhalb des **eigenen Hofs / der eigenen Farm**. Nicht als automatische Routine im Hintergrund, nicht gegen fremde Höfe und nicht serverweit über alle Fahrzeuge.

Ziel war der Kontrast zwischen einem zunächst bedrohlich inszenierten „Notfallprotokoll“ und einer später ausbrechenden musikalischen, bewusst humorvollen Wartungs-„Party“.

## Auslösung und Freigabe

- Explizite Spieleraktion. **Keine** automatische Aktivierung.
- **Fünf** getrennte Bestätigungen beim auslösenden Spieler. Darunter eine bewusst überspitzte Warnung, dass Mitspieler den Auslöser wahrscheinlich verfluchen werden.
- **Erst nach der fünften Bestätigung** gilt das Protokoll als gestartet; ab dann ist die Warnsequenz global sichtbar bzw. hörbar. Die fünf Bestätigungen werden **nicht** global eingeblendet.
- Berechtigungen und Zuordnung zur Farm sind technisch vor Ausführung zu prüfen (konkrete Rollen-/Permission-API noch nicht ausgearbeitet).
- Betroffener Fuhrpark: Fahrzeuge/Geräte **der Farm des Auslösers**; Fremdhöfe bleiben unangetastet.

## Inszenierung

1. Spieler löst die Aktion aus und durchläuft fünf Bestätigungen.
2. Nach endgültiger Bestätigung: globale Startmeldung mit dem Namen des Auslösers.
3. Warnende, dunkle Dramaturgie, vorzugsweise **roter Text**, alarmierende Darstellung.
4. Musikalischer Beginn eher bedrohlich/treibend, passend zur Referenz „Let the Chaos Begin“; im weiteren Verlauf fließender Übergang zu **hellerem, fröhlicherem Retro-/Rock-Feeling**.
5. Start und tatsächlicher Ablauf der Wartungswelle werden mit der Musik/Inszenierung koordiniert. **Keine präzisen Zeitcodes festgelegt.**

**Humorvoller Entwurf einer globalen Meldung** (nicht final/lokalisiert):

> „[Spielername] hat das Mass Maintenance Protocol ausgelöst. Falls Ihnen danach ist, dürfen Sie dieser Person jetzt Ihren Unmut mitteilen.“

Originaler Humorwunsch war ausdrücklich frecher („bitte schreien oder beleidigen ...“). Die Formulierung ist ein **Platzhalter**, kein genehmigter finaler UI-String. Nachrichten und Humor sollten serverfreundlich und für alle Spieler verständlich bleiben.

## Was noch **nicht** festgelegt oder gebaut ist

- Keine Implementierung des MMP und keine Zusage, dass alle Fahrzeuge gleichzeitig wartbar wären.
- Noch keine genaue Definition von Reihenfolge, Konfliktauflösung, Farmberechtigung, Fahrzeugauswahl, Sessionzuständen und Performance-Grenzen.
- Keine festgelegte Synchronisation des Musikstarts oder des Übergangs zur heiteren Phase.
- Keine getestete Multiplayer-/Dedi-Synchronisation.
- Kein produktives A.S.S.-FIFO-Warten oder physisches Nachrücken.
- Die fünf Bestätigungsdialoge sind **konzeptionell**, nicht als finale UI-Elemente überliefert.

## Nicht mit dem aktuellen Agriculture Science Pack verwechseln

APS parkt/koordiniert Fahrzeuge, L.E.G.S. verwaltet Tore und Service-Bays, A.S.S. führt unterstützte einzelne Services aus. Das MMP wäre ein **separater Orchestrierungsmodus darüber**, nicht einfach eine bereits vorhandene Checkbox.
