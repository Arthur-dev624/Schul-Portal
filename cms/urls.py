from django.urls import path

from .views.cmsLogin import cms_login, cms_logout, cms_dashboard, admin_dashboard
from .views.seitenVerwaltung import to_seiten_main, seiten_search, seite_erstellen

urlpatterns = [
    path("", cms_login, name="cms_login"),
    path("cms_logout/", cms_logout, name="cms_logout"),
    path("dashboard/", cms_dashboard, name="cms_dashboard"),
    path("dashboard/admindashboard/", admin_dashboard, name="admin_dashboard"),
    path("dashboard/admindashboard/seitenverwaltung/", to_seiten_main, name="to_seiten_main"),
    path("dashboard/admindashboard/seitenverwaltung/erstellen/", seite_erstellen, name="seite_erstellen"),
    path("seiten_search/", seiten_search, name="seiten_search"),
]
