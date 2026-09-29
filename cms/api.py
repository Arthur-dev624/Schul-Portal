from builtins import id
from collections import defaultdict
from tokenize import String

from django.db import transaction
from django.db.models import Q, Exists, OuterRef, When, IntegerField, FloatField, Count, ExpressionWrapper, Case, Value, F, Prefetch
from google.genai._gaos.utils import values
from pip._internal.commands import index
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
    pages_with_versions = []
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
        mediumBlocks__block_id__pageBlocks__page_version_id__page_id_id=page_id,
        mediumBlocks__block_id__pageBlocks__page_version_id__version=page_version
    ).values_list(
        "title",
        flat=True
    ).distinct()

    return list(medium_titles)

def get_page_block_used_in_page(page_id= int, given_page_version=int):
    """ returns PageBlocks ordered after position and grouped by layout region which are used by the page """

    current_page_version = PageVersion.objects.get(
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

def get_layout_regions_of_page(page_id= int):
    """ returns the layout regions of the layout used by the page"""
    page = Page.objects.get(id=page_id)
    layout_regions = LayoutRegion.objects.filter(
        layout_id=page.layout_id.id
    )

    return layout_regions

def get_all_media():
    """ returns all media """
    media = CmsMedium.objects.all()
    return media

@transaction.atomic
def create_header_block(header_text = String, level = int, header_alignment = String,
                        block_type = String, layout_region = LayoutRegion, page_version = PageVersion):
    """ creates a header block with PageBlock """
    if header_text is None or header_alignment is None or level is None or block_type is None:
        raise ValueError("Alle Werte müssen ausgefüllt sein")
    else:
        position = (
            PageBlock.objects.filter(
                page_version_id=page_version,
                layout_region_id=layout_region
            ).count() + 1
        )

        header_block = Block.objects.create(
            block_type=block_type,
            config={
                "text": header_text,
                "level": level,
                "alignment": header_alignment,
            }
        )

        page_block = PageBlock.objects.create(
            page_version_id=page_version,
            block_id=header_block,
            layout_region_id=layout_region,
            position=position
        )

        return page_block

@transaction.atomic
def create_text_block(text = String, text_alignment = String,
                      block_type = String, layout_region = LayoutRegion, page_version = PageVersion):
    """ creates a text block with PageBlock """
    if text is None or text_alignment is None or block_type is None:
        raise ValueError("Alle Werte müssen ausgefüllt sein")
    else:
        position = (
                PageBlock.objects.filter(
                    page_version_id=page_version,
                    layout_region_id=layout_region
                ).count() + 1
        )

        text_block = Block.objects.create(
            block_type=block_type,
            config={
                "text": text,
                "alignment": text_alignment,
            }
        )

        page_block = PageBlock.objects.create(
            page_version_id=page_version,
            block_id=text_block,
            layout_region_id=layout_region,
            position=position
        )

        return page_block

@transaction.atomic
def create_image_block(caption = String, width = String, height = String,
                       image_alignment = String, media_object = CmsMedium, block_type = String,
                       layout_region = LayoutRegion, page_version = PageVersion):
    """ creates an image block with PageBlock and BlockMedium """
    if (caption is None or width is None or height is None or
            image_alignment is None or media_object is None or block_type is None):
        raise ValueError("Alle Werte müssen ausgefüllt sein")
    else:
        position = (
                PageBlock.objects.filter(
                    page_version_id=page_version,
                    layout_region_id=layout_region
                ).count() + 1
        )

        image_block = Block.objects.create(
            block_type=block_type,
            config={
                "caption": caption,
                "width": width,
                "height": height,
                "alignment": image_alignment
            }
        )

        page_block = PageBlock.objects.create(
            page_version_id=page_version,
            block_id=image_block,
            layout_region_id=layout_region,
            position=position
        )

        BlockMedium.objects.create(
            block_id=image_block,
            medium_id=media_object,
            position=1
        )

        return page_block

@transaction.atomic
def create_button_block(button_text = String, url = String, button_style = String, block_type = String,
                        layout_region = LayoutRegion, page_version = PageVersion):
    """ creates a button block and PageBlock """
    if button_text is None or url is None or button_style is None or block_type is None:
        raise ValueError("Alle Werte müssen ausgefüllt sein")
    else:
        position = (
                PageBlock.objects.filter(
                    page_version_id=page_version,
                    layout_region_id=layout_region
                ).count() + 1
        )

        button_block = Block.objects.create(
            block_type=block_type,
            config={
                "text": button_text,
                "style": button_style,
                "url": url
            }
        )

        PageBlock.objects.create(
            page_version_id=page_version,
            block_id=button_block,
            layout_region_id=layout_region,
            position=position
        )

def update_header_block(header_text = String, level = int, header_alignment = String,
                        selected_page_block = PageBlock, page_version = PageVersion):
    """ updates header block with PageBlock and config """
    # if all passed values of form are None return Error
    if header_text is None and level is None and header_alignment is None:
        raise ValueError("Mindestens ein Wert muss ausgefüllt sein")
    else:
        values = [header_text, header_alignment, level]

        for index, value in enumerate(values):
            if index == 0 and value is not None:
                selected_page_block.block_id.config["text"] = header_text
            elif index == 1 and value is not None:
                selected_page_block.block_id.config["alignment"] = header_alignment
            elif index == 2 and value is not None:
                selected_page_block.block_id.config["level"] = level

        selected_page_block.page_version_id = page_version
        selected_page_block.block_id.save()
        selected_page_block.save()

def update_text_block(text = String, text_alignment = String, selected_page_block = PageBlock,
                      page_version = PageVersion,):
    """ updates text block with PageBlock and config """
    # if all passed values of form are None return Error
    if text is None and text_alignment is None:
        raise ValueError("Mindestens ein Wert muss ausgefüllt sein")
    else:
        values = [text, text_alignment]

        for index, value in enumerate(values):
            if index == 0 and value is not None:
                selected_page_block.block_id.config["text"] = text
            elif index == 1 and value is not None:
                selected_page_block.block_id.config["alignment"] = text_alignment

        selected_page_block.page_version_id = page_version
        selected_page_block.block_id.save()
        selected_page_block.save()

def update_image_block(caption = String, width = String, height = String, image_alignment = String,
                       media_object = CmsMedium, page_version = PageVersion, selected_page_block = PageBlock):
    """ updates image block with PageBlock, BlockMedium and config """
    # if all passed Values of Form are None return Error
    if (caption is None and width is None and height is None and image_alignment is None
        and media_object is None):
        raise ValueError("Mindestens ein Wert muss ausgefüllt sein")
    else:
        values = [caption, width, height, image_alignment, media_object]

        for index, value in enumerate(values):
            if index == 0 and value is not None:
                selected_page_block.block_id.config["caption"] = caption
            elif index == 1 and value is not None:
                selected_page_block.block_id.config["width"] = width
            elif index == 2 and value is not None:
                selected_page_block.block_id.config["height"] = height
            elif index == 3 and value is not None:
                selected_page_block.block_id.config["alignment"] = image_alignment
            elif index == 4 and value is not None:
                # medien die vom block verwendet werden
                selected_block_medium = BlockMedium.objects.filter(
                    block_id=selected_page_block.block_id
                ).order_by("id").first()

                # wenn bereits ein Medium vorhanden ist, aktualisieren
                if selected_block_medium is not None:
                    selected_block_medium.medium_id = media_object
                    selected_block_medium.save(
                        update_fields=["medium_id"]
                    )

                # wenn noch kein Medium vorhanden ist, neues erstellen
                else:
                    BlockMedium.objects.create(
                        block_id=selected_page_block.block_id,
                        medium_id=media_object,
                        position=1
                    )

        selected_page_block.page_version_id = page_version
        selected_page_block.block_id.save()
        selected_page_block.save()

def update_button_block(button_text = String, url = String, button_style = String, selected_page_block = PageBlock,
                        page_version = PageVersion):
    """ updates button block with PageBlock and config """
    # if all passed Values of Form are None return Error
    if button_text is None and url is None and button_style is None:
        raise ValueError("Mindestens ein Wert muss ausgefüllt sein")
    else:
        values = [button_text, url, button_style]

        for index, value in enumerate(values):
            if index == 0 and value is not None:
                selected_page_block.block_id.config["text"] = button_text
            elif index == 1 and value is not None:
                selected_page_block.block_id.config["url"] = url
            elif index == 2 and value is not None:
                selected_page_block.block_id.config["style"] = button_style

        selected_page_block.page_version_id = page_version
        selected_page_block.block_id.save()
        selected_page_block.save()
