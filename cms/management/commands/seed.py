from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from cms.models import Layout, LayoutRegion, Design
from datetime import date

class Command(BaseCommand):
    help = "Erstellt Testdaten"

    def handle(self, *args, **kwargs):
        Layout.objects.create(
            name="Startseite",
            description="Layout mit Hero Section und Main Section",
            template="startseite.html",
        )

        Design.objects.create(
            name="Simple Design für Startseite",
            custom_css="startseiten_design.css",
        )

        self.stdout.write(self.style.SUCCESS("Daten erstellt"))