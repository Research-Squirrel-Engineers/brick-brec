# Vom SfM-Original zur Rekonstruktion: Was wurde geändert?

Beide Modelle stammen aus KIRI-Engine-Scans (Structure-from-Motion). Die Rekonstruktionen sind **keine bereinigten Scan-Netze**, sondern prozedural aus idealisierten LEGO-Steinen neu aufgebaut. Vom Scan wurden nur Maße und Aufbau abgelesen, kein Netz und keine Textur übernommen.

## Gemeinsame Methode

- Steine sind Quader mit kleinen Fasen (0,14 mm), 0,05 mm Fuge und zylindrischen Noppen (Ø 4,8 mm, 1,7 mm hoch). Raster 8 mm, Steinhöhe 9,6 mm, alles mit 2/3 skaliert (Szenenmaßstab).
- Steintypen: 2x4, 2x2, 1x1. Die Belegung der Flächen erfolgt zufällig (viele Versuche, beste Lösung nach möglichst wenigen und möglichst großen Steinen).
- Noppen gibt es nur dort, wo die nächste Ebene nicht aufliegt.
- Materialien als Farben (PBR, Rauheit 0,3), Export als GLB und OBJ/MTL.

## Modell 1: weiße Stufenpyramide mit Säule und Minifigur

**Original:** unsaubere Basis, verrauschte Kanten und Noppen, die Figur oben verformt und gestreckt.

**Zwischenschritt:** Erst nur bereinigt (ausgerichtet, Basis abgeschnitten, Höhen begrenzt, Taubin-Glättung, Löcher geschlossen). Das war dir zu stark geglättet.

**Rekonstruktion:**
- 9 Ebenen mit 14x18, 12x16, 10x14, 8x12, 6x10, 4x8, 2x6, 2x4, 2x2 Noppen, darauf eine Säule aus 5 Steinen 1x1. Alles weiß, nur 2x4/2x2/1x1.
- Die Figur ist komplett neu modelliert, nach deinen 11 Fotos, in Minifigurenmaßen. Helm mit Spitze und Wangenklappen, Gesicht mit Schnurrbart, Kettenhemd-Druck mit Schal und Gürtel, Tunika, Umhang, C-Hände, blaue Beine, braune Schuhe. Kopf und Oberkörper haben gemalte Texturen.

**Abweichungen:** Farben von Umhang, Händen und Ärmeln etwas blasser als im Foto; Kettenhemd als Wabenmuster; Wangenklappen flach; Ärmel einfache Röhren. Die verdeckte Steinverteilung ist zufällig.

## Modell 2: Stufenpyramide mit grauen Treppenarmen und Tempel

**Original:** Das Netz hat rund 69.600 Punkte und 53.500 Dreiecke. Die Pyramide ist gegenüber dem Boden um ca. 16° gedreht, der Boden wellig und zur Pyramide hin ansteigend, der Scan in einer Achse um etwa den Faktor 0,72 gestaucht, die Treppenseite teils zerfallen, die Textur fast farblos.

**Messung:** Ausrichtung um 16,25° (Schärfe-Histogramm um den Tempelmittelpunkt), Höhen- und Farbkarte aus 4 Mio. Oberflächenpunkten, daraus Raster (ca. 13 Zellen pro Noppe) und Steinhöhe.

**Rekonstruktion (Version 4):**
- 7 Ebenen. Die vier grauen Treppenarme sind 4 Noppen breit und reichen pro Ebene eine Noppe weniger weit (9, 8, 7, 6, 5, 4, 3 Noppen vom Zentrum).
- Weiße Eckflächen mit 6x6, 5x5, 4x4, 3x3 und in Ebene 5 als 2x2. Darüber sind die Ecken frei.
- Tempel mit 4 Lagen: graue 4x4-Lage, vier weiße 1x1-Eckpfeiler (hohl dazwischen), graue 4x4-Lage als Sturz, graues 2x2 oben.
- Die oberen weißen Eckblöcke sind leicht gedreht (2–7° je nach Ecke, aus dem Scan gemessen). Die vier Pfeiler sind nach Augenmaß aus deinem Nahfoto um 14°, −12°, 16° und −9° gedreht.
- Anzahl Steine: weiß 32x 2x4, 20x 2x2, 12x 1x1 und 8 Sondersteine 1x2/1x4; grau 70x 2x4 und 9x 2x2.

**Annahmen und Unsicherheiten:**
- Stufenzahl 7 nach Foto und deiner Angabe. Der Scan zeigt eher 8 Stufen mit 20x20 Noppen unten, vermutlich verschmelzen Boden-Ebenen mit dem Tisch.
- Drehrichtung der Pfeiler und Stärke der Drehung der Blöcke sind geschätzt.
- Einzelne 1x2/1x4-Steine, weil ungerade Flächen sonst viele 1x1 brauchen.
- Treppenarme in Ebene 6/7 im Foto nicht ganz symmetrisch, im Modell symmetrisch. Bodenfläche des Scans nicht übernommen.
