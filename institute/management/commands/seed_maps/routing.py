"""Legacy URL routing maps.

These maps control how legacy links are rewritten to new category/service/page URLs.
"""

LEGACY_TOPLEVEL_TO_SERVICE = {
    "epilation-bio-a-montpellier": "epilation-femme",
    "soins-visage-bio-a-montpellier": "soins-visage-bio",
    "black-pearl-pour-peaux-noires": "black-pearl-peaux-noires",
    "soins-corps-bio-a-montpellier": "soins-corps-bio",
    "minceur-a-montpellier-et-jambes-lourdes": "minceur-jambes-lourdes",
    "massage-bio-a-montpellier": "massage-bio",
    "relaxation-et-coaching": "gestion-du-stress",
    "femme-enceinte-et-jeune-maman": "femme-enceinte-jeune-maman",
    "hammam-a-montpellier": "hammam-sauna",
    "onglerie-bio-soins-mains-et-pieds-a-montpellier": "onglerie-bio",
    "beaute-du-regard-a-montpellier": "beaute-du-regard",
    "maquillage-a-montpellier": "maquillage-evenementiel",
    "maquillage-permanent-a-montpellier": "maquillage-permanent",
}

LEGACY_ACHAT_TO_SERVICE = {
    "epilation-cire-orientale-miel-hommes-et-femmes": "epilation-femme",
    "epilation-a-la-cire-montpellier": "epilation-femme",
    "soins-visage": "soins-visage-bio",
    "soins-corps": "soins-corps-bio",
    "minceur": "minceur-jambes-lourdes",
    "amincissement": "minceur-jambes-lourdes",
    "massages-hommes-femmes-et-bebe": "massage-bio",
    "gestion-du-stress": "gestion-du-stress",
    "hammam-sauna": "hammam-sauna",
    "beaute-des-mains-et-pieds": "onglerie-bio",
    "maquillage": "maquillage-evenementiel",
    "nouvelle-page": "maquillage-evenementiel",
}

LEGACY_STANDALONE_SLUG_MAP = {
    "about": "mentions-legales",
    "faq": "faq",
    "nous-ecrire": "nous-ecrire",
    "a-propos": "a-propos",
    "les-formations": "les-formations",
    "galerie-photos-1": "galerie-photos-1",
    "galerie-photos-2": "galerie-photos-2",
    "carte-de-visite": "carte-de-visite",
    "aromazone-v-i-p": "aromazone-v-i-p",
    "promotions": "promotions",
}

LEGACY_TOPLEVEL_TO_CATEGORY = {
    "epilation-bio-a-montpellier": "epilation",
    "soins-visage-bio-a-montpellier": "soins-visage",
    "black-pearl-pour-peaux-noires": "soins-visage",
    "soins-corps-bio-a-montpellier": "soins-corps-minceur",
    "minceur-a-montpellier-et-jambes-lourdes": "soins-corps-minceur",
    "massage-bio-a-montpellier": "massages-relaxation",
    "relaxation-et-coaching": "massages-relaxation",
    "femme-enceinte-et-jeune-maman": "massages-relaxation",
    "hammam-a-montpellier": "hammam-spa",
    "onglerie-bio-soins-mains-et-pieds-a-montpellier": "onglerie",
    "beaute-du-regard-a-montpellier": "regard-maquillage",
    "maquillage-a-montpellier": "regard-maquillage",
    "maquillage-permanent-a-montpellier": "regard-maquillage",
}