const menuButton = document.querySelector("[data-menu-toggle]");
const menuButtonsClose = document.querySelectorAll("[data-menu-close]");
const menuOverlay = document.querySelector("[data-menu-overlay]");
const menu = document.querySelector("[data-menu]");
const dropdowns = document.querySelectorAll("[data-dropdown]");
const scrollTopButton = document.querySelector("[data-scroll-top]");
const siteHeader = document.querySelector(".site-header");

if (siteHeader) {
    requestAnimationFrame(() => {
        siteHeader.classList.add("is-mounted");
    });
}

const toggleHeaderState = () => {
    if (siteHeader) {
        siteHeader.classList.toggle("is-scrolled", window.scrollY > 8);
    }
};

const closeMenu = () => {
    if (menu) menu.classList.remove("is-open");
    if (menuOverlay) menuOverlay.classList.remove("is-active");
    document.body.style.overflow = '';
};

if (menuButton && menu) {
    menuButton.addEventListener("click", () => {
        menu.classList.add("is-open");
        if (menuOverlay) menuOverlay.classList.add("is-active");
        document.body.style.overflow = 'hidden';
    });
}

menuButtonsClose.forEach(btn => {
    btn.addEventListener("click", closeMenu);
});

if (menuOverlay) {
    menuOverlay.addEventListener("click", closeMenu);
}

dropdowns.forEach(dropdown => {
    const toggle = dropdown.querySelector('.nav-dropdown-toggle');
    if (toggle) {
        toggle.addEventListener('click', (e) => {
            // Only acts as a click toggle on mobile/touch, desktop handles via CSS hover
            if (window.innerWidth <= 980) {
                e.preventDefault();
                dropdown.classList.toggle('is-open');
                const isExpanded = dropdown.classList.contains('is-open');
                toggle.setAttribute('aria-expanded', isExpanded);
            }
        });
    }
});

if (scrollTopButton) {
    const toggleScrollButton = () => {
        if (window.scrollY > 380) {
            scrollTopButton.classList.add("is-visible");
        } else {
            scrollTopButton.classList.remove("is-visible");
        }
    };

    window.addEventListener(
        "scroll",
        () => {
            toggleScrollButton();
        },
        { passive: true },
    );

    toggleScrollButton();

    scrollTopButton.addEventListener("click", () => {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });
}

window.addEventListener("scroll", toggleHeaderState, { passive: true });
toggleHeaderState();

const revealElements = document.querySelectorAll(".reveal");
const partnerNodes = document.querySelectorAll(".partner-node[data-top][data-left]");
const certShowcase = document.querySelector("[data-cert-showcase]");

partnerNodes.forEach((node) => {
    const top = Number.parseFloat(node.dataset.top || "");
    const left = Number.parseFloat(node.dataset.left || "");
    const rotation = Number.parseFloat(node.dataset.rotation || "0");
    const size = Number.parseFloat(node.dataset.size || "120");

    if (!Number.isNaN(top)) {
        node.style.top = `${top}%`;
    }

    if (!Number.isNaN(left)) {
        node.style.left = `${left}%`;
    }

    if (!Number.isNaN(rotation)) {
        node.style.setProperty("--spin", `${rotation}deg`);
    }

    if (!Number.isNaN(size)) {
        node.style.setProperty("--node-size", `${size}px`);
    }
});

if (certShowcase) {
    const certThumbs = certShowcase.querySelectorAll("[data-cert-thumb]");
    const featureImage = certShowcase.querySelector("[data-cert-feature-image]");
    const featureTitle = certShowcase.querySelector("[data-cert-feature-title]");
    const featureDescription = certShowcase.querySelector("[data-cert-feature-description]");
    const featureLink = certShowcase.querySelector("[data-cert-feature-link]");

    certThumbs.forEach((thumb) => {
        thumb.addEventListener("click", () => {
            certThumbs.forEach((node) => node.classList.remove("is-active"));
            thumb.classList.add("is-active");

            const title = thumb.dataset.title || "Certification";
            const description = thumb.dataset.description || "";
            const image = thumb.dataset.image || "";
            const link = thumb.dataset.link || "#";

            if (featureTitle) {
                featureTitle.textContent = title;
            }

            if (featureDescription) {
                featureDescription.textContent = description;
            }

            if (featureLink) {
                featureLink.setAttribute("href", link);
                if (link === "#") {
                    featureLink.removeAttribute("target");
                    featureLink.removeAttribute("rel");
                } else {
                    featureLink.setAttribute("target", "_blank");
                    featureLink.setAttribute("rel", "noreferrer noopener");
                }
            }

            if (featureImage && image) {
                featureImage.classList.add("is-fading");
                setTimeout(() => {
                    featureImage.setAttribute("src", image);
                    featureImage.setAttribute("alt", title);
                    featureImage.classList.remove("is-fading");
                }, 150);
            }
        });
    });

    // Auto rotate
    let certIndex = 0;
    let certInterval = setInterval(() => {
        certIndex = (certIndex + 1) % certThumbs.length;
        if (certThumbs[certIndex]) {
            certThumbs[certIndex].click();
        }
    }, 5000);

    certShowcase.addEventListener('mouseenter', () => clearInterval(certInterval));
}

if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                }
            });
        },
        {
            threshold: 0.12,
            rootMargin: "0px 0px -30px 0px",
        },
    );

    revealElements.forEach((el) => observer.observe(el));
} else {
    revealElements.forEach((el) => el.classList.add("is-visible"));
}

/* Lightbox Logic */
const galleryImages = document.querySelectorAll('.legacy-gallery img, .flex-block-media img, .cert-feature-link img');
if (galleryImages.length > 0) {
    const lightbox = document.createElement('div');
    lightbox.className = 'lightbox';
    lightbox.innerHTML = `
        <button class="lightbox-close" aria-label="Close">&times;</button>
        <img src="" alt="">
    `;
    document.body.appendChild(lightbox);
    
    const lightboxImg = lightbox.querySelector('img');
    const lightboxClose = lightbox.querySelector('.lightbox-close');

    galleryImages.forEach(img => {
        img.style.cursor = 'zoom-in';
        img.addEventListener('click', (e) => {
            e.preventDefault();
            lightboxImg.src = img.src;
            lightbox.classList.add('is-open');
        });
    });

    const closeLightbox = () => {
        lightbox.classList.remove('is-open');
    };

    lightboxClose.addEventListener('click', closeLightbox);
    lightbox.addEventListener('click', (e) => {
        if (e.target === lightbox) closeLightbox();
    });
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeLightbox();
    });
}
