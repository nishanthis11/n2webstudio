import re
from urllib.parse import quote

from django.conf import settings
from django.db import models
from django.utils.text import slugify


def unique_slug(instance, source):
    base = slugify(source)[:80] or "item"
    slug, n = base, 2
    while instance.__class__.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
        slug = f"{base}-{n}"
        n += 1
    return slug


class SiteSettings(models.Model):
    """Single row that powers site-wide content, contact details and stats."""

    studio_name = models.CharField(max_length=80, default="N2 Web Studio")
    hero_title = models.CharField(
        max_length=200, default="We Build Digital Experiences That Grow Your Business"
    )
    hero_subtitle = models.TextField(
        default="N2 Web Studio designs and develops fast, responsive websites and custom web "
        "solutions for businesses ready to stand out online."
    )
    email = models.EmailField(default="n2webstudioo@gmail.com")
    phone = models.CharField(max_length=30, blank=True)
    whatsapp_number = models.CharField(
        max_length=20, blank=True,
        help_text="Digits with country code, e.g. 919876543210. Leave empty to link the button to the contact page.",
    )
    whatsapp_message = models.CharField(
        max_length=200, default="Hi N2 Web Studio, I'd like to discuss a project."
    )
    location = models.CharField(max_length=120, blank=True)
    who_we_are = models.TextField(
        default="N2 Web Studio is a web design and development studio. We pair considered design "
        "with clean engineering to build websites that look sharp and perform for the business behind them."
    )
    vision = models.TextField(
        default="To be the studio businesses trust to turn ideas into digital products that last."
    )
    mission = models.TextField(
        default="To deliver honest, well-crafted web solutions with clear communication at every step."
    )
    stat_projects_delivered = models.PositiveIntegerField("Projects delivered", default=0, help_text="Stats with value 0 are hidden.")
    stat_happy_clients = models.PositiveIntegerField("Clients served", default=0)
    stat_years = models.PositiveIntegerField("Years of experience", default=0)
    stat_response_hours = models.PositiveIntegerField("Hours to first reply", default=0)

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return "Site settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def whatsapp_url(self):
        digits = re.sub(r"\D", "", self.whatsapp_number or "")
        return f"https://wa.me/{digits}?text={quote(self.whatsapp_message)}" if digits else ""


class Service(models.Model):
    title = models.CharField(max_length=80)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(max_length=40, default="code", help_text="A Lucide icon name, e.g. code, smartphone, pen-tool.")
    summary = models.TextField()
    deliverables = models.TextField(blank=True, help_text="One deliverable per line.")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.title)
        super().save(*args, **kwargs)

    @property
    def deliverable_list(self):
        return [x.strip() for x in self.deliverables.splitlines() if x.strip()]


class Project(models.Model):
    CATEGORIES = [
        ("website", "Website"),
        ("business", "Business Website"),
        ("uiux", "UI/UX Design"),
        ("custom", "Custom Solution"),
    ]
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORIES, default="website")
    summary = models.CharField(max_length=220)
    description = models.TextField(blank=True)
    tech_stack = models.CharField(max_length=200, blank=True, help_text="Comma separated, e.g. Django, JavaScript, MySQL")
    image = models.ImageField(upload_to="projects/", blank=True)
    live_url = models.URLField(blank=True)
    is_demo = models.BooleanField(default=False, help_text="Tick for concept/demo work so it is labelled publicly.")
    is_featured = models.BooleanField(default=False, help_text="Show on the home page.")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.title)
        super().save(*args, **kwargs)

    @property
    def tech_list(self):
        return [x.strip() for x in self.tech_stack.split(",") if x.strip()]


class Testimonial(models.Model):
    name = models.CharField(max_length=80)
    role = models.CharField(max_length=80, blank=True)
    company = models.CharField(max_length=80, blank=True)
    quote = models.TextField(help_text="Only add words a real client has given you permission to publish.")
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.name} ({self.company})" if self.company else self.name


class FAQ(models.Model):
    question = models.CharField(max_length=200)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=20, blank=True)
    business_name = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f"Profile of {self.user}"


def get_profile(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


class Enquiry(models.Model):
    STATUSES = [
        ("pending", "Pending"),
        ("review", "In Review"),
        ("progress", "In Progress"),
        ("completed", "Completed"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="enquiries")
    name = models.CharField(max_length=80)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    business_name = models.CharField(max_length=120, blank=True)
    service = models.ForeignKey(Service, null=True, blank=True, on_delete=models.SET_NULL, related_name="enquiries")
    brief = models.TextField()
    status = models.CharField(max_length=12, choices=STATUSES, default="pending")
    studio_note = models.TextField("Note to client", blank=True, help_text="Visible to the client in their portal.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "enquiries"

    def __str__(self):
        return f"#{self.pk} {self.name} – {self.get_status_display()}"

    @property
    def steps(self):
        keys = [k for k, _ in self.STATUSES]
        idx = keys.index(self.status)
        return [
            {"label": label, "state": "done" if i < idx else "current" if i == idx else "todo"}
            for i, (_, label) in enumerate(self.STATUSES)
        ]
