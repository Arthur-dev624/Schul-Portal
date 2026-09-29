import logging
from cProfile import label
from pathlib import Path

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.validators import FileExtensionValidator
from django.db import transaction
from django.db.models import Count
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from cms.models import CmsMedium

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10mb groß darf die Datei sein

IMAGE_FORMATS = {
    "JPEG": ({"jpg", "jpeg"}, "image/jpeg"),
    "PNG": ({"png"}, "image/png"),
    "GIF": ({"gif"}, "image/gif"),
    "WEBP": ({"webp"}, "image/webp"),
}

# django form Eingabe, um medien hochzuladen oder zu ersetzen
class CmsImageForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        label="Titel"
    )

    alt_text = forms.CharField(
        max_length=255,
        label="AlternativText"
    )

    file = forms.ImageField(
        label="Bilddatei",
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    "jpg", "jpeg", "png", "gif", "webp"
                ]
            )
        ]
    )

    def clean_file(self):
        uploaded_file = self.cleaned_data["file"]

        # dateigröße überprüfen
        if uploaded_file.size > MAX_FILE_SIZE:
            raise forms.ValidationError(
                "Die Datei darf maximal 10 MB groß sein"
            )

        # forms ImageField überprüft den tatsächlichen Bildinhalt:
        image_format = uploaded_file.image.format

        if image_format not in IMAGE_FORMATS:
            raise forms.ValidationError(
                "Dieses Bildformat wird nicht unterstützt"
            )

        # Dateiendung muss tum tatsächlichen Bildformat passen
        extension = Path(uploaded_file.name).suffix.lower().lstrip(".")
        allowed_extensions = IMAGE_FORMATS[image_format]

        if extension not in allowed_extensions:
            raise forms.ValidationError(
                "Dateiendung und tatsächliches Bildformat stimmen nicht überein"
            )

        return uploaded_file

def _get_media_type(uploaded_file):
    """ermittelt den MIME-Typ des validierten Bildes"""

    image_format = uploaded_file.image.format
    return IMAGE_FORMATS[image_format][1]

def _delete_old_file(file_name, storage):
    """
    löscht eine ersetzte Datei, wenn kein CmsMedium mehr auf diesen Dateipfad verweist
    """

    if not file_name:
        return

    if CmsMedium.objects.filter(file=file_name).exists():
        return

    try:
        storage.delete(file_name)
    except Exception:
        logger.exception(
            "Alte Mediendatei konnte nicht gelöscht werden: %s",
                file_name
            )

@login_required
def to_medien_verwaltung(request):

    # zugriff nur für admins
    if not hasattr(request.user, "person") or request.user.person.role != "admin":
        return HttpResponseForbidden(
            "Du besitzt keine Berechtigung für die Medienverwaltung"
        )

    if request.method == "POST":
        action = request.POST.get("action")

        if action not in {"upload", "replace"}:
            return HttpResponseBadRequest("Ungültige Aktion")

        form = CmsImageForm(request.POST, request.FILES)

        if form.is_valid():
            uploaded_file = form.cleaned_data["file"]
            title = form.cleaned_data["title"]
            alt_text = form.cleaned_data["alt_text"]

            media_type = _get_media_type(uploaded_file)

            #neues medium hochladen
            if action == "upload":
                CmsMedium.objects.create(
                    file=uploaded_file,
                    title=title,
                    media_type=media_type,
                    alt_text=alt_text,
                    uploaded_by=request.user
                )

                messages.success(
                    request,
                    "Das Medium wurde erfolgreich hochgeladen"
                )

                return redirect("to_medien_verwaltung")

            # bestehendes medium ersetzen
            elif action == "replace":
                medium_id = request.POST.get("medium_id", "")

                if not medium_id.isdecimal():

                    messages.error(
                        request,
                        "Ungültige Medien-ID"
                    )

                else:
                    with transaction.atomic():
                        medium = get_object_or_404(
                            CmsMedium.objects.select_for_update(),
                            id=int(medium_id)
                        )

                    # nur bildmedien ersetzen
                    is_image = (
                        medium.media_type == "image"
                        or medium.media_type.startswith("image/")
                    )

                    if not is_image:
                        messages.error(
                            request, "Dieses Medium ist kein Bild"
                        )

                        return redirect("to_medien_verwaltung")

                    #alten Dateipfad vor dem Austausch speichern
                    old_file_name = medium.file.name
                    old_storage = medium.file.storage

                    # bestehenden Datensatz aktualisieren
                    medium.file = uploaded_file
                    medium.title = title
                    medium.alt_text = alt_text
                    medium.media_type = media_type
                    medium.uploaded_by = request.user
                    medium.uploaded_at = timezone.now()
                    medium.save(
                        update_fields=[
                            "file", "title", "alt_text", "media_type", "uploaded_by", "uploaded_at"
                        ]
                    )

                    # alte datei erst nach erfolgreichem abschluss der datenbanktransaktion entfernen
                    if old_file_name != medium.file.name:
                        transaction.on_commit(
                            lambda name= old_file_name, storage=old_storage:
                                _delete_old_file(name, storage),
                            robust = True
                        )

                messages.success(
                    request, "Das Medium wurde erfolgreich ersetzt"
                )

                return redirect("to_medien_verwaltung")

        else:
            # Validierungsfehler ausgeben
            for field, errors in form.errors.items():
                label = (
                    form.fields[field].label
                    if field in form.fields
                    else "Formular"
                )

                for error in errors:
                    messages.error(request, f"{label}: {error}")


    # alle medien aus der Datenbank laden
    media = (
        CmsMedium.objects.
        select_related("uploaded_by")
        .annotate(
            block_count=Count(
                "mediumBlocks__block_id",
                distinct=True
            )
        )
        .order_by("-uploaded_at", "-id")
    )

    # für die Vorschau unterscheiden, ob es ein Bild ist
    # auch ältere Einträge mit media_type="image" unterstützen
    for medium in media:
        medium.is_image (
            medium.media_type == "image"
            or medium.media_type.startswith("image/")
        )

    context = {
        "username": request.user.username,
        "media": media,
        "media_count": len(media),
        "upload_values": (
            request.POST
            if request.method == "POST"
            and request.POST.get("action") == "upload"
            else {}
        ),
    }

    return render(request, "medienverwaltung.html", context)