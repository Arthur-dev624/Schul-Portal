from copy import deepcopy

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from cms.models import (
    Page,
    PageVersion,
    PageBlock,
    Block,
    BlockMedium,
    FunctionBlock,
    Publication,
)

def is_cms_admin(user):
    return (
        hasattr(user, "person")
        and user.person.role == "admin"
    )

def get_latest_draft(page):
    """
    Gibt die neueste noch nie veröffentlichte
    Entwurfsversion einer Seite zurück.
    """
    return (
        PageVersion.objects
        .filter(
            page_id=page,
            status=False,
            published__isnull=True,
        )
        .order_by("-version", "-id")
        .first()
    )

def create_next_draft(source_version, user):
    """
    Erstellt eine neue Entwurfsversion.

    Kopiert:
    - PageBlocks
    - Block-Konfigurationen
    - Medienzuordnungen
    - Funktionsblock-Zuordnungen

    Die eigentlichen Mediendateien werden
    nicht dupliziert.
    """

    page = source_version.page_id

    latest_version = (
        PageVersion.objects
        .filter(page_id=page)
        .order_by("-version", "-id")
        .first()
    )

    next_number = latest_version.version + 1

    new_version = PageVersion.objects.create(
        page_id=page,
        created_by=user,
        version=next_number,
        status=False,
    )

    # Alte und neue Block-IDs zuordnen.
    block_mapping = {}

    old_page_blocks = (
        PageBlock.objects
        .filter(page_version_id=source_version)
        .select_related("block_id")
        .prefetch_related(
            "block_id__blockMedia",
            "block_id__functionBlocks",
        )
        .order_by("id")
    )

    for old_page_block in old_page_blocks:

        old_block = old_page_block.block_id

        # Ein gemeinsam verwendeter Block wird
        # innerhalb dieser Version nur einmal kopiert.
        new_block = block_mapping.get(old_block.id)

        if new_block is None:

            new_block = Block.objects.create(
                block_type=old_block.block_type,
                config=deepcopy(old_block.config),
            )

            block_mapping[old_block.id] = new_block

            # Medienbeziehungen kopieren.
            for old_medium in old_block.blockMedia.all():

                BlockMedium.objects.create(
                    block_id=new_block,
                    medium_id=old_medium.medium_id,
                    position=old_medium.position,
                )

            # Funktionsblock-Beziehungen kopieren.
            for old_function in old_block.functionBlocks.all():

                FunctionBlock.objects.create(
                    block_id=new_block,
                    function_id=old_function.function_id,
                    config=deepcopy(old_function.config),
                )

        # Position und Layoutregion übernehmen.
        PageBlock.objects.create(
            page_version_id=new_version,
            block_id=new_block,
            layout_region_id=old_page_block.layout_region_id,
            position=old_page_block.position,
        )

    return new_version

@login_required
@require_GET
def to_veroeffentlichungs_verwaltung(request):
    """
    Übersichtsseite der Veröffentlichungsverwaltung.
    """

    if not is_cms_admin(request.user):
        return HttpResponseForbidden(
            "Keine Berechtigung"
        )

    pages = Page.objects.all().order_by("-id")

    rows = []

    for page in pages:

        # Aktuell öffentlich angezeigte Version.
        live_version = None

        if page.status:
            live_version = (
                PageVersion.objects
                .filter(
                    page_id=page,
                    status=True,
                )
                .order_by("-version", "-id")
                .first()
            )

        rows.append({
            "page": page,
            "live_version": live_version,
            "draft_version": get_latest_draft(page),
        })

    # Die letzten zehn Veröffentlichungen.
    history = (
        Publication.objects
        .select_related(
            "page_version_id",
            "page_version_id__page_id",
            "published_by",
        )
        .order_by("-published_at", "-id")[:10]
    )

    return render(
        request,
        "veröffentlichungsVerwaltung.html",
        {
            "username": request.user.username,
            "rows": rows,
            "history": history,
        },
    )

@login_required
@require_POST
def release_page(request, page_id):
    """
    Veröffentlicht den neuesten Entwurf
    und erzeugt anschließend eine neue
    bearbeitbare Entwurfsversion.
    """

    if not is_cms_admin(request.user):
        return HttpResponseForbidden(
            "Keine Berechtigung"
        )

    with transaction.atomic():

        # Seite während der Veröffentlichung sperren.
        page = get_object_or_404(
            Page.objects.select_for_update(),
            id=page_id,
        )

        draft = get_latest_draft(page)

        if draft is None:
            messages.error(
                request,
                "Keine unveröffentlichte Entwurfsversion vorhanden.",
            )

            return redirect(
                "to_veroeffentlichungs_verwaltung"
            )

        # Eventuell bestehende öffentliche
        # Seitenversion deaktivieren.
        PageVersion.objects.filter(
            page_id=page,
            status=True,
        ).update(status=False)

        # Gewählte Entwurfsversion veröffentlichen.
        draft.status = True
        draft.published_at = timezone.now()

        draft.save(
            update_fields=["status", "published_at"]
        )

        # Veröffentlichung protokollieren.
        Publication.objects.create(
            page_version_id=draft,
            published_by=request.user,
        )

        # Seite insgesamt aktivieren.
        page.status = True

        page.save(
            update_fields=["status", "updated_at"]
        )

        # Neue Arbeitsversion erzeugen.
        new_draft = create_next_draft(
            source_version=draft,
            user=request.user,
        )

    messages.success(
        request,
        (
            f"Seite '{page.title}' veröffentlicht "
            f"(Version {draft.version}). "
            f"Entwurf {new_draft.version} wurde erstellt."
        ),
    )

    return redirect(
        "to_veroeffentlichungs_verwaltung"
    )

@login_required
@require_POST
def archive_page(request, page_id):
    """
    Nimmt eine Seite offline, ohne ihre
    Versionen oder Blöcke zu löschen.
    """

    if not is_cms_admin(request.user):
        return HttpResponseForbidden(
            "Keine Berechtigung"
        )

    with transaction.atomic():

        page = get_object_or_404(
            Page.objects.select_for_update(),
            id=page_id,
        )

        # Öffentliche Version deaktivieren.
        PageVersion.objects.filter(
            page_id=page,
            status=True,
        ).update(status=False)

        # Gesamte Seite deaktivieren.
        page.status = False

        page.save(
            update_fields=["status", "updated_at"]
        )

    messages.success(
        request,
        f"Seite '{page.title}' wurde archiviert.",
    )

    return redirect(
        "to_veroeffentlichungs_verwaltung"
    )

