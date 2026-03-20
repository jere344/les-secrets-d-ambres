from django.core.management.base import BaseCommand
from django.db import transaction

from institute.models import (
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


CATEGORY_SEED = [
    {
        "title": "Hammam et sauna IR",
        "slug": "hammam-sauna-ir",
        "intro": "Rituels de purification, detente musculaire et bien-etre oriental.",
        "body": "<h2>Rituels autour du hammam</h2><p>Le hammam prepare la peau, detend le corps et soutient la recuperation. Les formules peuvent etre completees avec gommage, enveloppement, massage ou soin visage.</p>",
        "services": [
            {
                "name": "Seance Hammam ou Sauna IR",
                "slug": "seance-hammam-sauna-ir",
                "summary": "Acces individuel ou a plusieurs pour une detente immediate.",
                "details": "<p>Ideal avant un soin corps, un massage ou une seance minceur.</p>",
                "featured": True,
                "tariffs": [
                    {"label": "Solo", "duration": "45 min", "price": "49EUR", "promo": "42EUR", "notes": "Ideal pour preparer la peau avant un soin corps."},
                    {"label": "Duo (prix / personne)", "duration": "45 min", "price": "45EUR", "notes": "Version partagee pour une parenthese bien-etre a deux."},
                    {"label": "Trio (prix / personne)", "duration": "45 min", "price": "40EUR", "notes": "Format convivial adapte aux petits groupes."},
                ],
            },
            {
                "name": "Rituel Purete",
                "slug": "rituel-purete",
                "summary": "Hammam ou sauna IR + gommage corps.",
                "details": "<p>Un rituel express pour retrouver une peau douce et lumineuse.</p>",
                "tariffs": [
                    {"label": "Formule", "duration": "60 min", "price": "89EUR", "notes": "Purifie, lisse et laisse la peau lumineuse."},
                ],
            },
            {
                "name": "Rituel Evasion",
                "slug": "rituel-evasion",
                "summary": "Hammam + gommage + enveloppement + soin visage ethnique.",
                "details": "<p>Un soin global visage et corps pour une detente profonde.</p>",
                "tariffs": [
                    {"label": "Formule complete", "duration": "120 min", "price": "189EUR", "notes": "Rituel visage et corps pour une detente profonde."},
                ],
            },
        ],
    },
    {
        "title": "Soins visage",
        "slug": "soins-visage",
        "intro": "Protocoles anti-age, eclat et correction des imperfections.",
        "body": "<h2>Diagnostic + personnalisation</h2><p>Chaque protocole visage est adapte au type de peau et peut etre complete par des options ciblees.</p>",
        "services": [
            {
                "name": "Kobido mix Mukhabyangha",
                "slug": "kobido-mix-mukhabyangha",
                "summary": "Lifting naturel japonais et ayurvedique.",
                "details": "<p>Gestuelle profonde pour lisser, tonifier et redonner de l'eclat.</p>",
                "featured": True,
                "tariffs": [
                    {"label": "Seance", "duration": "60 min", "price": "85EUR", "promo": "75EUR", "notes": "Massage facial anti-age inspire des techniques japonaises."},
                    {"label": "Cure 5 seances", "duration": "5 x 60 min", "price": "315EUR", "notes": "Pour installer un resultat plus visible dans le temps."},
                ],
            },
            {
                "name": "Kobido mix plus",
                "slug": "kobido-mix-plus",
                "summary": "Kobido + soin Mer Morte.",
                "details": "<p>Effet tenseur et eclat avec actifs mineraux.</p>",
                "tariffs": [
                    {"label": "Seance", "duration": "75 min", "price": "109EUR", "notes": "Association kobido + actifs mineraux pour eclat immediat."},
                    {"label": "Cure 5 seances", "duration": "5 x 75 min", "price": "479EUR", "notes": "Cure anti-age progressive, ideale en entretien."},
                ],
            },
            {
                "name": "Peeling bio purifiant",
                "slug": "peeling-bio-purifiant",
                "summary": "Nettoyage profond et eclat du teint.",
                "details": "<p>Peeling au miel pour relancer le renouvellement cutane.</p>",
                "tariffs": [
                    {"label": "Seance", "duration": "45 min", "price": "69EUR", "notes": "Nettoyage profond et texture de peau affinee."},
                ],
            },
        ],
    },
    {
        "title": "Massage bio",
        "slug": "massage-bio",
        "intro": "Massages de relaxation et recup musculaire personnalises.",
        "body": "<h2>Massages sur mesure</h2><p>Les techniques sont adaptees a votre besoin: detente, drainage, energie ou relachement profond.</p>",
        "services": [
            {
                "name": "Massage signature oriental",
                "slug": "massage-signature-oriental",
                "summary": "Massage enveloppant aux huiles naturelles.",
                "details": "<p>Travail profond et progressif pour soulager les tensions.</p>",
                "featured": True,
                "tariffs": [
                    {"label": "Essentiel", "duration": "30 min", "price": "55EUR", "promo": "49EUR", "notes": "Detente express, focalisee sur les tensions principales."},
                    {"label": "Complet", "duration": "60 min", "price": "95EUR", "notes": "Equilibre global corps et esprit."},
                    {"label": "Immersion", "duration": "90 min", "price": "130EUR", "notes": "Experience profonde et enveloppante."},
                ],
            }
        ],
    },
    {
        "title": "Epilation bio",
        "slug": "epilation-bio",
        "intro": "Techniques douces: miel oriental, cire adaptee et protocole peau sensible.",
        "body": "<h2>Approche experte de la pilosite</h2><p>Chaque zone est epilee avec la methode la plus adaptee a votre peau et a votre poil.</p>",
        "services": [
            {
                "name": "Epilation orientale au miel",
                "slug": "epilation-orientale-miel",
                "summary": "Solution naturelle pour peaux sensibles et poils incarnes.",
                "details": "<p>Hydratation post-epilatoire et conseils personnalises.</p>",
                "tariffs": [
                    {"label": "Zone visage", "duration": "15 min", "price": "A partir de 12EUR", "notes": "Precision pour zones sensibles et finition nette."},
                    {"label": "Zone corps", "duration": "20-40 min", "price": "A partir de 18EUR", "notes": "Approche douce pour minimiser l'inconfort."},
                    {"label": "Forfait multi-zones", "duration": "45 min", "price": "Sur devis", "notes": "Personnalisation selon zones et frequence."},
                ],
            }
        ],
    },
    {
        "title": "Onglerie bio",
        "slug": "onglerie-bio",
        "intro": "Soins mains et pieds avec protocoles propres et produits respectueux.",
        "body": "<h2>Mains et pieds impeccables</h2><p>Manucure, pedicure et finition semi-permanente selon vos attentes.</p>",
        "services": [
            {
                "name": "Manucure soin",
                "slug": "manucure-soin",
                "summary": "Mise en forme, soin cuticules, hydratation.",
                "details": "<p>Un resultat net, elegant et naturel.</p>",
                "tariffs": [
                    {"label": "Manucure", "duration": "35 min", "price": "35EUR", "notes": "Mise en forme, cuticules et nutrition."},
                    {"label": "Manucure + semi-permanent", "duration": "60 min", "price": "49EUR", "notes": "Resultat longue tenue et fini brillant."},
                ],
            }
        ],
    },
]

PARTNER_SEED = [
    {
        "name": "CASSC Montpellier",
        "slug": "cassc-montpellier",
        "website_url": "https://www.cassc.fr/",
        "external_image_url": "https://dummyimage.com/420x260/e9c17d/5a2b1f&text=CASSC+Montpellier",
    },
    {
        "name": "Keepcool Social Sport",
        "slug": "keepcool-social-sport",
        "website_url": "https://www.keepcool.fr/",
        "external_image_url": "https://dummyimage.com/420x260/e9c17d/5a2b1f&text=Keepcool+Social+Sport",
    },
    {
        "name": "Palais des Thes",
        "slug": "palais-des-thes",
        "website_url": "https://www.palaisdesthes.com/",
        "external_image_url": "https://dummyimage.com/420x260/e9c17d/5a2b1f&text=Palais+des+Thes",
    },
    {
        "name": "Centre RNCP",
        "slug": "centre-rncp",
        "website_url": "https://www.francecompetences.fr/recherche/rncp/",
        "external_image_url": "https://dummyimage.com/420x260/e9c17d/5a2b1f&text=Centre+RNCP",
    },
    {
        "name": "Montpellier Business School",
        "slug": "montpellier-business-school",
        "website_url": "https://www.montpellier-bs.com/",
        "external_image_url": "https://dummyimage.com/420x260/e9c17d/5a2b1f&text=Montpellier+Business+School",
    },
    {
        "name": "Aroma-Zone",
        "slug": "aroma-zone",
        "website_url": "https://www.aroma-zone.com/",
        "external_image_url": "https://dummyimage.com/420x260/e9c17d/5a2b1f&text=Aroma+Zone",
    },
]

RITUAL_POINT_SEED = [
    {
        "title": "Rituels orientaux",
        "text": "Des protocoles inspires de traditions ancestrales, reinterpretes avec une execution contemporaine.",
        "icon_class": "bi bi-moon-stars",
    },
    {
        "title": "Approche naturelle",
        "text": "Produits selectionnes pour les peaux sensibles, avec priorite au confort et a la tolerance cutanee.",
        "icon_class": "bi bi-flower1",
    },
    {
        "title": "Tarification claire",
        "text": "Chaque soin propose plusieurs options de tarifs visibles sans avoir a parcourir des pages longues.",
        "icon_class": "bi bi-gem",
    },
    {
        "title": "Parcours personnalise",
        "text": "Structure categorie -> soin -> tarifs, parfaite pour reorganiser l'offre facilement depuis l'admin.",
        "icon_class": "bi bi-stars",
    },
]

HOME_FLEXIBLE_SEED = [
    {
        "title": "Avant / Apres, coulisses, videos",
        "subtitle": "Bloc libre personnalisable",
        "body_html": "<p>Utilisez cette zone pour publier vos nouveautes: videos, reels embed, resultats, focus produit, evenements ou offres saisonnieres.</p>",
        "external_image_url": "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=1100&q=80",
    },
    {
        "title": "Editorial maison",
        "subtitle": "Ajoutez vos propres sections",
        "body_html": "<p>Chaque bloc peut contenir un texte riche, une image ou une video. Vous pouvez les reordonner facilement depuis l'administration.</p>",
        "video_embed_url": "https://www.youtube.com/embed/x5R3xSQwo2s",
    },
]

TESTIMONIAL_SEED = [
    {
        "name": "Leila",
        "stars": 5,
        "text": "Accueil chaleureux, soins precis et ambiance vraiment unique. Je ressors apaisee a chaque visite.",
    },
    {
        "name": "Camille",
        "stars": 5,
        "text": "Le diagnostic est tres juste, les tarifs sont clairs et le resultat sur ma peau est visible des la premiere cure.",
    },
    {
        "name": "Nora",
        "stars": 4,
        "text": "J'adore la qualite des produits utilises et la facon de personnaliser chaque soin selon mon besoin du jour.",
    },
]

CERTIFICATION_SEED = [
    {"name": "Certification 01", "slug": "certification-01", "description": "Certification professionnalisante orientee qualite de service.", "external_image_url": "https://dummyimage.com/520x280/f1cf8f/5a2b1f&text=Certification+01"},
    {"name": "Certification 02", "slug": "certification-02", "description": "Validation des protocoles d'hygiene et de securite.", "external_image_url": "https://dummyimage.com/520x280/f1cf8f/5a2b1f&text=Certification+02"},
    {"name": "Certification 03", "slug": "certification-03", "description": "Approche soins visage et expertise peau sensible.", "external_image_url": "https://dummyimage.com/520x280/f1cf8f/5a2b1f&text=Certification+03"},
    {"name": "Certification 04", "slug": "certification-04", "description": "Perfectionnement massage bien-etre et detente profonde.", "external_image_url": "https://dummyimage.com/520x280/f1cf8f/5a2b1f&text=Certification+04"},
    {"name": "Certification 05", "slug": "certification-05", "description": "Specialisation rituels orientaux et modelages traditionnels.", "external_image_url": "https://dummyimage.com/520x280/f1cf8f/5a2b1f&text=Certification+05"},
    {"name": "Certification 06", "slug": "certification-06", "description": "Formation continue en cosmetique naturelle.", "external_image_url": "https://dummyimage.com/520x280/f1cf8f/5a2b1f&text=Certification+06"},
    {"name": "Certification 07", "slug": "certification-07", "description": "Qualification techniques de soin corps personnalise.", "external_image_url": "https://dummyimage.com/520x280/f1cf8f/5a2b1f&text=Certification+07"},
    {"name": "Certification 08", "slug": "certification-08", "description": "Conformite et excellence de la prise en charge cliente.", "external_image_url": "https://dummyimage.com/520x280/f1cf8f/5a2b1f&text=Certification+08"},
    {"name": "Certification 09", "slug": "certification-09", "description": "Attestation avancee en techniques esthetiques bio.", "external_image_url": "https://dummyimage.com/520x280/f1cf8f/5a2b1f&text=Certification+09"},
    {"name": "Certification 10", "slug": "certification-10", "description": "Certification relation client et conseil sur mesure.", "external_image_url": "https://dummyimage.com/520x280/f1cf8f/5a2b1f&text=Certification+10"},
]

PAGE_SEED = [
    {
        "title": "A propos",
        "slug": "a-propos",
        "summary": "Presentation de l'institut, de son approche et de ses valeurs.",
        "body": "<h2>Notre approche</h2><p>Les soins sont personnalises selon la peau, la sensibilite et les objectifs de chaque personne.</p>",
        "nav_order": 1,
        "show_in_nav": True,
    },
    {
        "title": "FAQ",
        "slug": "faq",
        "summary": "Questions frequentes avant votre rendez-vous.",
        "body": (
            "<h2>Questions frequentes</h2>"
            "<h3>Comment reserver un soin ?</h3><p>Par telephone ou via le bouton de reservation present sur le site.</p>"
            "<h3>Realisez-vous un diagnostic ?</h3><p>Oui, un echange est prevu pour adapter le soin a votre peau et votre objectif.</p>"
            "<h3>Que dois-je signaler avant la seance ?</h3><p>Merci d'indiquer toute sensibilite cutanee, grossesse ou traitement medical en cours.</p>"
        ),
        "nav_order": 2,
        "show_in_nav": True,
    },
    {
        "title": "Nous ecrire",
        "slug": "nous-ecrire",
        "summary": "Informations pratiques et moyens de contact.",
        "body": "<h2>Contact</h2><p>Par telephone ou via la plateforme de reservation en ligne.</p>",
        "nav_order": 3,
        "show_in_nav": True,
    },
    {
        "title": "Mentions legales",
        "slug": "mentions-legales",
        "summary": "Informations legales de l'institut.",
        "body": (
            "<h2>Mentions legales</h2>"
            "<p>Cette page est entierement editable depuis l'administration.</p>"
            "<p>Renseignez ici la raison sociale, l'adresse, le numero de telephone, l'email de contact, "
            "l'hebergeur et toute mention obligatoire applicable a votre activite.</p>"
        ),
        "nav_order": 90,
        "show_in_nav": False,
    },
    {
        "title": "Politique de confidentialite",
        "slug": "politique-confidentialite",
        "summary": "Gestion des donnees personnelles et cookies.",
        "body": (
            "<h2>Politique de confidentialite</h2>"
            "<p>Le site ne depose aucun cookie marketing ni de tracking.</p>"
            "<p>Les informations partagees lors d'une prise de contact ou reservation sont utilisees uniquement "
            "pour la gestion des rendez-vous.</p>"
        ),
        "nav_order": 91,
        "show_in_nav": False,
    },
    {
        "title": "RGPD",
        "slug": "rgpd",
        "summary": "Droits d'acces, rectification, suppression et opposition.",
        "body": (
            "<h2>RGPD</h2>"
            "<p>Vous pouvez demander l'acces, la rectification ou la suppression de vos donnees personnelles.</p>"
            "<p>Aucun cookie analytique ni publicitaire n'est utilise sur ce site.</p>"
        ),
        "nav_order": 92,
        "show_in_nav": False,
    },
]


class Command(BaseCommand):
    help = "Seed a structured non-empty content base with categories, cares and multiple tariffs."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing categories/services/tariffs/pages before seeding curated content.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            self._reset_content()
        self._upsert_site_settings()
        self._seed_categories()
        self._seed_pages()
        self._seed_ritual_points()
        self._seed_flexible_sections()
        self._seed_testimonials()
        self._seed_certifications()
        self._seed_partners()
        self.stdout.write(self.style.SUCCESS("Structured seed content loaded."))

    def _reset_content(self):
        Tariff.objects.all().delete()
        Service.objects.all().delete()
        Category.objects.all().delete()
        StandalonePage.objects.all().delete()
        RitualPoint.objects.all().delete()
        HomeFlexibleSection.objects.all().delete()
        Testimonial.objects.all().delete()
        Certification.objects.all().delete()
        Partner.objects.all().delete()

    def _upsert_site_settings(self):
        SiteSettings.objects.update_or_create(
            pk=1,
            defaults={
                "brand_name": "Les secrets d'ambre",
                "tagline": "Institut de beaute bio a Montpellier - soins hautement personnalises",
                "hero_title": "Rituels de beaute orientale, version contemporaine",
                "hero_subtitle": "Des categories de soins claires, des cures lisibles et une experience elegante centree sur la peau et le bien-etre.",
                "contact_phone": "+33662360108",
                "contact_phone_display": "06 62 36 01 08",
                "address_line": "17 rue Lunaret",
                "postal_code_city": "34090 Montpellier",
                "opening_hours": "Du lundi au samedi, sur rendez-vous",
                "gps_notice": "Pour le GPS: saisir 17 rue Lunaret, Montpellier",
                "referral_offer_text": "Offre parrainage: -15% pour vous et votre proche sur la prochaine visite.",
                "booking_label": "Prendre rendez-vous",
                "booking_url": "https://www.planity.com/les-secrets-dambre-34090-montpellier",
                "instagram_url": "https://www.instagram.com/lessecretsdambre/",
                "facebook_url": "https://www.facebook.com/LesSecretsDAmbre/",
                "tripadvisor_url": "https://www.tripadvisor.fr/",
                "google_maps_url": "https://maps.google.com/?q=Les+secrets+d+ambre+Montpellier",
                "map_embed_url": "https://www.openstreetmap.org/export/embed.html?bbox=3.8794%2C43.6147%2C3.8875%2C43.6202&layer=mapnik&marker=43.6174%2C3.8834",
                "map_title": "Les secrets d'ambre - Montpellier",
                "certification_label": "Institut engage dans une approche naturelle et personnalisee depuis 2012.",
                "footer_note": "Institut maman & bebe - quartier Beaux Arts",
                "seo_description": "Institut de beaute bio a Montpellier. Rituels orientaux, soins visage, massage, hammam et epilation douce.",
                "seo_keywords": "institut bio montpellier, soin visage, hammam, massage, epilation orientale",
            },
        )

    def _seed_categories(self):
        for cat_index, payload in enumerate(CATEGORY_SEED, start=1):
            category, _ = Category.objects.update_or_create(
                slug=payload["slug"],
                defaults={
                    "title": payload["title"],
                    "short_intro": payload["intro"],
                    "body_html": payload["body"],
                    "display_order": cat_index,
                    "is_published": True,
                    "seo_title": payload["title"],
                    "seo_description": payload["intro"][:160],
                    "seo_keywords": payload["title"].lower(),
                },
            )

            for service_index, service_payload in enumerate(payload["services"], start=1):
                service, _ = Service.objects.update_or_create(
                    category=category,
                    slug=service_payload["slug"],
                    defaults={
                        "name": service_payload["name"],
                        "short_description": service_payload.get("summary", ""),
                        "details_html": service_payload.get("details", ""),
                        "display_order": service_index,
                        "is_featured": service_payload.get("featured", False),
                        "is_published": True,
                    },
                )

                for tariff_index, tariff_payload in enumerate(service_payload["tariffs"], start=1):
                    notes = tariff_payload.get("notes", "")
                    Tariff.objects.update_or_create(
                        service=service,
                        label=tariff_payload["label"],
                        defaults={
                            "duration_text": tariff_payload.get("duration", ""),
                            "price_label": tariff_payload["price"],
                            "promo_price_label": tariff_payload.get("promo", ""),
                            "notes": notes,
                            "details_html": f"<p>{notes}</p>" if notes else "",
                            "display_order": tariff_index,
                            "is_published": True,
                        },
                    )

    def _seed_pages(self):
        for page in PAGE_SEED:
            StandalonePage.objects.update_or_create(
                slug=page["slug"],
                defaults={
                    "title": page["title"],
                    "summary": page["summary"],
                    "body_html": page["body"],
                    "show_in_nav": page.get("show_in_nav", True),
                    "nav_order": page["nav_order"],
                    "is_published": True,
                    "seo_title": page["title"],
                    "seo_description": page["summary"][:160],
                },
            )

    def _seed_ritual_points(self):
        for index, payload in enumerate(RITUAL_POINT_SEED, start=1):
            RitualPoint.objects.update_or_create(
                title=payload["title"],
                defaults={
                    "text": payload["text"],
                    "icon_class": payload.get("icon_class", "bi bi-stars"),
                    "display_order": index,
                    "is_published": True,
                },
            )

    def _seed_flexible_sections(self):
        for index, payload in enumerate(HOME_FLEXIBLE_SEED, start=1):
            HomeFlexibleSection.objects.update_or_create(
                title=payload["title"],
                defaults={
                    "subtitle": payload.get("subtitle", ""),
                    "body_html": payload.get("body_html", ""),
                    "external_image_url": payload.get("external_image_url", ""),
                    "video_embed_url": payload.get("video_embed_url", ""),
                    "display_order": index,
                    "is_published": True,
                },
            )

    def _seed_testimonials(self):
        for index, payload in enumerate(TESTIMONIAL_SEED, start=1):
            Testimonial.objects.update_or_create(
                name=payload["name"],
                defaults={
                    "stars": payload.get("stars", 5),
                    "text": payload["text"],
                    "display_order": index,
                    "is_published": True,
                },
            )

    def _seed_certifications(self):
        for index, payload in enumerate(CERTIFICATION_SEED, start=1):
            Certification.objects.update_or_create(
                slug=payload["slug"],
                defaults={
                    "name": payload["name"],
                    "description": payload.get("description", ""),
                    "website_url": payload.get("website_url", ""),
                    "external_image_url": payload.get("external_image_url", ""),
                    "display_order": index,
                    "is_published": True,
                },
            )

    def _seed_partners(self):
        for index, payload in enumerate(PARTNER_SEED, start=1):
            Partner.objects.update_or_create(
                slug=payload["slug"],
                defaults={
                    "name": payload["name"],
                    "website_url": payload.get("website_url", ""),
                    "external_image_url": payload.get("external_image_url", ""),
                    "display_order": index,
                    "is_published": True,
                },
            )
