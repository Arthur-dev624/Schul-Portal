# **1 Projektübersicht:**

Django Projekt für Schulen, um generisch Webseiten zu erstellen ohne ProgrammiererfahrungProjekt-Aufbau:

Schul-CMS ist ein Content-Management-System, mit dem Schulen ihre Web-präsenz selbst gestalten können.
Entwickelt mit dem Django Framework, ist das Projekt im Rahmen einer Universitätsaufgabe erstellt worden und
demonstriert, wie man eine datenbankgestützte Webanwendung erstellt.

## 1.1 Systemumfang:
- Übersicht - Zeigt aktuelle Daten zu Seiten, veröffentlichten Seiten, Entwürfen und Medien sowie die
zuletzt bearbeiteten Seiten und Navigation zu den anderen CMS-Modulen.

- Seiten - Seiten erstellen, suchen, bearbeiten und löschen sowie verschiedene Seitenversionen verwalten.

- Editor - Über die Seitenverwaltung zugänglich. Ermöglicht das Erstellen und Bearbeiten von Überschriften-, Text-, Bild- 
und Buttonblöcken, deren Zuordnung zu Layoutregionen und Positionen sowie eine Live-Vorschau der Seite.

- Medien - Übersicht aller Medien sowie Hochladen und Ersetzen von Bildern. Hochgeladene Dateien werden nach Dateigröße, 
Dateiendung und tatsächlichem Bildformat validiert.

- Navigation - Navigationseinträge erstellen, bearbeiten und löschen sowie Position und Sichtbarkeit festlegen. 
Im aktuellen Prototyp werden Navigationseinträge ohne Untermenüs unterstützt.

- Veröffentlichung - Entwürfe veröffentlichen, Seiten archivieren und Veröffentlichungshistorie anzeigen. 
Beim Veröffentlichen wird automatisch eine neue bearbeitbare Entwurfsversion erzeugt.

- Funktionen - Funktionsblöcke können einer Seite zugeordnet und bei der Seitennutzung abgefragt werden. Eine vollständige 
Verwaltungsoberfläche ist noch nicht implementiert.

- Layouts - Layouts werden vom Entwickler bereitgestellt und bestimmen die verfügbaren Layoutregionen einer Seite. 
Eine eigene Layout-Verwaltungsoberfläche ist noch nicht implementiert.

- Design - Designs werden vom Entwickler bereitgestellt und können Seiten zugeordnet werden. Eine eigene 
Design-Verwaltungsoberfläche ist noch nicht implementiert.

- Benutzer & Rechte - Der Zugriff auf die CMS-Verwaltungsbereiche wird aktuell über die Rolle admin kontrolliert. 
Eine vollständige Benutzer- und Rechteverwaltung innerhalb des CMS ist noch nicht implementiert.

# **2 Technologien:**
Backend: Python 3, Django<br>
Frontend: HTML5, CSS, Bootstrap, JavaScript<br>
Datenbank: Es wird SQLite verwendet, PostgreSQL in der Produktion (mögliche Option, nicht umgesetzt)<br>
Bibliotheken: Django 6.0.7; google-genai 2.15.0; Pillow 12.3.0; pyasn1 0.6.4

# **3 Projektstruktur:**
Schul-Portal/<br>
|- cms/<br>
|  |- management/commands/<br>
|  |- migrations/<br>
|  |- static/cms/<br>
|  |- templates/<br>
|     |- blocks/<br>
|     |- components/<br>
|     |- layouts/<br>
|  |- views/<br>
|  |- models.py<br>
|  |- api.py<br>
|  |- urls.py<br>
|  |- Models.md<br>
|- myapp/<br>
|- schoolwebsite/<br>
|- manage.py<br>
|- requirements.txt<br>
|- README.md<br>

- management/commands/: Daten in die Datenbank einfügen, wie Layouts oder Designs (nur vom Entwickler möglich)<br>
- migrations: Datenbankmigrationen<br>
- static/cms/: CSS Dateien für die Layouts, mit Ziel, dass jede CSS Datei zu jedem Layout passt<br>
- templates: Webseiten des Schul-CMS<br>
- templates/layouts/: html-Layouts um eine neue Seite zu erstellen in "Seiten"<br>
- templates/blocks/: html-block renderer und wird in den Layouts mit Django include hinzugefügt<br>
- templates/components/: html-Navigations einträge Liste und wird in den Layouts im Header mit Django include hinzugefügt<br>
- views: Views um die Oberflächen des Schul-CMS zu rendern und beinhaltet deren Hilfsfunktionen

# **4 Systemarchitektur:**
Das Content-Management-System ist als Django-App cms implementiert und baut auf der bestehenden myapp-App auf.<br>
Die App erweitert die vorhandene Schulplattform um die Möglichkeit, Webseiten und deren Inhalte dynamisch zu erstellen, 
zu bearbeiten und zu veröffentlichen.<br>
<br>
Die Implementierung orientiert sich an der Model-View-Template-Architektur (MVT) des Django-Frameworks.
Dabei werden die Datenhaltung, die Verarbeitung von Anfragen und die Darstellung der Benutzeroberfläche voneinander getrennt.<br>
<br>
**Aufbau der Architektur**<br>

Die zentralen Bestandteile des Systems sind:

1. Datenhaltung (cms/models.py)<br>
    Die Datenhaltung erfolgt über Django-Models, deren Objekte mithilfe des Django ORM in der Datenbank gespeichert und abgefragt werden.
    Die Models bilden unter anderem Webseiten, Seitenversionen, Layouts, Layoutregionen, Designs, Inhaltsblöcke, Medien, Navigationspunkte und Veröffentlichungen ab.

2. Anwendungslogik (cms/views/)<br>
    Die Verarbeitung von HTTP-Anfragen erfolgt in den Django-Views. Diese übernehmen die Validierung von Eingaben, die Abfrage und Veränderung von Datenbankobjekten
    sowie die Bereitstellung der benötigten Daten für die Templates. Die Zuordnung von URLs zu den jeweiligen View-Funktionen erfolgt über cms/urls.py

3. Datenzugriff und Hilfsfunktionen (cms/api.py)<br>
    Die Datei cms/api.py enthält wiederverwendbare Funktionen für den Zugriff auf CMS-Daten und deren Aufbereitung.
    Sie unterstützt insbesondere die Abfrage von Inhaltsblöcken und deren Zuordnung zu Webseiten und deren Layoutregionen.
    Dadurch können verschiedene Views dieselben Funktionen verwenden, ohne die zugehörige Abfragelogik mehrfach implementieren zu müssen.

4. Darstellung (cms/templates/)<br>
    Die Darstellung der CMS-Oberflächen und der erstellten Webseiten erfolgt mithilfe des Django-Template-Systems. Hierbei
    wird zwischen den Verwaltungsoberflächen des CMS und den Templates für die dynamisch erzeugten Webseiten unterschieden.
    Die Darstellung einer Webseite basiert auf einem zugeordneten Layout-Template, in dem die verfügbaren Layoutregionen
    definiert sind. Innerhalb dieser Regionen werden die zugehörigen Inhaltsblöcke dargestellt.<br>
    Für die Darstellung einzelner Inhaltsblöcke wird das Template cms/templates/blocks/blockRenderer.html verwendet. Es 
    unterscheidet anhand des Blocktyps, welches HTML erzeugt werden soll, und verwendet dabei die im Block gespeicherte Konfiguration.

5. Integration in das bestehende Schul-Portal<br>
    Die CMS-App ist in das vorhandene Django-Projekt integriert und verwendet dessen bestehende Infrastruktur. Die App
    myapp stellt weiterhin die bereits vorhandenen Funktionen des Schul-Portals sowie die bestehenden Benutzer und Rollendaten bereit.
    CMS-App erweitert diese Struktur, ohne die vorhandenen Funktionen vollständig zu ersetzen. Zugriffsteuerung auf die CMS-Verwaltungsoberfläche, 
    erfolgt durch das bereits vorhandene Benutzer und Rollensystem.<br>
    Administratorrechte werden derzeit nicht einheitlich in allen Views geprüft, deshalb muss eine weitergehende 
    Vereinheitlichung der Berechtigungsprüfung erfolgen.<br>

**Zusammenwirken der Komponenten**<br>

Wenn eine Anfrage an das CMS gemacht wird, wird zunächst anhand der URL die zuständige View Funktion aufgerufen.<br>

Diese View verarbeitet dann die Anfrage und bei Bedarf wird über das Django ORM oder die Hilfsfunktionen in cms/api.py die benötigten Daten abgerufen.<br>

Anschließend werden jene Daten an ein Template übergeben, das die entsprechende HTML-Ausgabe erzeugt.<br>

Bei der Darstellung einer dynamisch erzeugten Webseite werden zusätzlich das ausgewählte Layout, 
die zugehörigen Layoutregionen und die darin enthaltenen Blöcke berücksichtigt.<br>

Dadurch sind die Struktur einer Webseite und ihre Inhalte weitgehend voneinander getrennt. Eine Änderung der Blockkonfiguration
kann gemacht werden, ohne das Layout-Template bearbeiten zu müssen.

# **5 Datenmodell:**

Page kann mehrere PageVersionen haben und eine PageVersion zeigt immer auf eine Page. Ein PageBlock verknüpft
eine PageVersion mit einem Block. So weiß das Modell, welcher Block zu welcher PageVersion gehört und das eine Page
mehrere Variationen hat, durch PageVersion.<br>
Blöcke werden einer LayoutRegion zugeordnet, dort haben sie auch eine bestimmte Position. Medien werden einem BlockMedium
zugeordnet welcher dann zu Block zugeordnet ist. So werden auch Funktionen einem FunctionBlock zugeordnet, der dann einem
Block zugeordnet ist.<br>
<br>
Vollständige Dokumentation des Django-Models: [Model Dokumentation](cms/Models.md)<br>
[ER-Diagramm](django_inhaltsverwaltung.png)

# **6 Zentrale Abläufe**

## 6.1 Erstellung und Bearbeitung einer Webseite

Eine Seite wird über die Seitenverwaltung des CMS erstellt. Wenn gerade eine neue Seite angelegt wird, muss man zuerst
den Titel, den Slug sowie das zu verwendete Layout und Design ausfüllen. Dann werden diese Informationen in einem neuen
Objekt des Models Page gespeichert und zudem die dazugehörige PageVersion als bearbeitbare Version bereitgestellt. Die 
Page ist dabei nur das Übergeordnete Webseiten Objekt, während die PageVersion den konkreten Inhaltsstand definiert.
Die Bearbeitung des Inhalts erfolgt danach im Seiteneditor, wo es möglich ist, einer Seitenversion neue Inhaltsblöcke
hinzuzufügen und bestehende Blöcke zu bearbeiten.<br>
Dabei werden zwei Models verwendet:<br>
- Block speichert den Typ und die Konfiguration des Inhaltsblocks<br>
- PageBlock stellt die Verbindung zwischen einem Block, der bearbeitenden Seitenversion und einer Layoutregion her<br>

Die Konfiguration wird im JSON-Feld config gespeichert und welche Werte gespeichert werden hängt vom Blocktyp ab.

Die Position wird im PageBlock gespeichert nicht im Block selbst, dadurch wird die Darstellung eines Blocks 
von seiner Positionierung auf der Webseite getrennt. Wenn ein Block bearbeitet wird, können sowohl Position innerhalb einer Layoutregion,
als auch die Layoutregion selbst geändert werden und auch die config Eigenschaften.<br>

Die Bearbeitung erfolgt an einer Entwurfsversion. Veröffentlichte Seitenversionen werden nicht direkt überschrieben.

## 6.2 Dynamisches Rendering von Webseiten

Der Inhalt einer Webseite wird auf der Grundlage der in der Datenbank gespeicherten Informationen erzeugt. Zur Darstellung werden zuerst
die Seitenversionen und das Layout der Seite ermittelt. Dabei verweist das Layout auf ein Django Template, welches die HTML-Struktur vorgibt.
Dort befinden sich die Layoutregionen und jede Region enthält Schlüssel (key), über den die Inhaltsblöcke zugeordnet werden können.<br>

Das Rendering erfolgt in folgenden Schritten:<br>
1. Die seitenVerwaltung.py View ermittelt die darzustellende Seitenversion
2. Die zugehörigen PageBlock-Objekte werden mit ihrer referenzierten Blöcke und Layoutregionen abgefragt
3. Die Blöcke werden anhand ihrer Layoutregion und ihrer Position innerhalb dieser Region aufbereitet
4. Das ausgewählte Layout-Template wird mit den vorbereiteten Daten gerendert
5. Innerhalb der jeweiligen Layoutregionen werden die Blöcke über den Block-Renderer ausgegeben<br>

Der Block-Renderer (templates/blocks/blockRenderer.html) entscheidet anhand des gespeicherten Blocktyps, welche
HTML-Struktur erzeugt werden soll. Dabei gibt es folgende Blocktypen:<br>
- heading: Darstellung einer Überschrift
- text: Darstellung eines Textinhalts
- image: Darstellung eines Bildes
- button: Darstellung einer Schaltfläche<br>

Der Blocktyp function ist auch im Datenmodell und im Rendering-Konzept vorgesehen, jedoch nicht in den Seiteneditor und die
funktionale Ausführung integriert. Dadurch, dass Blöcke zu Layoutregionen zugeordnet werden, 
kann derselbe Rendering-Mechanismus für unterschiedliche Layouts verwendet werden. 

## 6.3 Seiteneditor und Live-Vorschau

Der Seiteneditor ist eine Benutzeroberfläche, über die Webseiten bearbeitet werden können, ohne dass der Benutzer 
Programmierkenntnisse benötigt. Dort ist es möglich, die Inhaltsblöcke zu verwalten und gleichzeitig hat der Benutzer
eine Vorschau der zu bearbeitenden Webseite. Diese Vorschau wird serverseitig durch Django gerendert und in einem
HTML-iframe angezeigt. Dort wird derselbe Rendering-Mechanismus verwendet wie auch zur Darstellung der öffentlichen Seite.
Dabei basiert die Vorschau auf der aktuell zu bearbeitenden Seitenversion und beinhaltet ihre gespeicherten Blöcke, 
und die Layoutzuordnungen, sowie die Positionen.

Der Ablauf läuft wie folgt ab:<br>
1. Der Benutzer öffnet eine Webseite zum Bearbeiten
2. Die zuständige View lädt die erforderlichen Daten der bearbeitbaren Seitenversion zusammen mit dem Editor
3. Der Editor stellt die verfügbaren Bearbeitungsfunktionen und die Vorschau bereit
4. Änderungen an Blöcken werden durch Anfragen an den Server gespeichert
5. Die gespeicherten Änderungen wirken sich dann auf die erneute Darstellung der Vorschau aus<br>

Somit ist die Vorschau eine visuelle Kontrolle der Änderungen, ohne dass die Webseite sofort veröffentlicht wird. 
Außerdem wird im Editor auch das ausgewählte Django-Template für das Page-Objekt und der Block-Renderer verwendet. So wird 
vermieden, dass man für die Vorschau und die öffentliche Webseite zwei Rendering-Systeme implementieren muss.

Wie schon erwähnt wird die Vorschau anhand der geänderten und gespeicherten Daten aktualisiert, somit ist es keine 
clientseitige Echtzeitdarstellung von noch nicht gespeicherten Änderungen.

## 6.4 Versionierung und Veröffentlichung

Das CMS trennt die Verwaltung einer Webseite von ihrer Versionen, dazu werden die Models Page und PageVersion verwendet.
Dadurch ermöglichen die einzelnen Versionen einen bearbeitbaren Entwurf unabhängig von einer bereits veröffentlichten Version zu verwalten.

**Bearbeitung eines Entwurfs**<br>

Ein Entwurf ist eine Seitenversion, die nicht veröffentlicht ist, dazu gibt es im Model PageVersion das Feld "status". 
Ist es False ist die Version ein Entwurf, ist es True, dann ist die Version veröffentlicht. Neue Inhalte und Änderungen
können somit nur einer bearbeitbaren Seitenversion zugeordnet werden.

**Veröffentlichung eines Entwurfs**<br>

Die Veröffentlichungslogik befindet sich in cms/views/pageRelease.py.<br>
Wird eine Seitenversion veröffentlicht, wird sie zur öffentlichen Version der Webseite.<br>
Bei der Veröffentlichung wird das Feld "status" auf True gesetzt. Wenn es bereits eine veröffentlichte Version dieser Page 
existiert, wird sie nun durch die neue Veröffentlichung ersetzt, somit kann es keine mehrere Versionen einer Webseite 
öffentlich gemacht werden. Zusätzlich wird die Veröffentlichung im Model Publication gespeichert.

**Automatische erstellung eines neuen Entwurfs**<br>

Das System erstellt nun eine neue bearbeitbare Seitenversion auf Basis des veröffentlichten Inhaltsstands. Dazu werden die 
zugeordneten PageBlock-Objekte und die benötigten Blöcke für die neue Version übernommen. So kann die Webseite weiterhin
bearbeitet werden, während die veröffentlichte Version unverändert bleibt. Dadurch wird verhindert, dass Änderungen an einem 
Entwurf auswirkungen auf die öffentlich sichtbare Webseite haben. 

**Öffentliche Darstellung**<br>

Das Model Page hat ein Feld "slug", dort wird der Slug der Webseite gespeichert, der beim Erstellen einer Seite eingegeben wird. 
Über diesen Slug kann die Webseite öffentlich aufgerufen werden und die veröffentlichte Seitenversion wird ermittelt.
Die Darstellung erfolgt über die Route /cms/seite/<slug>/.<br>
Seitenversionen, die nicht veröffentlicht sind, können nicht über diese Route dargestellt werden.

**Archivierung**<br>

Eine veröffentlichte Seitenversion kann auch durch archivierung aus dem öffentlichen Zustand entfernt werden und somit
wird sie wieder zu einem Entwurf. Die Inhalte dieser Version und Daten bleiben dabei in der Datenbank erhalten.

# **7 Installation und Einrichtung:**

1. Voraussetzung zur installation: Python 3, pip
2. Repository clonen: https://github.com/Arthur-dev624/Schul-Portal.git cd Schul-CMS
3. Virtuelle Umgebung erstellen im Schul-CMS directory: python -m venv env, Aktivieren: env/Scripts/activate
4. Abhängigkeiten installieren: pip install -r requirements.txt
5. Migrationen: python manage.py makemigrations python manage.py migrate
6. Django Superuser erstellen: python manage.py createsuperuser Username und Passwort eingeben für Djangos Admin Oberfläche
7. Entwicklungsserver starten: python manage.py runserver
8. Layout und Layoutregionen erstellen: python manage.py seed
9. Im Browser öffnen: http://127.0.0.1:8000/admin/ -> Admin Oberfläche von Django
10. In Admin Oberfläche unter Benutzer einen neuen Benutzer anlegen, dann unter Persons neue Person mit Rolle Admin für CMS zugang
11. Im Browser öffnen: http://127.0.0.1:8000/cms/ -> Anmelden für CMS mit angelegtem Benutzer<br>

Admin-Seite: Verwaltung der Modelle in myapp/models.py -> Modelle für die Funktionen der Schulwebseite
CMS-Seite: System um Webseiten zu erstellen

# **8 Code Dokumentation der cms app:**

**cmsLogin.py:**<br> 
1. cms_dashboard prüft nach dem Login die Rolle des Benutzers, mit der Rolle admin wird dieser dann zum Admin-
            Dashboard weitergeleitet
2. admin_dashboard rendert die CMS-Übersicht cmsSurface.html, diese View lädt die Anzahl der Seiten, veröffentlichte
            Seiten, Entwürfe und Medien sowie die drei zuletzt bearbeiteten Seiten mit ihrer aktuellen Version und ihrem Status
3. cms_login rendert die Login-Seite cmsLogin.html und bei einem POST-Request werden Benutzername und Passwort
            mit Djangos authenticate überprüft und der Benutzer anschließend angemeldet
4. cms_logout meldet den Benutzer ab und leitet diesen zurück zur CMS-Login Seite<br>

**seitenVerwaltung.py:**<br> 
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
14. delete_page löscht die ausgewählte Page aus der Datenbank und leitet anschließend zurück zur Seitenverwaltung<br>

**medienVerwaltung.py:**<br>
1. CmsImageForm.clean_file validiert hochgeladene Bilddateien, geprüft wird eine maximale Bildgröße von 10 MB,
                tatsächliches Bildformat und die Dateiendung und Bildformat
2. _get_media_type ermittelt anhand des validierten Bildformats den passenden MIME-Type des Medium
3. _delete_old_file löscht eine ersetzte Mediendatei aus dem Dateispeicher, sofern kein anderer CmsMedium-
                Datensatz auf diese Datei verweist
4. to_medien_verwaltung rendert die Medienverwaltung medienVerwaltung.html und nur admins dürfen darauf zugreifen,
                die View ermöglicht das Hochladen von Bildern und das ersetzen von Bildern. Die Dateien werden geprüft und als
                CmsMedium gespeichert. Es werden alle vorhandenen Medien, ihre Verwendung in Blöcken und die Anzahl der Medien geladen<br>

**navigationVerwaltung.py:**<br>
1. NavigationForm.__init__ erstellt das Formular zur Navigationsverwaltung und stellt nur veröffentlichte Seiten
                als auswählbare Ziele eines Navigationseintrags zur Verfügung
2. get_visible_navigation gibt alle sichtbaren Navigationseinträge zurück, deren verlinkte Seite veröffentlicht ist
                Die Einträge werden nach ihrer Position sortiert
3. to_navigation_verwaltung rendert die Navigationsverwaltung navigationsverwaltung.html nur admins können
                Einträge erstellen, bearbeiten und löschen. Im aktuellen Prototyp werden nur Einträge ohne Untermenüs unterstützt
4. cms_page stellt eine veröffentlichte CMS-Seite öffentlich über ihren Slug dar. Dafür wird die aktuell veröffentlichte
                PageVersion geladen und zusammen mit Layout, Design, Blöcken und Navigation gerendert<br>

**pageRelease.py:**<br>
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
                deaktiviert, ohne Versionen oder Blöcke zu löschen<br>

**api.py:**<br>
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
22. update_button_block aktualisiert Text, URL und Style eines vorhandenen Buttonblocks<br>

**admin.py:** leer
**apps.py:** leer
**urls.py:**<br>
1. Die Login-, Logout- und Dashboard-Routen führen zu den Views aus cmsLogin.py. 
2. Die Routen der Seitenverwaltung ermöglichen das Anzeigen, Erstellen, Bearbeiten, Löschen und Suchen von Seiten. 
3. Für den Editor gibt es eigene URLs zum Bearbeiten einer Seitenversion, zum Erstellen neuer Blöcke sowie zum Bearbeiten einzelner vorhandener PageBlocks. 
4. Die Vorschau-Routen zeigen eine bestimmte Seitenversion entweder direkt im Editor oder in einer eigenen Vorschauansicht an. 
5. Die Medienverwaltungs-Route öffnet die Verwaltungsoberfläche zum Hochladen und Ersetzen von Medien. 
6. Die Navigationsverwaltungs-Route öffnet die Oberfläche zum Erstellen und Bearbeiten von Navigationseinträgen. 
7. seite/<slug:slug>/ stellt eine veröffentlichte CMS-Seite öffentlich über ihren Slug dar. 
8. Die Veröffentlichungsverwaltung besitzt Routen für die Übersicht sowie für das Veröffentlichen und Archivieren einzelner Seiten.<br>

Die dynamischen URL-Parameter wie <int:page_id>, <int:version>, <int:page_block_id> und <slug:slug> werden an die 
jeweilige View übergeben, damit gezielt mit einer bestimmten Seite, Version oder einem bestimmten Block gearbeitet werden kann.

# **9 Einschränkungen:**

Das Content-Management-System wurde im Rahmen der Projektarbeit als funktionsfähiger Prototyp entwickelt. Einige Funktionen
sind daher bislang nur teilweise implementiert oder bewusst auf einen bestimmten Funktionsumfang beschränkt.

**Funktionsblöcke**<br>

Bestehende Schulportal-Funktionen als Inhaltsblöcke anzubieten, ist nicht umgesetzt. Die dafür vorgesehenen Datenmodelle
Function und FunctionBlock sind vorhanden. Das Erstellen und Einbinden von Funktionsblöcken über den Seiteneditor sowie deren
Darstellung stehen jedoch aus.<br>

**Layout- und Designverwaltung**<br>

Layouts, Layoutregionen und Designs werden derzeit durch den Entwickler bereitgestellt. Eine eigenständige Verwaltungsoberfläche, 
mit der Benutzer Layouts und Designs bearbeiten oder erstellen können, ist nicht implementiert und war auch im Projektumfang 
nicht vorgesehen. Der Seed-Befehl stellt aktuell ein Landingpage-Layout mit drei Layoutregionen bereit. Weitere Designs, Layouts und 
Layoutregionen müssen vom Entwickler gesondert angelegt werden.<br>

**Navigationsverwaltung**<br>

Durch das angelegte Datenmodell und der Beziehung parent_id ist es möglich hierarchische Navigationen zu erstellen. 
Es wird jedoch nach der aktuellen Implementierung nur Navigationseinträge auf oberster Ebene unterstützt. Die Verwaltung
verschachtelter Menüs ist daher noch nicht umgesetzt.<br>

**Berechtigungssystem**<br>

Bei der Zugriffssteuerung wird das vorhandene Benutzer- und Rollensystem des Schul-Portals verwendet. Die Überprüfung der 
Administratorrechte erfolgt nicht in allen CMS-Views einheitlich. Eine vollständige Absicherung der Verwaltungsfunktionen steht aus.<br>

**Medienverwaltung**<br>

In der Medienverwaltung werden nur Bilddateien des Formats JPEG, PNG, GIF und WebP mit einer maximalen Dateigröße von 10 MB unterstützt.<br>

**Seiteneditor und Vorschau**<br>

Der Seiteneditor ermöglicht die Bearbeitung und Positionierung von Inhaltsblöcken sowie die Darstellung einer Vorschau
innerhalb eines iframe.<br>

**Automatisierte Tests**<br>

Es ist keine Testsuite für die CMS-App enthalten.
