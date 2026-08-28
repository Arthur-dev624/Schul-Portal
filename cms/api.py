from builtins import id
from tokenize import String

from django.db.models import Q, Exists, OuterRef, When, IntegerField, FloatField, Count, ExpressionWrapper, Case, Value, F, Prefetch
from pyasn1.type.univ import Null

from cms.models import *
from myapp.models import Person, User

def _get_person(user) -> Person:
    """ Given a Person object, gets the CMS Person object from the request """
    try:
        user = User.objects.get(id=user.id)
    except User.DoesNotExist:
        raise PermissionError("User does not exist")
    return user.person

def _get_user(person) -> User:
    """ Given a Person object, gets the User object from the request """
    try:
        person = Person.objects.get(id=person.id)
    except Person.DoesNotExist:
        raise PermissionError("Person does not exist")
    return person.user

def count_pages():
    """ gets the CMS Pages count """
    count = Page.objects.all().count()
    return count

def count_releases():
    """ gets the released pages count """
    count = Publication.objects.all().count()
    return count

def count_drafts():
    """ gets the drafts count """
    count = Page.objects.filter(status=False).count()
    return count

def count_media():
    """ gets the media count """
    count = CmsMedium.objects.all().count()
    return count

def search_pages_with_title(title = String):
    """ gets the CMS Pages of searched title """
    pages = Page.objects.all()
    if title:
        pages = pages.filter(title__icontains=title)

    return pages