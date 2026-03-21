"""Manual content placement for category/service architecture.

This file is the manual orchestration layer:
- choose which legacy chunk goes to category shared content
- choose which legacy chunk goes to each service main content

Workflow:
1) Build chunk catalog from legacy_content.json
2) Edit source_refs/chunk_ids here
3) Re-run seed
"""


CATEGORY_CONTENT_ASSIGNMENTS = {
    "epilation": {
        "source_refs": [],
        "chunk_ids": [],
    },
    "soins-visage": {
        "source_refs": [],
        "chunk_ids": [],
    },
    "soins-corps-minceur": {
        "source_refs": [],
        "chunk_ids": [],
    },
    "massages-relaxation": {
        "source_refs": [],
        "chunk_ids": [],
    },
    "hammam-spa": {
        "source_refs": [],
        "chunk_ids": [],
    },
    "onglerie": {
        "source_refs": [],
        "chunk_ids": [],
    },
    "regard-maquillage": {
        "source_refs": [],
        "chunk_ids": [],
    },
}


SERVICE_CONTENT_ASSIGNMENTS = {
    "epilation-femme": {
        "source_refs": [],
        "chunk_ids": [
            "epilation-bio-a-montpellier::001",
            "epilation-bio-a-montpellier::002",
            "epilation-bio-a-montpellier::003",
            "epilation-bio-a-montpellier::005",
            "achat/epilation-cire-orientale-miel-hommes-et-femmes::001",
        ],
    },
    "epilation-homme": {
        "source_refs": [],
        "chunk_ids": [
            "epilation-bio-a-montpellier::004",
            "achat/epilation-cire-orientale-miel-hommes-et-femmes::001",
        ],
    },
    "epilation-au-fil": {
        "source_refs": [],
        "chunk_ids": [],
    },
    "soins-visage-bio": {
        "source_refs": [],
        "chunk_ids": [
            "soins-visage-bio-a-montpellier::001",
            "soins-visage-bio-a-montpellier::002",
            "achat/soins-visage::001",
        ],
    },
    "black-pearl-peaux-noires": {
        "source_refs": [],
        "chunk_ids": [
            "black-pearl-pour-peaux-noires::001",
        ],
    },
    "soins-corps-bio": {
        "source_refs": [],
        "chunk_ids": [
            "soins-corps-bio-a-montpellier::001",
            "soins-corps-bio-a-montpellier::003",
            "achat/soins-corps::001",
            "achat/soins-corps::002",
        ],
    },
    "minceur-jambes-lourdes": {
        "source_refs": [],
        "chunk_ids": [
            "soins-corps-bio-a-montpellier::002",
            "minceur-a-montpellier-et-jambes-lourdes::001",
            "minceur-a-montpellier-et-jambes-lourdes::002",
            "minceur-a-montpellier-et-jambes-lourdes::003",
            "minceur-a-montpellier-et-jambes-lourdes::004",
            "minceur-a-montpellier-et-jambes-lourdes::005",
            "achat/minceur::001",
            "achat/minceur::002",
            "achat/amincissement::001",
        ],
    },
    "massage-bio": {
        "source_refs": [],
        "chunk_ids": [
            "massage-bio-a-montpellier::001",
            "achat/soins-corps::003",
        ],
    },
    "gestion-du-stress": {
        "source_refs": [],
        "chunk_ids": [
            "relaxation-et-coaching::001",
            "achat/gestion-du-stress::001",
            "achat/gestion-du-stress::002",
        ],
    },
    "femme-enceinte-jeune-maman": {
        "source_refs": [],
        "chunk_ids": [
            "femme-enceinte-et-jeune-maman::001",
        ],
    },
    "hammam-sauna": {
        "source_refs": [],
        "chunk_ids": [
            "hammam-a-montpellier::001",
            "achat/hammam-sauna::001",
        ],
    },
    "rituels-orientaux-spa": {
        "source_refs": [],
        "chunk_ids": [],
    },
    "onglerie-bio": {
        "source_refs": [],
        "chunk_ids": [
            "onglerie-bio-soins-mains-et-pieds-a-montpellier::002",
            "onglerie-bio-soins-mains-et-pieds-a-montpellier::003",
            "onglerie-bio-soins-mains-et-pieds-a-montpellier::005",
        ],
    },
    "manucure-pedicure-bio": {
        "source_refs": [],
        "chunk_ids": [
            "onglerie-bio-soins-mains-et-pieds-a-montpellier::001",
            "onglerie-bio-soins-mains-et-pieds-a-montpellier::006",
            "onglerie-bio-soins-mains-et-pieds-a-montpellier::007",
        ],
    },
    "beaute-du-regard": {
        "source_refs": [],
        "chunk_ids": [
            "beaute-du-regard-a-montpellier::001",
            "beaute-du-regard-a-montpellier::002",
            "beaute-du-regard-a-montpellier::003",
            "beaute-du-regard-a-montpellier::004",
        ],
    },
    "maquillage-evenementiel": {
        "source_refs": [],
        "chunk_ids": [
            "maquillage-a-montpellier::001",
            "achat/maquillage::001",
        ],
    },
    "maquillage-permanent": {
        "source_refs": [],
        "chunk_ids": [
            "maquillage-permanent-a-montpellier::001",
        ],
    },
}
