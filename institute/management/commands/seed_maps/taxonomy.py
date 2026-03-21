"""Dictionary-first content taxonomy.

Edit these structures as you discover better grouping from the legacy website.
The importer iterates over these dictionaries and rebuilds category/service trees.
"""

CATEGORY_DEFINITIONS = [
    {
        "slug": "epilation",
        "title": "Epilation bio et peau sensible",
        "sources": ["epilation-bio-a-montpellier"],
    },
    {
        "slug": "soins-visage",
        "title": "Soins visage personnalises",
        "sources": ["soins-visage-bio-a-montpellier", "black-pearl-pour-peaux-noires"],
    },
    {
        "slug": "soins-corps-minceur",
        "title": "Soins corps, minceur et drainage",
        "sources": ["soins-corps-bio-a-montpellier", "minceur-a-montpellier-et-jambes-lourdes"],
    },
    {
        "slug": "massages-relaxation",
        "title": "Massages energetiques et relaxation",
        "sources": ["massage-bio-a-montpellier", "relaxation-et-coaching"],
    },
    {
        "slug": "hammam-spa",
        "title": "Hammam, sauna et rituels orientaux",
        "sources": ["hammam-a-montpellier"],
    },
    {
        "slug": "onglerie",
        "title": "Onglerie et soins mains/pieds",
        "sources": ["onglerie-bio-soins-mains-et-pieds-a-montpellier"],
    },
    {
        "slug": "regard-maquillage",
        "title": "Regard, sourcils, cils et maquillage",
        "sources": [
            "beaute-du-regard-a-montpellier",
            "maquillage-a-montpellier",
            "maquillage-permanent-a-montpellier",
        ],
    },
]

SERVICE_DEFINITIONS = [
    {
        "slug": "epilation-femme",
        "title": "Epilation femme",
        "category": "epilation",
        "sources": ["epilation-bio-a-montpellier", "achat/epilation-cire-orientale-miel-hommes-et-femmes"],
        "featured": True,
    },
    {
        "slug": "epilation-homme",
        "title": "Epilation homme",
        "category": "epilation",
        "sources": ["epilation-bio-a-montpellier", "achat/epilation-cire-orientale-miel-hommes-et-femmes"],
        "featured": True,
    },
    {
        "slug": "epilation-au-fil",
        "title": "Epilation au fil",
        "category": "epilation",
        "sources": ["epilation-bio-a-montpellier", "beaute-du-regard-a-montpellier"],
        "featured": True,
    },
    {
        "slug": "soins-visage-bio",
        "title": "Soins visage bio",
        "category": "soins-visage",
        "sources": ["soins-visage-bio-a-montpellier", "achat/soins-visage"],
        "featured": True,
    },
    {
        "slug": "black-pearl-peaux-noires",
        "title": "Black Pearl pour peaux noires",
        "category": "soins-visage",
        "sources": ["black-pearl-pour-peaux-noires"],
        "featured": True,
    },
    {
        "slug": "soins-corps-bio",
        "title": "Soins corps bio",
        "category": "soins-corps-minceur",
        "sources": ["soins-corps-bio-a-montpellier", "achat/soins-corps"],
        "featured": True,
    },
    {
        "slug": "minceur-jambes-lourdes",
        "title": "Minceur et jambes lourdes",
        "category": "soins-corps-minceur",
        "sources": ["minceur-a-montpellier-et-jambes-lourdes", "achat/minceur", "achat/amincissement"],
        "featured": True,
    },
    {
        "slug": "massage-bio",
        "title": "Massages energetiques intuitifs",
        "category": "massages-relaxation",
        "sources": ["massage-bio-a-montpellier", "achat/massages-hommes-femmes-et-bebe"],
        "featured": True,
    },
    {
        "slug": "gestion-du-stress",
        "title": "Gestion du stress et relaxation",
        "category": "massages-relaxation",
        "sources": ["relaxation-et-coaching", "achat/gestion-du-stress"],
        "featured": False,
    },
    {
        "slug": "femme-enceinte-jeune-maman",
        "title": "Femme enceinte et jeune maman",
        "category": "massages-relaxation",
        "sources": ["femme-enceinte-et-jeune-maman"],
        "featured": False,
    },
    {
        "slug": "hammam-sauna",
        "title": "Hammam et sauna",
        "category": "hammam-spa",
        "sources": ["hammam-a-montpellier", "achat/hammam-sauna"],
        "featured": True,
    },
    {
        "slug": "rituels-orientaux-spa",
        "title": "Rituels orientaux spa",
        "category": "hammam-spa",
        "sources": ["hammam-a-montpellier"],
        "featured": False,
    },
    {
        "slug": "onglerie-bio",
        "title": "Onglerie bio mains et pieds",
        "category": "onglerie",
        "sources": ["onglerie-bio-soins-mains-et-pieds-a-montpellier", "achat/beaute-des-mains-et-pieds"],
        "featured": True,
    },
    {
        "slug": "manucure-pedicure-bio",
        "title": "Manucure pedicure spa",
        "category": "onglerie",
        "sources": ["achat/beaute-des-mains-et-pieds", "onglerie-bio-soins-mains-et-pieds-a-montpellier"],
        "featured": False,
    },
    {
        "slug": "beaute-du-regard",
        "title": "Sourcils, cils et microblading",
        "category": "regard-maquillage",
        "sources": ["beaute-du-regard-a-montpellier"],
        "featured": True,
    },
    {
        "slug": "maquillage-evenementiel",
        "title": "Maquillage evenementiel",
        "category": "regard-maquillage",
        "sources": ["maquillage-a-montpellier", "achat/maquillage"],
        "featured": False,
    },
    {
        "slug": "maquillage-permanent",
        "title": "Dermopigmentation et maquillage permanent",
        "category": "regard-maquillage",
        "sources": ["maquillage-permanent-a-montpellier"],
        "featured": False,
    },
]