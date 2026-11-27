from django.urls import reverse

from .models import Service, SiteSettings


def site(request):
    s = SiteSettings.load()
    return {
        "site": s,
        "whatsapp_ready": bool(s.whatsapp_url),
        "whatsapp_url": s.whatsapp_url or reverse("contact"),
        "footer_services": Service.objects.filter(is_active=True)[:6],
    }
