from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from cms.models import Page

@login_required
def release_page(request, page_id):
    page = Page.objects.get(id=page_id)
    page.status = True
    page.save()

    messages.success(request, "Die Seite wurde veröffentlicht")
    return redirect("to_seiten_main")

