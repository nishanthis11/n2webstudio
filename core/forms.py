from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from django.db.models import Q

from .models import FAQ, Enquiry, Project, Profile, Service, SiteSettings, Testimonial, get_profile

User = get_user_model()
phone_validator = RegexValidator(r"^[0-9+\-\s()]{7,20}$", "Enter a valid phone number (digits, +, spaces, dashes).")


class StyledMixin:
    """Adds design-system classes to every widget."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            w = f.widget
            if isinstance(w, forms.CheckboxInput):
                w.attrs.setdefault("class", "check")
            elif not w.is_hidden:
                w.attrs.setdefault("class", "input")
            if isinstance(w, forms.Textarea):
                w.attrs.setdefault("rows", 5)


# ---------- public ----------
class EnquiryForm(StyledMixin, forms.ModelForm):
    phone = forms.CharField(max_length=20, validators=[phone_validator])
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}))  # honeypot

    class Meta:
        model = Enquiry
        fields = ["name", "email", "phone", "business_name", "service", "brief"]
        labels = {"business_name": "Business name", "brief": "Project brief"}
        widgets = {"brief": forms.Textarea(attrs={"rows": 6, "placeholder": "Tell us about your business, goals and timeline."})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service"].queryset = Service.objects.filter(is_active=True)
        self.fields["service"].empty_label = "Select a service"
        self.fields["service"].required = True
        self.fields["business_name"].required = False

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Spam detected.")
        return ""

    def clean_brief(self):
        brief = self.cleaned_data["brief"].strip()
        if len(brief) < 20:
            raise forms.ValidationError("Please share a little more detail (at least 20 characters).")
        return brief


class LoginForm(StyledMixin, AuthenticationForm):
    username = forms.CharField(label="Email or username", widget=forms.TextInput(attrs={"autofocus": True}))

    def clean_username(self):
        value = self.cleaned_data["username"].strip()
        user = User.objects.filter(username__iexact=value).first() or User.objects.filter(email__iexact=value).first()
        return user.username if user else value


class RegisterForm(StyledMixin, forms.Form):
    full_name = forms.CharField(max_length=80)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20, required=False, validators=[phone_validator])
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(Q(username__iexact=email) | Q(email__iexact=email)).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        data = super().clean()
        p1, p2 = data.get("password1"), data.get("password2")
        if p1 and p2:
            if p1 != p2:
                self.add_error("password2", "Passwords do not match.")
            else:
                try:
                    validate_password(p1)
                except forms.ValidationError as e:
                    self.add_error("password1", e)
        return data

    def save(self):
        d = self.cleaned_data
        user = User.objects.create_user(username=d["email"], email=d["email"], password=d["password1"], first_name=d["full_name"])
        Profile.objects.create(user=user, phone=d.get("phone", ""))
        return user


# ---------- customer portal ----------
class ProfileForm(StyledMixin, forms.Form):
    first_name = forms.CharField(label="Full name", max_length=80)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20, required=False, validators=[phone_validator])
    business_name = forms.CharField(max_length=120, required=False)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        profile = get_profile(user)
        kwargs.setdefault("initial", {"first_name": user.first_name, "email": user.email, "phone": profile.phone, "business_name": profile.business_name})
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("That email is already in use.")
        return email

    def save(self):
        d = self.cleaned_data
        self.user.first_name, self.user.email = d["first_name"], d["email"]
        self.user.save(update_fields=["first_name", "email"])
        profile = get_profile(self.user)
        profile.phone, profile.business_name = d["phone"], d["business_name"]
        profile.save()


class StyledPasswordChangeForm(StyledMixin, PasswordChangeForm):
    pass


# ---------- studio dashboard ----------
class ProjectForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Project
        exclude = ["slug", "created_at"]


class ServiceForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Service
        exclude = ["slug"]


class TestimonialForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = "__all__"


class FAQForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = FAQ
        fields = "__all__"


class SiteSettingsForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = "__all__"


class EnquiryAdminForm(StyledMixin, forms.ModelForm):
    class Meta:
        model = Enquiry
        fields = ["status", "studio_note"]
