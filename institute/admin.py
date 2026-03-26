from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin, SummernoteModelAdminMixin, SummernoteInlineModelAdmin

from .models import (
	Category,
	Certification,
	HomeFlexibleSection,
	GalleryImage,
	Partner,
	RitualPoint,
	Service,
	SiteSettings,
	StandalonePage,
	Tariff,
	Testimonial,
	Tag,
	BlogPost,
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
	list_display = ("brand_name", "contact_phone", "booking_url")
	fieldsets = (
		(
			"Identite",
			{
				"fields": (
					"brand_name",
					"logo",
					"tagline",
					"hero_title",
					"hero_subtitle",
					"hero_image",
				)
			},
		),
		(
			"Contact",
			{
				"fields": (
					"contact_phone",
					"contact_phone_display",
					"address_line",
					"postal_code_city",
					"opening_hours",
					"gps_notice",
					"referral_offer_text",
				)
			},
		),
		(
			"Reseaux et reservation",
			{
				"fields": (
					"booking_label",
					"booking_url",
					"instagram_url",
					"facebook_url",
					"tiktok_url",
					"youtube_url",
					"linkedin_url",
					"tripadvisor_url",
					"google_maps_url",
					"map_embed_url",
					"map_title",
				)
			},
		),
		(
			"SEO global",
			{
				"fields": (
					"seo_description",
					"seo_keywords",
					"footer_note",
				)
			},
		),
	)

	def has_add_permission(self, request):
		if SiteSettings.objects.exists():
			return False
		return super().has_add_permission(request)


class ServiceInline(admin.TabularInline):
	model = Service
	extra = 0
	fields = (
		"name",
		"slug",
		"display_order",
		"is_published",
	)
	show_change_link = True


class TariffInline(SummernoteInlineModelAdmin, admin.StackedInline):
	summernote_fields = ("details_html",)
	model = Tariff
	extra = 1
	show_change_link = True
	fields = (
		"label",
		"duration_text",
		"price_label",
		"promo_price_label",
		"price_from",
		"price_to",
		"notes",
		"details_html",
		"display_order",
		"is_published",
	)


@admin.register(Category)
class CategoryAdmin(SummernoteModelAdmin):
	list_display = ("title", "display_order", "is_published", "updated_at")
	list_filter = ("is_published",)
	search_fields = ("title", "short_intro", "seo_keywords")
	prepopulated_fields = {"slug": ("title",)}
	inlines = [ServiceInline]
	summernote_fields = ("body_html",)
	fieldsets = (
		(
			"Contenu",
			{
				"fields": (
					"title",
					"slug",
					"short_intro",
					"body_html",
					"cover_image",
					"legacy_url",
				)
			},
		),
		(
			"Actions",
			{"fields": ("cta_label", "cta_url", "display_order", "is_published")},
		),
		(
			"SEO",
			{"fields": ("seo_title", "seo_description", "seo_keywords")},
		),
	)


@admin.register(Service)
class ServiceAdmin(SummernoteModelAdmin):
	list_display = (
		"name",
		"category",
		"first_tariff_label",
		"display_order",
		"is_featured",
		"is_published",
	)
	list_filter = ("category", "is_featured", "is_published")
	list_select_related = ("category",)
	search_fields = ("name", "short_description", "seo_title")
	prepopulated_fields = {"slug": ("name",)}
	inlines = [TariffInline]
	summernote_fields = ("details_html",)
	fieldsets = (
		(
			"Infos",
			{
				"fields": (
					"category",
					"name",
					"slug",
					"short_description",
					"details_html",
					"image",
				)
			},
		),
		("Reservation", {"fields": ("booking_url",)}),
		(
			"Publication",
			{"fields": ("display_order", "is_featured", "is_published")},
		),
		(
			"SEO",
			{"fields": ("seo_title", "seo_description")},
		),
	)

	@admin.display(description="Tarif d'appel")
	def first_tariff_label(self, obj):
		return obj.from_price_label()


@admin.register(Tariff)
class TariffAdmin(SummernoteModelAdmin):
	list_display = ("label", "service", "price_label", "duration_text", "display_order", "is_published")
	list_filter = ("is_published", "service__category")
	list_select_related = ("service", "service__category")
	search_fields = ("label", "service__name", "service__category__title", "price_label")
	summernote_fields = ("details_html",)
	fields = (
		"service",
		"label",
		"duration_text",
		"price_label",
		"promo_price_label",
		"price_from",
		"price_to",
		"notes",
		"details_html",
		"display_order",
		"is_published",
	)


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
	list_display = ("name", "display_order", "is_published")
	list_filter = ("is_published",)
	search_fields = ("name", "slug")
	prepopulated_fields = {"slug": ("name",)}
	fields = (
		"name",
		"slug",
		"description",
		"website_url",
		"image",
		"external_image_url",
		"display_order",
		"is_published",
	)


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
	list_display = ("__str__", "image_preview", "is_featured", "display_order", "is_published")
	list_filter = ("is_published", "is_featured")
	search_fields = ("title",)
	list_editable = ("is_featured", "display_order", "is_published")

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
	list_display = ("name", "display_order", "is_published")
	list_filter = ("is_published",)
	search_fields = ("name", "slug")
	prepopulated_fields = {"slug": ("name",)}
	fields = (
		"name",
		"slug",
		"website_url",
		"image",
		"external_image_url",
		"display_order",
		"is_published",
	)


@admin.register(RitualPoint)
class RitualPointAdmin(admin.ModelAdmin):
	list_display = ("title", "icon_class", "display_order", "is_published")
	list_filter = ("is_published",)
	search_fields = ("title", "text", "icon_class")
	fields = ("title", "text", "icon_class", "display_order", "is_published")


@admin.register(HomeFlexibleSection)
class HomeFlexibleSectionAdmin(SummernoteModelAdmin):
	list_display = ("title", "display_order", "is_published")
	list_filter = ("is_published",)
	search_fields = ("title", "subtitle", "body_html")
	summernote_fields = ("body_html",)
	fields = (
		"title",
		"subtitle",
		"body_html",
		"image",
		"external_image_url",
		"video_embed_url",
		"cta_label",
		"cta_url",
		"display_order",
		"is_published",
	)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
	list_display = ("name", "stars", "display_order", "is_published")
	list_filter = ("is_published", "stars")
	search_fields = ("name", "text")
	fields = ("name", "stars", "text", "display_order", "is_published")


@admin.register(StandalonePage)
class StandalonePageAdmin(SummernoteModelAdmin):
	list_display = ("title", "show_in_nav", "nav_order", "is_published", "updated_at")
	list_filter = ("show_in_nav", "is_published")
	search_fields = ("title", "summary", "seo_keywords")
	prepopulated_fields = {"slug": ("title",)}
	summernote_fields = ("body_html",)
	fieldsets = (
		(
			"Contenu",
			{"fields": ("title", "slug", "summary", "body_html", "hero_image")},
		),
		(
			"Menu",
			{"fields": ("show_in_nav", "nav_order", "is_published")},
		),
		(
			"SEO",
			{"fields": ("seo_title", "seo_description", "seo_keywords")},
		),
	)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(BlogPost)
class BlogPostAdmin(SummernoteModelAdmin):
    list_display = ('title', 'created_at', 'is_published')
    list_filter = ('is_published', 'tags')
    search_fields = ('title', 'summary')
    prepopulated_fields = {'slug': ('title',)}
    summernote_fields = ('content',)
    filter_horizontal = ('tags',)
