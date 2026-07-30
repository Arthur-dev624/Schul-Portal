from django.test import TestCase
from django.contrib.auth.models import User
from myapp.models import *
from django.utils import timezone
from datetime import timedelta
from django.db import IntegrityError
from decimal import Decimal

class BrancheModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.branche = Branche.objects.create(name="Chemie")

    def test_name_field_label(self):
        self.assertEqual(self.branche._meta.get_field('name').verbose_name, 'name')

    def test_name_max_length(self):
        self.assertEqual(self.branche._meta.get_field('name').max_length, 255)

    def test_str_branche(self):
        self.assertEqual(str(self.branche), "Chemie")


class PersonModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='usertest', password='testpassword')
        cls.person = Person.objects.create(user=cls.user, role='student')

    def test_role(self):
        self.assertIn(self.person.role, ['teacher', 'student'])

    def test_str_person(self):
        self.assertEqual(str(self.person), "usertest (student)")

    def test_branch_null(self):
        self.assertIsNone(self.person.branch)

    def test_phone_max_length(self):
        self.assertEqual(self.person._meta.get_field('phone').max_length, 20)


class StudentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='studentuser', password='studentpassword')
        cls.person = Person.objects.create(user=cls.user, role='student')
        cls.student = Student.objects.create(user=cls.user)

    def test_student_str(self):
        self.assertEqual(str(self.student), "studentuser")

    def test_blank(self):
        self.assertEqual(self.student.address, "")
        self.assertIsNone(self.student.birth_date)
        self.assertIsNone(self.student.grade_level)

    def test_student_role(self):
        self.assertEqual(self.student.user.person.role, "student")

class LessonsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user( username='teacheruser',password='teacherpassword')
        cls.lesson = Lesson.objects.create(name='Mathematik')
        cls.person = Person.objects.create(user=cls.user, role='teacher')
        cls.lesson.teachers.add(cls.user)

    def test_length_name(self):
        self.assertEqual(
            self.lesson._meta.get_field('name').max_length,200)

    def test_branch_is_none(self):
        self.assertIsNone(self.lesson.branch)

    def test_teacher_added(self):
        self.assertIn(self.user, self.lesson.teachers.all())

class EnrollmentModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='studentuser',password='testpassword')

   
        cls.student = Student.objects.create(user=cls.user)

        
        cls.lesson = Lesson.objects.create(name='Mathematik')


        cls.enrollment = Enrollment.objects.create(student=cls.student,lesson=cls.lesson )

    def test_enrollment_created(self):
        self.assertEqual(
            Enrollment.objects.count(),
            1
        )

    def test_str_method(self):
        expected = f"{self.student} - {self.lesson}"
        self.assertEqual(str(self.enrollment), expected)

    def test_unique_together(self):
        with self.assertRaises(IntegrityError):
            Enrollment.objects.create(
                student=self.student,
                lesson=self.lesson
            )

    def test_enrolled_at_auto_created(self):
        self.assertIsNotNone(self.enrollment.enrolled_at)


class AnnouncementModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.announcement = Announcement.objects.create(
            text='anntext'
        )

    def test_str_method(self):
        self.assertEqual(
            str(self.announcement),
            "anntext"
        )

    def test_text_max_length(self):
        self.assertEqual(
            self.announcement._meta.get_field('text').max_length,
            255
        )
class GradeModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='studentuser',password='testpassword')

   
        cls.student = Student.objects.create(user=cls.user)

        
        cls.lesson = Lesson.objects.create(name='Mathematik')


        cls.enrollment = Enrollment.objects.create(student=cls.student,lesson=cls.lesson)

class GradeModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.student_user = User.objects.create_user(username='student_1',password='testpassword')
        cls.student = Student.objects.create(user=cls.student_user)
        cls.lesson = Lesson.objects.create(name='Mathematik')

        cls.enrollment = Enrollment.objects.create(student=cls.student,lesson=cls.lesson)


        cls.teacher = User.objects.create_user(username='teacher1',password='test')
        cls.grade = Grade.objects.create(enrollment=cls.enrollment,value=Decimal("80.50"),given_by=cls.teacher)

    def test_grade_created(self):
        self.assertEqual(Grade.objects.count(), 1)

    def test_str_method(self):
        expected = f"{self.student} - {self.lesson}: {self.grade.value}"
        self.assertEqual(str(self.grade), expected)

    def test_decimal_field(self):
        self.assertEqual(self.grade.value, Decimal("80.50"))

    def test_note_blank(self):
        self.assertEqual(self.grade.note, "")

    def test_given_by_nullable(self):
        grade2 = Grade.objects.create(enrollment=self.enrollment,value=Decimal("70.00"))
        self.assertIsNone(grade2.given_by)

class EventModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.event = Event.objects.create(title="Exam",anfang=timezone.now(),audience="teacher")

    def test_title_max_length(self):self.assertEqual(self.event._meta.get_field('title').max_length,200)

    def test_ende_is_nullable(self):
        self.assertIsNone(self.event.ende)

    def test_audience_choice(self):
        self.assertIn(self.event.audience,["teacher", "student", "both"])
    
    def test_event_created(self):
        self.assertEqual(Event.objects.count(), 1)

class KategorieModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.kategorie = Kategorie.objects.create(name="Sport News")

    def test_name_max_length(self):
        self.assertEqual(self.kategorie._meta.get_field('name').max_length,100)

    def test_str_method(self):
        self.assertEqual(str(self.kategorie),"Sport News")

    def test_beschreibung_blank(self):
        self.assertEqual(self.kategorie.beschreibung, "")

    def test_gestaltet_at_auto_created(self):
        self.assertIsNotNone(self.kategorie.gestaltet_at)

class PostModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.user = User.objects.create_user(username="author",password="authorpassword" )

        cls.kategorie = Kategorie.objects.create(name="Studentlife")

        cls.post = Post.objects.create(kategorie=cls.kategorie,content="Testcontent",author=cls.user)

    def test_content_max_length(self):
        self.assertEqual(self.post._meta.get_field('content').max_length,200)

    def test_str_method(self):
        self.assertEqual(str(self.post),"Testcontent")

    def test_image_nullable(self):
        self.assertFalse(self.post.image)

    def test_comment_count(self):
        self.assertEqual(self.post.comment_count(), 0)

    def test_like_count(self):
        self.assertEqual(self.post.like_count(), 0)
    def test_comment_count_after_adding(self):
        Comment.objects.create(post=self.post,commentcontent="Nice!",commentauthor=self.user)

        self.assertEqual(self.post.comment_count(), 1)

class CommentModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="123")
        cls.kategorie = Kategorie.objects.create(name="General")
        cls.post = Post.objects.create(
            kategorie=cls.kategorie,
            content="Test Post",
            author=cls.user
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            commentcontent="Nice Post!",
            commentauthor=cls.user
        )

    def test_str(self):
        expected = f"{self.user.username} - Nice Post!"
        self.assertEqual(str(self.comment), expected)

    def test_ordering(self):
        second_comment = Comment.objects.create(
            post=self.post,
            commentcontent="Second",
            commentauthor=self.user
        )

        comments = Comment.objects.all()
        self.assertEqual(comments.first(), second_comment)

class LikeModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="likeuser", password="123")
        cls.kategorie = Kategorie.objects.create(name="General")
        cls.post = Post.objects.create(
            kategorie=cls.kategorie,
            content="Like Post",
            author=cls.user
        )
        cls.like = Like.objects.create(post=cls.post, user=cls.user)

    def test_str(self):
        expected = f"{self.user.username} liked {self.post.id}"
        self.assertEqual(str(self.like), expected)

    def test_unique_like(self):
        with self.assertRaises(IntegrityError):
            Like.objects.create(post=self.post, user=self.user)
class LunchModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.lunch = Lunch.objects.create(
            lunchname="Pizza",
            preis=10.50,
            inhalte="Cheese, Tomato",
            allergiewarn=True,
            date=timezone.now().date()
        )

    def test_max_length(self):
        self.assertEqual(
            self.lunch._meta.get_field("lunchname").max_length,
            200
        )

    def test_decimal_places(self):
        field = self.lunch._meta.get_field("preis")
        self.assertEqual(field.max_digits, 7)
        self.assertEqual(field.decimal_places, 2)

class QuizModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.quiz = Quiz.objects.create(
            frage="What is 2+2?",
            antwort1="3",
            antwort2="4",
            antwort3="5",
            antwort4="6",
            richtigeantwort="4"
        )

    def test_str(self):
        self.assertEqual(str(self.quiz), "What is 2+2?")

    def test_nullable_fields(self):
        self.assertIsNone(self.quiz.lesson)

class QuizSammlungModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="quizuser", password="123")
        cls.lesson = Lesson.objects.create(name="Math")

        cls.questions_data = {
            "q1": "What is 2+2?",
            "a1": "4"
        }

        cls.quiz_sammlung = Quiz_Sammlung.objects.create(
            lesson=cls.lesson,
            title="Math Quiz",
            questions=cls.questions_data
        )

    def test_json_saved(self):
        self.assertEqual(self.quiz_sammlung.questions["q1"], "What is 2+2?")

    def test_str(self):
        expected = f"Math Quiz ({self.lesson.name})"
        self.assertEqual(str(self.quiz_sammlung), expected)

class QuizVersuchModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="student", password="123")
        cls.quiz = Quiz.objects.create(frage="Test Question")

        cls.versuch = Quiz_Versuch.objects.create(
            quiz=cls.quiz,
            user=cls.user
        )

    def test_auto_now_add(self):
        self.assertIsNotNone(self.versuch.angefangen_at)

    def test_nullable_fields(self):
        self.assertIsNone(self.versuch.beendet_at)
        self.assertIsNone(self.versuch.ergebniss)

    def test_str(self):
        expected = f"{self.user.username} - {self.quiz.frage} - {self.versuch.ergebniss}"
        self.assertEqual(str(self.versuch), expected)

class NewsModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="newsuser", password="123")
        cls.news = News.objects.create(
            titel="School News",
            kurz_text="Short text",
            voll_text="Full text",
            bild="news/test.jpg",
            kategorie="General"
        )

    def test_str(self):
        self.assertEqual(str(self.news), "School News")

    def test_max_length(self):
        self.assertEqual(
            self.news._meta.get_field("titel").max_length,
            200
        )
class SchoolbilderModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.bild = Schoolbilder.objects.create(
            bild="bilder/test.jpg",
            titel="School Image"
        )

    def test_str(self):
        self.assertEqual(str(self.bild), "School Image")

    def test_max_length(self):
        self.assertEqual(
            self.bild._meta.get_field("titel").max_length,
            100
        )

