# Dokumentation der CMS-Models

Die Models bilden die Grundlage für Seiten, Layouts, Designs, Inhaltsblöcke, Medien, Navigation, Funktionen 
und Veröffentlichungen.

# Layout

Speichert ein Seitenlayout, das beim Erstellen einer CMS-Seite ausgewählt werden kann.

Felder:
- `id`: Primärschlüssel
- `name`: Name des Layouts, z. B. `Startseite`.
- `description`: Beschreibung des Layouts.
- `template`: Name der HTML-Template-Datei, die gerendert wird, z. B. `startseite.html`.

Beziehungen:
- Ein `Layout` kann mehrere `LayoutRegion`-Einträge haben.
- Eine `Page` verweist auf genau ein `Layout`.

# LayoutRegion

Beschreibt Bereiche innerhalb eines Layouts, in die Inhaltsblöcke eingefügt werden können.

Felder:
- `id`: Primärschlüssel.
- `layout_id`: Fremdschlüssel auf `Layout`.
- `name`: Anzeigename der Region.
- `key`: Technischer Schlüssel der Region, z. B. `hero`, `main` oder `footer`.

Beziehungen:
- Eine `LayoutRegion` gehört zu einem `Layout`.
- `PageBlock` nutzt `LayoutRegion`, um einen Block an einer Stelle im Layout zu platzieren.

# Design

Speichert Designvorgaben für CMS-Seiten.

Felder:
- `id`: Primärschlüssel.
- `name`: Name des Designs.
- `font_family`: Schriftart.
- `primary_color`: Primärfarbe.
- `secondary_color`: Sekundärfarbe.
- `background_color`: Hintergrundfarbe.
- `border_radius`: Optionaler Radius für abgerundete Ecken.
- `content_width`: Optionale Inhaltsbreite.
- `content_height`: Optionale Inhaltshöhe.
- `distance`: Optionaler Abstandswert.
- `font_size`: Optionale Schriftgröße.
- `font_color`: Optionale Schriftfarbe.
- `custom_css`: Name oder Pfad zu einer CSS-Datei.

Beziehungen:
- Eine `Page` verweist auf genau ein `Design`.

# Page

Repräsentiert eine CMS-Seite.

Felder:
- `id`: Primärschlüssel.
- `title`: Seitentitel.
- `slug`: URL-freundlicher eindeutiger Seitenname.
- `status`: Gibt an, ob die Seite veröffentlicht ist.
- `layout_id`: Fremdschlüssel auf `Layout`.
- `design_id`: Fremdschlüssel auf `Design`.
- `created_by`: Benutzer, der die Seite erstellt hat.
- `created_at`: Erstellungszeitpunkt.
- `updated_at`: Zeitpunkt der letzten Änderung.

Beziehungen:
- Eine `Page` hat ein Layout und ein Design.
- Eine `Page` kann mehrere `PageVersion`-Einträge haben.
- Eine `Page` kann über `NavigationItem` in der Navigation verlinkt werden.

# PageVersion

Speichert eine Version einer CMS-Seite. Dadurch kann eine Seite theoretisch mehrere Bearbeitungs- oder Veröffentlichungsstände besitzen.

Felder:
- `id`: Primärschlüssel.
- `page_id`: Fremdschlüssel auf `Page`.
- `created_by`: Benutzer, der die Version erstellt hat.
- `created_at`: Erstellungszeitpunkt der Version.
- `version`: Versionsnummer.
- `status`: Status der Version.
- `published_at`: Optionaler Zeitpunkt der Veröffentlichung.

Beziehungen:
- Eine `PageVersion` gehört zu einer `Page`.
- `PageBlock` verbindet eine `PageVersion` mit ihren Blöcken.
- `Publication` verweist auf eine veröffentlichte `PageVersion`.

# NavigationItem

Speichert einen Navigationseintrag für die generierte Schulwebsite.

Felder:
- `id`: Primärschlüssel.
- `page_id`: Fremdschlüssel auf die verlinkte `Page`.
- `parent_id`: Optionaler Fremdschlüssel auf einen übergeordneten Navigationseintrag.
- `title`: Titel des Navigationseintrags.
- `position`: Optionale Sortierposition.
- `visible`: Gibt an, ob der Eintrag sichtbar ist.

Beziehungen:
- Ein `NavigationItem` verweist auf eine `Page`.
- Durch `parent_id` können hierarchische Navigationen aufgebaut werden.

# Block

Speichert einen einzelnen Inhaltsblock.

Felder:
- `id`: Primärschlüssel.
- `block_type`: Typ des Blocks, z. B. Text, Bild oder Funktionsblock.
- `config`: Optionale JSON-Konfiguration für block-spezifische Inhalte.
- `created_at`: Erstellungszeitpunkt.
- `updated_at`: Zeitpunkt der letzten Änderung.

Beziehungen:
- `PageBlock` ordnet einen `Block` einer Seitenversion und Layoutregion zu.
- `BlockMedium` verbindet einen `Block` mit Medien.
- `FunctionBlock` verbindet einen `Block` mit einer CMS-Funktion.

# CmsMedium

Speichert hochgeladene Medien für das CMS.

Felder:
- `id`: Primärschlüssel.
- `file`: Datei im Upload-Pfad `media/cms`.
- `title`: Titel des Mediums.
- `media_type`: Medientyp, z. B. Bild oder Dokument.
- `alt_text`: Alternativtext für Barrierefreiheit.
- `uploaded_by`: Benutzer, der das Medium hochgeladen hat.
- `uploaded_at`: Upload-Zeitpunkt.

Beziehungen:
- `BlockMedium` kann Medien mit Inhaltsblöcken verbinden.

# Function

Beschreibt aktivierbare Funktionen, die als dynamische Bestandteile der Website genutzt werden können.

Felder:
- `id`: Primärschlüssel.
- `function_type`: Eindeutiger Funktionstyp aus einer festen Auswahlliste, z. B. `news`, `forum`, `quiz` oder `ai chat`.
- `code`: Textfeld für den zugehörigen Code oder technische Beschreibung.
- `active`: Gibt an, ob die Funktion aktiv ist.

Beziehungen:
- `FunctionBlock` verbindet eine Funktion mit einem Block.

# PageBlock

Verknüpft eine Seitenversion mit einem Block und einer Layoutregion.

Felder:
- `id`: Primärschlüssel.
- `page_version_id`: Fremdschlüssel auf `PageVersion`.
- `block_id`: Fremdschlüssel auf `Block`.
- `layout_region_id`: Fremdschlüssel auf `LayoutRegion`.
- `position`: Reihenfolge des Blocks innerhalb der Region.

Beziehungen:
- Dieses Model ist die zentrale Zuordnung zwischen Seitenversion, Inhalt und Layoutposition.

# BlockMedium

Verknüpft einen Inhaltsblock mit einem Medium.

Felder:
- `id`: Primärschlüssel.
- `block_id`: Fremdschlüssel auf `Block`.
- `medium_id`: Fremdschlüssel auf `CmsMedium`.
- `position`: Reihenfolge des Mediums innerhalb des Blocks.

Beziehungen:
- Ermöglicht mehrere Medien pro Block.

# FunctionBlock

Verknüpft einen Block mit einer CMS-Funktion.

Felder:
- `id`: Primärschlüssel.
- `function_id`: Fremdschlüssel auf `Function`.
- `block_id`: Fremdschlüssel auf `Block`.
- `config`: Optionale JSON-Konfiguration für die konkrete Funktion im Block.

Beziehungen:
- Ermöglicht dynamische Funktionsblöcke, z. B. News, Kalender, Quiz oder Forum.

# Publication

Speichert eine Veröffentlichung einer Seitenversion.

Felder:
- `id`: Primärschlüssel.
- `page_version_id`: Fremdschlüssel auf die veröffentlichte `PageVersion`.
- `published_at`: Zeitpunkt der Veröffentlichung.
- `published_by`: Benutzer, der die Veröffentlichung ausgeführt hat.

Beziehungen:
- Eine `Publication` dokumentiert, welche `PageVersion` durch welchen Benutzer veröffentlicht wurde.

Hinweis:
- Die aktuelle View `release_page` setzt bisher nur `Page.status = True`. Sie erstellt aktuell keinen `Publication`-Eintrag.
