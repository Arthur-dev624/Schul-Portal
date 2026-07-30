from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from myapp.models import *
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.contrib.auth.models import User
from unittest.mock import patch
import json



class ViewTests(TestCase):

    def setUp(self):
        self.client = Client()

        # Users
        self.teacher_user = User.objects.create_user(
            username="teacher",
            password="StrongPass123!"
        )
        self.student_user = User.objects.create_user(
            username="student",
            password="StrongPass123!"
        )

        # Roles
        self.teacher_person = Person.objects.create(
            user=self.teacher_user,
            role="teacher"
        )
        self.student_person = Person.objects.create(
            user=self.student_user,
            role="student"
        )

        self.student = Student.objects.create(user=self.student_user)

        # Lesson
        self.lesson = Lesson.objects.create(name="Math")
        self.lesson.teachers.add(self.teacher_user)

        # Enrollment
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            lesson=self.lesson
        )

        # Category
        self.category = Kategorie.objects.create(
            name="General",
            beschreibung="Test"
        )

        # Post
        self.post = Post.objects.create(
            content="Test Post",
            author=self.teacher_user,
            kategorie=self.category
        )


    # HOME
   
    def test_home_view(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    
    # DASHBOARD REDIRECT

    def test_dashboard_redirect_teacher(self):
        self.client.login(username="teacher", password="StrongPass123!")
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(response, reverse("teacher_dashboard"))

    def test_dashboard_redirect_student(self):
        self.client.login(username="student", password="StrongPass123!")
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(response, reverse("student_dashboard"))

   
    # FORBIDDEN TEST

    def test_student_cannot_add_grade(self):
        self.client.login(username="student", password="StrongPass123!")
        response = self.client.get(
            reverse("add_grade", args=[self.enrollment.id])
        )
        self.assertEqual(response.status_code, 403)


    # TEACHER ADD GRADE

    def test_teacher_can_add_grade(self):
        self.client.login(username="teacher", password="StrongPass123!")

        response = self.client.post(
            reverse("add_grade", args=[self.enrollment.id]),
            {
                "value": 100,
                "note": "Excellent"
            }
        )

        self.assertRedirects(response, reverse("teacher_dashboard"))
        self.assertEqual(Grade.objects.count(), 1)


    # CREATE POST
   
    def test_create_post(self):
        self.client.login(username="teacher", password="StrongPass123!")

        response = self.client.post(
            reverse("create_post"),
            {
                "content": "New Post",
                "kategorie": self.category.id
            }
        )

        self.assertRedirects(response, reverse("post_list"))
        self.assertEqual(Post.objects.count(), 2)

    # LIKE POST

    def test_like_post(self):
        self.client.login(username="student", password="StrongPass123!")

        response = self.client.get(
            reverse("like_post", args=[self.post.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.post.likes.count(), 1)

   
    # ENROLL LESSON

    def test_enroll_lesson(self):
        new_lesson = Lesson.objects.create(name="Physics")

        self.client.login(username="student", password="StrongPass123!")
        response = self.client.get(
            reverse("enroll_lesson", args=[new_lesson.id])
        )

        self.assertRedirects(response, reverse("my_lessons"))
        self.assertTrue(
            Enrollment.objects.filter(
                student=self.student,
                lesson=new_lesson
            ).exists()
        )

   
    # CONTACT EMAIL

    def test_contact_view_sends_email(self):
        response = self.client.post(
            reverse("contact"),
            {
                "name": "John",
                "email": "john@test.com",
                "subject": "Test",
                "message": "Hello"
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Test", mail.outbox[0].subject)

    
    # EVENT JSON LIST
  
    def test_event_list_json(self):
        Event.objects.create(
            title="Meeting",
            anfang="2026-02-21T10:00:00Z",
            ende="2026-02-21T12:00:00Z",
            audience="both"
        )

        self.client.login(username="teacher", password="StrongPass123!")
        response = self.client.get(reverse("event_list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")


    # ADD QUIZ (Teacher only)

    def test_teacher_can_add_quiz(self):
        self.client.login(username="teacher", password="StrongPass123!")

        response = self.client.post(
            reverse("add_quiz"),
            {
                "lesson": self.lesson.id,
                "frage": "2+2?",
                "antwort1": "3",
                "antwort2": "4",
                "antwort3": "5",
                "antwort4": "6",
                "richtigeantwort": "4",
            }
        )

        self.assertRedirects(response, reverse("teacher_dashboard"))
        self.assertEqual(Quiz.objects.count(), 1)

    def test_student_cannot_add_quiz(self):
        self.client.login(username="student", password="StrongPass123!")
        response = self.client.get(reverse("add_quiz"))
        self.assertEqual(response.status_code, 403)


    # MY QUIZ (Student only)
    
    def test_student_can_view_my_quiz(self):
        quiz = Quiz.objects.create(
            lesson=self.lesson,
            frage="2+2?",
            antwort1="3",
            antwort2="4",
            antwort3="5",
            antwort4="6",
            richtigeantwort="4",
        )

        self.client.login(username="student", password="StrongPass123!")
        response = self.client.get(reverse("my_quiz"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "2+2?")


    # TAKE QUIZ

    def test_take_quiz_correct_answer(self):
        quiz = Quiz.objects.create(
            lesson=self.lesson,
            frage="2+2?",
            antwort1="3",
            antwort2="4",
            antwort3="5",
            antwort4="6",
            richtigeantwort="4",
        )

        self.client.login(username="student", password="StrongPass123!")

        response = self.client.post(
            reverse("take_quiz", args=[quiz.id]),
            {"answer": "4"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Quiz_Versuch.objects.count(), 1)
        self.assertEqual(
            Quiz_Versuch.objects.first().ergebniss, 1
        )

    def test_take_quiz_wrong_answer(self):
        quiz = Quiz.objects.create(
            lesson=self.lesson,
            frage="2+2?",
            antwort1="3",
            antwort2="4",
            antwort3="5",
            antwort4="6",
            richtigeantwort="4",
        )

        self.client.login(username="student", password="StrongPass123!")

        self.client.post(
            reverse("take_quiz", args=[quiz.id]),
            {"answer": "3"}
        )

        self.assertEqual(
            Quiz_Versuch.objects.first().ergebniss, 0
        )


    # UPLOAD MATERIAL
  
    def test_teacher_can_upload_material(self):
        self.client.login(username="teacher", password="StrongPass123!")

        test_file = SimpleUploadedFile(
            "test.pdf",
            b"file_content",
            content_type="application/pdf"
        )

        response = self.client.post(
            reverse("upload_material"),
            {
                "lesson": self.lesson.id,
                "title": "Test File",
                "description": "Test Desc",
                "file": test_file
            }
        )

        self.assertRedirects(response, reverse("teacher_dashboard"))
        self.assertEqual(File_Lernmaterial.objects.count(), 1)

    def test_student_cannot_upload_material(self):
        self.client.login(username="student", password="StrongPass123!")
        response = self.client.get(reverse("upload_material"))
        self.assertEqual(response.status_code, 403)


    # MATERIAL DETAIL PERMISSION

    def test_student_can_view_enrolled_material(self):
        self.client.login(username="student", password="StrongPass123!")

        response = self.client.get(
            reverse("material_detail", args=[self.lesson.id])
        )

        self.assertEqual(response.status_code, 200)

    def test_student_cannot_view_unenrolled_material(self):
        new_lesson = Lesson.objects.create(name="Chemistry")

        self.client.login(username="student", password="StrongPass123!")

        response = self.client.get(
            reverse("material_detail", args=[new_lesson.id])
        )

        self.assertEqual(response.status_code, 403)
