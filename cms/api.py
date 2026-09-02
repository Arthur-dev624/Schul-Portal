from builtins import id
from tokenize import String

from django.db.models import Q, Exists, OuterRef, When, IntegerField, FloatField, Count, ExpressionWrapper, Case, Value, F, Prefetch
from pyasn1.type.univ import Null

from cms.models import *
from cms.models import PageBlock
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
    count = Page.objects.filter(status=True).count()
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

def get_blocks_and_layout_region_by_page_id(page_id= int):
    """ gets the CMS Object Page_block and blocks by the given page id """
    # get PageBlock objects which belong to page and order them by position
    page_blocks = PageBlock.objects.filter(page_version_id__page_id_id=page_id).order_by("position")
    # since PageBlock contains the information about a Block Object,
    # we need the Block Objects which belong to the filtered Page Blocks
    blocks_ids = [pageblock.block_id for pageblock in page_blocks]
    blocks = Block.objects.filter(id__in=blocks_ids)
    # needing also the regions where the Blocks are located in the layout
    regions_ids = [pageblock.layout_region_id for pageblock in page_blocks]
    layout_regions = LayoutRegion.objects.filter(id__in=regions_ids)

    return blocks, layout_regions


