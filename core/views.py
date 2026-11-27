from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordChangeView, redirect_to_login
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST

from .forms import (
    EnquiryAdminForm, EnquiryForm, FAQForm, LoginForm, ProfileForm, ProjectForm, RegisterForm,
    ServiceForm, SiteSettingsForm, StyledPasswordChangeForm, TestimonialForm,
)
from .models import FAQ, Enquiry, Project, Service, SiteSettings, Testimonial, get_profile

User = get_user_model()


# ------------------------------------------------------------------ public
def home(request):
    site = SiteSettings.load()
    featured = list(Project.objects.filter(is_featured=True)[:3]) or list(Project.objects.all()[:3])
    stats = [
        {"value": v, "label": label}
        for v, label in [
            (site.stat_projects_delivered, "Projects delivered"),
            (site.stat_happy_clients, "Clients served"),
            (site.stat_years, "Years of experience"),
            (site.stat_response_hours, "Hours to first reply"),
        ]
        if v
    ]
    return render(request, "home.html", {
        "stats": stats,
        "featured": featured,
        "services": Service.objects.filter(is_active=True),
        "testimonials": Testimonial.objects.filter(is_published=True)[:3],
    })


def about(request):
    return render(request, "about.html")


def services(request):
    return render(request, "services.html", {"services": Service.objects.filter(is_active=True)})


def portfolio(request):
    projects = Project.objects.all()
    used = {p.category for p in projects}
    categories = [(k, v) for k, v in Project.CATEGORIES if k in used]
    return render(request, "portfolio.html", {"projects": projects, "categories": categories})


def portfolio_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    related = Project.objects.filter(category=project.category).exclude(pk=project.pk)[:2]
    return render(request, "portfolio_detail.html", {"project": project, "related": related})


def contact(request):
    site = SiteSettings.load()
    if request.method == "POST":
        form = EnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save(commit=False)
            if request.user.is_authenticated:
                enquiry.user = request.user
            enquiry.save()
            send_mail(
                f"New enquiry from {enquiry.name}",
                f"Service: {enquiry.service}\nEmail: {enquiry.email}\nPhone: {enquiry.phone}\n"
                f"Business: {enquiry.business_name or '-'}\n\n{enquiry.brief}",
                None, [site.email], fail_silently=True,
            )
            messages.success(request, "Thanks — your enquiry is in. We'll get back to you shortly.")
            if request.user.is_authenticated:
                return redirect("portal_enquiry", pk=enquiry.pk)
            return redirect("contact")
    else:
        initial = {}
        if request.user.is_authenticated:
            u, p = request.user, get_profile(request.user)
            initial.update(name=u.first_name, email=u.email, phone=p.phone, business_name=p.business_name)
        svc = Service.objects.filter(slug=request.GET.get("service", ""), is_active=True).first()
        if svc:
            initial["service"] = svc
        form = EnquiryForm(initial=initial)
    return render(request, "contact.html", {"form": form, "faqs": FAQ.objects.filter(is_active=True)})


def not_found(request, exception=None):
    return render(request, "404.html", status=404)


# -------------------------------------------------------------------- auth
class RoleLoginView(LoginView):
    template_name = "auth/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or reverse("dash_home" if self.request.user.is_staff else "portal_home")


def register(request):
    if request.user.is_authenticated:
        return redirect("dash_home" if request.user.is_staff else "portal_home")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        # Attach any earlier guest enquiries made with the same email
        Enquiry.objects.filter(user__isnull=True, email__iexact=user.email).update(user=user)
        login(request, user)
        messages.success(request, "Welcome aboard. Your portal is ready.")
        return redirect("portal_home")
    return render(request, "auth/register.html", {"form": form})


# ------------------------------------------------------------ customer portal
@login_required
def portal_home(request):
    enquiries = request.user.enquiries.select_related("service")
    counts = {k: 0 for k, _ in Enquiry.STATUSES}
    for e in enquiries:
        counts[e.status] += 1
    return render(request, "portal/home.html", {
        "enquiries": enquiries,
        "counts": [(label, counts[k]) for k, label in Enquiry.STATUSES],
    })


@login_required
def portal_enquiry(request, pk):
    enquiry = get_object_or_404(Enquiry, pk=pk, user=request.user)
    return render(request, "portal/enquiry.html", {"enquiry": enquiry})


@login_required
def portal_profile(request):
    form = ProfileForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect("portal_profile")
    return render(request, "portal/profile.html", {"form": form})


class PortalPasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = "portal/password.html"
    form_class = StyledPasswordChangeForm
    success_url = reverse_lazy("portal_profile")
    success_message = "Password changed."


# ---------------------------------------------------------- studio dashboard
def staff_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not request.user.is_staff:
            messages.error(request, "That area is for the studio team only.")
            return redirect("portal_home")
        return view(request, *args, **kwargs)
    return wrapper


CRUD = {
    "projects": {"model": Project, "form": ProjectForm, "label": "Project", "plural": "Portfolio projects",
                 "cols": ["title", "category", "is_demo", "is_featured", "order"]},
    "services": {"model": Service, "form": ServiceForm, "label": "Service", "plural": "Services",
                 "cols": ["title", "icon", "order", "is_active"]},
    "testimonials": {"model": Testimonial, "form": TestimonialForm, "label": "Testimonial", "plural": "Testimonials",
                     "cols": ["name", "company", "is_published"]},
    "faqs": {"model": FAQ, "form": FAQForm, "label": "FAQ", "plural": "FAQs",
             "cols": ["question", "order", "is_active"]},
}


def get_cfg(key):
    cfg = CRUD.get(key)
    if not cfg:
        raise Http404
    return cfg


def _cell(obj, name):
    field = obj._meta.get_field(name)
    if field.choices:
        return getattr(obj, f"get_{name}_display")()
    val = getattr(obj, name)
    return ("Yes" if val else "No") if isinstance(val, bool) else val


@staff_required
def dash_home(request):
    by_status = {r["status"]: r["c"] for r in Enquiry.objects.values("status").annotate(c=Count("id"))}
    return render(request, "studio/home.html", {
        "status_counts": [(label, by_status.get(k, 0)) for k, label in Enquiry.STATUSES],
        "recent": Enquiry.objects.select_related("service")[:6],
        "content_counts": [(c["plural"], c["model"].objects.count(), k) for k, c in CRUD.items()],
        "customers": User.objects.filter(is_staff=False).count(),
    })


@staff_required
def dash_list(request, key):
    cfg = get_cfg(key)
    model = cfg["model"]
    rows = [(o, [_cell(o, c) for c in cfg["cols"]]) for o in model.objects.all()]
    headers = [model._meta.get_field(c).verbose_name.capitalize() for c in cfg["cols"]]
    return render(request, "studio/list.html", {"cfg": cfg, "key": key, "rows": rows, "headers": headers})


@staff_required
def dash_edit(request, key, pk=None):
    cfg = get_cfg(key)
    obj = get_object_or_404(cfg["model"], pk=pk) if pk else None
    form = cfg["form"](request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"{cfg['label']} saved.")
        return redirect("dash_list", key=key)
    return render(request, "studio/form.html", {"cfg": cfg, "key": key, "obj": obj, "form": form})


@staff_required
def dash_delete(request, key, pk):
    cfg = get_cfg(key)
    obj = get_object_or_404(cfg["model"], pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, f"{cfg['label']} deleted.")
        return redirect("dash_list", key=key)
    return render(request, "studio/confirm_delete.html", {"cfg": cfg, "key": key, "obj": obj})


@staff_required
def dash_settings(request):
    form = SiteSettingsForm(request.POST or None, instance=SiteSettings.load())
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Site settings saved.")
        return redirect("dash_settings")
    return render(request, "studio/settings.html", {"form": form})


@staff_required
def dash_enquiries(request):
    status = request.GET.get("status", "")
    qs = Enquiry.objects.select_related("service", "user")
    if status in dict(Enquiry.STATUSES):
        qs = qs.filter(status=status)
    return render(request, "studio/enquiries.html", {"enquiries": qs, "status": status, "statuses": Enquiry.STATUSES})


@staff_required
def dash_enquiry(request, pk):
    enquiry = get_object_or_404(Enquiry, pk=pk)
    form = EnquiryAdminForm(request.POST or None, instance=enquiry)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Enquiry updated — the client sees this in their portal.")
        return redirect("dash_enquiry", pk=pk)
    return render(request, "studio/enquiry.html", {"enquiry": enquiry, "form": form})


@staff_required
@require_POST
def dash_enquiry_delete(request, pk):
    get_object_or_404(Enquiry, pk=pk).delete()
    messages.success(request, "Enquiry deleted.")
    return redirect("dash_enquiries")
