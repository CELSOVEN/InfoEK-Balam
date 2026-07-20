"use strict";

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-explorador-pozos]").forEach((explorador) => {
        const selectorPlataforma = explorador.querySelector("[data-selector-plataforma]");
        const estadoPlataforma = explorador.querySelector("[data-estado-plataforma]");
        const gruposPozos = explorador.querySelectorAll("[data-grupo-plataforma]");

        selectorPlataforma.addEventListener("change", () => {
            const mostrarTodos = selectorPlataforma.value === "todos";

            gruposPozos.forEach((grupo) => {
                grupo.hidden = !mostrarTodos
                    && grupo.dataset.grupoPlataforma !== selectorPlataforma.value;
            });

            if (mostrarTodos) {
                const total = Array.from(explorador.querySelectorAll(".ficha-pozo"))
                    .reduce((suma, ficha) => suma + Number(ficha.dataset.cantidadProduccion || 0), 0);
                estadoPlataforma.textContent = `Todas las plataformas: ${total} pozos de producción encontrados.`;
                return;
            }

            const grupoActivo = Array.from(gruposPozos).find(
                (grupo) => grupo.dataset.grupoPlataforma === selectorPlataforma.value
            );

            if (!grupoActivo) {
                estadoPlataforma.textContent = "Elige una plataforma para mostrar sus pozos.";
                return;
            }

            const total = Array.from(grupoActivo.querySelectorAll(".ficha-pozo"))
                .reduce((suma, ficha) => suma + Number(ficha.dataset.cantidadProduccion || 0), 0);
            estadoPlataforma.textContent = `${grupoActivo.dataset.plataforma}: ${total} pozos de producción encontrados.`;
        });
    });

    document.querySelectorAll("[data-selector-historiales]").forEach((selector) => {
        const botones = selector.querySelectorAll("[data-mostrar-historial]");
        const paneles = selector.querySelectorAll("[data-panel-historial]");
        const estado = selector.querySelector("[data-estado-historial]");

        const cerrarHistorial = () => {
            botones.forEach((elemento) => {
                elemento.setAttribute("aria-pressed", "false");
            });
            paneles.forEach((panel) => {
                panel.hidden = true;
            });
            estado.textContent = "Elige una plataforma para mostrar la gráfica.";
            selector.scrollIntoView({ behavior: "smooth", block: "start" });
        };

        botones.forEach((boton) => {
            boton.addEventListener("click", () => {
                if (boton.getAttribute("aria-pressed") === "true") {
                    cerrarHistorial();
                    return;
                }

                const identificador = boton.dataset.mostrarHistorial;

                botones.forEach((elemento) => {
                    elemento.setAttribute("aria-pressed", String(elemento === boton));
                });

                paneles.forEach((panel) => {
                    const activo = panel.dataset.panelHistorial === identificador;
                    panel.hidden = !activo;

                    if (activo) {
                        const imagen = panel.querySelector("img[data-src]");
                        if (imagen && !imagen.hasAttribute("src")) {
                            imagen.src = imagen.dataset.src;
                        }
                    }
                });

                estado.textContent = `Mostrando historial de producción de ${boton.textContent.trim()}.`;
            });
        });

        selector.querySelectorAll("[data-cerrar-historial]").forEach((boton) => {
            boton.addEventListener("click", cerrarHistorial);
        });
    });

    const botonMenu = document.querySelector(".boton-menu-movil");
    const menuMovil = document.querySelector(".menu-movil");

    if (!botonMenu || !menuMovil) return;

    const cerrarMenu = () => {
        menuMovil.classList.remove("abierto");
        botonMenu.setAttribute("aria-expanded", "false");
    };

    botonMenu.addEventListener("click", () => {
        const abierto = menuMovil.classList.toggle("abierto");
        botonMenu.setAttribute("aria-expanded", String(abierto));
    });

    menuMovil.addEventListener("click", (evento) => {
        if (evento.target.closest("a")) cerrarMenu();
    });

    document.addEventListener("click", (evento) => {
        if (!evento.target.closest(".encabezado-contenido")) cerrarMenu();
    });

    window.addEventListener("resize", () => {
        if (window.innerWidth > 760) cerrarMenu();
    });

    document.querySelectorAll("[data-abrir-modal]").forEach((activador) => {
        const modal = document.getElementById(activador.dataset.abrirModal);
        if (!modal) return;

        const mostrarModal = () => modal.showModal();

        activador.addEventListener("click", mostrarModal);
        activador.addEventListener("keydown", (evento) => {
            if (evento.key === "Enter" || evento.key === " ") {
                evento.preventDefault();
                mostrarModal();
            }
        });
    });

    document.querySelectorAll("[data-cerrar-modal]").forEach((boton) => {
        boton.addEventListener("click", () => boton.closest("dialog").close());
    });

    document.querySelectorAll("dialog.modal-plataformas").forEach((modal) => {
        modal.addEventListener("click", (evento) => {
            if (evento.target === modal) modal.close();
        });
    });
});
