# Stromnetz Graz für Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/)

Custom Integration für Home Assistant, die die Smart-Meter-Daten aus dem (inoffiziellen) [Stromnetz Graz Webportal](https://webportal.stromnetz-graz.at/) abruft.

Dieses Repository ist ein Fork von [dreautall/stromnetzgraz](https://github.com/dreautall/stromnetzgraz). Die Python-Bibliothek `sngraz` ist direkt in der Integration enthalten (`custom_components/stromnetzgraz/sngraz`), die Home-Assistant-Integration basiert auf [dreautall/ha-stromnetzgraz](https://github.com/dreautall/ha-stromnetzgraz).

## Voraussetzungen

Du musst dich im Webportal anmelden und dort die Verbrauchsdaten sehen können. Wie du den Zugang zu den Smart-Meter-Daten einrichtest, erklärt Stromnetz Graz. Am besten funktioniert der Modus `IME` (Messwerte alle 15 Minuten). Die Integration kommt aber auch mit `IMS` (ein Messwert pro Tag) zurecht. Die neuesten Daten sind immer die vom Vortag (siehe [FAQ](https://www.stromnetz-graz.at/sgg/stromzaehler/intelligenter-stromzaehler/faqs)).

## Installation über HACS

1. In Home Assistant **HACS** öffnen.
2. Rechts oben über das Drei-Punkte-Menü **Benutzerdefinierte Repositories** öffnen.
3. Als Repository `https://github.com/RookieIVG/Stromnetzgraz` eintragen und als Typ **Integration** wählen.
4. In HACS nach **Stromnetz Graz** suchen und herunterladen.
5. Home Assistant neu starten (mindestens Version 2025.10).
6. Unter **Einstellungen → Geräte & Dienste → Integration hinzufügen** nach **Stromnetz Graz** suchen und die Zugangsdaten zum Webportal eingeben.

### Manuelle Installation

Den Ordner `custom_components/stromnetzgraz` in das Verzeichnis `config/custom_components/` deiner Home-Assistant-Installation kopieren und Home Assistant neu starten.

## Was die Integration bereitstellt

Für jeden Zähler werden angelegt:

- **Meter Reading**: der letzte Zählerstand in kWh (für das Energie-Dashboard geeignet)
- **Meter Consumption**: der letzte Verbrauch in kWh
- **Externe Statistik** `stromnetzgraz:energy_consumption_<Zähler-ID>`: der stündliche Verbrauch. Beim ersten Start werden bis zu 5 Jahre rückwirkend importiert. Diese Statistik kannst du im Energie-Dashboard als Netzbezug eintragen.

Zusätzlich gibt es Diagnose-Sensoren:

- **Last Reading**: Zeitpunkt des letzten gültigen Zählerstands. Die 15-Minuten-Werte kommen meist mit etwa einem halben Tag Verzögerung.
- **Data Mode**: der Datenmodus `OptIn` (15-Minuten-Werte), `OptMiddle` (Tageswerte) oder `OptOut` (keine Daten). Ein beantragter Wechsel steht im Attribut `pending`.
- **Customer Interface**: ob die Kundenschnittstelle am Zähler aktiviert ist (`On`/`Off`).
- **Display** und **Accounting Period** (standardmäßig deaktiviert): ob der Verbrauch am Zählerdisplay angezeigt wird und ob monatlich oder jährlich abgerechnet wird.

Die Daten werden stündlich abgefragt.

## Diagnose-Daten

Unter **Einstellungen → Geräte & Dienste → Stromnetz Graz → ⋮ → Diagnosedaten herunterladen** bekommst du eine JSON-Datei mit den rohen API-Antworten. Persönliche Daten wie Adresse, Kundennummer, Zählpunkt und Zugangsdaten sind darin geschwärzt. Die Zusammenfassung `getMeterReading_summary` zeigt, welche Messwert-Typen (`readingTypes`) dein Zähler liefert. So lässt sich herausfinden, ob die API mehr liefert, als die Integration bisher nutzt, z. B. Einspeisung.

Hinweis: Felder, die die Integration noch nicht kennt, werden nur geschwärzt, wenn ihr Name auf der Liste in `diagnostics.py` steht. Schau die Datei deshalb kurz durch, bevor du sie weitergibst.

## Lizenz

MIT, siehe [LICENSE](LICENSE).
