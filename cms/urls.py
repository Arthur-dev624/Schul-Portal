from django.urls import path

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
    path ("dashboard/admindashboard/seitenverwaltung/<int:page_id>/veroeffentlichen/", release_page, name="release_page"),
    path("dashboard/admindashboard/seitenverwaltung/<int:page_id>/delete", delete_page, name="delete_page"),
    path("dashboard/admindashboard/seitenverwaltung/<int:page_id>/editor", seite_bearbeiten, name="seite_bearbeiten"),
    path("dashboard/admindashboard/seitenverwaltung/<int:page_id>/preview", seiten_vorschau, name="seiten_vorschau"),
    path("dashboard/admindashboard/seitenverwaltung/<int:page_id>/vorschau", vorschau_view, name="vorschau"),
    path("seiten_search/", seiten_search, name="seiten_search"),
]
