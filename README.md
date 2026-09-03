Schul-CMS: Django Projekt für Schulen, um generisch Webseiten zu erstellen ohne Programmiererfahrung

Schul-CMS ist ein Content-Management-System, mit dem Schulen ihre Web-präsenz selbst gestalten können.
Entwickelt mit dem Django Framework, ist das Projekt im Rahmen einer Universitätsaufgabe erstellt worden und
demonstriert, wie man eine datenbankgestützte Webanwendung erstellt.

Projekt-Aufbau:
|-Schulprojekt-main
    |-myapp (bestehendes Django-Projekt auf welchem aufgebaut wird)
    |-cms
        |-forms
        |-layouts
        |-management
        |-migrations
        |-static
        |-templates
        |-views

Das System umfasst:
Übersicht - Zeigt aktuelle Daten zu Seiten und Funktionen sowie eine Navigation zu den anderen Modulen
Seiten - Seite erstellen, bearbeiten, löschen, Vorschau anzeigen
Editor - Über Seitenverwaltung zugänglich, ermöglicht die Bearbeitung der Inhalte der Seite mit Live Vorschau (in bearbeitung)
Medien - Übersicht der Medien und neue Medien in die Datenbank hinzufügen (nicht implementiert)
Navigation - Navigation der Webseiten bearbeiten (nicht implementiert)
Funktionen - Übersicht aller Funktion und ein und abschaltbar (nicht implementiert)
Veröffentlichung - Übersicht von veröffentlichten Seiten und Entwürfe -> Seite veröffentlichen/ archivieren (nicht implementiert)
Layouts - Übersicht aller Layouts mit Vorschau (nicht implementiert)
Design - Übersicht aller Designs (nicht implementiert)
Benutzer & Rechte - Übersicht aller Benutzer des CMS, admin kann bearbeiten (nicht implementiert)

Technologien:
Backend: Python 3, Django
Frontend: HTML5, CSS, Bootstrap, Javascript
Datenbank: SQLite für Entwicklung, PostgreSQL in der Produktion

Installation:
1. Voraussetzung zur installation: Python 3, pip
2. Repository clonen: https://github.com/yourusername/Schul-Portal.git cd Schul-CMS
3. Virtuelle Umgebung erstellen im Schul-CMS directory: python -m venv env, Aktivieren: env/Scripts/activate
4. Abhängigkeiten installieren: pip install django
5. Migrationen: python manage.py makemigrations python manage.py migrate
6. Django Superuser erstellen: python manage.py createsuperuser Username und Passwort eingeben für Djangos Admin Oberfläche
7. Entwicklungsserver starten: python manage.py runserver
8. Im Browser öffnen: http://127.0.0.1:8000/admin/ -> Admin Oberfläche von Django
9. In Admin Oberfläche unter Benutzer einen neuen Benutzer anlegen, dann unter Persons neue Person mit Rolle Admin für CMS zugang
10. Im Browser öffnen: http://127.0.0.1:8000/cms/ -> Anmelden für CMS mit angelegtem Benutzer

Admin-Seite: Verwaltung der Modelle in myapp/models.py -> Modelle für die Funktionen der Schulwebseite
CMS-Seite: System um Webseiten zu erstellen

Code Dokumentation der cms app:

forms: leer stehend, später Formulare hinzufügen die in Webseiten gerendert werden
layouts: Layouts um eine neue Seite zu erstellen in "Seiten" (Wenn Django html rendert, sucht er nach templates
    Ordner, deswegen wurde layouts in schoolwebsite|-settings.py als Path für templates hinzugefügt)
management|-commands|-seed.py: Daten in die Datenbank einfügen, wie Layouts oder Designs (nur vom Entwickler möglich)
migrations: Datenbankmigrationen
static|-cms|-design: CSS Dateien für die Layouts, mit Ziel, dass jede CSS Datei zu jedem Layout passt
templates: Webseiten des Schul-CMS
templates|-layouts: html-Layouts um eine neue Seite zu erstellen in "Seiten"
views: Django views um Schul_CMS Seiten zu rendern
    cmsLogin.py: 
        1. cms_dashboard prüft ob angemeldeter Benutzer "admin" Rolle besitzt, 
        2. weiterleitung an admin_dashboard, welches dann die "Übersicht" Seite rendert(cmsSurface.html), 
        3. cms_login rendert die Login Seite(cmsLogin.html) für das CMS und nimmt die Daten,
            die eingegeben werden und authentiziert diese mit djangos authenticate, 
        4. cms_logout wird benutzer abgemeldet und zum Login weitergeleitet
    seitenVerwaltung.py: 
        1. to_seiten_main rendert die "Seiten" Seite(seitenVerwaltung.html), 
        2. seiten_search nimmt den query aus dem formular in seitenVerwaltung.html aus dem input feld und sucht in der 
            Datenbank nach diesen Seiten und gibt sie in Tabellenform aus, 
        3. seite_erstellen rendert die seiteErstellen.html Seite, nimmt alle Layouts und Designs in der Datenbank und 
            gibt sie als Auswahl vor, die im Formular eingegebenen Daten in seiteErstellen.html werden mit POST an die
            view gegeben und mit den Daten ein neuer Page Eintrag im Page Model gemacht, dazu wird auch die erste Page_Version
            angelegt,
        4. seite_bearbeiten rendert den editor.html zu der ausgewählten page und rendert auch die zur page gehörigen 
            Blöcke
        5. seiten_vorschau rendert die ausgewählte page mit Design, Layout, Blöcke und wo die Blöcke im Layout angeordnet
            sind im iFrame in editor.html
        6. vorschau_view rendert die vorschau.html und dort wird einfach die page angezeigt als vorschau
        7. delete_page löscht die ausgewählte Seite, vorher kommt jedoch in seitenVerwaltung.html eine Warnung und dann
            beim erfolgreichem Löschen, wird eintrag aus der Datenbank entfernt und eine Erfolgsmeldung angezeigt
    pageRelease.py:
        1. release_page setzt den Status bei ausgewählter page in seitenVerwaltung.html auf True

api: Funktionen um Daten aus datenbank abzufragen
    1. count_pages zählt alle Seiten in der Datenbank
    2. count_releases zählt alle veröffentlichte Seiten in der Datenbank
    3. count_drafts zählt alle unveröffentlichten Seiten in der Datenbank
    4. count_media zählt alle Medieninhalte in der Datenbank
    5. search_pages_with_title gibt alle pages mit dem gleichen titel zurück
    6. get_blocks_and_layout_region_by_page_id gibt alle blöcke und ihre zugehörigen layout regionen zurück die zu einer 
        page gehören
