from builtins import id
from collections import defaultdict
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

def current_page_versions(pages):
    """ returns every page with its latest version """
    pages_with_versions = defaultdict(list)
    for page in pages:
        current_version = (
            PageVersion.objects.filter(page_id=page.id)
            .order_by("-version")
            .values_list("version", flat=True)
            .first()
        )

        pages_with_versions.append({
            "page": page,
            "version": current_version
        })

    return pages_with_versions

def get_blocks_and_layout_region_by_page_id(page_id= int, page_version= int):
    """ gets the CMS Object Page_block and blocks by the given page id """
    # get PageBlock objects which belong to page and order them by position
    page_blocks = PageBlock.objects.filter(page_version_id__page_id_id=page_id,
                                           page_version_id__version=page_version).order_by("position")
    # since PageBlock contains the information about a Block Object,
    # we need the Block Objects which belong to the filtered Page Blocks
    blocks_ids = [pageblock.block_id for pageblock in page_blocks]
    blocks = Block.objects.filter(id__in=blocks_ids)
    # needing also the regions where the Blocks are located in the layout
    regions_ids = [pageblock.layout_region_id for pageblock in page_blocks]
    layout_regions = LayoutRegion.objects.filter(id__in=regions_ids)

    return blocks, layout_regions

def get_functions_by_page_id(page_id= int, page_version= int):
    """ returns the function_types of the Function Objects which are used by the page """
    used_function_types = FunctionBlock.objects.filter(
        block_id__pageBlocks__page_version_id__page_id_id=page_id,
        block_id__pageBlocks__page_version_id__version=page_version
    ).values_list(
        "function_id__function_type",
        flat=True
    ).distinct()

    return list(used_function_types)

def get_media_used_by_page_id(page_id= int, page_version= int):
    """ returns the titles of the Media Objects which are used by the page """
    medium_titles = CmsMedium.objects.filter(
        block_id__pageBlocks__page_version_id__page_id_id=page_id,
        block_id__pageBlocks__page_version_id__version=page_version
    ).values_list(
        "medium_id__title",
        flat=True
    ).distinct()

    return list(medium_titles)

def get_block_ids_used_in_page(page_id= int, given_page_version=int):
    """ returns PageBlocks ordered after position and grouped by layout region which are used by the page """

    current_page_version = PageVersion.objects.filter(
        page_id=page_id,
        version=given_page_version
    )

    page_blocks = PageBlock.objects.filter(
        page_version_id=current_page_version
    ).select_related(
        "block_id",
        "layout_region_id"
    ).order_by(
        "layout_region_id_id",
        "position",
        "id"
    )

    page_blocks_by_region = defaultdict(list)

    for page_block in page_blocks:
        region_key = page_block.layout_region_id.key
        page_blocks_by_region[region_key].append(page_block)

    return dict(page_blocks_by_region)

