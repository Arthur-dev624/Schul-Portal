from django.urls import path

from .views.cmsLogin import cms_login, cms_logout, cms_dashboard, admin_dashboard

urlpatterns = [
    path("", cms_login, name="cms_login"),
    path("cms_logout/", cms_logout, name="cms_logout"),
    path("dashboard/", cms_dashboard, name="cms_dashboard"),
    path("dashboard/admindashboard/", admin_dashboard, name="admin_dashboard"),
]