from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# -------------------------------------------------
# Datenbank-Modelle für das Django-Projekt
# -------------------------------------------------

# Branche-Modell (Fachbereich / Abteilung)
class Branche(models.Model):
    name = models.CharField(max_length=255)  # Name der Branche

    class Meta:
        verbose_name = "Branche"
        verbose_name_plural = "Branches"

    def __str__(self):
        return self.name


# Person-Modell für Lehrer oder Schüler
class Person(models.Model):
    ROLE_CHOICES = (
        ("student", "Student"),
        ("teacher", "Teacher"),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="person"
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)  # Rolle auswählen
    branch = models.ForeignKey(Branche, on_delete=models.SET_NULL, null=True, blank=True)  # Zugehörige Branche
    phone = models.CharField(max_length=20, blank=True)  # Telefonnummer
    profile_image = models.ImageField(upload_to="teachers/", blank=True, null=True)  # Profilbild

    def __str__(self):
        return f"{self.user.username} ({self.role})"


# --------------------
# Student-Modell (nur Schülerdaten)
# --------------------
class Student(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student"
    )
    address = models.CharField(max_length=255, blank=True)  # Adresse
    birth_date = models.DateField(null=True, blank=True)  # Geburtsdatum
    grade_level = models.PositiveSmallIntegerField(null=True, blank=True)  # Klassenstufe
    profile_image = models.ImageField(upload_to="students/", blank=True, null=True)  # Profilbild

    def __str__(self):
        return self.user.username


# Unterricht / Lesson
class Lesson(models.Model):
    name = models.CharField(max_length=200)  # Name der Lektion
    branch = models.ForeignKey(Branche, on_delete=models.SET_NULL, null=True, blank=True)
    teachers = models.ManyToManyField(User, related_name="lessons", blank=True)  # Lehrer der Lektion

    def __str__(self):
        return self.name


# Einschreibung eines Schülers in eine Lektion
class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrollments")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(default=timezone.now)  # Zeitpunkt der Einschreibung

    class Meta:
        unique_together = ("student", "lesson")  # Doppelte Einträge verhindern

    def __str__(self):
        return f"{self.student} - {self.lesson}"


# Noten
class Grade(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="grades")
    value = models.DecimalField(max_digits=5, decimal_places=2)  # Notenwert
    note = models.CharField(max_length=255, blank=True)  # optionale Bemerkung
    given_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="given_grades")  # Lehrer
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.enrollment.student} - {self.enrollment.lesson}: {self.value}"


# Ankündigungen
class Announcement(models.Model):
    text = models.CharField(max_length=255)  # Text der Ankündigung
    date = models.DateField(null=True, blank=True)  # Datum

    def __str__(self):
        return self.text


# Kalenderereignisse
class Event(models.Model):
    title = models.CharField(max_length=200)
    anfang = models.DateTimeField()  # Startzeit
    ende = models.DateTimeField(null=True, blank=True)  # Endzeit
    audience = models.CharField(
        choices=[("teacher","Teacher"),("student","Student"),("both","Both")],
        max_length=10
    )  # Zielgruppe


# Kategorie für Forum/Beiträge
class Kategorie(models.Model):
    name = models.CharField(max_length=100)
    beschreibung = models.TextField(blank=True)
    gestaltet_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# Forum-Post
class Post(models.Model):
    kategorie = models.ForeignKey(Kategorie,on_delete=models.CASCADE,related_name="posts")
    content = models.CharField(max_length=200)  # Inhalt
    image = models.ImageField(upload_to="images/", blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content

    # Anzahl Kommentare
    def comment_count(self):
        return self.comments.count()

    # Anzahl Likes
    def like_count(self):
        return self.likes.count()


# Kommentare
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    commentcontent = models.CharField(max_length=200)  # Kommentartext
    commentauthor = models.ForeignKey(User, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.commentauthor.username} - {self.commentcontent[:20]}"

    class Meta:
        ordering = ["-submitted_at"]


# Likes für Posts
class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("post", "user")  # Doppelte Likes verhindern

    def __str__(self):
        return f"{self.user.username} liked {self.post.id}"


# Mittagessen
class Lunch(models.Model):
    lunchname = models.CharField(max_length=200)
    preis = models.DecimalField(max_digits=7, decimal_places=2)
    inhalte = models.CharField(max_length=200)
    allergiewarn = models.BooleanField()  # Allergiehinweis
    date = models.DateField()  # Datum


# Quiz
class Quiz(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE,null=True,blank=True, related_name="quiz")
    frage = models.CharField(max_length=200,null=True)
    antwort1= models.CharField(max_length=100,null=True)
    antwort2= models.CharField(max_length=100,null=True)
    antwort3= models.CharField(max_length=100,null=True)
    antwort4= models.CharField(max_length=100,null=True)
    richtigeantwort=models.CharField(max_length=100,null=True)      

    def __str__(self):
        return self.frage


# Sammlung von Quizfragen
class Quiz_Sammlung(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)   # Titel der Sammlung
    questions = models.JSONField()             # Fragen als JSON

    def __str__(self):
        return f"{self.title} ({self.lesson.name})"


# Quiz-Versuche
class Quiz_Versuch(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="versuche")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quiz_versuche")
    angefangen_at = models.DateTimeField(auto_now_add=True)  # Startzeit
    beendet_at = models.DateTimeField(null=True, blank=True)  # Endzeit
    ergebniss = models.FloatField(null=True, blank=True)  # Ergebnis

    def __str__(self):
        return f"{self.user.username} - {self.quiz.frage} - {self.ergebniss}"


# Lernmaterialien
class File_Lernmaterial(models.Model):
    lesson = models.ForeignKey(Lesson,on_delete=models.CASCADE,related_name="lernmaterials")
    title = models.CharField(max_length=200)
    file= models.FileField(upload_to=('learnmaterials/'))
    hochgeladen_um =models.DateTimeField(auto_now=True,blank=True)
    description = models.TextField(blank=True, null=True)


# News
class News(models.Model):
    titel = models.CharField(max_length=200)
    kurz_text = models.TextField()
    voll_text = models.TextField()
    bild = models.ImageField(upload_to="news/")
    kategorie = models.CharField(max_length=50)
    erstellt_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titel


# Schulbilder
class Schoolbilder(models.Model):
    bild= models.ImageField(upload_to="bilder/")
    titel =models.CharField(max_length=100)

    def __str__(self):
        return self.titel 


# Karriere / Jobangebote
class Karriere(models.Model):
    jobtitel= models.CharField(max_length=100,blank=False)
    jobbeschreibung= models.CharField(max_length=1000)
    erstellt_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.jobtitel


# AI Chat Integration
class Chat_ai(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Message_ai(models.Model):
    chat = models.ForeignKey(Chat_ai, related_name="messages", on_delete=models.CASCADE)
    role = models.CharField(max_length=10)  # user / model
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)