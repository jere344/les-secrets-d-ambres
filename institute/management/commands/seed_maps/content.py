"""Curated category and service content maps.

These dictionaries are the source of truth for category/service page copy.
They allow reorganization without re-parsing raw HTTrack HTML.
"""


CATEGORY_CONTENT_OVERRIDES = {
    "epilation": {
        "short_intro": (
            "Epilation douce et technique adaptee: cire orientale au miel, cires ciblees et epilation au fil."
        ),
        "body_html": (
            "<section><h2>Notre approche epilation</h2>"
            "<p>Cette categorie regroupe les protocoles d'epilation femmes, hommes et precision au fil. "
            "Les techniques sont choisies selon la zone, la sensibilite de la peau et la nature du poil.</p>"
            "</section>"
            "<section><h2>Techniques disponibles</h2>"
            "<ul>"
            "<li>Cire orientale au miel pour les peaux reactives.</li>"
            "<li>Cires techniques (vegan, coton, boudoir, fleur de coton) selon le besoin.</li>"
            "<li>Epilation au fil pour une precision maximale du visage.</li>"
            "</ul>"
            "</section>"
            "<section><h2>Organisation de la categorie</h2>"
            "<p>Les pages service ci-dessous distinguent clairement les offres femme, homme et au fil. "
            "Cette page conserve la vision globale des methodes et conseils.</p>"
            "</section>"
        ),
    },
    "soins-visage": {
        "short_intro": "Soins visage personnalises: hydratation, anti-age, eclat et protocoles experts.",
        "body_html": (
            "<section><h2>Vision globale soins visage</h2>"
            "<p>Cette categorie couvre les soins visage bio, les cures expertes et les protocoles dedies "
            "aux peaux noires et metissees.</p></section>"
            "<section><h2>Methodologie</h2>"
            "<ul>"
            "<li>Diagnostic cutane et objectifs personnalises.</li>"
            "<li>Protocoles unitaires ou en cure selon l'etat de la peau.</li>"
            "<li>Travail combine texture, eclat, confort et prevention anti-age.</li>"
            "</ul></section>"
        ),
    },
    "soins-corps-minceur": {
        "short_intro": "Soins corps, minceur et drainage avec programmes de seances et cures.",
        "body_html": (
            "<section><h2>Soins corps et silhouette</h2>"
            "<p>La categorie rassemble les soins corps de confort (gommage, enveloppement) et les parcours "
            "cibles minceur et jambes lourdes.</p></section>"
            "<section><h2>Structure des offres</h2>"
            "<ul>"
            "<li>Soins corps bio pour la qualite de peau et la detente tissulaire.</li>"
            "<li>Programmes minceur/drainage sur zones et en cure.</li>"
            "</ul></section>"
        ),
    },
    "massages-relaxation": {
        "short_intro": "Massages energetiques, relaxation guidee et accompagnements bien-etre.",
        "body_html": (
            "<section><h2>Massages et regulation du stress</h2>"
            "<p>Cette categorie distingue les massages energetiques, la gestion du stress et les prestations "
            "specifiques femme enceinte / jeune maman.</p></section>"
            "<section><h2>Objectif</h2>"
            "<p>Retrouver un equilibre global: relachement musculaire, recuperation nerveuse et meilleure "
            "respiration.</p></section>"
        ),
    },
    "hammam-spa": {
        "short_intro": "Hammam, sauna et rituels orientaux de detente profonde.",
        "body_html": (
            "<section><h2>Univers hammam et rituels</h2>"
            "<p>La categorie separe l'acces hammam/sauna des rituels orientaux complets pour clarifier "
            "les niveaux de prestation.</p></section>"
            "<section><h2>Parcours type</h2>"
            "<p>Chaleur, gommage, enveloppement et massage selon la formule choisie.</p></section>"
        ),
    },
    "onglerie": {
        "short_intro": "Onglerie bio et soins mains/pieds: vernis, spa, paraffine et anti-age.",
        "body_html": (
            "<section><h2>Bar a ongles et soins experts</h2>"
            "<p>Cette categorie distingue la partie onglerie (poses/deposes) des protocoles spa mains-pieds "
            "plus traitants.</p></section>"
            "<section><h2>Deux niveaux d'offre</h2>"
            "<ul>"
            "<li>Onglerie bio: finitions, semi-permanent, options esthetiques.</li>"
            "<li>Manucure/pedicure spa: soin profond, paraffine, correction et entretien.</li>"
            "</ul></section>"
        ),
    },
    "regard-maquillage": {
        "short_intro": "Sourcils, cils, microblading, maquillage evenementiel et dermopigmentation.",
        "body_html": (
            "<section><h2>Architecture du regard</h2>"
            "<p>La categorie separe les actes regard (sourcils/cils), le maquillage evenementiel et "
            "la dermopigmentation pour un parcours plus lisible.</p></section>"
            "<section><h2>Logique des services</h2>"
            "<ul>"
            "<li>Sourcils/cils/microblading pour la structure du regard.</li>"
            "<li>Maquillage evenementiel pour les besoins ponctuels et la formation.</li>"
            "<li>Dermopigmentation pour les demandes de longue duree.</li>"
            "</ul></section>"
        ),
    },
}


SERVICE_CONTENT_OVERRIDES = {
    "epilation-femme": {
        "short_description": "Epilation femme par zones et forfaits combines, avec cires adaptees a la peau.",
        "details_html": (
            "<section><h2>Epilation femme</h2>"
            "<p>Service dedie aux zones feminines avec plusieurs technologies de cire et des forfaits "
            "combines jambes/maillot/aisselles.</p></section>"
            "<section><h2>Ce que couvre cette page</h2>"
            "<ul>"
            "<li>Tarifs par zone.</li>"
            "<li>Forfaits et abonnements 10 seances.</li>"
            "<li>Soin Vajacial post-epilatoire.</li>"
            "</ul></section>"
        ),
    },
    "epilation-homme": {
        "short_description": "Epilation homme par zones avec options torse/dos et soin post-epilatoire.",
        "details_html": (
            "<section><h2>Epilation homme</h2>"
            "<p>Service cible sur les zones masculines, avec adaptation selon densite du poil et "
            "surface travaillee.</p></section>"
            "<section><h2>Principales zones</h2>"
            "<ul>"
            "<li>Nez, oreilles, sourcils, nuque.</li>"
            "<li>Bras, jambes, aisselles, maillot integral.</li>"
            "<li>Dos ou torse a partir d'un tarif de base.</li>"
            "</ul></section>"
        ),
    },
    "epilation-au-fil": {
        "short_description": "Epilation au fil pour le visage: precision, symetrie et douceur.",
        "details_html": (
            "<section><h2>Epilation au fil</h2>"
            "<p>Technique de precision destinee aux zones du visage pour un tracage net et une finition "
            "propre, notamment sur sourcils et contours.</p></section>"
            "<section><h2>Zones traitees</h2>"
            "<ul><li>Sourcils</li><li>Levres</li><li>Menton</li><li>Joues</li><li>Visage entier</li></ul>"
            "</section>"
        ),
    },
    "soins-visage-bio": {
        "short_description": "Soins visage bio en seance ou en cure: hydratation, eclat et anti-age.",
        "details_html": (
            "<section><h2>Soins visage bio</h2>"
            "<p>Protocoles visage personnalises selon l'objectif: nettoyer, hydrater, lisser, illuminer "
            "ou travailler les signes de l'age.</p></section>"
            "<section><h2>Formats disponibles</h2>"
            "<ul><li>Seance unitaire</li><li>Cure 5 seances</li><li>Kobido</li></ul>"
            "</section>"
        ),
    },
    "black-pearl-peaux-noires": {
        "short_description": "Soin Black Pearl et protocoles adaptes aux peaux noires et metissees.",
        "details_html": (
            "<section><h2>Black Pearl</h2>"
            "<p>Service dedie aux besoins specifiques des peaux noires et metissees, avec une approche "
            "sur mesure et une vigilance forte sur l'homogeneite du teint.</p></section>"
            "<section><h2>Compliments possibles</h2>"
            "<p>Selon le besoin, l'offre peut etre combinee a des options corps et maquillage.</p></section>"
        ),
    },
    "soins-corps-bio": {
        "short_description": "Gommages, enveloppements et soins corps bio pour confort cutane et detente.",
        "details_html": (
            "<section><h2>Soins corps bio</h2>"
            "<p>Service orientee qualite de peau et confort corporel: exfoliation, nutrition et "
            "relachement tissulaire.</p></section>"
            "<section><h2>Parcours type</h2>"
            "<p>Gommage, enveloppement et options combinees selon l'objectif.</p></section>"
        ),
    },
    "minceur-jambes-lourdes": {
        "short_description": "Programmes minceur et drainage, par zones, en seance ou en cure.",
        "details_html": (
            "<section><h2>Minceur et jambes lourdes</h2>"
            "<p>Accompagnement cible sur la circulation, la sensation de jambes lourdes et le travail "
            "silhouette avec progression en cure.</p></section>"
            "<section><h2>Organisation</h2>"
            "<ul><li>1 ou 2 zones</li><li>Cures 5/10 seances</li><li>Drainage dedie</li></ul>"
            "</section>"
        ),
    },
    "massage-bio": {
        "short_description": "Massages energetiques intuitifs, solo et 4 mains, avec forfaits.",
        "details_html": (
            "<section><h2>Massages energetiques intuitifs</h2>"
            "<p>Massages progressifs de 30 a 120 minutes avec options intensives et forfaits de suivi.</p>"
            "</section>"
            "<section><h2>Variantes</h2>"
            "<ul><li>Formats 30/60/90/120 min</li><li>Massage 4 mains</li><li>Initiation duo</li></ul>"
            "</section>"
        ),
    },
    "gestion-du-stress": {
        "short_description": "Seances de gestion du stress avec rythme en cure pour stabiliser les resultats.",
        "details_html": (
            "<section><h2>Gestion du stress</h2>"
            "<p>Service centre sur l'apaisement nerveux, la respiration et la recuperation mentale, "
            "en seance unique ou en parcours de cure.</p></section>"
        ),
    },
    "femme-enceinte-jeune-maman": {
        "short_description": "Protocoles confort et recuperation dedies femme enceinte et jeune maman.",
        "details_html": (
            "<section><h2>Femme enceinte et jeune maman</h2>"
            "<p>Prestations adaptees a la periode perinatale: confort, drainage, relachement et "
            "accompagnement douceur.</p></section>"
            "<section><h2>Points forts</h2>"
            "<ul><li>Massages cibles</li><li>Formules globales</li><li>Shantala</li></ul>"
            "</section>"
        ),
    },
    "hammam-sauna": {
        "short_description": "Acces hammam/sauna en solo, duo ou groupe, avec options d'accompagnement.",
        "details_html": (
            "<section><h2>Hammam et sauna</h2>"
            "<p>Service d'acces chaleur et detente, en format individuel ou partage, avec timing court "
            "ou prolonge selon la formule.</p></section>"
        ),
    },
    "rituels-orientaux-spa": {
        "short_description": "Rituels orientaux complets: chaleur, gommage, enveloppement et massage.",
        "details_html": (
            "<section><h2>Rituels orientaux spa</h2>"
            "<p>Parcours complets de detente profonde avec niveaux decouverte, signature, premium et duo long.</p>"
            "</section>"
        ),
    },
    "onglerie-bio": {
        "short_description": "Onglerie bio: poses, deposes et finitions mains/pieds.",
        "details_html": (
            "<section><h2>Onglerie bio</h2>"
            "<p>Service dedie a l'esthetique de l'ongle: depose, pose semi-permanent, options de finition et french.</p>"
            "</section>"
        ),
    },
    "manucure-pedicure-bio": {
        "short_description": "Manucure/pedicure spa avec soins paraffine et protocoles correctifs.",
        "details_html": (
            "<section><h2>Manucure pedicure spa</h2>"
            "<p>Approche soin plus profonde que l'onglerie classique: cuticules, modelage, paraffine, "
            "anti-taches et correction.</p></section>"
        ),
    },
    "beaute-du-regard": {
        "short_description": "Sourcils, cils et microblading pour structurer durablement le regard.",
        "details_html": (
            "<section><h2>Beaute du regard</h2>"
            "<p>Service centre sur l'architecture du regard: browlift, lashlift, lashfiller, microblading "
            "et restructuration sourcils.</p></section>"
        ),
    },
    "maquillage-evenementiel": {
        "short_description": "Maquillage evenementiel et cours d'auto-maquillage.",
        "details_html": (
            "<section><h2>Maquillage evenementiel</h2>"
            "<p>Offres pour jour, soir, oriental, scene et accompagnement pedagogique en cours individuels.</p>"
            "</section>"
        ),
    },
    "maquillage-permanent": {
        "short_description": "Dermopigmentation et maquillage permanent apres diagnostic personnalise.",
        "details_html": (
            "<section><h2>Dermopigmentation</h2>"
            "<p>Le service commence par un diagnostic complet, puis un protocole sur mesure est etabli selon "
            "la zone, le style souhaite et l'historique cutane.</p></section>"
        ),
    },
}
