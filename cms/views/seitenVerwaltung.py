from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from cms.api import search_pages_with_title, get_blocks_and_layout_region_by_page_id
from cms.models import Design, Layout, Page, PageVersion
from django.utils.text import slugify
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.contrib import messages

@login_required
def to_seiten_main(request):
    username = request.user.username
    pages = Page.objects.all()
    context = {
        "username": username,
        "pages": pages,
    }
    return render(request, "seitenVerwaltung.html", context)

def seiten_search(request):
    query = request.GET.get("q", "")
    pages_found = search_pages_with_title(query)
    return render(request, "seitenVerwaltung.html",
                  {"pages_found": pages_found, "query": query})

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

# öffnet den editor mit dem Page_Objekt welches zu bearbeiten ist,
# welches benötigt wird, um die seiten_vorschau funktion mit der page_id aufzurufen
@login_required
def seite_bearbeiten(request, page_id):
    page = Page.objects.get(id=page_id)
    blocks, _ = get_blocks_and_layout_region_by_page_id(page.id)
    context = {
        "page": page,
        "blocks": blocks,
    }
    return render(request, "editor.html", context)

# rendert die zu bearbeitende Page mit ihrem Layout, Design, Blöcke und die anordnung der Blöcke in der Page
# in einem iframe in editor.html
@login_required
@xframe_options_sameorigin
def seiten_vorschau(request, page_id):
    page = Page.objects.get(id=page_id)
    design = page.design_id

    blocks, layout_regions = get_blocks_and_layout_region_by_page_id(page.id)

    context = {
        "page": page,
        "blocks": blocks,
        "layout_regions": layout_regions,
        "design": design,
    }

    return render(request, page.layout_id.template, context)

@login_required
def vorschau_view(request, page_id):
    page = Page.objects.get(id=page_id)
    username = request.user.username
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
