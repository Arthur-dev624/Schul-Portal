🎓 SaarSchool – Django Schul-Website Projekt
📌 Projektübersicht

SaarSchool ist eine dynamische, mehrsprachige Schul-Website, entwickelt mit dem Django Framework.
Dieses Projekt wurde im Rahmen einer Universitätsaufgabe erstellt und demonstriert, wie man eine datenbankgestützte Webanwendung mit Internationalisierung und Benutzerverwaltung erstellt.

Die Plattform umfasst:

🏠 Startseite – Zeigt aktuelle Nachrichten und Ankündigungen dynamisch an.

💼 Karriereseite – Stellenangebote, verwaltet über das Django Admin Panel.

🏫 Schulpräsentation – Geschichte, Team, Gebäude und Einrichtungen.

📚 Bibliothek & Sporteinrichtungen – Informationsseiten mit strukturierten Inhalten.

📩 Kontaktformular – Benutzer können Nachrichten direkt senden.

👤 Benutzerregistrierung & Authentifizierung – Schüler und Lehrer.

🌍 Mehrsprachige Unterstützung – Deutsch / Englisch.

⚙️ Django Admin Panel – Für die Inhaltsverwaltung.

🤖 AI-Bot Integration – Mit Gemini API für interaktive Unterstützung.

🛠 Verwendete Technologien

Backend:

Python 3

Django

Frontend:

HTML5

CSS3

Bootstrap / MDB UI Kit

JavaScript

Datenbank:

SQLite (Standard für Entwicklung)

PostgreSQL empfohlen für Produktion

Internationalisierung:

Django i18n-System

Optional: django-modeltranslation für mehrsprachige Modellfelder

AI-Integration:

Gemini API – AI-Chatbot für schulbezogene Anfragen

📂 Projektstruktur
djangoschulhomepage/
│
├── manage.py
├── db.sqlite3
├── schoolwebsite/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
└── myapp/
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── admin.py
    ├── templates/
    │   └── school/
    ├── tests
    |--- static/
    └── locale/

🚀 Installationsanleitung

1️⃣ Voraussetzungen
Stellen Sie sicher, dass folgende Software installiert ist:

Python 3.x

pip

Versionen prüfen:

python --version
pip --version

2️⃣ Repository klonen

git clone https://github.com/yourusername/djangoschulhomepage.git
cd djangoschulhomepage

3️⃣ Virtuelle Umgebung erstellen

python -m venv env

Aktivieren:

Windows: env\Scripts\activate

Mac/Linux: source env/bin/activate

4️⃣ Abhängigkeiten installieren

pip install -r requirements.txt

Wenn keine requirements.txt vorhanden ist:

pip install django

5️⃣ Migrationen anwenden

python manage.py makemigrations
python manage.py migrate

6️⃣ Superuser erstellen

python manage.py createsuperuser
Username und Passwort eingeben. Das ist wichtig beim einloggen auf Admin.py.

7️⃣ Entwicklungsserver starten

python manage.py runserver

Öffnen im Browser:

Startseite: http://127.0.0.1:8000/home/

Admin-Panel: http://127.0.0.1:8000/admin/

🌍 Mehrsprachige Unterstützung

Statische Texte in Templates:
Oben -> {% load i18n %}

{% trans "Dein Text hier" %}

Nach Bearbeitung der Übersetzungen:

django-admin makemessages -l de
Danach musst du die Worter in django.po ubersetzen
ZB:
#: myapp/templates/school/my_lessons.html:199
msgid "Lesson:"
msgstr ""   ---> hier das ubzersetzte Wort schreiben.

Du musst die ubersetzten Wortern mit 
django-admin compilemessages 
bestatigen.

Für dynamische Datenbankfelder (z. B. Jobtitel, Beschreibung) unterstützt django-modeltranslation mehrsprachige Inhalte.

🤖 AI-Bot Integration (Gemini API)

Die Website enthält einen AI-gestützten Assistenten mithilfe der Gemini API.

Schüler und Besucher können Fragen stellen und sich beraten lassen 

💡 Einrichtung:

Gemini API Key besorgen

Registrieren Sie sich für ein Gemini API Konto auf Google AI Studio.

Erstellen Sie einen API-Key (geheim halten!).

Gemini API Client installieren (für Python SDK)

pip install gemini-api

API-Key in Django Settings einfügen

# settings.py
GEMINI_API_KEY = 'dein_api_schluessel_hier'
CONTACT_RECIPIENT_EMAIL="<empfangsadresse@example.com>"
EMAIL_HOST_USER = "yourmail@gmail.com" 
EMAIL_HOST_PASSWORD = "app password"   # write the gmail app password

Hinweise:

Jeder Entwickler kann seinen eigenen API-Key nutzen.

Rate-Limits und mögliche Kosten hängen vom Gemini-Konto ab.

Beispiel für Views (ai_chat):

from gemini_api import GeminiClient
from django.conf import settings
from django.shortcuts import render

client = GeminiClient(api_key=settings.GEMINI_API_KEY)

def ai_chat(request):
    antwort = None
    if request.method == "POST":
        frage = request.POST.get("frage")
        antwort = client.ask(frage)
    return render(request, "school/ai_chat.html", {"antwort": antwort})

Beispiel für Template:

<form method="post">
  {% csrf_token %}
  <input type="text" name="frage" placeholder="Stellen Sie Ihre Frage hier">
  <button type="submit">Senden</button>
</form>

{% if antwort %}
  <div class="alert alert-info mt-2">{{ antwort }}</div>
{% endif %}

👥 Benutzerrollen

Schüler

Lehrer

Die Authentifizierung erfolgt über Djangos eingebautes Auth-System.

⚙️ Funktionen
🔒 Admin-Seite:
![image url](https://github.com/Boralpturkoglu/Schoolprojekt/blob/11e43ce4949fce6e16e8c551f0178b52a507cf0a/Screenshot%202026-03-26%20at%2014.51.44.png)
Hier konnen Sie alle Modelle verwalten
 
🏠 Startseite:
![image url](https://github.com/Boralpturkoglu/Schoolprojekt/blob/11e43ce4949fce6e16e8c551f0178b52a507cf0a/Screenshot%202026-03-26%20at%2013.40.47.png)


Zeigt dynamisch aktuelle Nachrichten und Ankündigungen.

💼 Karriereseite:
![image url](https://github.com/Boralpturkoglu/Schoolprojekt/blob/11e43ce4949fce6e16e8c551f0178b52a507cf0a/Screenshot%202026-03-26%20at%2013.44.17.png)

Stellenangebote verwaltet über Django Admin.

👨‍🏫 Teamseite:
![image url](https://github.com/Boralpturkoglu/Schoolprojekt/blob/11e43ce4949fce6e16e8c551f0178b52a507cf0a/Screenshot%202026-03-26%20at%2014.39.55.png)

Vorstellung von Lehrern und Verwaltungsmitarbeitern.

📚 Bibliothek & Einrichtungen:
![image url](https://github.com/Boralpturkoglu/Schoolprojekt/blob/11e43ce4949fce6e16e8c551f0178b52a507cf0a/Screenshot%202026-03-26%20at%2015.33.22.png)

Informationsseiten mit strukturiertem Inhalt.

📩 Kontaktformular:
![image url](https://github.com/Boralpturkoglu/Schoolprojekt/blob/11e43ce4949fce6e16e8c551f0178b52a507cf0a/Screenshot%202026-03-26%20at%2014.47.20.png )

Benutzer können direkt Nachrichten an die Schule senden.

🤖 AI-Bot Integration:
![image url](https://github.com/Boralpturkoglu/Schoolprojekt/blob/11e43ce4949fce6e16e8c551f0178b52a507cf0a/Screenshot%202026-03-26%20at%2014.44.50.png)

Beispiele:
![image url](https://github.com/Boralpturkoglu/Schoolprojekt/blob/11e43ce4949fce6e16e8c551f0178b52a507cf0a/Screenshot%202026-03-26%20at%2015.30.48.png)

![umage url](https://github.com/Boralpturkoglu/Schoolprojekt/blob/11e43ce4949fce6e16e8c551f0178b52a507cf0a/Screenshot%202026-03-26%20at%2015.31.24.png)

Interaktive Unterstützung via Gemini API.

Beantwortet FAQs und hilft Benutzern bei Anfragen.

🔒 Entwicklungsnotizen

DEBUG = True für Entwicklung

DEBUG = False für Produktion

Nie SECRET_KEY öffentlich freigeben

Verwenden Sie PostgreSQL in Produktion

## License
![image url](https://github.com/Boralpturkoglu/Schoolprojekt/blob/11e43ce4949fce6e16e8c551f0178b52a507cf0a/Screenshot%202026-03-26%20at%2015.27.34.png)

This project is licensed under the MIT License - see the [LICENSE] file for details.
Kostenlos nutzbar und modifizierbar.
//////////////////////////////////


