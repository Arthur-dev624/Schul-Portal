from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import *

# Registrierungsformular für neue Benutzer
class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)  # E-Mail Feld ist erforderlich

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]  # Felder im Formular

    # E-Mail auf Einzigartigkeit prüfen
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("this e-mail already used.")  # Fehler wenn E-Mail schon existiert
        return email

    # Benutzer speichern
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

# Formular für Noten
class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ["value", "note"]  # Nur die vom Lehrer benötigten Felder

# Formular für Veranstaltungen
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'anfang', 'ende', 'audience']  # Felder für Event
        widgets = {
            'anfang': forms.DateTimeInput(attrs={'type': 'datetime-local'}),  # Datumsauswahl Start
            'ende': forms.DateTimeInput(attrs={'type': 'datetime-local'}),   # Datumsauswahl Ende
        }

# Formular für Forum-Beiträge
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content','image','kategorie']  # Felder für Beitrag
        widgets = {
            'content': forms.Textarea(attrs={'rows':3, 'placeholder':'Post your Idea...'}),  # Textarea für Inhalt
            'kategorie': forms.Select(attrs={'class': 'form-select'}),  # Auswahl Kategorie
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),  # Bild-Upload
        }

# Formular für Kommentare
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["commentcontent"]  # Nur Inhalt des Kommentars
        widgets = {
            "commentcontent": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Write a comment..."  # Platzhalter
            })
        }

# Formular für Quiz-Erstellung
class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['lesson', 'frage', 'antwort1', 'antwort2', 'antwort3', 'antwort4', 'richtigeantwort']  # Quizfelder

    # Filtert die Lektionen, die der Lehrer unterrichtet
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['lesson'].queryset = Lesson.objects.filter(teachers=user)  # Nur eigene Lektionen

# Formular für Lernmaterial-Upload
class UploadFileForm(forms.ModelForm):
    class Meta:
        model = File_Lernmaterial
        fields = ["lesson", "title", "file", "description"]  # Felder für Upload

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["lesson"].queryset = Lesson.objects.filter(teachers=user)  # Nur eigene Lektionen

# Kontaktformular für externe Nachrichten
class KontaktForm(forms.Form):
    name = forms.CharField(max_length=100)  # Name des Absenders
    email = forms.EmailField()  # E-Mail-Adresse
    subject = forms.CharField(max_length=200, required=False)  # Betreff optional
    text = forms.CharField(widget=forms.Textarea)  # Nachrichtentext

# Formular zur Bearbeitung von Personendaten
class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ["phone", "profile_image", "branch"]  # Telefonnummer, Profilbild, Branche

# Formular zur Bearbeitung von Studentendaten
class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["address", "birth_date", "grade_level"]  # Adresse, Geburtsdatum, Klassenstufe

# Formular für die Gemini AI Chatfunktion
class GeminiAiChatForm(forms.Form):
    question = forms.CharField(
        label="Ask Gemini",  # Feldbeschriftung
        widget=forms.Textarea(attrs={"rows":3, "placeholder":"Type your question here..."}),  # Textarea
        max_length=500  # Maximale Länge
    )