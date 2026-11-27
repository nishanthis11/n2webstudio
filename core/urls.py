from django.conf import settings
from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("portfolio/", views.portfolio, name="portfolio"),
    path("portfolio/<slug:slug>/", views.portfolio_detail, name="portfolio_detail"),
    path("contact/", views.contact, name="contact"),

    path("login/", views.RoleLoginView.as_view(), name="login"),
    path("register/", views.register, name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),

    path("portal/", views.portal_home, name="portal_home"),
    path("portal/enquiry/<int:pk>/", views.portal_enquiry, name="portal_enquiry"),
    path("portal/profile/", views.portal_profile, name="portal_profile"),
    path("portal/password/", views.PortalPasswordView.as_view(), name="portal_password"),

    path("studio/", views.dash_home, name="dash_home"),
    path("studio/settings/", views.dash_settings, name="dash_settings"),
    path("studio/enquiries/", views.dash_enquiries, name="dash_enquiries"),
    path("studio/enquiries/<int:pk>/", views.dash_enquiry, name="dash_enquiry"),
    path("studio/enquiries/<int:pk>/delete/", views.dash_enquiry_delete, name="dash_enquiry_delete"),
    path("studio/<slug:key>/", views.dash_list, name="dash_list"),
    path("studio/<slug:key>/new/", views.dash_edit, name="dash_new"),
    path("studio/<slug:key>/<int:pk>/edit/", views.dash_edit, name="dash_edit"),
    path("studio/<slug:key>/<int:pk>/delete/", views.dash_delete, name="dash_delete"),
]

if settings.DEBUG:  # preview the custom 404 page while developing
    urlpatterns.append(path("404-preview/", views.not_found, name="preview_404"))
