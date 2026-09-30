from django.core.management.base import BaseCommand
from cms.models import Layout, LayoutRegion


class Command(BaseCommand):
    help = "Erstellt bzw. aktualisiert die CMS-Layouts und Layoutregionen"

    def handle(self, *args, **kwargs):
        layouts = [
            {
                "name": "Landingpage",
                "description": "Startseite mit Hero-, Main- und Footerbereich",
                "template": "layouts/startseite.html",
                "regions": [
                    ("Hero", "hero"),
                    ("Main", "main"),
                    ("Footer", "footer"),
                ],
            },
        ]

        for layout_data in layouts:
            layout, _ = Layout.objects.update_or_create(
                name=layout_data["name"],
                defaults={
                    "description": layout_data["description"],
                    "template": layout_data["template"],
                },
            )

            for region_name, region_key in layout_data["regions"]:
                LayoutRegion.objects.update_or_create(
                    layout_id=layout,
                    key=region_key,
                    defaults={
                        "name": region_name,
                    },
                )

        self.stdout.write(
            self.style.SUCCESS(
                "CMS-Layouts und Layoutregionen wurden erfolgreich erstellt oder aktualisiert."
            )
        )