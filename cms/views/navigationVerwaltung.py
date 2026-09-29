from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from cms.api import get_page_block_used_in_page
from cms.models import NavigationItem, Page, PageVersion

# Formular zum Erstellen und Bearbeiten
class NavigationForm(forms.ModelForm):

    class Meta:
        model = NavigationItem
        fields = ["page_id", "title", "position", "visible"]

        widgets = {
            "page_id": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "position": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
            }),
            "visible": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Nur veröffentlichte Seiten anbieten
        self.fields["page_id"].queryset = (
            Page.objects.filter(status=True).order_by("title")
        )

        self.fields["page_id"].empty_label = "Seite auswählen"
        self.fields["position"].required = True
        self.fields["position"].min_value = 0


# Navigation für den Website-Header laden
def get_visible_navigation():
    return (
        NavigationItem.objects
        .filter(
            visible=True,
            parent_id__isnull=True,
            page_id__status=True,
        )
        .select_related("page_id")
        .order_by("position", "id")
    )

@login_required
def to_navigation_verwaltung(request):

    # Gleiche Berechtigungsprüfung wie in der Medienverwaltung
    if (
        not hasattr(request.user, "person")
        or request.user.person.role != "admin"
    ):
        return HttpResponseForbidden("Keine Berechtigung")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "create":
            form = NavigationForm(request.POST, prefix="create")

        elif action in ("update", "delete"):
            item_id = request.POST.get("item_id", "")

            if not item_id.isdecimal():
                return HttpResponseBadRequest("Ungültige ID")

            item = get_object_or_404(
                NavigationItem,
                id=int(item_id),
                parent_id__isnull=True,
            )

            # Eintrag entfernen, nicht die verlinkte Seite!
            if action == "delete":
                item.delete()
                messages.success(request, "Eintrag gelöscht.")
                return redirect("to_navigation_verwaltung")

            form = NavigationForm(
                request.POST,
                instance=item,
                prefix=f"item-{item.id}",
            )

        else:
            return HttpResponseBadRequest("Ungültige Aktion")

        if form.is_valid():
            navigation_item = form.save(commit=False)

            # Prototyp: keine Untermenüs
            navigation_item.parent_id = None
            navigation_item.save()

            messages.success(request, "Navigation gespeichert.")
        else:
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, error)

        return redirect("to_navigation_verwaltung")

    # Vorhandene Einträge mit Bearbeitungsformularen laden
    navigation_items = (
        NavigationItem.objects
        .filter(parent_id__isnull=True)
        .select_related("page_id")
        .order_by("position", "id")
    )

    rows = [
        {
            "item": item,
            "form": NavigationForm(
                instance=item,
                prefix=f"item-{item.id}",
            ),
        }
        for item in navigation_items
    ]

    context = {
        "username": request.user.username,
        "create_form": NavigationForm(
            prefix="create",
            initial={
                "visible": True,
                "position": len(rows) + 1,
            },
        ),
        "rows": rows,
    }

    return render(request, "navigationVerwaltung.html", context)


# Eine veröffentlichte CMS-Seite öffentlich darstellen
def cms_page(request, slug):

    page = get_object_or_404(
        Page,
        slug=slug,
        status=True,
    )

    # Vorhandene Version mit der höchsten Versionsnummer
    page_version = (
        PageVersion.objects
        .filter(page_id=page)
        .order_by("-version", "-id")
        .first()
    )

    if page_version is None:
        raise Http404("Keine Seitenversion vorhanden")

    context = {
        "page": page,
        "design": page.design_id,
        "blocks_by_region": get_page_block_used_in_page(
            page.id,
            page_version.version,
        ),
        "navigation_entries": get_visible_navigation(),
    }

    return render(request, page.layout_id.template, context)
