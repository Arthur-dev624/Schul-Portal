import json
from json import JSONDecodeError

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from cms.api import search_pages_with_title, get_page_block_used_in_page, get_functions_by_page_id, get_media_used_by_page_id, get_blocks_and_layout_region_by_page_id, current_page_versions, get_layout_regions_of_page, get_all_media, create_header_block, create_text_block, create_image_block, create_button_block, update_header_block, update_text_block, update_image_block, update_button_block
from cms.models import Design, Layout, Page, PageVersion, PageBlock, Block, BlockMedium
from django.utils.text import slugify
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.contrib import messages
from django.db import transaction

from models import CmsMedium


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

def seiten_search(request):
    query = request.GET.get("q", "")
    pages_found = search_pages_with_title(query)
    context = {
        "query": query,
        "pages_found": pages_found
    }
    return render(request, "seitenVerwaltung.html", context)

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

# rendert das editor.html template als POST View
@login_required
def seite_bearbeiten(request, page_id, version, page_block_id=None, create_page_block=None):
    """
        rendert den Editor und rendert die Einstellungen zu einem ausgewähltem PageBlock und speichert diese

        page_id: Seite die bearbeitet wird
        version: Version der zu bearbeitenden Seite
        page_block_id: optional, wenn vorhanden dann wurde links im Editor ein PageBlock ausgewählt
    """
    page = Page.objects.get(id=page_id)
    page_version = PageVersion.objects.get(page_id=page, version=version)
    layout_regions, regions_with_blocks = _build_regions_with_blocks(page.id, version)
    media = get_all_media()
    used_function_types = get_functions_by_page_id(page_id, version)
    medium_titles = get_media_used_by_page_id(page_id, version)
    # kein Block ist am Anfang ausgewählt
    selected_page_block = None
    config_form_value = None
    # blockTypes speichern
    block_types = Block.BlockType.choices
    #blockmedium vom ausgewähltem Block mit Medium
    selected_block_medium = None

    # wenn Einstellungen zu einem PageBlock gespeichert werden, oder ein Block erstellt wird, also POST-Request
    if request.method == "POST":
        action = request.POST.get("action")
        # werte aus dem Formular laden
        # werte für Überschrift
        header_text = request.POST.get("text")
        level = request.POST.get("level")
        header_alignment = request.POST.get("alignment")
        # werte für Text
        text = request.POST.get("text")
        text_alignment = request.POST.get("alignment")
        # werte für Bild
        caption = request.POST.get("caption")
        width = request.POST.get("width")
        height = request.POST.get("height")
        image_alignment = request.POST.get("alignment")
        # werte für button
        button_text = request.POST.get("text")
        url = request.POST.get("url")
        button_style = request.POST.get("button-style")

        # wenn POST ein request ist, um einen Block zu ändern
        if action == "change_block":
            # speichert PageBlock, der geändert worden ist
            page_block_id = request.POST.get("page_block_id")
            selected_page_block = PageBlock.objects.select_related(
                "block_id",
                "layout_region_id",
                "page_version_id",
            ).get(
                id=page_block_id,
                page_version_id=page_version,   # PageBlock muss zur aktuellen version gehören
            )

            # nimm eingegebene werte für layout_region und position
            layout_region_id = request.POST.get("layout_region_id")
            position = request.POST.get("position")

            # prüfen ob config_data gültiges JSON ist, new_layout_region eine vorhandene Layoutregion ist und
            # new_position eine für die layoutregion gültige Zahl ist
            try:
                new_layout_region = layout_regions.get(id=layout_region_id)
                new_position = int(position)
            except (ValueError, TypeError):
                messages.error(request, "Die ausgewählte Position ist ungültig.")
            except layout_regions.model.DoesNotExist:
                messages.error(request, "Die ausgewählte Layoutregion gehört nicht zu diesem Layout.")
            else:
                # berechne, welche Position ist maximal erlaubt
                max_position = PageBlock.objects.filter(
                    page_version_id=page_version,
                    layout_region_id=new_layout_region,
                ).exclude(id=selected_page_block.id).count() + 1

                # prüfe, dass neue position erlaubt ist
                if new_position < 1 or new_position > max_position:
                    messages.error(request, "Die ausgewählte Position ist außerhalb des erlaubten Bereichs.")
                else:
                    # werte aus dem Formular speichern, abhängig vom blockType
                    if selected_page_block.block_id.block_type == Block.BlockType.HEADING:
                        try:
                            with transaction.atomic():
                                level = int(level)
                                update_header_block(header_text, level, header_alignment, selected_page_block,
                                    page_version)
                        except ValueError as error:
                            messages.error(request, str(error))
                        except (ValueError, TypeError):
                            messages.error(request, "Die ausgewählte größe ""level"" ist ungültig")
                        else:
                            messages.success(request, "Block wurde erfolgreich gespeichert.")

                    elif selected_page_block.block_id.block_type == Block.BlockType.TEXT:
                        try:
                            with transaction.atomic():
                                update_text_block(text, text_alignment, selected_page_block, page_version)
                        except ValueError as error:
                            messages.error(request, str(error))
                        else:
                            messages.success(request, "Block wurde erfolgreich gespeichert.")

                    elif selected_page_block.block_id.block_type == Block.BlockType.IMAGE:
                        media_id = request.POST.get("media_id")

                        if not media_id:
                            messages.error(request, "Bitte ein Bild auswählen")
                            return redirect("block_erstellen", page_id=page.id, version=version)

                        media_object = get_object_or_404(
                            CmsMedium,
                            id=media_id
                        )

                        try:
                            with transaction.atomic():
                                update_image_block(caption, width, height, image_alignment, media_object, page_version,
                                    selected_page_block)
                        except ValueError as error:
                            messages.error(request, str(error))
                        else:
                            messages.success(request, "Block wurde erfolgreich gespeichert.")

                    elif selected_page_block.block_id.block_type == Block.BlockType.BUTTON:
                        try:
                            with transaction.atomic():
                                update_button_block(button_text, url, button_style, selected_page_block, page_version)
                        except ValueError as error:
                                messages.error(request, error)
                        else:
                            messages.success(request, "Block wurde erfolgreich gespeichert.")

                    _reorder_page_blocks(page_version, selected_page_block, new_layout_region, new_position)

                return redirect("seite_bearbeiten", page_id=page.id, version=version)

        # wenn POST ein request ist, um einen Block zu erstellen
        elif action == "create_block":
            create_page_block = None

            # Blocktyp aus Formular speichern
            block_type = request.POST.get("block_type")
            # layoutregion aus Formular laden
            layout_region_id = request.POST.get("layout_region_id")
            layout_region = layout_regions.get(id=layout_region_id)

            # werte aus Formular speichern, abhängig vom Blocktyp, danach Datenbankeinträge machen
            if block_type is not None and block_type == Block.BlockType.HEADING:
                # Block und PageBlock in Datenbank speichern mit config
                try:
                    level = int(level)
                    create_header_block(header_text, level, header_alignment, block_type,
                                    layout_region, page_version)
                except ValueError as error:
                    messages.error(request, str(error))
                except (ValueError, TypeError):
                    messages.error(request, "Die ausgewählte größe ""level"" ist ungültig")
                else:
                    messages.success(request, "Block wurde erfolgreich erstellt.")

            elif block_type is not None and block_type == Block.BlockType.TEXT:
                try:
                    create_text_block(text, text_alignment, block_type, layout_region, page_version)
                except ValueError as error:
                    messages.error(request, str(error))
                else:
                    messages.success(request, "Block wurde erfolgreich erstellt.")

            elif block_type is not None and block_type == Block.BlockType.IMAGE:
                media_id = request.POST.get("media_id")

                if not media_id:
                    messages.error(request, "Bitte ein Bild auswählen")
                    return redirect("block_erstellen", page_id=page.id, version=version)

                media_object = get_object_or_404(
                    CmsMedium,
                    id=media_id
                )

                try:
                    create_image_block(caption, width, height, image_alignment,
                                   media_object, block_type, layout_region, page_version)
                except ValueError as error:
                    messages.error(request, str(error))
                else:
                    messages.success(request, "Block wurde erfolgreich erstellt.")

            elif block_type is not None and block_type == Block.BlockType.BUTTON:
                try:
                    create_button_block(button_text, url, button_style, block_type, layout_region, page_version)
                except ValueError as error:
                    messages.error(request, str(error))
                else:
                    messages.success(request, "Block wurde erfolgreich erstellt.")

    # ein PageBlock wurde ausgewählt aber nicht gespeichert
    elif page_block_id is not None:
        # speichert den ausgewählten Block
        selected_page_block = PageBlock.objects.select_related(
            "block_id",
            "layout_region_id",
            "page_version_id",
        ).get(
            id=page_block_id,
            page_version_id=page_version,
        )

        selected_block_medium = BlockMedium.objects.get(
            block_id=selected_page_block.block_id
        )

    # config und auswählbare positionen
    selected_config = ""
    position_choices = []

    if selected_page_block:
        selected_config = config_form_value
        if selected_config is None:
            selected_config = json.dumps(selected_page_block.block_id.config or {}, indent=2)
        position_choices = _build_position_choices(page_version, selected_page_block)

    # mit dem Kontext kann das editor.html links alle Regionen und Blöcke anzeigen, leere Regionen,
    # rechts das Formular, wenn ein Block ausgewählt ist und die Vorschau in der iframe laden
    context = {
        "page": page,
        "page_version": page_version,
        "media": media,
        "version": version,
        "layout_regions": layout_regions,
        "regions_with_blocks": regions_with_blocks,
        "selected_page_block": selected_page_block,
        "selected_block_medium": selected_block_medium,
        "create_page_block": create_page_block,
        "selected_config": selected_config,
        "position_choices": position_choices,
        "region_position_counts_json": json.dumps(_build_region_position_counts(page_version, layout_regions)),
        "used_function_types": used_function_types,
        "medium_titles": medium_titles,
        "block_types": block_types,
    }

    return render(request, "editor.html", context)

# rendert die zu bearbeitende Page mit ihrem Layout, Design, Blöcke und die anordnung der Blöcke in der Page
# in einem iframe in editor.html
@login_required
@xframe_options_sameorigin
def seiten_vorschau(request, page_id, version):
    page = Page.objects.get(id=page_id)
    design = page.design_id
    blocks_by_region = get_page_block_used_in_page(page.id, version)

    # TODO: Logik einbauen wo welche Blöcke gerendert werden sollen
    context = {
        "page": page,
        "design": design,
        "blocks_by_region": blocks_by_region,
    }

    return render(request, page.layout_id.template, context)

@login_required
def vorschau_view(request, page_id, version):
    page = Page.objects.get(id=page_id)
    username = request.user.username
    block_ids_by_region = get_page_block_used_in_page(page.id, version)
    # TODO: Block objekte aus den block_ids dem context übergeben
    context = {
        "page": page,
        "username": username,
    }
    return render(request, "vorschau.html", context)

@login_required
def delete_page(request, page_id):
    page = Page.objects.get(id=page_id)
    page.delete()

    messages.success(request, "Die Seite wurde gelöscht")
    return redirect("to_seiten_main")
