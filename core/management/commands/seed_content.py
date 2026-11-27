from django.core.management.base import BaseCommand

from core.models import FAQ, Project, Service, SiteSettings

SERVICES = [
    ("Website Development", "code", "Fast, secure websites built on clean, maintainable code.",
     "Custom build on Django or static stack\nSEO-ready structure\nContact forms and integrations\nDeployment support"),
    ("Responsive Design", "smartphone", "Layouts that feel native on every screen size, from phones to wide monitors.",
     "Mobile-first layouts\nCross-browser testing\nPerformance tuning\nAccessible markup"),
    ("UI/UX Design", "pen-tool", "Interfaces shaped around how your customers actually think and behave.",
     "User flows and wireframes\nVisual design system\nClickable prototypes\nDeveloper-ready handoff"),
    ("Business Websites", "briefcase", "Credible, conversion-minded websites for service businesses and growing brands.",
     "Home, About, Services, Contact\nLead capture and WhatsApp links\nContent guidance\nEasy content updates"),
    ("Custom Web Solutions", "layers", "Dashboards, portals and internal tools tailored to your workflow.",
     "Requirements workshop\nRole-based portals\nDatabase design\nAPI integrations"),
    ("Website Maintenance", "wrench", "Reliable upkeep so your site stays fast, secure and current.",
     "Updates and backups\nSecurity checks\nContent changes\nPerformance monitoring"),
]

FAQS = [
    ("How long does a typical website take?", "Most business websites take two to six weeks from kickoff, depending on scope and how quickly content and feedback arrive."),
    ("How much does a project cost?", "Pricing depends on pages, features and integrations. Send us a brief and we will reply with a clear, itemised quote."),
    ("Will my website work on mobile?", "Yes. Every site we build is responsive and tested on common phone, tablet and desktop sizes."),
    ("Can I update the content myself?", "Yes. We can build simple admin tools so you can edit text, images and listings without touching code."),
    ("Do you offer support after launch?", "We offer maintenance plans covering updates, backups, security checks and content changes."),
    ("How can I track my project?", "Create a free account, submit your enquiry while logged in, and follow its status live in your client portal."),
]

DEMOS = [
    ("Demo: Atelier Storefront", "business", "Concept storefront site for a fictional furniture brand.", "Django, HTML, CSS, JavaScript"),
    ("Demo: Northwind Dashboard", "custom", "Concept analytics dashboard showing role-based views and reporting.", "Django, SQLite, Chart.js"),
    ("Demo: Lumen Brand Site", "uiux", "Concept brand and UI exploration for a fictional design collective.", "Figma, HTML, CSS"),
]


class Command(BaseCommand):
    help = "Seed starter services, FAQs and clearly-labelled demo projects (safe to re-run)."

    def handle(self, *args, **opts):
        SiteSettings.load()
        if not Service.objects.exists():
            for i, (t, icon, s, d) in enumerate(SERVICES):
                Service.objects.create(title=t, icon=icon, summary=s, deliverables=d, order=i)
        if not FAQ.objects.exists():
            for i, (q, a) in enumerate(FAQS):
                FAQ.objects.create(question=q, answer=a, order=i)
        if not Project.objects.exists():
            for i, (t, c, s, tech) in enumerate(DEMOS):
                Project.objects.create(
                    title=t, category=c, summary=s, tech_stack=tech, is_demo=True, is_featured=True, order=i,
                    description=f"{s}\n\nThis is a demo project created by N2 Web Studio to illustrate our approach. "
                                "It is not work for a real client. Replace it with your own projects from the studio dashboard.",
                )
        self.stdout.write(self.style.SUCCESS("Starter content ready. No testimonials were created — add only real ones."))
