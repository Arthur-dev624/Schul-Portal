from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from myapp.models import (
    Person, Student, Lesson, Enrollment, Grade, Event, Kategorie, Post, Comment,
    Quiz, File_Lernmaterial
)
from myapp.forms import (
    RegistrationForm, GradeForm, EventForm, PostForm, CommentForm,
    QuizForm, UploadFileForm, KontaktForm
)
from django.core.files.uploadedfile import SimpleUploadedFile

class AllFormsSimpleTestCase(TestCase):

    def setUp(self):
        # --------------------
        # Users
        # --------------------
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="password123")
        self.teacher = User.objects.create_user(username="teacher", email="teacher@example.com", password="password123")
        
        # Person / role
        self.person_teacher = Person.objects.create(user=self.teacher, role="teacher")
        self.person_student = Person.objects.create(user=self.user, role="student")
        self.student = Student.objects.create(user=self.user)
        
        # Lesson
        self.lesson = Lesson.objects.create(name="Math")
        self.lesson.teachers.add(self.teacher)
        
        # Kategorie
        self.category = Kategorie.objects.create(name="General", beschreibung="Test Kategorie")
        
        # Enrollment
        self.enrollment = Enrollment.objects.create(student=self.student, lesson=self.lesson)
        
        # Post
        self.post = Post.objects.create(content="Test Post", kategorie=self.category, author=self.user)

    # --------------------
    # RegistrationForm
    # --------------------
    def test_registration_form_save_role_student(self):
        form_data = {
          "username": "newstudent",
          "email": "newstudent@example.com",
          "password1": "ComplexPass123!",  # güçlü şifre
          "password2": "ComplexPass123!",
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        
        # Person ve role
        role = "student"
        person = Person.objects.create(user=user, role=role)
        if role == "student":
            student = Student.objects.create(user=user)
        else:
            student = None
        
        self.assertEqual(person.role, "student")
        self.assertIsNotNone(student)
        self.assertEqual(student.user, user)

    # --------------------
    # GradeForm
    # --------------------
    def test_grade_form_save(self):
        form_data = {"value": 95, "note": "Very Good"}
        form = GradeForm(data=form_data)
        self.assertTrue(form.is_valid())
        grade = form.save(commit=False)
        grade.enrollment = self.enrollment
        grade.given_by = self.teacher
        grade.save()
        self.assertEqual(Grade.objects.count(), 1)
        self.assertEqual(grade.value, 95)
        self.assertEqual(grade.enrollment, self.enrollment)
        self.assertEqual(grade.given_by, self.teacher)

    # --------------------
    # EventForm
    # --------------------
    def test_event_form_valid(self):
        form_data = {
            "title": "Test Event",
            "anfang": "2026-02-21T10:00",
            "ende": "2026-02-21T12:00",
            "audience": "teacher",
        }
        form = EventForm(data=form_data)
        self.assertTrue(form.is_valid())

    # --------------------
    # PostForm with image
    # --------------------
        

def test_post_form_save_with_image(self):
    image = SimpleUploadedFile("test.jpg", b"dummycontent", content_type="image/jpeg")
    
    # form data
    form_data = {
        "content": "Post with image",
        "kategorie": self.category.pk  # ForeignKey için PK gönderiyoruz
    }
    form_files = {"image": image}
    
    form = PostForm(data=form_data, files=form_files)
    
    # Hata mesajlarını görmek için:
    if not form.is_valid():
        print(form.errors)
    
    self.assertTrue(form.is_valid())
    
    post = form.save(commit=False)
    post.author = self.user
    post.save()
    self.assertEqual(Post.objects.count(), 2)
    self.assertEqual(post.content, "Post with image")
    self.assertEqual(post.kategorie, self.category)
    # --------------------
    # CommentForm
    # --------------------
    def test_comment_form_save(self):
        form_data = {"commentcontent": "Nice post!"}
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())
        comment = form.save(commit=False)
        comment.post = self.post
        comment.commentauthor = self.user
        comment.save()
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.commentauthor, self.user)

    # --------------------
    # QuizForm
    # --------------------
    def test_quiz_form_save(self):
        form_data = {
            "lesson": self.lesson.id,
            "frage": "Test Frage",
            "antwort1": "A",
            "antwort2": "B",
            "antwort3": "C",
            "antwort4": "D",
            "richtigeantwort": "A"
        }
        form = QuizForm(data=form_data, user=self.teacher)
        self.assertTrue(form.is_valid())
        quiz = form.save()
        self.assertEqual(Quiz.objects.count(), 1)
        self.assertEqual(quiz.lesson, self.lesson)
        self.assertEqual(quiz.richtigeantwort, "A")

    # --------------------
    # UploadFileForm
    # --------------------
    def test_upload_file_form_save(self):
        file_content = b"Test file content"
        uploaded_file = SimpleUploadedFile("testfile.pdf", file_content, content_type="application/pdf")
        form_data = {
            "lesson": self.lesson.id,
            "title": "Test File",
            "description": "File description"
        }
        form_files = {"file": uploaded_file}
        form = UploadFileForm(data=form_data, files=form_files, user=self.teacher)
        self.assertTrue(form.is_valid())
        file_obj = form.save()
        self.assertEqual(File_Lernmaterial.objects.count(), 1)
        self.assertEqual(file_obj.title, "Test File")
        self.assertEqual(file_obj.lesson, self.lesson)

    # --------------------
    # KontaktForm
    # --------------------
    def test_kontakt_form_valid(self):
        form_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "subject": "Hello",
            "text": "This is a test message"
        }
        form = KontaktForm(data=form_data)
        self.assertTrue(form.is_valid())