from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.utils import translation
from .models import *
from django.db.models import Count
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .forms import *
from .models import *
from google import genai
import json
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import gettext as _

# home view
def home(request):
    school_image = Schoolbilder.objects.filter(bild__icontains="Hibbing_High_School_2014_hqiUPEK.jpg").first()
    # du kannst Name von deinem Bild und Bild datei andern, indem du auf Admin das gewunschte Bild hochzuladest.
    news = News.objects.order_by('-erstellt_at')
    announcements = Announcement.objects.order_by('-date')
    return render(request, "school/home.html", {"school_image": school_image,"news": news, "announcements": announcements})

# dashboard view
@login_required
def dashboard(request):
    role = request.user.person.role
    if role == "teacher":
        return redirect("teacher_dashboard")
    elif role == "student":
        return redirect("student_dashboard")
    else:
        return redirect("login")

# dashboard fur teacher
@login_required
def teacher_dashboard(request):
    if request.user.person.role != "teacher":
        return redirect("dashboard")

    lessons = request.user.lessons.prefetch_related("enrollments__student")
  
    announcements = Announcement.objects.order_by("-date")
    return render(request, "school/teacher_dashboard.html", {"lessons": lessons,"announcements": announcements,})

#dashboard fur student
@login_required
def student_dashboard(request):
    if request.user.person.role != "student":
        return redirect("teacher_dashboard")

    person = request.user.person

    enrollments = Enrollment.objects.filter(student__user=request.user)
    grades = Grade.objects.filter(enrollment__student__user=request.user)
    return render(request, "school/student_dashboard.html", { "person": person, "enrollments": enrollments, "grades": grades, })

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = request.POST.get("role") # student / teacher
            Person.objects.create(
                user=user,
                role=role
            )
            if role == "student":
                Student.objects.create(user=user)
            auth_login(request, user)
            return redirect("dashboard")
    else:
        form = UserCreationForm()
    return render(request, "school/register.html", {"form": form})

# history view
def history(request):
    bild1= Schoolbilder.objects.filter(bild__icontains="siyah_beyaz_okul.jpg").first()
    bild2= Schoolbilder.objects.filter(bild__icontains="oldschoolpic.avif").first()
    bild3= Schoolbilder.objects.filter(bild__icontains="Hibbing_High_School_2014_hqiUPEK.jpg").first()
    return render(request, "school/history.html", {"bild1": bild1, "bild2":bild2,"bild3":bild3})

# school view
def school(request):
    bilder = Schoolbilder.objects.all()
    return render(request, "school/school.html", {"bilder": bilder})

# die Nachrichten alle
def news_list(request):
    news = News.objects.order_by('-erstellt_at')
    return render(request, "school/news_list.html", {"news": news})

# detaillierte Nachricht
def news_detail(request, pk):
    news_item = get_object_or_404(News, pk=pk)
    return render(request, "school/news_detail.html", {"news_item": news_item})

# Ankundigungen
def announcement_list(request):
    announcements = Announcement.objects.order_by('-date')
    return render(request, "school/announcement_list.html", {"announcements": announcements})

#Bibliothek view
def library(request):
    librarybild = Schoolbilder.objects.filter(bild__icontains="library.jpeg").first()
    # du kannst Name von deinem Bild und Bild datei andern, indem du auf Admin das gewunschte Bild hochzuladest.
    return render(request, "school/library.html", {"librarybild": librarybild})

# view Schulgebaude
def building(request):
    bild1 = Schoolbilder.objects.filter(bild__icontains="building1.jpeg").first()
    bild2 = Schoolbilder.objects.filter(bild__icontains="building2.jpeg").first()
    bild3 = Schoolbilder.objects.filter(bild__icontains="lageplan.jpeg").first()
    return render(request, "school/building.html", { "bild1": bild1, "bild2": bild2, "bild3": bild3 })

#view Sport Einrichtungen
def sport_fields(request):
    swimbild = Schoolbilder.objects.filter(bild__icontains="swim.jpeg").first()
    # du kannst Name von deinem Bild und Bild datei andern, indem du auf Admin das gewunschte Bild hochzuladest.
    runningbild=Schoolbilder.objects.filter(bild__icontains= "running.jpeg").first()
    basketballbild =Schoolbilder.objects.filter(bild__icontains="basketball.jpeg").first()
    return render(request, "school/sport_fields.html", {"swimbild": swimbild,"runningbild":runningbild,"basketballbild":basketballbild})

def team(request):
    staff_image = Schoolbilder.objects.filter(bild__icontains="teachers.jpg").first()
    # du kannst Name von deinem Bild und Bild datei andern, indem du auf Admin das gewunschte Bild hochzuladest.
    return render(request, "school/team.html", {"staff_image": staff_image})

def pricing(request):
    return render(request, "school/price.html")

def contact(request):
    sent = False
    form = KontaktForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        sent = True
        form = KontaktForm()

    return render(request, "school/contact.html", {"form": form, "sent": sent})

def login(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('dashboard')
        else:
            error = "Invalid username or password"
    return render(request, "school/login.html", {"error": error})

def logout(request):
    auth_logout(request)
    return redirect('home')

@login_required
def add_grade(request, enrollment_id):
    # Nur Lehrer dürfen Noten hinzufügen
    if request.user.person.role != "teacher":
        return HttpResponseForbidden("Bu işlemi gerçekleştirmek için yetkiniz yok.")
    
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    
    # Prüfen, ob der Lehrer diesen Kurs unterrichtet
    if enrollment.lesson not in request.user.lessons.all():
        return HttpResponseForbidden("Bu derse not ekleme yetkiniz yok.")
    
    if request.method == "POST":
        form = GradeForm(request.POST)
        if form.is_valid():
            grade = form.save(commit=False)
            grade.enrollment = enrollment  # Note dem Einschreibung zuweisen
            grade.given_by = request.user  # Note vom Lehrer
            grade.save()
            return redirect("teacher_dashboard")
    else:
        form = GradeForm()  # Leeres Formular für GET
    
    return render(request, "school/add_grade.html", {"form": form, "enrollment": enrollment})


@login_required
def calendar_view(request):
    # Zeigt den Kalender an
    return render(request, "school/calendar.html")


@login_required
def add_event(request):
    # Ereignis hinzufügen
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()  # Speichert das Ereignis
            return redirect("teacher_dashboard")
    else:
        form = EventForm()  # Leeres Formular für GET
    return render(request, "school/add_event.html", {"form": form})


@login_required
def event_list(request):
    # Alle Ereignisse abrufen
    events = Event.objects.all()
    
    # Filter je nach Rolle des Benutzers
    if hasattr(request.user, "person"):
        if request.user.person.role == "teacher":
            events = events.filter(audience__in=["teacher","both"])
        elif request.user.person.role == "student":
            events = events.filter(audience__in=["student","both"])
    
    # Daten für JSON-Ausgabe vorbereiten
    data = [
        {
            "title": event.title,
            "start": event.anfang.isoformat(),
            "end": event.ende.isoformat() if event.ende else None,
        } for event in events
    ]
    return JsonResponse(data, safe=False)


@login_required
def my_grades(request):
    # Nur Schüler dürfen ihre Noten sehen
    if request.user.person.role != "student":
        return redirect("teacher_dashboard")
    
    enrollments = Enrollment.objects.filter(student__user=request.user)
    grades = Grade.objects.filter(enrollment__student__user=request.user)
    return render(request, "school/mygrades.html", {"enrollments": enrollments, "grades": grades})


# Forum – Liste für Schüler
@login_required
def student_forum_list(request):
    posts = Post.objects.all().order_by('-submitted_at')  # Beiträge nach Datum sortieren
    return render(request, 'school/student_forum.html', {'posts': posts})


# Forum – Liste für Lehrer
@login_required
def teacher_forum_list(request):
    posts = Post.objects.all().order_by('-submitted_at')  # Beiträge nach Datum sortieren
    return render(request, 'school/teacher_forum.html', {'posts': posts})


# Forum – Detailansicht eines Beitrags
@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all().order_by("-submitted_at")  # Kommentare nach Datum sortieren
    
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post  # Kommentar mit Beitrag verknüpfen
            comment.commentauthor = request.user  # Autor setzen
            comment.save()
            return redirect("post_detail", pk=post.pk)
    else:
        form = CommentForm()  # Leeres Formular für GET
    
    context = {
        "post": post,
        "comments": comments,
        "form": form,
        "like_count": post.likes.count(),  # Anzahl Likes
    }
    return render(request, "school/post_detail.html", context)


# Forum – alle Beiträge auflisten
@login_required
def post_list(request, kategorie_id=None):
    # Beiträge nach Anzahl Likes annotieren und nach Datum sortieren
    posts = Post.objects.annotate(like_count=Count("likes")).order_by("-submitted_at")
    kategories = Kategorie.objects.all()  # Alle Kategorien abrufen
    
    if kategorie_id:
        posts = posts.filter(kategorie_id=kategorie_id)  # Filter nach Kategorie
    
    top_post = posts.order_by("-like_count").first()  # Beitrag mit den meisten Likes
    context = {
        "posts": posts,
        "kategories": kategories,
        "top_post": top_post,
        "kategorie_id": int(kategorie_id) if kategorie_id else None,
    }
    return render(request, "school/post_list.html", context)


# Forum – Beiträge nach Kategorie filtern
@login_required
def post_list_by_category(request, kategorie_id):
    kategories = Kategorie.objects.all()  # Alle Kategorien abrufen
    active_kategorie = kategorie_id  # Aktive Kategorie markieren
    
    posts = Post.objects.filter(kategorie_id=kategorie_id).order_by("-submitted_at")  # Beiträge filtern
    context = {
        "posts": posts,
        "kategories": kategories,
        "active_kategorie": active_kategorie,
    }
    return render(request, "school/post_list.html", context)
# Forum – create post

@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("post_list")
    else:
        form = PostForm()
    return render(request, "school/create_post.html", {"form": form})


# Forum – Like / Toggle

@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create( post=post, user=request.user )
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({ "liked": liked, "like_count": post.likes.count() })

@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
  
    # Prüfen, ob der angemeldete Benutzer der Autor des Beitrags ist
    if request.user != post.author :
        return HttpResponseForbidden("You are not allowed.")
    post.delete()  # Beitrag löschen
    return redirect("post_list")

@login_required
def add_quiz(request):
    # Nur Lehrer dürfen Quiz erstellen
    if not hasattr(request.user, "person") or request.user.person.role != "teacher":
        return HttpResponseForbidden("You are not allowed")
    
    if request.method == "POST":
        form = QuizForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()  # Quiz speichern
            return redirect("teacher_dashboard")
    else:
        form = QuizForm(user=request.user)  # Leeres Formular für GET
    return render(request, "school/add_question.html", {"form": form})

@login_required
def my_lessons(request):
    # Nur Schüler dürfen ihre Kurse sehen
    if request.user.person.role != "student":
        return HttpResponseForbidden("you are not allowed")
    
    student = request.user.student
    lessons = Lesson.objects.all()
    
    # IDs der Kurse, in die der Schüler eingeschrieben ist
    enrolled_lesson_ids = list(Enrollment.objects.filter(student=student).values_list('lesson__id', flat=True))
    return render(request, "school/my_lessons.html", {"lessons": lessons, "enrolled_lesson_ids": enrolled_lesson_ids})

@login_required
def enroll_lesson(request, lesson_id):
    # Nur Schüler können sich einschreiben
    if request.user.person.role != "student":
        return HttpResponseForbidden("Only students can enroll.")
    
    student = request.user.student
    lesson = get_object_or_404(Lesson, id=lesson_id)
    Enrollment.objects.get_or_create(student=student, lesson=lesson)  # Einschreibung erstellen, falls nicht vorhanden
    return redirect("my_lessons")

@login_required
def dropout_lesson(request, lesson_id):
    # Nur Schüler können sich abmelden
    if request.user.person.role != "student":
        return HttpResponseForbidden("Only students can dropout.")
    
    student = request.user.student
    enrollment = Enrollment.objects.filter(student=student, lesson_id=lesson_id).first()
    if enrollment:
        enrollment.delete()  # Einschreibung löschen
    return redirect("my_lessons")

@login_required
def lunch_view(request):
    # Nur Schüler und Lehrer dürfen den Speiseplan sehen
    if request.user.person.role not in ["student", "teacher"]:
        return HttpResponseForbidden("You are not allowed")
    
    lunches = Lunch.objects.all()
    return render(request, "school/lunch.html", {"lunches": lunches})

@login_required
def my_quiz(request):
    # Nur Schüler dürfen Quiz sehen
    if request.user.person.role != "student":
        return HttpResponseForbidden("you are not allowed")
    
    student = request.user.student
    # IDs der Kurse, in die der Schüler eingeschrieben ist
    enrolled_lesson_ids = list(Enrollment.objects.filter(student=student).values_list('lesson__id', flat=True))
    
    # Alle Quiz für eingeschriebene Kurse
    quizes = Quiz.objects.filter(lesson__id__in=enrolled_lesson_ids)
    return render(request, "school/my_quizez.html", {"quizes": quizes, "enrolled_lesson_ids": enrolled_lesson_ids})

@login_required
def take_quiz(request, pk):
    # Nur Schüler dürfen Quiz machen
    if request.user.person.role != "student":
        return HttpResponseForbidden("You are not allowed")
    
    student = request.user.student
    quiz = get_object_or_404(Quiz, pk=pk)
   
    # Prüfen, ob der Schüler für den Kurs eingeschrieben ist
    if not Enrollment.objects.filter(student=student, lesson=quiz.lesson).exists():
        return HttpResponseForbidden("You are not enrolled in this lesson")
    
    # Antwort erhalten und Richtigkeit prüfen
    if request.method == "POST":
        selected_answer = request.POST.get("answer")  # Antwort vom Formular
        ergebniss = 1 if selected_answer == quiz.richtigeantwort else 0  # Prüfen der richtigen Antwort
        
        # Quiz-Versuch erstellen
        Quiz_Versuch.objects.create(quiz=quiz, user=request.user, ergebniss=ergebniss)
      
        return render(request, "school/quiz_result.html", {"quiz": quiz, "ergebniss": ergebniss, "selected_answer": selected_answer})
    
    # GET: Quiz anzeigen
    return render(request, "school/take_quiz.html", {"quiz": quiz})

@login_required
def upload_material(request):
    # Nur Lehrer dürfen Materialien hochladen
    if request.user.person.role != "teacher":
        return HttpResponseForbidden("Only teachers can upload materials")
    
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()  # Material speichern
            return redirect("material_detail", lesson_id=form.cleaned_data["lesson"].id)
    else:
        form = UploadFileForm(user=request.user)  # Leeres Formular für GET
    
    return render(request, "school/upload_material.html", {"form": form})
@login_required
def material_detail(request, lesson_id):
    # Material-Details für eine bestimmte Lektion anzeigen
    lesson = get_object_or_404(Lesson, id=lesson_id)
   
    # Zugriffskontrolle für Schüler
    if request.user.person.role == "student":
        student = request.user.student
        is_enrolled = Enrollment.objects.filter(student=student, lesson=lesson).exists()
        if not is_enrolled:
            return HttpResponseForbidden("Sie sind nicht für diese Lektion eingeschrieben")
 
    # Zugriffskontrolle für Lehrer
    if request.user.person.role == "teacher":
        if lesson not in request.user.lessons.all():
            return HttpResponseForbidden("Sie unterrichten diese Lektion nicht")

    # Materialien abrufen
    materials = lesson.lernmaterials.all()
    return render(request, "school/material_detail.html", {"lesson": lesson, "materials": materials})


def karriere_view(request):
    # Alle Karriereangebote abrufen und nach Erstellungsdatum sortieren
    job = Karriere.objects.all().order_by("-erstellt_at")
    return render(request, "school/karrierepage.html", {"job": job})


def job_detail_view(request, pk):
    # Details zu einem bestimmten Job abrufen
    job = get_object_or_404(Karriere, pk=pk)
    return render(request, "school/jobdetail.html", {"job": job})


@login_required
def profile_view(request):
    # Profilansicht des aktuellen Benutzers
    return render(request, "school/profile.html")


@login_required
def profile_edit(request):
    # Profilbearbeitung für Lehrer oder Schüler
    person = request.user.person
    student = None
   
    if person.role == "teacher":
        # Lehrer: PersonForm mit Branch-Feld
        person_form = PersonForm(request.POST or None, request.FILES or None, instance=person)
    else:
        # Schüler: Branch-Feld entfernen
        person_form = PersonForm(request.POST or None, request.FILES or None, instance=person)
        person_form.fields.pop("branch")

    if person.role == "student":
        # Schüler-spezifische Daten bearbeiten
        student = request.user.student
        student_form = StudentForm(request.POST or None, instance=student)
    else:
        student_form = None

    if request.method == "POST":
        if person_form.is_valid() and (not student_form or student_form.is_valid()):
            person_form.save()
            if student_form:
                student_form.save()
            return redirect("profile_view")

    return render(request, "school/profile_edit.html", {"person_form": person_form, "student_form": student_form})


# Google Gemini Client initialisieren
client = genai.Client(api_key=settings.GEMINI_API_KEY) 


@login_required
def chat_page(request):
    # Chat-Seite anzeigen
    return render(request, "school/chat.html")


@require_POST
@csrf_protect
@login_required
def gemini_chat(request):
    # API-Endpunkt für den Gemini Chat
    try:
        api_key = getattr(settings, "GEMINI_API_KEY", None)
        if not api_key:
            return JsonResponse({"error": "GEMINI_API_KEY ist nicht konfiguriert."}, status=500)

        from google import genai
        client = genai.Client(api_key=api_key)

        data = json.loads(request.body)
        message = data.get("message", "").strip()
        if not message:
            return JsonResponse({"error": "Keine Nachricht"}, status=400)

        # Antwort vom Gemini-Modell generieren
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=message,
        )
        return JsonResponse({"reply": response.text})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)