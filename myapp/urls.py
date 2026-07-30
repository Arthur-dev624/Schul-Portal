from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("home/", views.home, name="home"),  # Startseite
    path("register/",views.register,name="register"),  # Registrierung
    path("pricing/", views.pricing, name="pricing"),  # Preise / Tarife
    path("history/", views.history, name="history"),  # Verlauf / History
    path("team/", views.team, name="team"),  # Team-Seite
    path("school/", views.school, name="school"),  # Schulinformationen
    path("login/",views.login,name="login"),  # Login-Seite
    path("logout/" ,views.logout,name="logout"),  # Logout
    path("studentpage/", views.student_dashboard, name="student_dashboard"),  # Schüler-Dashboard
    path("teacherpage/", views.teacher_dashboard, name="teacher_dashboard"),  # Lehrer-Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),  # Allgemeines Dashboard
    path("add_grade/<int:enrollment_id>/", views.add_grade, name="add_grade"),  # Note hinzufügen
    path('calendar/', views.calendar_view, name='calendar_view'),  # Kalenderansicht
    path('add-event/', views.add_event, name='add_event'),  # Neues Event hinzufügen
    path('event-list/', views.event_list, name='event_list'),  # Eventliste
    path('profile/', views.profile_view, name='profile_view'),  # Profil anzeigen
    path('profile/edit', views.profile_edit,name='profile_edit'),  # Profil bearbeiten
    path('my-grades/', views.my_grades, name='my_grades'),  # Meine Noten
    path("student/", views.student_forum_list, name="student_forum_list"),  # Schüler-Forum
    path("teacher/", views.teacher_forum_list, name="teacher_forum_list"),  # Lehrer-Forum
    path("post/<int:pk>/", views.post_detail, name="post_detail"),  # Detailansicht eines Posts
    path("post/create/", views.create_post, name="create_post"),  # Post erstellen
    path("post/<int:pk>/like/", views.like_post, name="like_post"),  # Post liken
    path("posts/", views.post_list, name="post_list"),  # Alle Posts anzeigen
    path('delete/<int:pk>/', views.delete_post, name='delete_post'),  # Post löschen
    path("quiz/add/", views.add_quiz, name="add_quiz"),  # Quiz hinzufügen
    path("my_lessons/", views.my_lessons, name="my_lessons"),  # Meine Lektionen
    path("enroll/<int:lesson_id>/", views.enroll_lesson, name="enroll_lesson"),  # Einschreiben in Lektion
    path('dropout/<int:lesson_id>/', views.dropout_lesson, name='dropout_lesson'),  # Lektion abbrechen
    path('lunch_programm/',views.lunch_view,name="lunch_view"),  # Mittagessen-Programm
    path("quiz/",views.my_quiz, name="my_quiz"),  # Meine Quizzes
    path("quiz/<int:pk>/take/", views.take_quiz, name="take_quiz"),  # Quiz durchführen
    path("materials/upload/", views.upload_material, name="upload_material"),  # Lernmaterial hochladen
    path("materials/<int:lesson_id>/",views.material_detail, name="material_detail"),  # Lernmaterial anzeigen
    path("contact/",views.contact, name="contact"),  # Kontaktformular
    path("news/", views.news_list, name="news_list"),  # News-Liste
    path("news/<int:pk>/", views.news_detail, name="news_detail"),  # News-Detailseite
    path("post/<int:post_id>/like/", views.like_post, name="like_post"),  # Post liken (wiederholt)
    path('forum/kategorie/<int:kategorie_id>/', views.post_list, name='post_list_by_category'),  # Posts nach Kategorie
    path('library/',views.library,name="library"),  # Bibliothek
    path('sport_fields/',views.sport_fields,name="sport_fields"),  # Sportplätze
    path('buildings/',views.building,name="building"),  # Gebäude
    path('karriere/',views.karriere_view,name="karriere_view"),  # Karriere / Jobs
    path('karriere/<int:pk>/', views.job_detail_view, name='job_detail'),  # Job-Details
    path('announcements/', views.announcement_list, name='announcement_list'),  # Ankündigungen
    path("chat/", views.chat_page, name="chat_page"),  # Chat-Seite
    path("chat/api/", views.gemini_chat, name="gemini_chat"),  # Chat API
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Medien-Dateien im Debug-Modus