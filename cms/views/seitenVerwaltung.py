import json
import re
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from cms.api import search_pages_with_title, get_page_block_used_in_page, get_functions_by_page_id, get_media_used_by_page_id, get_blocks_and_layout_region_by_page_id, current_page_versions, get_layout_regions_of_page, get_all_media, create_header_block, create_text_block, create_image_block, create_button_block, update_header_block, update_text_block, update_image_block, update_button_block
from cms.models import Design, Layout, Page, PageVersion, PageBlock, Block, BlockMedium, CmsMedium
from cms.views.navigationVerwaltung import get_visible_navigation
from django.utils.text import slugify
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.contrib import messages
from django.db import transaction

@login_required
def to_seiten_main(request):
    username = request.user.username
    pages = Page.objects.all().order_by("-id")
    page_entries = current_page_versions(pages)
    context = {
        "username": username,
        "page_entries": page_entries
    }
    return render(request, "seitenVerwaltung.html", context)

@login_required
def seiten_search(request):
    query = request.GET.get("q", "").strip()

    pages = search_pages_with_title(query).order_by("-id")

    return render(
        request,
        "seitenVerwaltung.html",
        {
            "username": request.user.username,
            "query": query,
            "page_entries": current_page_versions(pages),
        },
    )

@login_required
def seite_erstellen(request):
    error = None
    layouts = Layout.objects.all()
    designs = Design.objects.all()

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        slug = request.POST.get("slug", "").strip()
        layout_id = request.POST.get("layout_id")
        design_id = request.POST.get("design_id")

        if not title or not slug or not layout_id or not design_id:
            error = "Bitte Titel, Slug, Layout und Design ausfüllen."
        else:
            try:
                layout = Layout.objects.get(id=layout_id)
                design = Design.objects.get(id=design_id)
            except (Layout.DoesNotExist, Design.DoesNotExist):
                error = "Das ausgewählte Layout oder Design existiert nicht."
            else:
                page = Page.objects.create(
                    title=title,
                    slug=slugify(slug),
                    layout_id=layout,
                    design_id=design,
                    created_by=request.user,
                )

                PageVersion.objects.create(
                    page_id=page,
                    created_by=request.user,
                    version=1,
                )

                return redirect("to_seiten_main")

    return render(request, "seiteErstellen.html", {
        "username": request.user.username,
        "layouts": layouts,
        "designs": designs,
        "error": error,
    })

# gibt layout_regions zurück, mit den Layoutregionen der zu bearbeitenden page,
# sowie regions_with_blocks als Dictionary mit {"region": LayoutRegion, "blocks": [PageBlock]},
# also eine Layoutregion der page mit ihren dazugehörigen Blöcken
def _build_regions_with_blocks(page_id, version):
    page_blocks_by_region = get_page_block_used_in_page(page_id, version)
    layout_regions = get_layout_regions_of_page(page_id)
    regions_with_blocks = []

    for layout_region in layout_regions:
        regions_with_blocks.append({
            "region": layout_region,
            "blocks": page_blocks_by_region.get(layout_region.key, []),
        })

    return layout_regions, regions_with_blocks

# gibt eine Liste counts zurück, wie viele PageBlock-Objekte für jede Layoutregion einer page zugewiesen sind,
# dabei wird die Id der Layoutregion verwendet, also id: PageBlock-anzahl, damit kann die Id im HTML-Formuar verwendet werden,
def _build_region_position_counts(page_version, layout_regions):
    counts = {}

    for layout_region in layout_regions:
        counts[str(layout_region.id)] = PageBlock.objects.filter(
            page_version_id=page_version,
            layout_region_id=layout_region,
        ).count()

    return counts

# gibt ein Tuple zurück mit (1, max PageBlock-Objekte innerhalb der Layoutregion, in der sich der aktuell ausgewählte,
# PageBlock befindet + 1)
def _build_position_choices(page_version, page_block):
    block_count = PageBlock.objects.filter(
        page_version_id=page_version,
        layout_region_id=page_block.layout_region_id,
    ).count()

    return range(1, block_count + 1)

# positioniert PageBlock neu, nachdem Position und/oder Layoutregion eines PageBlocks geändert worden ist
def _reorder_page_blocks(page_version, page_block, new_layout_region, new_position):
    """
        bei änderung der position eines Blocks in einer Layoutregion:
        alle Blöcke müssen neue positionen bekommen, abhängig wo neuer Block eingefügt worden ist /
        bei änderung der Layoutregion: Blöcke innerhalb alten Layoutregion und der neuen Layoutregion müssen neue Positionen bekommen,
        abhängig wo der Block eingefügt worden ist

         page_version: Seitenversion auf der gearbeitet wird
         page_block: Der Block, der verschoben wird
         new_layout_region: neue Layoutregion
         new_position: neue Position
    """

    # alte Layoutregion des Blocks speichern
    old_layout_region = page_block.layout_region_id

    # prüfen, ob der Block in derselben Layoutregion bleibt
    if old_layout_region.id == new_layout_region.id:
        # siblings = Liste von allen PageBlocks innerhalb der Layoutregion, außer des PageBlocks der verschoben wird, geordnet nach
        # position und id
        siblings = list(PageBlock.objects.filter(
            page_version_id=page_version,
            layout_region_id=new_layout_region,
        ).exclude(id=page_block.id).order_by("position", "id"))

        # insert_index speichert die Stelle an die, der PageBlock verschoben wird
        insert_index = max(0, min(new_position - 1, len(siblings)))
        # PageBlock an dieser Stelle in der Liste einfügen
        siblings.insert(insert_index, page_block)

        # Blöcke werden neu durchnummeriert
        for position, sibling in enumerate(siblings, start=1):
            sibling.position = position
            sibling.layout_region_id = new_layout_region
            sibling.save(update_fields=["position", "layout_region_id"])

        return

    # old_siblings = Liste mit allen alten PageBlocks, die in der alten Layoutregion liegen, außer dem PageBlock der verschoben wird
    old_siblings = list(PageBlock.objects.filter(
        page_version_id=page_version,
        layout_region_id=old_layout_region,
    ).exclude(id=page_block.id).order_by("position", "id"))

    # PageBlocks in alter Layoutregion neu durchnummerieren, da ein Block nun fehlt
    for position, sibling in enumerate(old_siblings, start=1):
        sibling.position = position
        sibling.save(update_fields=["position"])

    # Liste mit PageBlocks aus der neuen Layoutregion, außer dem zu verschiebenden PageBlock
    new_siblings = list(PageBlock.objects.filter(
        page_version_id=page_version,
        layout_region_id=new_layout_region,
    ).exclude(id=page_block.id).order_by("position", "id"))

    insert_index = max(0, min(new_position - 1, len(new_siblings)))
    # verschobene Block bekommt die neue Layoutregion
    page_block.layout_region_id = new_layout_region
    new_siblings.insert(insert_index, page_block)

    for position, sibling in enumerate(new_siblings, start=1):
        sibling.position = position
        sibling.layout_region_id = new_layout_region
        sibling.save(update_fields=["position", "layout_region_id"])

def _get_selected_layout_region(request, layout_regions):
    raw_id = request.POST.get("layout_region_id")

    try:
        region_id = int(raw_id)
    except (TypeError, ValueError):
        raise ValueError("Bitte eine gültige Layoutregion auswählen.")

    region = layout_regions.filter(id=region_id).first()

    if region is None:
        raise ValueError(
            "Die ausgewählte Layoutregion gehört nicht zum Layout dieser Seite."
        )

    return region


def _read_block_form(request, block_type):
    """
    Liest und validiert die zum Blocktyp gehörenden Eingaben.
    Gibt nur die Daten dieses Blocktyps zurück.
    """

    if block_type in (
        Block.BlockType.HEADING,
        Block.BlockType.TEXT,
        Block.BlockType.BUTTON,
    ):
        text = request.POST.get("text", "").strip()

        if not text:
            raise ValueError("Bitte einen Text eingeben.")

    if block_type in (
        Block.BlockType.HEADING,
        Block.BlockType.TEXT,
    ):
        alignment = request.POST.get("alignment")

        if alignment not in {"left", "right", "center", "justify"}:
            raise ValueError("Ungültige Textausrichtung.")

    if block_type == Block.BlockType.HEADING:
        try:
            level = int(request.POST.get("level"))
        except (TypeError, ValueError):
            raise ValueError("Bitte eine gültige Überschriftenebene eingeben.")

        if not 1 <= level <= 6:
            raise ValueError("Die Überschriftenebene muss zwischen 1 und 6 liegen.")

        return {
            "text": text,
            "level": level,
            "alignment": alignment,
        }

    if block_type == Block.BlockType.TEXT:
        return {
            "text": text,
            "alignment": alignment,
        }

    if block_type == Block.BlockType.IMAGE:
        alignment = request.POST.get("alignment")

        if alignment not in {"flex-start", "center", "flex-end"}:
            raise ValueError("Ungültige Bildausrichtung.")

        caption = request.POST.get("caption", "").strip()
        width = request.POST.get("width", "auto").strip()
        height = request.POST.get("height", "auto").strip()

        # Nur einfache CSS-Längen erlauben.
        allowed_size = (
            r"(?:auto|fit-content|max-content|min-content|0|"
            r"\d+(?:\.\d+)?(?:px|%|rem|em|vw|vh))"
        )

        if not re.fullmatch(allowed_size, width):
            raise ValueError("Ungültige Bildbreite.")

        if not re.fullmatch(allowed_size, height):
            raise ValueError("Ungültige Bildhöhe.")

        try:
            media_id = int(request.POST.get("media_id"))
        except (TypeError, ValueError):
            raise ValueError("Bitte ein Bild auswählen.")

        media_object = CmsMedium.objects.filter(id=media_id).first()

        if media_object is None:
            raise ValueError("Das ausgewählte Medium existiert nicht.")

        return {
            "caption": caption,
            "width": width,
            "height": height,
            "alignment": alignment,
            "media_object": media_object,
        }

    if block_type == Block.BlockType.BUTTON:
        url = request.POST.get("url", "").strip()
        style = request.POST.get("button-style")

        if style not in {
            "primary",
            "secondary",
            "success",
            "danger",
            "warning",
        }:
            raise ValueError("Ungültiger Button-Style.")

        # Interne Pfade oder absolute HTTP(S)-URLs.
        if not (url.startswith("/") and not url.startswith("//")):
            try:
                URLValidator(schemes=["http", "https"])(url)
            except ValidationError:
                raise ValueError(
                    "Bitte einen internen Pfad oder eine gültige HTTP(S)-URL eingeben."
                )

        return {
            "text": text,
            "url": url,
            "style": style,
        }

    raise ValueError("Dieser Blocktyp wird noch nicht unterstützt.")

@login_required
def seite_bearbeiten(
    request,
    page_id,
    version,
    page_block_id=None,
    create_page_block=False,
):
    """
    öffnet den editor mit einer seiten-vorschau und lädt alle blöcke in ihren layoutregionen und positionen
    """
    page = get_object_or_404(Page, id=page_id)

    page_version = get_object_or_404(
        PageVersion,
        page_id=page,
        version=version,
    )

    layout_regions = get_layout_regions_of_page(page.id)

    selected_page_block = None
    selected_medium_id = None

    if request.method == "POST":
        action = request.POST.get("action")

        # Festlegen, wohin bei einem Formularfehler zurückgeleitet wird
        if action == "create_block":
            error_redirect = "block_erstellen"

        elif action == "change_block" and page_block_id is not None:
            error_redirect = "seite_bearbeiten_block"

        else:
            messages.error(request, "Ungültige Editor-Aktion.")

            return redirect(
                "seite_bearbeiten",
                page_id=page.id,
                version=version,
            )

        try:
            with transaction.atomic():
                # neuen Block erstellen
                if action == "create_block":
                    block_type = request.POST.get("block_type")

                    allowed_types = {
                        Block.BlockType.HEADING,
                        Block.BlockType.TEXT,
                        Block.BlockType.IMAGE,
                        Block.BlockType.BUTTON,
                    }

                    if block_type not in allowed_types:
                        raise ValueError("Ungültiger Blocktyp.")

                    layout_region = _get_selected_layout_region(
                        request,
                        layout_regions,
                    )

                    data = _read_block_form(request, block_type)

                    if block_type == Block.BlockType.HEADING:
                        create_header_block(
                            data["text"],
                            data["level"],
                            data["alignment"],
                            block_type,
                            layout_region,
                            page_version,
                        )

                    elif block_type == Block.BlockType.TEXT:
                        create_text_block(
                            data["text"],
                            data["alignment"],
                            block_type,
                            layout_region,
                            page_version,
                        )

                    elif block_type == Block.BlockType.IMAGE:
                        create_image_block(
                            data["caption"],
                            data["width"],
                            data["height"],
                            data["alignment"],
                            data["media_object"],
                            block_type,
                            layout_region,
                            page_version,
                        )

                    elif block_type == Block.BlockType.BUTTON:
                        create_button_block(
                            data["text"],
                            data["url"],
                            data["style"],
                            block_type,
                            layout_region,
                            page_version,
                        )

                # vorhandenen block bearbeiten
                else:
                    # ausgewählten block speichern
                    selected_page_block = get_object_or_404(
                        PageBlock.objects.select_related(
                            "block_id",
                            "layout_region_id",
                        ),
                        id=page_block_id,
                        page_version_id=page_version,
                    )

                    # blocktyp speichern
                    block_type = selected_page_block.block_id.block_type

                    new_layout_region = _get_selected_layout_region(
                        request,
                        layout_regions,
                    )

                    try:
                        new_position = int(request.POST.get("position"))
                    except (TypeError, ValueError):
                        raise ValueError("Bitte eine gültige Position auswählen.")

                    max_position = (
                        PageBlock.objects.filter(
                            page_version_id=page_version,
                            layout_region_id=new_layout_region,
                        )
                        .exclude(id=selected_page_block.id)
                        .count() + 1
                    )

                    if not 1 <= new_position <= max_position:
                        raise ValueError(
                            "Die Position liegt außerhalb des erlaubten Bereichs."
                        )

                    data = _read_block_form(request, block_type)

                    if block_type == Block.BlockType.HEADING:
                        update_header_block(
                            data["text"],
                            data["level"],
                            data["alignment"],
                            selected_page_block,
                            page_version,
                        )

                    elif block_type == Block.BlockType.TEXT:
                        update_text_block(
                            data["text"],
                            data["alignment"],
                            selected_page_block,
                            page_version,
                        )

                    elif block_type == Block.BlockType.IMAGE:
                        update_image_block(
                            data["caption"],
                            data["width"],
                            data["height"],
                            data["alignment"],
                            data["media_object"],
                            page_version,
                            selected_page_block,
                        )

                    elif block_type == Block.BlockType.BUTTON:
                        update_button_block(
                            data["text"],
                            data["url"],
                            data["style"],
                            selected_page_block,
                            page_version,
                        )

                    else:
                        raise ValueError("Dieser Blocktyp ist nicht bearbeitbar.")

                    # erst nach erfolgreicher Inhaltsänderung verschieben.
                    _reorder_page_blocks(
                        page_version,
                        selected_page_block,
                        new_layout_region,
                        new_position,
                    )

        except (ValueError, TypeError) as error:
            messages.error(request, str(error))

            if error_redirect == "seite_bearbeiten_block":
                return redirect(
                    "seite_bearbeiten_block",
                    page_id=page.id,
                    version=version,
                    page_block_id=page_block_id,
                )

            return redirect(
                "block_erstellen",
                page_id=page.id,
                version=version,
            )

        if action == "create_block":
            messages.success(request, "Block wurde erfolgreich erstellt.")

            return redirect(
                "seite_bearbeiten",
                page_id=page.id,
                version=version,
            )

        messages.success(request, "Block wurde erfolgreich gespeichert.")

        return redirect(
            "seite_bearbeiten_block",
            page_id=page.id,
            version=version,
            page_block_id=page_block_id,
        )

    # bestehenden Block öffnen
    if page_block_id is not None:
        selected_page_block = get_object_or_404(
            PageBlock.objects.select_related(
                "block_id",
                "layout_region_id",
            ),
            id=page_block_id,
            page_version_id=page_version,
        )

        # Medien nur bei Bildblöcken abfragen!
        if (
            selected_page_block.block_id.block_type
            == Block.BlockType.IMAGE
        ):
            selected_medium_id = (
                BlockMedium.objects.filter(
                    block_id=selected_page_block.block_id,
                )
                .order_by("position", "id")
                .values_list("medium_id_id", flat=True)
                .first()
            )

    # Daten für den Editor
    layout_regions, regions_with_blocks = _build_regions_with_blocks(
        page.id,
        version,
    )

    position_choices = []

    if selected_page_block is not None:
        position_choices = _build_position_choices(
            page_version,
            selected_page_block,
        )

    block_types = [
        (value, label)
        for value, label in Block.BlockType.choices
        if value != Block.BlockType.FUNCTION
    ]

    context = {
        "page": page,
        "page_version": page_version,
        "version": version,
        "media": get_all_media(),
        "layout_regions": layout_regions,
        "regions_with_blocks": regions_with_blocks,
        "selected_page_block": selected_page_block,
        "selected_medium_id": selected_medium_id,
        "create_page_block": create_page_block,
        "position_choices": position_choices,
        "region_position_counts_json": json.dumps(
            _build_region_position_counts(
                page_version,
                layout_regions,
            )
        ),
        "used_function_types": get_functions_by_page_id(
            page_id,
            version,
        ),
        "medium_titles": get_media_used_by_page_id(
            page_id,
            version,
        ),
        "block_types": block_types,
    }

    return render(request, "editor.html", context)

# rendert die zu bearbeitende Page mit ihrem Layout, Design, Blöcke und die anordnung der Blöcke in der Page
# in einem iframe in editor.html

@login_required
@xframe_options_sameorigin
def seiten_vorschau(request, page_id, version):

    page = get_object_or_404(Page, id=page_id)

    design = page.design_id

    blocks_by_region = get_page_block_used_in_page(
        page.id,
        version,
    )

    context = {
        "page": page,
        "design": design,
        "blocks_by_region": blocks_by_region,
        "navigation_entries": get_visible_navigation(),
    }

    return render(request, page.layout_id.template, context)


@login_required
def vorschau_view(request, page_id, version):
    page = get_object_or_404(Page, id=page_id)

    get_object_or_404(
        PageVersion,
        page_id=page,
        version=version,
    )

    return render(
        request,
        "vorschau.html",
        {
            "page": page,
            "version": version,
            "username": request.user.username,
        },
    )

@login_required
def delete_page(request, page_id):
    page = Page.objects.get(id=page_id)
    page.delete()

    messages.success(request, "Die Seite wurde gelöscht")
    return redirect("to_seiten_main")
