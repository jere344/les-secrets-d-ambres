"""Illustration candidates selected from OCR catalog.

These paths are mirror-relative and intended to be copied to MEDIA_ROOT/imported.
Use CATEGORY_PRIMARY_COVER_IMAGE to auto-assign category cover images at seed time.
"""

CATEGORY_ILLUSTRATION_SHORTLIST = {
    "epilation": [
        "image.jimcdn.com/app/cms/image/transf/dimension=1920x1024_format=jpg/path/s3935d23759db2cb4/image/icee7aa93ee6aae57/version/1760996513/image.jpg",
        "image.jimcdn.com/app/cms/image/transf/dimension=1024x252_format=jpg_rotate=90/path/s3935d23759db2cb4/image/i62e61f308b42cad2/version/1760996975/image.jpg",
    ],
    "soins-visage": [
        "image.jimcdn.com/app/cms/image/transf/none/path/s3935d23759db2cb4/image/i571b390c89490f6a/version/1614636070/image.jpg",
        "image.jimcdn.com/app/cms/image/transf/dimension=4096x4096_format=jpg/path/s3935d23759db2cb4/image/ibf8e39a092b9744d/version/1760658631/image.jpg",
    ],
    "soins-corps-minceur": [
        "image.jimcdn.com/app/cms/image/transf/dimension=4096x4096_format=jpg/path/s3935d23759db2cb4/image/i72d8e42923fbca73/version/1760667861/image.jpg",
        "image.jimcdn.com/app/cms/image/transf/dimension=504x10000_format=jpg/path/s3935d23759db2cb4/image/i26729e44ccc0c1c9/version/1760667669/image.jpg",
    ],
    "massages-relaxation": [
        "image.jimcdn.com/app/cms/image/transf/dimension=252x1024_format=jpg/path/s3935d23759db2cb4/image/i7caead3609c98a6e/version/1663015566/image.jpg",
        "image.jimcdn.com/app/cms/image/transf/dimension=234x10000_format=jpg/path/s3935d23759db2cb4/image/i4112a3a37923aee9/version/1663015597/image.jpg",
    ],
    "hammam-spa": [
        "image.jimcdn.com/app/cms/image/transf/dimension=4096x4096_format=jpg/path/s3935d23759db2cb4/image/i3bdefa0392d0b516/version/1760667365/image.jpg",
        "image.jimcdn.com/app/cms/image/transf/dimension=1920x400_format=jpg/path/s3935d23759db2cb4/image/i831a4a29137b845f/version/1760667365/image.jpg",
    ],
    "onglerie": [
        "image.jimcdn.com/app/cms/image/transf/dimension=4096x4096_format=jpg/path/s3935d23759db2cb4/image/ieb489d7f7881221b/version/1769732858/image.jpg",
        "image.jimcdn.com/app/cms/image/transf/dimension=1920x400_format=jpg/path/s3935d23759db2cb4/image/i6f4a8c8fc5e71d9e/version/1769732858/image.jpg",
    ],
    "regard-maquillage": [
        "image.jimcdn.com/app/cms/image/transf/dimension=4096x4096_format=jpg/path/s3935d23759db2cb4/image/ibf8e39a092b9744d/version/1760658631/image.jpg",
        "image.jimcdn.com/app/cms/image/transf/none/path/s3935d23759db2cb4/image/i571b390c89490f6a/version/1614636070/image.jpg",
    ],
}

CATEGORY_PRIMARY_COVER_IMAGE = {
    slug: (f"imported/{paths[0]}" if paths else "")
    for slug, paths in CATEGORY_ILLUSTRATION_SHORTLIST.items()
}


SERVICE_PRIMARY_IMAGE = {
    "epilation-femme": "imported/image.jimcdn.com/app/cms/image/transf/dimension=1920x1024_format=jpg/path/s3935d23759db2cb4/image/icee7aa93ee6aae57/version/1760996513/image.jpg",
    "epilation-homme": "imported/image.jimcdn.com/app/cms/image/transf/dimension=252x1024_format=jpg/path/s3935d23759db2cb4/image/i69e56b40bdef9592/version/1760996618/image.jpg",
    "epilation-au-fil": "imported/image.jimcdn.com/app/cms/image/transf/dimension=1024x252_format=jpg_rotate=90/path/s3935d23759db2cb4/image/i62e61f308b42cad2/version/1760996975/image.jpg",
    "soins-visage-bio": "imported/image.jimcdn.com/app/cms/image/transf/none/path/s3935d23759db2cb4/image/i571b390c89490f6a/version/1614636070/image.jpg",
    "black-pearl-peaux-noires": "imported/image.jimcdn.com/app/cms/image/transf/none/path/s3935d23759db2cb4/image/i571b390c89490f6a/version/1614636070/image.jpg",
    "soins-corps-bio": "imported/image.jimcdn.com/app/cms/image/transf/dimension=4096x4096_format=jpg/path/s3935d23759db2cb4/image/i72d8e42923fbca73/version/1760667861/image.jpg",
    "minceur-jambes-lourdes": "imported/image.jimcdn.com/app/cms/image/transf/dimension=504x10000_format=jpg/path/s3935d23759db2cb4/image/i26729e44ccc0c1c9/version/1760667669/image.jpg",
    "massage-bio": "imported/image.jimcdn.com/app/cms/image/transf/dimension=252x1024_format=jpg/path/s3935d23759db2cb4/image/i7caead3609c98a6e/version/1663015566/image.jpg",
    "gestion-du-stress": "imported/image.jimcdn.com/app/cms/image/transf/dimension=234x10000_format=jpg/path/s3935d23759db2cb4/image/i4112a3a37923aee9/version/1663015597/image.jpg",
    "femme-enceinte-jeune-maman": "imported/image.jimcdn.com/app/cms/image/transf/dimension=252x1024_format=jpg/path/s3935d23759db2cb4/image/i7caead3609c98a6e/version/1663015566/image.jpg",
    "hammam-sauna": "imported/image.jimcdn.com/app/cms/image/transf/dimension=4096x4096_format=jpg/path/s3935d23759db2cb4/image/i3bdefa0392d0b516/version/1760667365/image.jpg",
    "rituels-orientaux-spa": "imported/image.jimcdn.com/app/cms/image/transf/dimension=1920x400_format=jpg/path/s3935d23759db2cb4/image/i831a4a29137b845f/version/1760667365/image.jpg",
    "onglerie-bio": "imported/image.jimcdn.com/app/cms/image/transf/dimension=4096x4096_format=jpg/path/s3935d23759db2cb4/image/ieb489d7f7881221b/version/1769732858/image.jpg",
    "manucure-pedicure-bio": "imported/image.jimcdn.com/app/cms/image/transf/dimension=1920x400_format=jpg/path/s3935d23759db2cb4/image/i6f4a8c8fc5e71d9e/version/1769732858/image.jpg",
    "beaute-du-regard": "imported/image.jimcdn.com/app/cms/image/transf/dimension=267x10000_format=jpg/path/s3935d23759db2cb4/image/i694d3a004fd3a075/version/1762472368/micro-blading-montpellier.jpg",
    "maquillage-evenementiel": "imported/image.jimcdn.com/app/cms/image/transf/dimension=298x10000_format=jpg/path/s3935d23759db2cb4/image/if5865b5708e9e26c/version/1762472826/image.jpg",
    "maquillage-permanent": "imported/image.jimcdn.com/app/cms/image/transf/dimension=1920x400_format=jpg/path/s3935d23759db2cb4/image/i526a025e5a7acfdf/version/1492728559/image.jpg",
}
