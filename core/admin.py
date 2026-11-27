from django.contrib import admin

from .models import FAQ, Enquiry, Profile, Project, Service, SiteSettings, Testimonial


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "service", "status", "created_at")
    list_filter = ("status", "service")
    search_fields = ("name", "email", "business_name")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_demo", "is_featured", "order")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_active")
    prepopulated_fields = {"slug": ("title",)}


admin.site.register([SiteSettings, Testimonial, FAQ, Profile])
