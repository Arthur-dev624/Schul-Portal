from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def to_medien_verwaltung(request):
    return render(request)