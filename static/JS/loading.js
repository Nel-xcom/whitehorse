// loading.js

window.onload = function () {
    const loadingContainer = document.getElementById("loading-container");

    // ✅ Oculta la pantalla de carga cuando la página ha cargado completamente
    if (loadingContainer) {
        setTimeout(() => {
            loadingContainer.classList.add("loading-hidden");
        }, 500);
    }

    // ✅ Manejar la navegación con la flecha de retroceso (BFCache y popstate)
    window.addEventListener("pageshow", (event) => {
        if (event.persisted) {
            // La página se cargó desde el caché del navegador
            if (loadingContainer) {
                loadingContainer.classList.add("loading-hidden");
            }
        }
    });

    window.addEventListener("popstate", () => {
        if (loadingContainer) {
            loadingContainer.classList.add("loading-hidden");
        }
    });

    // ✅ Muestra la pantalla de carga al enviar formularios
    const forms = document.querySelectorAll("form");
    forms.forEach(form => {
        form.addEventListener("submit", () => {
            if (loadingContainer) {
                loadingContainer.classList.remove("loading-hidden");
            }
        });
    });

    // ✅ Muestra la pantalla de carga al hacer clic en enlaces (excepto enlaces internos con #)
    const links = document.querySelectorAll("a");
    links.forEach(link => {
        link.addEventListener("click", (e) => {
            const href = link.getAttribute("href");
            if (href && !href.startsWith("#") && !href.startsWith("javascript") && link.target !== "_blank") {
                if (loadingContainer) {
                    loadingContainer.classList.remove("loading-hidden");
                }
            }
        });
    });
};
