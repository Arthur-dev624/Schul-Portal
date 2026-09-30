Schul-CMS: Django Projekt für Schulen, um generisch Webseiten zu erstellen ohne Programmiererfahrung

Schul-CMS ist ein Content-Management-System, mit dem Schulen ihre Web-präsenz selbst gestalten können.
Entwickelt mit dem Django Framework, ist das Projekt im Rahmen einer Universitätsaufgabe erstellt worden und
demonstriert, wie man eine datenbankgestützte Webanwendung erstellt.

Projekt-Aufbau:
|-Schulprojekt-main
    |-myapp (bestehendes Django-Projekt auf welchem aufgebaut wird)
    |-cms
        |-management
        |-static
        |-templates
            |- blocks
            |- components
            |- layouts
        |-views

Das System umfasst:
Übersicht - Zeigt aktuelle Daten zu Seiten, veröffentlichten Seiten, Entwürfen und Medien sowie die zuletzt bearbeiteten 
Seiten und Navigation zu den anderen CMS-Modulen.

Seiten - Seiten erstellen, suchen, bearbeiten und löschen sowie verschiedene Seitenversionen verwalten.

Editor - Über die Seitenverwaltung zugänglich. Ermöglicht das Erstellen und Bearbeiten von Überschriften-, Text-, Bild- 
und Buttonblöcken, deren Zuordnung zu Layoutregionen und Positionen sowie eine Live-Vorschau der Seite.

Medien - Übersicht aller Medien sowie Hochladen und Ersetzen von Bildern. Hochgeladene Dateien werden nach Dateigröße, 
Dateiendung und tatsächlichem Bildformat validiert.

Navigation - Navigationseinträge erstellen, bearbeiten und löschen sowie Position und Sichtbarkeit festlegen. 
Im aktuellen Prototyp werden Navigationseinträge ohne Untermenüs unterstützt.

Veröffentlichung - Entwürfe veröffentlichen, Seiten archivieren und Veröffentlichungshistorie anzeigen. 
Beim Veröffentlichen wird automatisch eine neue bearbeitbare Entwurfsversion erzeugt.

Funktionen - Funktionsblöcke können einer Seite zugeordnet und bei der Seitennutzung abgefragt werden. Eine vollständige 
Verwaltungsoberfläche ist noch nicht implementiert.

Layouts - Layouts werden vom Entwickler bereitgestellt und bestimmen die verfügbaren Layoutregionen einer Seite. 
Eine eigene Layout-Verwaltungsoberfläche ist noch nicht implementiert.

Design - Designs werden vom Entwickler bereitgestellt und können Seiten zugeordnet werden. Eine eigene 
Design-Verwaltungsoberfläche ist noch nicht implementiert.

Benutzer & Rechte - Der Zugriff auf die CMS-Verwaltungsbereiche wird aktuell über die Rolle admin kontrolliert. 
Eine vollständige Benutzer- und Rechteverwaltung innerhalb des CMS ist noch nicht implementiert.

Technologien:
Backend: Python 3, Django
Frontend: HTML5, CSS, Bootstrap, Javascript
Datenbank: SQLite für Entwicklung, PostgreSQL in der Produktion (mögliche Option) 

Installation:
1. Voraussetzung zur installation: Python 3, pip
2. Repository clonen: https://github.com/Arthur-dev624/Schul-Portal.git cd Schul-CMS
3. Virtuelle Umgebung erstellen im Schul-CMS directory: python -m venv env, Aktivieren: env/Scripts/activate
4. Abhängigkeiten installieren: pip install -r requirements.txt
5. Migrationen: python manage.py makemigrations python manage.py migrate
6. Django Superuser erstellen: python manage.py createsuperuser Username und Passwort eingeben für Djangos Admin Oberfläche
7. Entwicklungsserver starten: python manage.py runserver
8. Im Browser öffnen: http://127.0.0.1:8000/admin/ -> Admin Oberfläche von Django
9. In Admin Oberfläche unter Benutzer einen neuen Benutzer anlegen, dann unter Persons neue Person mit Rolle Admin für CMS zugang
10. Im Browser öffnen: http://127.0.0.1:8000/cms/ -> Anmelden für CMS mit angelegtem Benutzer

Admin-Seite: Verwaltung der Modelle in myapp/models.py -> Modelle für die Funktionen der Schulwebseite
CMS-Seite: System um Webseiten zu erstellen

Code Dokumentation der cms app:

management|-commands|-seed.py: Daten in die Datenbank einfügen, wie Layouts oder Designs (nur vom Entwickler möglich)
migrations: Datenbankmigrationen
static|-cms|-design: CSS Dateien für die Layouts, mit Ziel, dass jede CSS Datei zu jedem Layout passt
templates: Webseiten des Schul-CMS
templates|-layouts: html-Layouts um eine neue Seite zu erstellen in "Seiten"
templates|-blocks: html-block renderer und wird in den Layouts mit Django include hinzugefügt
templates|-components: html-Navigations einträge Liste und wird in den Layouts im Header mit Django include hinzugefügt
views: Views um die Oberflächen des Schul-CMS zu rendern und beinhaltet deren Hilfsfunktionen
    cmsLogin.py: 
        1. cms_dashboard prüft nach dem Login die Rolle des Benutzers, mit der Rolle admin wird dieser dann zum Admin-
            Dashboard weitergeleitet
        2. admin_dashboard rendert die CMS-Übersicht cmsSurface.html, diese View lädt die Anzahl der Seiten, veröffentlichte
            Seiten, Entwürfe und Medien sowie die drei zuletzt bearbeiteten Seiten mit ihrer aktuellen Version und ihrem Status
        3. cms_login rendert die Login-Seite cmsLogin.html und bei einem POST-Request werden Benutzername und Passwort
            mit Djangos authenticate überprüft und der Benutzer anschließend angemeldet
        4. cms_logout meldet den Benutzer ab und leitet diesen zurück zur CMS-Login Seite
    seitenVerwaltung.py: 
        1. to_seiten_main rendert die Seitenverwaltung seitenVerwaltung.html und gibt alle vorhandenen Seiten zusammen
            mit ihrer jeweils neuesten Version aus
        2. seiten_search nimmt den Suchbegriff aus der Suchleiste, sucht nach Seiten mit einem passenden Titel und zeigt
            die gefundenen Seiten zusammen mit ihrer aktuellen Versionen an
        3. seite_erstellen rendert seiteErstellen.html, lädt alle verfügbaren Layouts und Designs und erstellt bei einem gültigen
            POST-Request eine neue Page sowie die erste PageVersion
        4. _build_region_with_blocks lädt alle Layoutregionen einer Seite und ordnet jeder Region die darin enthaltenen
            PageBlocks zu
        5. _build_region_position_counts sucht für jede Layoutregion, wie viele PageBlocks in der aktuellen Version der Seite
            zugeordnet sind
        6. _build_position_choices berechnet die möglichen Positionen, an die ein bestehender PageBlock innerhalb seiner
            Layoutregion verschoben werden kann
        7. _reorder_page_blocks verschiebt einen PageBlock innerhalb einer Layoutregion oder in eine andere Layoutregion
            und nummeriert anschließend die Positionen der betroffenen Blöcke neu
        8. _get_selected_layout_region nimmt die Layoutregion aus einem POST-Request und prüft, ob diese zu einem Layout
            der bearbeiteten Seite gehört
        9. _read_block_form nimmt die Formularwerte von einem ausgewählten Blocktyp, Unterstützt werden Überschrift,
            Text, Bild, Form und Button dabei werden Textausrichtung, Überschriftenebene, Bildgröße, Medium, Button-Style
            geprüft
        10. _block_content_changed vergleicht die aktuell abgeschickten Formularwerte mit der gespeicherten config
             des Blocks. Die Funktion gibt true zurück, wenn sich blockspezifische Inhalte wie Text, Bilddaten oder Button
            URL geändert haben und False wenn nur Layoutregion oder Position geändert wurden
        11. seite_bearbeiten stellt den eigentlichen Editor bereit, dazu lädt die View Seite, Seitenversion, Layoutregionen,
            vorhandene Blöcke und Medien. Dort kann man Überschrift, Text, Bild, Button Blöcke erstellen und bearbeiten, 
            sowie das ändern ihrer Layoutregion und Position. Veröffentlichte Versionen können nicht verändert werden
        12. seiten_vorschau rendert die aktuell bearbeitete Seitenversion mit ihrem Layout, Design, ihren Blöcken und ihrer
            Navigation. Diese View wird für die Live-Vorschau innerhalb des Editors verwendet
        13. vorschau_view rendert die vorschau.html als eigene Vorschauansicht für eine bestimmte Seite und Version
        14. delete_page löscht die ausgewählte Page aus der Datenbank und leitet anschließend zurück zur Seitenverwaltung
    medienVerwaltung.py:
        1. CmsImageForm.clean_file validiert hochgeladene Bilddateien, geprüft wird eine maximale Bildgröße von 10 MB,
            tatsächliches Bildformat und die Dateiendung und Bildformat
        2. _get_media_type ermittelt anhand des validierten Bildformats den passenden MIME-Type des Medium
        3. _delete_old_file löscht eine ersetzte Mediendatei aus dem Dateispeicher, sofern kein anderer CmsMedium-
            Datensatz auf diese Datei verweist
        4. to_medien_verwaltung rendert die Medienverwaltung medienVerwaltung.html und nur admins dürfen darauf zugreifen,
            die View ermöglicht das Hochladen von Bildern und das ersetzen von Bildern. Die Dateien werden geprüft und als
            CmsMedium gespeichert. Es werden alle vorhandenen Medien, ihre Verwendung in Blöcken und die Anzahl der Medien geladen
    navigationVerwaltung.py:
        1. NavigationForm.__init__ erstellt das Formular zur Navigationsverwaltung und stellt nur veröffentlichte Seiten
            als auswählbare Ziele eines Navigationseintrags zur Verfügung
        2. get_visible_navigation gibt alle sichtbaren Navigationseinträge zurück, deren verlinkte Seite veröffentlicht ist
            Die Einträge werden nach ihrer Position sortiert
        3. to_navigation_verwaltung rendert die Navigationsverwaltung navigationsverwaltung.html nur admins können
            Einträge erstellen, bearbeiten und löschen. Im aktuellen Prototyp werden nur Einträge ohne Untermenüs unterstützt
        4. cms_page stellt eine veröffentlichte CMS-Seite öffentlich über ihren Slug dar. Dafür wird die aktuell veröffentlichte
            PageVersion geladen und zusammen mit Layout, Design, Blöcken und Navigation gerendert
    pageRelease.py:
        1. is_cms_admin prüft ob der Benutzer eine Person besitzt und Rolle amdin hat
        2. get_latest_draft gibt die neueste noch nie veröffentlichte Version einer bestimmten Seite zurück 
        3. create_next_draft erzeugt aus einer bestehenden Seitenversion eine neue Entwurfsversion, dabei werden
            PageBlock, Block-Konfiguration, Medienzuordnung und Funktionsblock Zuordnungen kopiert. Die eigentlichen
            Mediendateien werden nicht dupliziert
        4. to_veroeffentlichung_verwaltung rendert die Veröffentlichungsverwaltung veroeffentlichungsVerwaltung.html und
            für jede Seite werden die aktuell veröffentlichte Version und der neuste Entwurf geladen. Zusätzlich werden die 
            letzten zehn veröffentlichungen angezeigt
        5. release_page veröffentlicht den neuesten Entwurf einer Seite. Eine eventuell zuvor veröffentlichte Version wird 
            deaktiviert, die Veröffentlichung wird in Publication protokolliert und anschließend wird automatisch eine neue
            bearbeitbare Entwurfsversion auf Basis der veröffentlichten Version erstellt. 
        6. archive_page nimmt eine veröffentlichte Seite offline, diese Page und ihre veröffentlichte PageVersion werden
            deaktiviert, ohne Versionen oder Blöcke zu löschen

api: Funktionen um Daten aus datenbank abzufragen, sowie zum Erstellen und Bearbeiten von Inhaltsblöcken
1. _get_person gibt zu einem übergebenem User die zugehörige Person zurück und wirft einen Fehler, wenn der User nicht
        existiert
2. _get_user gibt zu einer Person den User zurück und wirft einen Fehler, wenn die Person nicht existiert
3. count_pages zählt alle Seiten in der Datenbank
4. count_releases zählt alle aktuell veröffentlichten Daten
5. count_drafts zählt alle aktuell unveröffentlichte Seiten
6. count_media zählt alle Medieninhalte in der Datenbank
7. search_pages_with_title durchsucht alle Seiten anhand des Titels
8. current_page_versions nimmt eine Menge von Seiten entgegen und gibt für jede Seite ihre höchste Version zurück
9. get_block_and_layout_region_by_page_id gibt die Blöcke und die zugehörigen Layoutregionen einer bestimmten Seiten-
    version zurück
10. get_functions_by_page_id gibt die Typen aller Funktionsblöcke zurück, die in einer Seite verwendet werden
11. get_media_used_by_page_id gibt die Titel der Medien zurück, die in einer Seite mit einer bestimmten Seiten-
    version verwendet werden
12. get_page_block_used_in_page lädt alle PageBlocks einer bestimmten Seitenversion, sortiert sie nach Layoutregionen
    und Positionen und gruppiert sie anhand des keys der Layoutregionen
13. get_layout_regions_of_page gibt alle Layoutregionen des Layouts zurück, welches von einer Seite verwendet wird
14. get_all_media gibt alle gespeicherten Medien aus der Datenbank zurück
15. create_header_block erstellt einen Überschriftenblock mit Text, Überschriftenebene und Ausrichtung und legt den
     zugehörigen PageBlock innerhalb einer Layoutregion an
16. create_text_block erstellt einen Textblock mit Text und Ausrichtung und legt den zugehörigen PageBlock innerhalb einer 
    Layoutregion an
17. create_image_block erstellt einen Bildblock mit Bildunterschrift, Breite, Höhe und Ausrichtung und es wird die 
    Verbindung zu PageBlock zwischen Block und Medium über BlockMedium angelegt
18. create_button_block erstellt einen Buttonblock mit Text, URL und einen Bootstrap-Style und ordnet ihn über einen 
    PageBlock einer Layoutregion zu
19. update_header_block aktualisiert die Werte eines vorhandenen Überschriftenblocks und speichert dessen Konfiguration
20. update_text_block aktualisiert die Werte eines vorhandenen Überschriftenblocks und speichert dessen Konfiguration
21. update_image_block aktualisiert die Werte eines vorhandenen Bildblocks und kann zusätzlich das vorhandene Medium austauschen
22. update_button_block aktualisiert Text, URL und Style eines vorhandenen Buttonblocks
admin.py: leer
apps.py: leer
urls.py: Enthält die URL-Routen der CMS-App und verbindet die jeweiligen URLs mit den passenden Django-Views
    1. Die Login-, Logout- und Dashboard-Routen führen zu den Views aus cmsLogin.py. 
    2. Die Routen der Seitenverwaltung ermöglichen das Anzeigen, Erstellen, Bearbeiten, Löschen und Suchen von Seiten. 
    3. Für den Editor gibt es eigene URLs zum Bearbeiten einer Seitenversion, zum Erstellen neuer Blöcke sowie zum Bearbeiten einzelner vorhandener PageBlocks. 
    4. Die Vorschau-Routen zeigen eine bestimmte Seitenversion entweder direkt im Editor oder in einer eigenen Vorschauansicht an. 
    5. Die Medienverwaltungs-Route öffnet die Verwaltungsoberfläche zum Hochladen und Ersetzen von Medien. 
    6. Die Navigationsverwaltungs-Route öffnet die Oberfläche zum Erstellen und Bearbeiten von Navigationseinträgen. 
    7. seite/<slug:slug>/ stellt eine veröffentlichte CMS-Seite öffentlich über ihren Slug dar. 
    8. Die Veröffentlichungsverwaltung besitzt Routen für die Übersicht sowie für das Veröffentlichen und Archivieren einzelner Seiten. 

Die dynamischen URL-Parameter wie <int:page_id>, <int:version>, <int:page_block_id> und <slug:slug> werden an die 
jeweilige View übergeben, damit gezielt mit einer bestimmten Seite, Version oder einem bestimmten Block gearbeitet werden kann.
