from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class PublishedQuerySet(models.QuerySet):
	def published(self):
		return self.filter(is_published=True)


class SiteSettings(models.Model):
	brand_name = models.CharField(max_length=180, default="Les secrets d'ambre")
	logo = models.ImageField(upload_to="branding/", blank=True)
	tagline = models.CharField(
		max_length=220,
		default="Institut de beaute bio a Montpellier - soins personnalises",
	)
	hero_title = models.CharField(max_length=200, default="Rituels beaute et bien-etre")
	hero_subtitle = models.TextField(
		default=(
			"Soins orientaux, naturels et personnalises. "
			"Votre institut vous accompagne avec douceur et expertise."
		),
		verbose_name="Sous-titre hero"
	)
	hero_image = models.ImageField(upload_to="hero/", blank=True, verbose_name="Image hero (En-tête)")
	contact_phone = models.CharField(max_length=32, blank=True, verbose_name="Téléphone de contact")
	contact_phone_display = models.CharField(max_length=32, blank=True)
	address_line = models.CharField(max_length=200, blank=True)
	postal_code_city = models.CharField(max_length=120, blank=True)
	opening_hours = models.CharField(max_length=180, blank=True)
	gps_notice = models.CharField(max_length=220, blank=True)
	referral_offer_text = models.CharField(max_length=220, blank=True)
	booking_label = models.CharField(max_length=80, default="Prendre rendez-vous")
	booking_url = models.URLField(blank=True)
	instagram_url = models.URLField(blank=True)
	facebook_url = models.URLField(blank=True)
	tiktok_url = models.URLField(blank=True)
	youtube_url = models.URLField(blank=True)
	linkedin_url = models.URLField(blank=True)
	tripadvisor_url = models.URLField(blank=True)
	google_maps_url = models.URLField(blank=True, verbose_name="Lien Google Maps")
	map_embed_url = models.URLField(blank=True, verbose_name="Lien iframe de la carte")
	map_title = models.CharField(max_length=140, blank=True, verbose_name="Titre de la carte")
	seo_description = models.TextField(blank=True, verbose_name="Description globale (SEO)")
	seo_keywords = models.CharField(max_length=255, blank=True, verbose_name="Mots-clés (SEO)")
	footer_note = models.CharField(max_length=240, blank=True, verbose_name="Texte pied de page (footer)")

	class Meta:
		verbose_name = "Parametres du site"
		verbose_name_plural = "Parametres du site"

	def save(self, *args, **kwargs):
		self.pk = 1
		super().save(*args, **kwargs)

	@classmethod
	def get_solo(cls):
		return cls.objects.first()

	def __str__(self):
		return "Parametres du site"


class Category(models.Model):
	title = models.CharField(max_length=180)
	slug = models.SlugField(max_length=180, unique=True)
	short_intro = models.TextField(blank=True)
	body_html = models.TextField(blank=True)
	cover_image = models.ImageField(upload_to="categories/", blank=True)
	legacy_url = models.URLField(blank=True)
	cta_label = models.CharField(max_length=80, blank=True, verbose_name="Texte du bouton")
	cta_url = models.URLField(blank=True, verbose_name="Lien du bouton")
	display_order = models.PositiveIntegerField(default=0, verbose_name='Ordre d\'affichage')
	is_published = models.BooleanField(default=True, verbose_name='En ligne (publiée)')
	seo_title = models.CharField(max_length=70, blank=True, verbose_name="Titre pour moteur de recherche (SEO)")
	seo_description = models.CharField(max_length=160, blank=True, verbose_name="Description (SEO)")
	seo_keywords = models.CharField(max_length=255, blank=True, verbose_name="Mots-clés (SEO)")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	objects = PublishedQuerySet.as_manager()

	class Meta:
		ordering = ["display_order", "title"]

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse("category-detail", kwargs={"slug": self.slug})


class Service(models.Model):
	category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="services")
	name = models.CharField(max_length=180)
	slug = models.SlugField(max_length=180)
	short_description = models.TextField(blank=True)
	details_html = models.TextField(blank=True)
	booking_url = models.URLField(blank=True)
	image = models.ImageField(upload_to="services/", blank=True)
	display_order = models.PositiveIntegerField(default=0, verbose_name='Ordre d\'affichage')
	is_featured = models.BooleanField(default=False, verbose_name='Mis en avant')
	is_published = models.BooleanField(default=True, verbose_name='En ligne (publiée)')
	seo_title = models.CharField(max_length=70, blank=True, verbose_name="Titre pour moteur de recherche (SEO)")
	seo_description = models.CharField(max_length=160, blank=True, verbose_name="Description (SEO)")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	objects = PublishedQuerySet.as_manager()

	class Meta:
		ordering = ["display_order", "name"]
		constraints = [
			models.UniqueConstraint(fields=["category", "slug"], name="uniq_service_slug_by_category")
		]

	def __str__(self):
		return f"{self.category.title} - {self.name}"

	def get_absolute_url(self):
		return reverse(
			"service-detail",
			kwargs={"category_slug": self.category.slug, "slug": self.slug},
		)

	def first_tariff(self):
		prefetched = getattr(self, "prefetched_tariffs", None)
		if prefetched:
			return prefetched[0]
		return self.tariffs.published().first()

	def from_price_label(self):
		tariff = self.first_tariff()
		return tariff.formatted_price() if tariff else "Tarif sur demande"


class Tariff(models.Model):
	service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="tariffs")
	label = models.CharField(max_length=140, help_text="Ex: Solo, Duo, Cure 5 seances")
	duration_text = models.CharField(max_length=80, blank=True)
	price_label = models.CharField(max_length=80, help_text="Ex: 49EUR, 95-210EUR")
	promo_price_label = models.CharField(max_length=80, blank=True, help_text="Ex: 39EUR")
	image = models.ImageField(upload_to="tariffs/", blank=True, null=True, help_text="Image optionnelle pour le tarif")
	price_from = models.DecimalField(
		max_digits=8,
		decimal_places=2,
		null=True,
		blank=True,
		validators=[MinValueValidator(Decimal("0.00"))],
	)
	price_to = models.DecimalField(
		max_digits=8,
		decimal_places=2,
		null=True,
		blank=True,
		validators=[MinValueValidator(Decimal("0.00"))],
	)
	notes = models.TextField(blank=True)
	details_html = models.TextField(blank=True)
	display_order = models.PositiveIntegerField(default=0, verbose_name='Ordre d\'affichage')
	is_published = models.BooleanField(default=True, verbose_name='En ligne (publiée)')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	objects = PublishedQuerySet.as_manager()

	class Meta:
		ordering = ["display_order", "id"]

	def clean(self):
		if self.price_from is not None and self.price_to is not None and self.price_to < self.price_from:
			raise ValidationError({"price_to": "Le prix max doit etre superieur au prix min."})

	def __str__(self):
		return f"{self.service.name} - {self.label}: {self.price_label}"

	def formatted_price(self):
		from django.utils.html import format_html
		if self.promo_price_label:
			return format_html('<span class="price-old">{}</span> <strong class="price-new">{}</strong>', self.price_label, self.promo_price_label)
		return self.price_label


class Partner(models.Model):
	name = models.CharField(max_length=140)
	slug = models.SlugField(max_length=160, unique=True)
	website_url = models.URLField(blank=True)
	image = models.ImageField(upload_to="partners/", blank=True)
	external_image_url = models.URLField(blank=True)
	display_order = models.PositiveIntegerField(default=0, verbose_name='Ordre d\'affichage')
	is_published = models.BooleanField(default=True, verbose_name='En ligne (publiée)')

	objects = PublishedQuerySet.as_manager()

	class Meta:
		ordering = ["display_order", "name"]

	def __str__(self):
		return self.name


class Certification(models.Model):
	name = models.CharField(max_length=140)
	slug = models.SlugField(max_length=160, unique=True)
	description = models.TextField(blank=True)
	website_url = models.URLField(blank=True)
	image = models.ImageField(upload_to="certifications/", blank=True)
	external_image_url = models.URLField(blank=True)
	display_order = models.PositiveIntegerField(default=0, verbose_name='Ordre d\'affichage')
	is_published = models.BooleanField(default=True, verbose_name='En ligne (publiée)')

	objects = PublishedQuerySet.as_manager()

	class Meta:
		ordering = ["display_order", "name"]

	def __str__(self):
		return self.name


class RitualPoint(models.Model):
	title = models.CharField(max_length=140)
	text = models.TextField()
	icon_class = models.CharField(
		max_length=80,
		default="bi bi-stars",
		help_text=(
			"Classe Bootstrap Icons (ex: bi bi-stars). "
			"Banque d'icones: https://icons.getbootstrap.com/"
		),
	)
	display_order = models.PositiveIntegerField(default=0, verbose_name='Ordre d\'affichage')
	is_published = models.BooleanField(default=True, verbose_name='En ligne (publiée)')

	objects = PublishedQuerySet.as_manager()

	class Meta:
		ordering = ["display_order", "id"]

	def __str__(self):
		return self.title


class HomeFlexibleSection(models.Model):
	title = models.CharField(max_length=160)
	subtitle = models.CharField(max_length=220, blank=True)
	body_html = models.TextField(blank=True)
	image = models.ImageField(upload_to="home/flexible/", blank=True)
	external_image_url = models.URLField(blank=True)
	video_embed_url = models.URLField(
		blank=True,
		help_text="URL d'embed video (YouTube, Vimeo, etc.).",
	)
	cta_label = models.CharField(max_length=80, blank=True, verbose_name="Texte du bouton")
	cta_url = models.URLField(blank=True, verbose_name="Lien du bouton")
	display_order = models.PositiveIntegerField(default=0, verbose_name='Ordre d\'affichage')
	is_published = models.BooleanField(default=True, verbose_name='En ligne (publiée)')

	objects = PublishedQuerySet.as_manager()

	class Meta:
		ordering = ["display_order", "id"]

	def __str__(self):
		return self.title


class Testimonial(models.Model):
	name = models.CharField(max_length=140)
	stars = models.PositiveSmallIntegerField(
		default=5,
		validators=[MinValueValidator(1), MaxValueValidator(5)],
	)
	text = models.TextField()
	display_order = models.PositiveIntegerField(default=0, verbose_name='Ordre d\'affichage')
	is_published = models.BooleanField(default=True, verbose_name='En ligne (publiée)')

	objects = PublishedQuerySet.as_manager()

	class Meta:
		ordering = ["display_order", "id"]

	def __str__(self):
		return f"{self.name} ({self.stars}/5)"


class StandalonePage(models.Model):
	title = models.CharField(max_length=180)
	slug = models.SlugField(max_length=180, unique=True)
	summary = models.TextField(blank=True)
	body_html = models.TextField(blank=True)
	hero_image = models.ImageField(upload_to="pages/", blank=True)
	show_in_nav = models.BooleanField(default=True, verbose_name="Afficher dans le menu")
	nav_order = models.PositiveIntegerField(default=0, verbose_name="Ordre dans le menu")
	is_published = models.BooleanField(default=True, verbose_name='En ligne (publiée)')
	seo_title = models.CharField(max_length=70, blank=True, verbose_name="Titre pour moteur de recherche (SEO)")
	seo_description = models.CharField(max_length=160, blank=True, verbose_name="Description (SEO)")
	seo_keywords = models.CharField(max_length=255, blank=True, verbose_name="Mots-clés (SEO)")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	objects = PublishedQuerySet.as_manager()

	class Meta:
		ordering = ["nav_order", "title"]

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse("page-detail", kwargs={"slug": self.slug})


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Nom du tag")
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.name

class BlogPost(models.Model):
    title = models.CharField(max_length=200, verbose_name="Titre de l'article")
    slug = models.SlugField(max_length=200, unique=True)
    image = models.ImageField(upload_to="blog/", blank=True, verbose_name="Image de couverture")
    summary = models.TextField(blank=True, verbose_name="Résumé rapide")
    content = models.TextField(verbose_name="Contenu de l'article")
    tags = models.ManyToManyField(Tag, blank=True, related_name="posts", verbose_name="Tags associés")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    is_published = models.BooleanField(default=True, verbose_name="Publié")

    objects = PublishedQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Article de blog"
        verbose_name_plural = "Articles de blog"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'slug': self.slug})
