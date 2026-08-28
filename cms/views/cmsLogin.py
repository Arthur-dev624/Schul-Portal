from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from cms.api import count_pages, count_releases, count_drafts, count_media

# TODO: Redakteur check hinzufügen und weiterleitung an redakteur_dashboard
# dashboard view checks if logged in person got admin role
@login_required
def cms_dashboard(request):
    role = request.user.person.role
    if role == "admin":
        return redirect("admin_dashboard")
    else:
        return redirect("cms_login")

# cmsSurface for admin
@login_required
def admin_dashboard(request):
    # check if user has admin role
    if request.user.person.role != "admin":
        return redirect("cms_dashboard")

    # count data to show in cmsSurface
    username = request.user.username
    site_count = count_pages()
    released_count = count_releases()
    draft_count = count_drafts()
    media_count = count_media()

    context = {
        "username": username,
        "siteCount": site_count,
        "releasedCount": released_count,
        "draftCount": draft_count,
        "mediaCount": media_count
    }

    # render cmsSurface template
    return render(request, "cmsSurface.html", context)

# TODO: redakteur_dashboard view implementieren und redakteurDashboard.html template erstellen

def cms_login(request):
    error = None
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('cms_dashboard')
        else:
            error = "Invalid username or password"
    return render(request, "cmsLogin.html", {"error": error})

def cms_logout(request):
    auth_logout(request)
    return redirect("cms_login")