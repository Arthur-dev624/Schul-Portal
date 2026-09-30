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
            layout = (
                Layout.objects
                .filter(template=layout_data["template"])
                .order_by("id")
                .first()
            )

            if layout is None:
                layout = Layout.objects.create(
                    name=layout_data["name"],
                    description=layout_data["description"],
                    template=layout_data["template"],
                )
            else:
                layout.name = layout_data["name"]
                layout.description = layout_data["description"]
                layout.template = layout_data["template"]
                layout.save(update_fields=["name", "description", "template"])

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