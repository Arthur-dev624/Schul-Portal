from django.urls import path

from .views.medienVerwaltung import to_medien_verwaltung
from .views.navigationVerwaltung import to_navigation_verwaltung, cms_page
from .views.pageRelease import to_veroeffentlichungs_verwaltung, release_page, archive_page
from .views.cmsLogin import cms_login, cms_logout, cms_dashboard, admin_dashboard
from .views.seitenVerwaltung import to_seiten_main, seiten_search, seite_erstellen, seite_bearbeiten, seiten_vorschau, vorschau_view, delete_page
from .views.pageRelease import release_page

urlpatterns = [
    path("", cms_login, name="cms_login"),
    path("cms_logout/", cms_logout, name="cms_logout"),
    path("dashboard/", cms_dashboard, name="cms_dashboard"),
    path("dashboard/admindashboard/", admin_dashboard, name="admin_dashboard"),
    path("dashboard/admindashboard/seitenverwaltung/", to_seiten_main, name="to_seiten_main"),
    path("dashboard/admindashboard/seitenverwaltung/erstellen/", seite_erstellen, name="seite_erstellen"),
    path("dashboard/admindashboard/seitenverwaltung/<int:page_id>/veroeffentlichen/", release_page, name="release_page"),
    path("dashboard/admindashboard/seitenverwaltung/<int:page_id>/delete", delete_page, name="delete_page"),
    path("dashboard/admindashboard/seitenverwaltung/<int:page_id>/<int:version>/editor", seite_bearbeiten, name="seite_bearbeiten"),
    path("dashboard/admindashboard/seitenverwaltung/<int:page_id>/<int:version>/editor/create/", seite_bearbeiten, {"create_page_block": True}, name="block_erstellen"),
    path("dashboard/admindashboard/seitenverwaltung/<int:page_id>/<int:version>/editor/block/<int:page_block_id>", seite_bearbeiten, name="seite_bearbeiten_block"),
    path("dashboard/admindashboard/seitenverwaltung/<int:page_id>/<int:version>/preview", seiten_vorschau, name="seiten_vorschau"),
    path("dashboard/admindashboard/seitenverwaltung/<int:page_id>/<int:version>/vorschau", vorschau_view, name="vorschau"),
    path("seiten_search/", seiten_search, name="seiten_search"),
    path("dashboard/admindashboard/medienverwaltung", to_medien_verwaltung, name="to_medien_verwaltung"),
    path("dashboard/admindashboard/navigationsverwaltung/", to_navigation_verwaltung, name="to_navigation_verwaltung"),
    path("seite/<slug:slug>/", cms_page, name="cms_page"),
    path("dashboard/admindashboard/veroeffentlichungsverwaltung/", to_veroeffentlichungs_verwaltung, name="to_veroeffentlichungs_verwaltung"),
    path("dashboard/admindashboard/seitenverwaltung/<int:page_id>/archivieren/", archive_page, name="archive_page"),
]
