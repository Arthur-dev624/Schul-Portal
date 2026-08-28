from django.shortcuts import render, redirect

def to_seiten_main(request):
    context = {}
    return render(request, "seitenVerwaltung.html", context)