"use strict";

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-explorador-pozos]").forEach((explorador) => {
        const selectorPlataforma = explorador.querySelector("[data-selector-plataforma]");
        const estadoPlataforma = explorador.querySelector("[data-estado-plataforma]");
        const gruposPozos = explorador.querySelectorAll("[data-grupo-plataforma]");

        selectorPlataforma.addEventListener("change", () => {
            gruposPozos.forEach((grupo) => {
                grupo.hidden = grupo.dataset.grupoPlataforma !== selectorPlataforma.value;
            });

            const grupoActivo = Array.from(gruposPozos).find(
                (grupo) => grupo.dataset.grupoPlataforma === selectorPlataforma.value
            );

            if (!grupoActivo) {
                estadoPlataforma.textContent = "Elige una plataforma para mostrar sus pozos.";
                return;
            }

            const total = grupoActivo.querySelectorAll(".ficha-pozo").length;
            estadoPlataforma.textContent = `${grupoActivo.dataset.plataforma}: ${total} pozos encontrados.`;
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
