from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from cms.models import Layout, LayoutRegion, Design
from datetime import date

class Command(BaseCommand):
    help = "Erstellt Testdaten"

    def handle(self, *args, **kwargs):
        layout = Layout.objects.create(
            name="Landingpage",
            description="Layout mit Hero Section und Main Section",
            template="startseite.html",
        )

        LayoutRegion.objects.create(
            layout_id=layout,
            name="Hero",
            key="hero"
        )

        LayoutRegion.objects.create(
            layout_id=layout,
            name="Main",
            key="main"
        )

        LayoutRegion.objects.create(
            layout_id=layout,
            name="Footer",
            key="footer"
        )

        self.stdout.write(self.style.SUCCESS("Daten erstellt"))