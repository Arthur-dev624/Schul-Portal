from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from cms.api import search_pages_with_title
from cms.models import Design, Layout, Page


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
                Page.objects.create(
                    title=title,
                    slug=slug,
                    layout_id=layout,
                    design_id=design,
                    created_by=request.user,
                )
                return redirect("to_seiten_main")

    return render(request, "seiteErstellen.html", {
        "username": request.user.username,
        "layouts": layouts,
        "designs": designs,
        "error": error,
    })
