from django.contrib import admin
from .models import (
    Branche,
    Person,
    Student,
    Lesson,
    Enrollment,
    Grade,
    Announcement,
    Event,
    Quiz,
    Lunch,
    Quiz_Sammlung,
    File_Lernmaterial,
    News,
    Kategorie,
    Schoolbilder,
    Karriere
)

# Admin-Registrierung für Branchen
@admin.register(Branche)
class BrancheAdmin(admin.ModelAdmin):
    list_display = ("name",)  # Anzeige der Spalten in der Admin-Liste

# Admin-Registrierung für Personen
@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "branch")  # Spaltenanzeige
    list_filter = ("role", "branch")  # Filtermöglichkeiten im Admin

# Admin-Registrierung für Studenten
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("user", "grade_level")  # Anzeige in der Liste
    search_fields = ("user__username",)  # Suchfunktion nach Benutzername

# Admin-Registrierung für Lektionen
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("name", "branch")  # Spaltenanzeige
    filter_horizontal = ("teachers",)  # Horizontale Mehrfachauswahl für Lehrer

# Admin-Registrierung für Einschreibungen
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "lesson", "enrolled_at")  # Spaltenanzeige

# Admin-Registrierung für Noten
@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "value", "given_by", "created_at")  # Anzeige in Liste

# Admin-Registrierung für Ankündigungen
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("text", "date")  # Spaltenanzeige

# Admin-Registrierung für Mittagessen
@admin.register(Lunch)
class LunchAdmin(admin.ModelAdmin):
    list_display = ("lunchname", "preis","inhalte","allergiewarn")  # Anzeige der Felder

# Admin-Registrierung für Veranstaltungen
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title","anfang","ende","audience")  # Spaltenanzeige

# Admin-Registrierung für Quiz
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("frage", "richtigeantwort")  # Anzeige von Frage und Antwort

# Admin-Registrierung für Quiz-Sammlungen
@admin.register(Quiz_Sammlung)
class Quiz_SammlungAdmin(admin.ModelAdmin):
    list_display = ["lesson","title"]  # Anzeige der Felder

# Admin-Registrierung für Lernmaterialien
@admin.register(File_Lernmaterial)
class LernMaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "lesson", "hochgeladen_um")  # Spaltenanzeige

# Admin-Registrierung für Nachrichten
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("titel", "kategorie", "erstellt_at")  # Spaltenanzeige
    search_fields = ("titel", "kurz_text")  # Suchfunktion
    list_filter = ("kategorie", "erstellt_at")  # Filtermöglichkeiten
    ordering = ("-erstellt_at",)  # Sortierung nach Erstellungsdatum

# Admin-Registrierung für Kategorien
@admin.register(Kategorie)
class KategorieAdmin(admin.ModelAdmin):
    list_display = ("name","beschreibung","gestaltet_at")  # Spaltenanzeige
    search_fields = ("name","beschreibung")  # Suchfunktion

# Admin-Registrierung für Schulbilder
@admin.register(Schoolbilder)
class SchoolbilderAdmin(admin.ModelAdmin):
    list_display = ("bild","titel")  # Anzeige der Felder

# Admin-Registrierung für Karrieren/Jobs
@admin.register(Karriere)
class KarreireAdmin(admin.ModelAdmin):
    list_display = ("jobtitel","jobbeschreibung","erstellt_at")  # Spaltenanzeige