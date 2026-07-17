"use strict";

document.addEventListener("DOMContentLoaded", () => {
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
});
