# Musik- und Audioarchiv: „Let the Chaos Begin“

**Status: Konzept und Bearbeitungsnotizen gesichert; Originaldateien/Binärmedien noch nicht im Vault.**

## Musikalische Idee

Der Nutzer orientierte sich an einem vorhandenen Referenztrack mit charakteristischem treibendem Retro-Rock-/Synth-Rock-Gefühl (im früheren Gespräch als Abspann von *Animality Bar: No Humanity* beschrieben). Die konkrete MMP-Idee: **erst ernster/bedrohlicher Auftritt nach der fünften Bestätigung**, rote Warntexte an die Spieler; dann allmählich Übergang in **fröhlichen, aufhellenden Rock**, sobald die eigentliche Wartungsaktion in Gang kommt.

Keine Übernahme fremder Song-Audiodateien oder Melodien ohne Rechte. Inspiration bezieht sich auf **Dramaturgie und allgemeine Stilmerkmale**, nicht auf ein lizenzfreies Sample.

## Bisheriger Track

- Arbeitstitel: **„Let the Chaos Begin“**.
- Zwischenstand war ein ca. **3:34** langes Stück; nach mehreren Suno-**Extend**-Schritten existierte laut Nutzer ein **knapp fünfminütiger** Mix.
- Es wurden mindestens zwei gefallende Varianten diskutiert, eine davon „hat mehr Feuer“. Eine endgültige binäre „Release-Master“-Datei ist **nicht** in diesem Vault abgelegt; daher nicht behaupten, dass ihre exakte Auswahl und ihr Hash archiviert wären.
- Der Track war **für MMP vorgesehen**, nicht als normale produktive APS-/A.S.S.-Hintergrundmusik freigegeben.

## Geplante technische Audioabschnitte – nur Konzept

- `MMP_Protocol_Intro`: musikalischer Aufbau / warnende Startinszenierung.
- `MMP_Chaos_Loop`: lebhafterer Hauptteil während des Ereignisses.
- `MMP_Protocol_Outro`: Abschluss.
- Die Segmentierung war eine **Planung**, kein Nachweis, dass diese drei Dateien bereits korrekt geschnitten oder geloopt wurden.
- Nach fünf Bestätigungen beginnt MMP; erst ab diesem Zeitpunkt sind serverweite Warnung und Audioinszenierung sinnvoll. Keine verbindliche Länge der Warnphase festgelegt.
- Bei künftiger Implementierung müssten Clients synchronisierte Eventzustände erhalten; der Dedicated Server darf keine lokales Musikabspielgerät voraussetzen.

## Suno-Stems und Restaurierung

Der Nutzer hatte Suno-Stems und einen fertigen Stereomix. Die Stems klangen teilweise stark artefaktbehaftet; **Bass** war gut brauchbar, **Keyboard und Synthesizer nur teilweise**. Andere Stems wurden nicht als verlässlich sauber bestätigt.

Bei längeren Hörproben fiel das typische scharfe **Zischeln in den Höhen** auf, teils bei Becken, Synths und Gitarren. Bevorzugter Bearbeitungsweg:

1. **Stereo-Master als Hauptquelle** sichern und unverändert behalten.
2. Einen repräsentativen **20–30-Sekunden-Ausschnitt** mit problematischen Höhen wählen.
3. Frequenzanalyse, behutsame **dynamische Hochton-EQ/De-Essing**-Korrektur; kein pauschaler harter Tiefpass.
4. Zwei bis drei auf gleiche wahrgenommene Lautheit angeglichene Varianten vergleichen: **Light**, **Balanced**, **Warm**.
5. Optional **Hybridversuch** mit wirklich brauchbarem Bass-/Keyboard-/Synth-Stem. **Nicht** unkontrolliert zum Originalmix dazumischen, weil die gleichen Signale dort bereits enthalten sind (Doppelung/Phasenprobleme).
6. Falls Stems das Ergebnis verschlechtern, beim Stereo-Master bleiben.
7. Erst nach A/B-Hörtest Gesamttrack bearbeiten; Loop-Übergänge gesondert testen.

**Bearbeitungsstatus:** Ein Codex-Auftrag zur lokalen Audiorestaurierung wurde erwogen; hier liegt kein bestätigter fertiger Remaster oder nachgewiesener Stemschnitt vor.

## Audio-Asset-/Rechtehinweise

Suno-Projektlinks, genaue Promptversionen und Downloadformate sind nicht vollständig verifiziert. Das Vorhandensein eines Suno-Exports belegt **nicht automatisch** eine Drittweitergabe-/Mod-Distributionsfreigabe. Vor jeder späteren Veröffentlichung die konkreten Nutzungsrechte und Entstehungsbedingungen des Tracks und der Stems prüfen.

Siehe [Assetinventar](ASSET_MANIFEST.md).
