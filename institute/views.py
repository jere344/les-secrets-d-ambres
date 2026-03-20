import random

from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, TemplateView, ListView

from .models import (
    BlogPost,
    Tag,
	Category,
	Certification,
	HomeFlexibleSection,
	Partner,
	RitualPoint,
	Service,
	SiteSettings,
	StandalonePage,
	Tariff,
	Testimonial,
)


PAGE_BODY_FALLBACKS = {
	"faq": (
		"<h2>Questions frequentes</h2>"
		"<h3>Comment reserver ?</h3><p>La reservation se fait par telephone ou via le lien de prise de rendez-vous.</p>"
		"<h3>Faites-vous un diagnostic avant soin ?</h3><p>Oui, chaque premiere visite commence par un echange sur vos besoins.</p>"
		"<h3>Y a-t-il des contre-indications ?</h3><p>Signalez toute sensibilite, grossesse ou traitement en cours avant le soin.</p>"
	),
	"mentions-legales": (
		"<h2>Mentions legales</h2>"
		"<p>Ce site est edite par Les secrets d'ambre. Les informations legales (raison sociale, contact, hebergeur) "
		"sont modifiables depuis l'administration.</p>"
	),
	"politique-confidentialite": (
		"<h2>Politique de confidentialite</h2>"
		"<p>Aucun suivi publicitaire ni cookie de tracking n'est utilise sur ce site. "
		"Les donnees eventuellement transmises via contact ou reservation sont utilisees uniquement pour la gestion des rendez-vous.</p>"
	),
	"rgpd": (
		"<h2>RGPD</h2>"
		"<p>Vous pouvez demander l'acces, la rectification ou la suppression de vos donnees en contactant l'institut. "
		"Aucun cookie analytique ni marketing n'est depose.</p>"
	),
}


def _meta_defaults(site_settings):
	title = site_settings.brand_name if site_settings else "Les secrets d'ambre"
	description = (
		site_settings.seo_description
		if site_settings and site_settings.seo_description
		else "Institut de beaute bio a Montpellier, soins orientaux et naturels."
	)
	keywords = site_settings.seo_keywords if site_settings else ""
	return {"meta_title": title, "meta_description": description, "meta_keywords": keywords}


def _partner_cloud(partners):
	rng = random.Random("les-secrets-d-ambre-partners")
	cloud = []
	count = len(partners)
	if not count:
		return cloud

	columns = 3 if count > 4 else 2
	for index, partner in enumerate(partners):
		row = index // columns
		column = index % columns
		top = 22 + row * 28 + rng.uniform(-3, 3)
		left = 18 + column * 32 + rng.uniform(-4, 4)
		rotation = rng.randint(-5, 5)
		size = rng.randint(88, 112)
		cloud.append(
			{
				"partner": partner,
				"top": round(max(12, min(88, top)), 2),
				"left": round(max(12, min(88, left)), 2),
				"rotation": rotation,
				"size": size,
			}
		)

	return cloud


class HomeView(TemplateView):
	template_name = "institute/home.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['latest_posts'] = BlogPost.objects.all()[:3]
		settings_obj = SiteSettings.get_solo()
		tariff_prefetch = Prefetch(
			"tariffs",
			queryset=Tariff.objects.published().order_by("display_order", "id"),
			to_attr="prefetched_tariffs",
		)
		service_prefetch = Prefetch(
			"services",
			queryset=Service.objects.published()
			.prefetch_related(tariff_prefetch)
			.order_by("display_order", "name"),
		)
		categories = Category.objects.published().prefetch_related(
			service_prefetch
		)
		partners = list(Partner.objects.published())
		certifications = list(Certification.objects.published())

		context.update(
			{
				"settings_obj": settings_obj,
				"categories": categories,
				"ritual_points": RitualPoint.objects.published(),
				"flexible_sections": HomeFlexibleSection.objects.published(),
				"testimonials": Testimonial.objects.published(),
				"partner_cloud": _partner_cloud(partners),
				"certifications": certifications,
				"featured_services": Service.objects.published()
				.filter(is_featured=True)
				.select_related("category")
				.prefetch_related(tariff_prefetch)[:9],
				"highlight_pages": StandalonePage.objects.published()
				.filter(show_in_nav=True)
				.exclude(slug__in=["mentions-legales", "politique-confidentialite", "rgpd"])[:3],
			}
		)
		context.update(_meta_defaults(settings_obj))
		return context


class CategoryDetailView(DetailView):
	template_name = "institute/category_detail.html"
	model = Category
	slug_field = "slug"
	slug_url_kwarg = "slug"
	context_object_name = "category"

	def get_queryset(self):
		tariff_prefetch = Prefetch(
			"tariffs",
			queryset=Tariff.objects.published().order_by("display_order", "id"),
			to_attr="prefetched_tariffs",
		)
		return Category.objects.published().prefetch_related(
			Prefetch(
				"services",
				queryset=Service.objects.published()
				.prefetch_related(tariff_prefetch)
				.order_by("display_order", "name"),
			)
		)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		category = self.object
		settings_obj = SiteSettings.get_solo()
		context["services"] = category.services.published()
		context.update(
			{
				"meta_title": category.seo_title or category.title,
				"meta_description": category.seo_description
				or (category.short_intro[:150] if category.short_intro else ""),
				"meta_keywords": category.seo_keywords,
				"settings_obj": settings_obj,
			}
		)
		return context


class ServiceDetailView(DetailView):
	template_name = "institute/service_detail.html"
	model = Service
	slug_field = "slug"
	slug_url_kwarg = "slug"
	context_object_name = "service"

	def get_queryset(self):
		tariff_prefetch = Prefetch(
			"tariffs",
			queryset=Tariff.objects.published().order_by("display_order", "id"),
			to_attr="prefetched_tariffs",
		)
		return Service.objects.published().select_related("category").prefetch_related(tariff_prefetch)

	def get_object(self, queryset=None):
		queryset = queryset or self.get_queryset()
		return get_object_or_404(
			queryset,
			slug=self.kwargs["slug"],
			category__slug=self.kwargs["category_slug"],
		)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		service = self.object
		settings_obj = SiteSettings.get_solo()
		context["tariffs"] = service.tariffs.published()
		context["siblings"] = (
			service.category.services.published()
			.exclude(pk=service.pk)
			.prefetch_related(
				Prefetch(
					"tariffs",
					queryset=Tariff.objects.published().order_by("display_order", "id"),
					to_attr="prefetched_tariffs",
				)
			)
		)
		context.update(
			{
				"meta_title": service.seo_title or f"{service.name} | {service.category.title}",
				"meta_description": service.seo_description
				or (service.short_description[:150] if service.short_description else ""),
				"meta_keywords": service.category.seo_keywords,
				"settings_obj": settings_obj,
			}
		)
		return context


class StandalonePageDetailView(DetailView):
	template_name = "institute/page_detail.html"
	model = StandalonePage
	slug_field = "slug"
	slug_url_kwarg = "slug"
	context_object_name = "page"

	def get_queryset(self):
		return StandalonePage.objects.published()

	def get_object(self, queryset=None):
		queryset = queryset or self.get_queryset()
		slug = self.kwargs["slug"]
		if slug in {"politique-confidentialite", "rgpd"}:
			merged_legal = queryset.filter(slug="mentions-legales").first()
			if merged_legal:
				return merged_legal
		return get_object_or_404(queryset, slug=slug)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		page = self.object
		settings_obj = SiteSettings.get_solo()
		resolved_body_html = page.body_html or PAGE_BODY_FALLBACKS.get(page.slug, "")
		context.update(
			{
				"meta_title": page.seo_title or page.title,
				"meta_description": page.seo_description
				or (page.summary[:150] if page.summary else ""),
				"meta_keywords": page.seo_keywords,
				"page_body_html": resolved_body_html,
				"settings_obj": settings_obj,
			}
		)
		return context


def robots_txt(_request):
	lines = [
		"User-agent: *",
		"Allow: /",
		"Disallow: /admin/",
		"Disallow: /summernote/",
		"Sitemap: /sitemap.xml",
	]
	return HttpResponse("\n".join(lines), content_type="text/plain")


class BlogListView(ListView):
    model = BlogPost
    template_name = "institute/blog_list.html"
    context_object_name = "posts"
    paginate_by = 12

    def get_queryset(self):
        qs = BlogPost.objects.published().prefetch_related('tags')
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            qs = qs.filter(tags__slug=tag_slug)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_tags"] = Tag.objects.all()
        context["current_tag"] = self.request.GET.get('tag')
        context["meta_title"] = "Le Blog - Les secrets d'ambre"
        return context

class BlogDetailView(DetailView):
    model = BlogPost
    template_name = "institute/blog_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return BlogPost.objects.published().prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["meta_title"] = f"{self.object.title} - Les secrets d'ambre"
        if self.object.summary:
            context["meta_description"] = self.object.summary
        return context
