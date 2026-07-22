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



    const formatoNumero = new Intl.NumberFormat("es-MX", {
        maximumFractionDigits: 2,
    });

    const mesesProduccion = [
        "ene",
        "feb",
        "mar",
        "abr",
        "may",
        "jun",
        "jul",
        "ago",
        "sep",
        "oct",
        "nov",
        "dic",
    ];

    const etiquetasVariablesProduccion = {
        gas: "GAS (MPCD)",
        agua: "AGUA (MBD)",
        aceite: "ACEITE (MBD)",
        goc: "GOR (pcd/bd)",
    };

    const variablesGraficaProduccion = {
        gas: {
            etiqueta: "GAS (MPCD)",
            etiquetaCorta: "GAS",
            eje: "derecho",
            convertir: (valor) => valor,
        },
        aceite: {
            etiqueta: "ACEITE (bpd)",
            etiquetaCorta: "ACEITE",
            eje: "izquierdo",
            convertir: (valor) => valor * 1000,
        },
        agua: {
            etiqueta: "AGUA (bpd)",
            etiquetaCorta: "AGUA",
            eje: "izquierdo",
            convertir: (valor) => valor * 1000,
        },
        goc: {
            etiqueta: "GOR (pcd/bd)",
            etiquetaCorta: "GOR",
            eje: "derecho",
            convertir: (valor) => valor,
        },
    };

    const ordenVariablesGrafica = ["aceite", "agua", "gas", "goc"];

    const coloresVariablesProduccion = {
        gas: "#f2c200",
        aceite: "#0052cc",
        agua: "#00875a",
        goc: "#c2188f",
    };

    const coloresTextoVariablesProduccion = {
        ...coloresVariablesProduccion,
        gas: "#9a6b00",
    };

    const coloresProduccion = [
        "#0052cc",
        "#00875a",
        "#f2c200",
        "#c2188f",
        "#5b2c83",
        "#c25100",
        "#17494d",
        "#626f86",
    ];

    const textosPeriodoGraficaProduccion = {
        semestre: "Datos mostrados de forma semestral",
        trimestre: "Datos mostrados de forma trimestral",
        anio: "Datos mostrados de forma anual",
        total: "Datos mostrados como acumulado total",
    };

    const esVistaMovilProduccion = () => window.matchMedia("(max-width: 760px)").matches;

    const serieProduccion = (fila) => [fila.campo, fila.plataforma, fila.pozo]
        .filter(Boolean)
        .join(" / ") || "TOTAL";

    const etiquetaPeriodo = (fila) => fila.periodo || "TOTAL";

    const formatearPeriodoProduccion = (periodo) => {
        if (!periodo || periodo === "TOTAL") return periodo || "TOTAL";

        const partes = String(periodo).split("-");
        const anio = partes[0];
        const mes = Number(partes[1]);
        if (/^\d{4}$/.test(anio) && mes >= 1 && mes <= 12) {
            return `${mesesProduccion[mes - 1]}-${anio}`;
        }

        return periodo;
    };

    const etiquetaNodoProduccion = (punto) => formatoNumero.format(punto.valor);

    const etiquetaTooltipPuntoProduccion = (punto) => (
        `${formatearPeriodoProduccion(punto.periodo)}: ${formatoNumero.format(punto.valor)}`
    );

    const descripcionLineaProduccion = (linea) => {
        const meta = variablesGraficaProduccion[linea.variable];
        return `${linea.serieCorta} - ${meta?.etiqueta || linea.variable}`;
    };

    const distanciaPuntoSegmento = (x, y, x1, y1, x2, y2) => {
        const dx = x2 - x1;
        const dy = y2 - y1;
        if (!dx && !dy) return Math.hypot(x - x1, y - y1);

        const proporcion = Math.max(0, Math.min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)));
        const px = x1 + proporcion * dx;
        const py = y1 + proporcion * dy;
        return Math.hypot(x - px, y - py);
    };

    const elementoGraficaEnPosicion = (canvas, evento) => {
        const elementos = canvas.__produccionInteractivos || [];
        const rect = canvas.getBoundingClientRect();
        const escala = window.devicePixelRatio || 1;
        const anchoLogico = canvas.width / escala;
        const altoLogico = canvas.height / escala;
        const x = ((evento.clientX - rect.left) / rect.width) * anchoLogico;
        const y = ((evento.clientY - rect.top) / rect.height) * altoLogico;
        let mejor = null;

        elementos.forEach((elemento) => {
            const distancia = elemento.tipo === "segmento"
                ? distanciaPuntoSegmento(x, y, elemento.x1, elemento.y1, elemento.x2, elemento.y2)
                : Math.hypot(x - elemento.x, y - elemento.y);
            const limite = elemento.tipo === "segmento" ? 9 : 12;

            if (distancia > limite) return;
            if (!mejor || distancia < mejor.distancia || elemento.tipo === "punto") {
                mejor = { ...elemento, distancia };
            }
        });

        return mejor;
    };

    const posicionarTooltipProduccion = (canvas, tooltip, elemento, evento) => {
        const contenedor = tooltip.offsetParent || tooltip.parentElement || canvas.parentElement;
        const contenedorRect = contenedor.getBoundingClientRect();
        const canvasRect = canvas.getBoundingClientRect();
        const escala = window.devicePixelRatio || 1;
        const anchoLogico = canvas.width / escala;
        const altoLogico = canvas.height / escala;
        const tienePunto = Number.isFinite(elemento.x) && Number.isFinite(elemento.y);
        const xReferencia = tienePunto
            ? canvasRect.left - contenedorRect.left + elemento.x * (canvasRect.width / anchoLogico)
            : evento.clientX - contenedorRect.left;
        const yReferencia = tienePunto
            ? canvasRect.top - contenedorRect.top + elemento.y * (canvasRect.height / altoLogico)
            : evento.clientY - contenedorRect.top;
        const margen = 8;
        const separacion = 10;

        tooltip.hidden = false;
        tooltip.style.transform = "none";

        const anchoTooltip = tooltip.offsetWidth;
        const altoTooltip = tooltip.offsetHeight;
        let izquierda = xReferencia + separacion;
        let superior = yReferencia - altoTooltip - separacion;

        if (izquierda + anchoTooltip > contenedorRect.width - margen) {
            izquierda = xReferencia - anchoTooltip - separacion;
        }
        if (superior < margen) {
            superior = yReferencia + separacion;
        }

        izquierda = Math.max(
            margen,
            Math.min(izquierda, contenedorRect.width - anchoTooltip - margen),
        );
        superior = Math.max(
            margen,
            Math.min(superior, contenedorRect.height - altoTooltip - margen),
        );

        tooltip.style.left = `${izquierda}px`;
        tooltip.style.top = `${superior}px`;
    };

    const filtrosProduccionPorNivel = {
        total: ["campo", "plataforma", "pozo"],
        campo: ["campo"],
        plataforma: ["campo", "plataforma"],
        pozo: ["campo", "plataforma", "pozo"],
    };

    const intervaloAutomaticoPorNivel = {
        campo: "anio",
        plataforma: "anio",
        pozo: "trimestre",
    };

    const obtenerValoresSeleccionados = (formulario, nombre) => Array.from(
        formulario.querySelectorAll(`[name="${nombre}"]`)
    ).flatMap((elemento) => {
        if (elemento instanceof HTMLSelectElement) {
            return Array.from(elemento.selectedOptions)
                .map((opcion) => opcion.value)
                .filter(Boolean);
        }

        if (elemento.type === "checkbox") {
            return elemento.checked ? [elemento.value] : [];
        }

        return elemento.value ? [elemento.value] : [];
    });

    const nivelProduccionPorSeleccion = (formulario) => {
        if (obtenerValoresSeleccionados(formulario, "pozo").length) return "pozo";
        if (obtenerValoresSeleccionados(formulario, "plataforma").length) return "plataforma";
        return "campo";
    };

    const aplicarNivelProduccion = (formulario, ajustarIntervalo = false) => {
        const nivel = nivelProduccionPorSeleccion(formulario);

        formulario.nivel.value = nivel;
        if (ajustarIntervalo && formulario.intervalo) {
            formulario.intervalo.value = intervaloAutomaticoPorNivel[nivel] || formulario.intervalo.value;
        }

        return nivel;
    };

    const actualizarFiltrosProduccion = (formulario) => {
        filtrarPlataformasProduccion(formulario);
        filtrarPozosProduccion(formulario);

        const campos = obtenerValoresSeleccionados(formulario, "campo");
        const plataformas = obtenerValoresSeleccionados(formulario, "plataforma");

        ["campo", "plataforma", "pozo"].forEach((nombre) => {
            const control = formulario.querySelector(`[name="${nombre}"]`);
            const contenedor = control?.closest(".control-produccion");
            let activo = true;

            if (!control) return;
            if (nombre === "plataforma") activo = campos.length > 0;
            if (nombre === "pozo") activo = plataformas.length > 0;

            control.disabled = !activo;
            if (contenedor) {
                contenedor.classList.toggle("control-produccion-inactivo", !activo);
            }
        });
    };

    const filtrarPlataformasProduccion = (formulario) => {
        const selectorPlataformas = formulario.querySelector('[name="plataforma"]');
        if (!selectorPlataformas) return;

        const campos = obtenerValoresSeleccionados(formulario, "campo");
        let visibles = 0;

        Array.from(selectorPlataformas.options).forEach((opcion) => {
            if (!opcion.value) {
                opcion.hidden = false;
                opcion.disabled = false;
                return;
            }

            const visible = !campos.length || campos.includes(opcion.dataset.campo);

            opcion.hidden = !visible;
            opcion.disabled = !visible;
            if (!visible && opcion.selected) selectorPlataformas.value = "";
            if (visible) visibles += 1;
        });

        selectorPlataformas.title = visibles
            ? `${visibles} plataformas disponibles para la seleccion actual.`
            : "No hay plataformas para el campo seleccionado.";
    };

    const filtrarPozosProduccion = (formulario) => {
        const selectorPozos = formulario.querySelector('[name="pozo"]');
        if (!selectorPozos) return;

        const campos = obtenerValoresSeleccionados(formulario, "campo");
        const plataformas = obtenerValoresSeleccionados(formulario, "plataforma");
        let visibles = 0;

        Array.from(selectorPozos.options).forEach((opcion) => {
            if (!opcion.value) {
                opcion.hidden = false;
                opcion.disabled = false;
                return;
            }

            const coincideCampo = !campos.length || campos.includes(opcion.dataset.campo);
            const coincidePlataforma = plataformas.length
                ? plataformas.includes(opcion.dataset.plataforma)
                : false;
            const visible = coincideCampo && coincidePlataforma;

            opcion.hidden = !visible;
            opcion.disabled = !visible;
            if (!visible && opcion.selected) selectorPozos.value = "";
            if (visible) visibles += 1;
        });

        selectorPozos.title = visibles
            ? `${visibles} pozos disponibles para la seleccion actual.`
            : "No hay pozos para la plataforma seleccionada.";
    };

    const rectangulosSeEnciman = (a, b) => !(
        a.x + a.ancho < b.x
        || b.x + b.ancho < a.x
        || a.y + a.alto < b.y
        || b.y + b.alto < a.y
    );

    const dibujarEtiquetaNodo = (contexto, etiquetas, texto, x, y, limites) => {
        contexto.font = "11px Arial";
        const anchoTexto = contexto.measureText(texto).width;
        const opciones = [
            { x: x - anchoTexto / 2 - 4, y: y - 24 },
            { x: x - anchoTexto / 2 - 4, y: y + 8 },
            { x: x + 8, y: y - 8 },
            { x: x - anchoTexto - 16, y: y - 8 },
        ];

        for (const opcion of opciones) {
            const rectangulo = {
                x: opcion.x,
                y: opcion.y,
                ancho: anchoTexto + 8,
                alto: 16,
            };
            const visible = rectangulo.x >= limites.izquierda
                && rectangulo.y >= limites.superior
                && rectangulo.x + rectangulo.ancho <= limites.derecha
                && rectangulo.y + rectangulo.alto <= limites.inferior;
            const libre = etiquetas.every((etiqueta) => !rectangulosSeEnciman(rectangulo, etiqueta));

            if (!visible || !libre) continue;

            contexto.fillStyle = "rgba(255, 255, 255, 0.86)";
            contexto.fillRect(rectangulo.x, rectangulo.y, rectangulo.ancho, rectangulo.alto);
            contexto.fillStyle = "#292929";
            contexto.textAlign = "center";
            contexto.fillText(texto, rectangulo.x + rectangulo.ancho / 2, rectangulo.y + 12);
            etiquetas.push(rectangulo);
            return true;
        }

        return false;
    };

    const nombreCortoSerie = (serie) => {
        const partes = serie.split(" / ").filter(Boolean);
        return partes[partes.length - 1] || serie;
    };

    const dibujarEtiquetaSerie = (contexto, etiquetas, texto, x, y, color, limites) => {
        contexto.font = "bold 11px Arial";
        const anchoTexto = contexto.measureText(texto).width;
        const ancho = anchoTexto + 14;
        const alto = 19;
        const opciones = [
            { x: x + 10, y: y - alto / 2 },
            { x: x - ancho - 10, y: y - alto / 2 },
            { x: x - ancho / 2, y: y - 30 },
            { x: x - ancho / 2, y: y + 12 },
        ];

        for (const opcion of opciones) {
            const rectangulo = {
                x: opcion.x,
                y: opcion.y,
                ancho,
                alto,
            };
            const visible = rectangulo.x >= limites.izquierda
                && rectangulo.y >= limites.superior
                && rectangulo.x + rectangulo.ancho <= limites.derecha
                && rectangulo.y + rectangulo.alto <= limites.inferior;
            const libre = etiquetas.every((etiqueta) => !rectangulosSeEnciman(rectangulo, etiqueta));

            if (!visible || !libre) continue;

            contexto.fillStyle = "rgba(255, 255, 255, 0.92)";
            contexto.fillRect(rectangulo.x, rectangulo.y, rectangulo.ancho, rectangulo.alto);
            contexto.strokeStyle = color;
            contexto.lineWidth = 1;
            contexto.strokeRect(rectangulo.x, rectangulo.y, rectangulo.ancho, rectangulo.alto);
            contexto.fillStyle = color;
            contexto.textAlign = "center";
            contexto.fillText(texto, rectangulo.x + rectangulo.ancho / 2, rectangulo.y + 13);
            etiquetas.push(rectangulo);
            return true;
        }

        return false;
    };

    const variablesActivasGrafica = (variable, variablesSeleccionadas) => {
        if (variable !== "todas") return [variable];

        const seleccionadas = variablesSeleccionadas.length
            ? variablesSeleccionadas
            : ordenVariablesGrafica;

        return ordenVariablesGrafica.filter((item) => seleccionadas.includes(item));
    };

    const construirLineasGrafica = (filas, variable, variablesSeleccionadas) => {
        const variables = variablesActivasGrafica(variable, variablesSeleccionadas)
            .filter((item) => variablesGraficaProduccion[item]);
        const series = [...new Set(filas.map(serieProduccion))];
        const variasVariables = variable === "todas";
        const lineas = [];

        series.forEach((serie) => {
            variables.forEach((variableActual) => {
                const meta = variablesGraficaProduccion[variableActual];
                const puntos = filas
                    .filter((fila) => serieProduccion(fila) === serie)
                    .sort((a, b) => etiquetaPeriodo(a).localeCompare(etiquetaPeriodo(b)))
                    .map((fila) => ({
                        fila,
                        periodo: etiquetaPeriodo(fila),
                        valor: meta.convertir(Number(fila[variableActual] || 0)),
                    }));

                if (!puntos.length) return;

                const serieCorta = nombreCortoSerie(serie);
                const indice = lineas.length;
                lineas.push({
                    id: `${serie}-${variableActual}`,
                    serie,
                    serieCorta,
                    variable: variableActual,
                    eje: meta.eje,
                    etiqueta: variasVariables ? `${serieCorta} - ${meta.etiqueta}` : serie,
                    etiquetaGrafica: variasVariables ? `${serieCorta} ${meta.etiquetaCorta}` : serieCorta,
                    color: coloresVariablesProduccion[variableActual]
                        || coloresProduccion[indice % coloresProduccion.length],
                    puntos,
                });
            });
        });

        return lineas;
    };

    const renderizarLeyendaProduccion = (contenedor, filas, variable, variablesSeleccionadas) => {
        if (!contenedor) return;

        const lineas = construirLineasGrafica(filas, variable, variablesSeleccionadas);
        if (lineas.length <= 1) {
            contenedor.innerHTML = "";
            contenedor.hidden = true;
            return;
        }

        contenedor.hidden = false;
        contenedor.innerHTML = lineas.map((linea) => `
            <span class="elemento-leyenda-produccion">
                <span
                    class="muestra-leyenda-produccion"
                    style="background-color: ${linea.color}"
                    aria-hidden="true"
                ></span>
                <span>${linea.etiqueta}</span>
            </span>
        `).join("");
    };

    const crearEscalaProduccion = (maximo, preferirDecenas = false) => {
        const valorMaximo = Math.max(Number(maximo) || 0, 1);

        if (preferirDecenas && valorMaximo <= 100) {
            return {
                maximo: Math.max(10, Math.ceil(valorMaximo / 10) * 10),
                paso: 10,
            };
        }

        const divisionesDeseadas = 4;
        const pasoCrudo = valorMaximo / divisionesDeseadas;
        const magnitud = 10 ** Math.floor(Math.log10(pasoCrudo));
        const normalizado = pasoCrudo / magnitud;
        const pasoNormalizado = normalizado <= 1
            ? 1
            : normalizado <= 2
                ? 2
                : normalizado <= 5
                    ? 5
                    : 10;
        let paso = pasoNormalizado * magnitud;

        if (preferirDecenas) {
            paso = Math.max(10, Math.ceil(paso / 10) * 10);
        }

        return {
            maximo: Math.max(paso, Math.ceil(valorMaximo / paso) * paso),
            paso,
        };
    };

    const dibujarEjeProduccion = (contexto, margen, anchoPlot, altoPlot, escala, posicion, color) => {
        contexto.fillStyle = color;
        contexto.font = "12px Arial";
        contexto.textAlign = posicion === "izquierdo" ? "right" : "left";

        for (let valor = 0; valor <= escala.maximo + escala.paso / 2; valor += escala.paso) {
            const y = margen.superior + altoPlot - (valor / escala.maximo) * altoPlot;
            const x = posicion === "izquierdo"
                ? margen.izquierda - 8
                : margen.izquierda + anchoPlot + 8;
            contexto.fillText(formatoNumero.format(valor), x, y + 4);
        }
    };

    const variablesEjeProduccion = (lineas, eje) => ordenVariablesGrafica
        .filter((variable) => lineas.some((linea) => linea.eje === eje && linea.variable === variable));

    const dibujarTituloEjeProduccion = (contexto, variables, x, y, alineacion, prefijo = "") => {
        if (!variables.length) return;

        contexto.font = "bold 12px Arial";
        contexto.textAlign = "left";
        const segmentos = [];

        if (prefijo) {
            segmentos.push({
                texto: prefijo,
                color: "#515151",
            });
        }

        variables.forEach((variable, indice) => {
            const etiqueta = variablesGraficaProduccion[variable]?.etiqueta;
            if (!etiqueta) return;

            segmentos.push({
                texto: `${indice ? ", " : ""}${etiqueta}`,
                color: coloresTextoVariablesProduccion[variable] || "#515151",
            });
        });

        const anchoTotal = segmentos.reduce(
            (suma, segmento) => suma + contexto.measureText(segmento.texto).width,
            0,
        );
        let xActual = alineacion === "right" ? x - anchoTotal : x;

        segmentos.forEach((segmento) => {
            contexto.fillStyle = segmento.color;
            contexto.fillText(segmento.texto, xActual, y);
            xActual += contexto.measureText(segmento.texto).width;
        });
    };

    const dibujarGraficaProduccion = (
        canvas,
        filas,
        variable,
        variablesSeleccionadas = ordenVariablesGrafica,
    ) => {
        const contexto = canvas.getContext("2d");
        const rect = canvas.getBoundingClientRect();
        const escala = window.devicePixelRatio || 1;
        const esMovil = esVistaMovilProduccion();
        const anchoGrafica = esMovil
            ? Math.max(280, rect.width || canvas.clientWidth || 320)
            : Math.max(720, rect.width);
        const altoGrafica = esMovil ? 340 : 460;
        canvas.width = anchoGrafica * escala;
        canvas.height = altoGrafica * escala;
        contexto.scale(escala, escala);

        const ancho = canvas.width / escala;
        const alto = canvas.height / escala;
        contexto.clearRect(0, 0, ancho, alto);
        canvas.__produccionInteractivos = [];

        if (!filas.length) {
            contexto.fillStyle = "#606060";
            contexto.font = "14px Arial";
            contexto.fillText("No hay datos para graficar.", 24, 48);
            return;
        }

        const lineas = construirLineasGrafica(filas, variable, variablesSeleccionadas);
        if (!lineas.length) {
            contexto.fillStyle = "#606060";
            contexto.font = "14px Arial";
            contexto.fillText("Selecciona al menos una variable para graficar.", 24, 48);
            return;
        }

        const hayEjeDerecho = lineas.some((linea) => linea.eje === "derecho");
        const hayEjeIzquierdo = lineas.some((linea) => linea.eje === "izquierdo");
        const margen = {
            superior: esMovil ? (variable === "todas" ? 38 : 20) : (variable === "todas" ? 50 : 34),
            derecha: esMovil ? (hayEjeDerecho ? 48 : 14) : (hayEjeDerecho ? 84 : 24),
            inferior: esMovil ? 42 : 54,
            izquierda: esMovil ? (hayEjeIzquierdo ? 48 : 22) : 76,
        };
        const anchoPlot = ancho - margen.izquierda - margen.derecha;
        const altoPlot = alto - margen.superior - margen.inferior;
        const periodos = [...new Set(filas.map(etiquetaPeriodo))];
        const maximoIzquierdo = Math.max(
            ...lineas
                .filter((linea) => linea.eje === "izquierdo")
                .flatMap((linea) => linea.puntos.map((punto) => punto.valor)),
            1,
        );
        const maximoDerecho = Math.max(
            ...lineas
                .filter((linea) => linea.eje === "derecho")
                .flatMap((linea) => linea.puntos.map((punto) => punto.valor)),
            1,
        );
        const escalaIzquierda = crearEscalaProduccion(maximoIzquierdo);
        const escalaDerecha = crearEscalaProduccion(maximoDerecho, true);
        const escalaGrid = hayEjeIzquierdo ? escalaIzquierda : escalaDerecha;
        const etiquetasValor = [];
        const limitesEtiquetas = {
            izquierda: margen.izquierda,
            superior: margen.superior,
            derecha: margen.izquierda + anchoPlot,
            inferior: margen.superior + altoPlot,
        };
        const mostrarEtiquetasNodos = !esMovil;
        const mostrarEtiquetasSerie = !esMovil || lineas.length === 1;
        const radioPunto = esMovil ? 2.6 : 3;
        const grosorLinea = esMovil ? 2.4 : 2;
        const yParaValor = (valor, eje) => {
            const escalaActual = eje === "derecho" ? escalaDerecha : escalaIzquierda;
            return margen.superior + altoPlot - (valor / escalaActual.maximo) * altoPlot;
        };
        const xParaPeriodo = (periodo) => {
            const posicionPeriodo = periodos.indexOf(periodo);
            return margen.izquierda + (posicionPeriodo / Math.max(periodos.length - 1, 1)) * anchoPlot;
        };
        const puntosLineaGrafica = (linea) => linea.puntos.map((punto) => ({
            ...punto,
            x: xParaPeriodo(punto.periodo),
            y: yParaValor(punto.valor, linea.eje),
        }));
        const registrarInteraccionLinea = (linea, puntos) => {
            const descripcion = descripcionLineaProduccion(linea);
            puntos.forEach((punto, indice) => {
                canvas.__produccionInteractivos.push({
                    tipo: "punto",
                    x: punto.x,
                    y: punto.y,
                    texto: `${descripcion} | ${etiquetaTooltipPuntoProduccion(punto)}`,
                });
                if (indice === 0) return;
                const previo = puntos[indice - 1];
                canvas.__produccionInteractivos.push({
                    tipo: "segmento",
                    x1: previo.x,
                    y1: previo.y,
                    x2: punto.x,
                    y2: punto.y,
                    texto: descripcion,
                });
            });
        };

        contexto.strokeStyle = "#d7d7d7";
        contexto.lineWidth = 1;
        contexto.beginPath();
        contexto.moveTo(margen.izquierda, margen.superior);
        contexto.lineTo(margen.izquierda, margen.superior + altoPlot);
        contexto.lineTo(margen.izquierda + anchoPlot, margen.superior + altoPlot);
        if (hayEjeDerecho) {
            contexto.moveTo(margen.izquierda + anchoPlot, margen.superior);
            contexto.lineTo(margen.izquierda + anchoPlot, margen.superior + altoPlot);
        }
        contexto.stroke();

        for (let valor = 0; valor <= escalaGrid.maximo + escalaGrid.paso / 2; valor += escalaGrid.paso) {
            const y = margen.superior + altoPlot - (valor / escalaGrid.maximo) * altoPlot;
            contexto.strokeStyle = "rgba(0, 0, 0, 0.08)";
            contexto.beginPath();
            contexto.moveTo(margen.izquierda, y);
            contexto.lineTo(margen.izquierda + anchoPlot, y);
            contexto.stroke();
        }

        if (hayEjeIzquierdo) {
            dibujarEjeProduccion(
                contexto,
                margen,
                anchoPlot,
                altoPlot,
                escalaIzquierda,
                "izquierdo",
                "#515151",
            );
        }
        if (hayEjeDerecho) {
            dibujarEjeProduccion(
                contexto,
                margen,
                anchoPlot,
                altoPlot,
                escalaDerecha,
                "derecho",
                "#292929",
            );
        }

        if (variable === "todas" && !esMovil) {
            const variablesIzquierda = variablesEjeProduccion(lineas, "izquierdo");
            const variablesDerecha = variablesEjeProduccion(lineas, "derecho");

            dibujarTituloEjeProduccion(
                contexto,
                variablesIzquierda,
                margen.izquierda,
                20,
                "left",
                "Producción: ",
            );
            dibujarTituloEjeProduccion(
                contexto,
                variablesDerecha,
                margen.izquierda + anchoPlot,
                20,
                "right",
            );
        }

        if (periodos.length === 1) {
            const barraAncho = Math.max(8, anchoPlot / Math.max(lineas.length * 1.7, 1));
            lineas.forEach((linea, indice) => {
                const punto = linea.puntos[0];
                const altoBarra = Math.max(0, margen.superior + altoPlot - yParaValor(punto.valor, linea.eje));
                const x = margen.izquierda + indice * (anchoPlot / Math.max(lineas.length, 1)) + 8;
                const y = margen.superior + altoPlot - altoBarra;
                contexto.fillStyle = linea.color;
                contexto.fillRect(x, y, barraAncho, altoBarra);
                if (mostrarEtiquetasNodos) {
                    dibujarEtiquetaNodo(
                        contexto,
                        etiquetasValor,
                        etiquetaNodoProduccion(punto),
                        x + barraAncho / 2,
                        y,
                        limitesEtiquetas,
                    );
                }
                if (mostrarEtiquetasSerie) {
                    dibujarEtiquetaSerie(
                        contexto,
                        etiquetasValor,
                        linea.etiquetaGrafica,
                        x + barraAncho / 2,
                        y + Math.max(12, altoBarra / 2),
                        linea.color,
                        limitesEtiquetas,
                    );
                }
                canvas.__produccionInteractivos.push({
                    tipo: "punto",
                    x: x + barraAncho / 2,
                    y,
                    texto: `${descripcionLineaProduccion(linea)} | ${etiquetaTooltipPuntoProduccion(punto)}`,
                });
            });
        } else {
            lineas.forEach((linea) => {
                const puntosDibujo = puntosLineaGrafica(linea);
                registrarInteraccionLinea(linea, puntosDibujo);
                contexto.strokeStyle = linea.color;
                contexto.fillStyle = linea.color;
                contexto.lineWidth = grosorLinea;
                contexto.beginPath();
                puntosDibujo.forEach((punto, indice) => {
                    if (indice === 0) contexto.moveTo(punto.x, punto.y);
                    else contexto.lineTo(punto.x, punto.y);
                });
                contexto.stroke();

                if (mostrarEtiquetasSerie && puntosDibujo.length) {
                    const ultimoPunto = puntosDibujo[puntosDibujo.length - 1];
                    dibujarEtiquetaSerie(
                        contexto,
                        etiquetasValor,
                        linea.etiquetaGrafica,
                        ultimoPunto.x,
                        ultimoPunto.y,
                        linea.color,
                        limitesEtiquetas,
                    );
                }

                puntosDibujo.forEach((punto) => {
                    contexto.beginPath();
                    contexto.arc(punto.x, punto.y, radioPunto, 0, Math.PI * 2);
                    contexto.fill();
                    if (mostrarEtiquetasNodos) {
                        dibujarEtiquetaNodo(
                            contexto,
                            etiquetasValor,
                            etiquetaNodoProduccion(punto),
                            punto.x,
                            punto.y,
                            limitesEtiquetas,
                        );
                    }
                });
            });
        }

        contexto.fillStyle = "#292929";
        contexto.font = esMovil ? "10px Arial" : "11px Arial";
        contexto.textAlign = "center";
        const aniosPeriodo = periodos.map((periodo) => String(periodo).slice(0, 4));
        const esSerieAnual = periodos.every((periodo) => /^\d{4}-\d{2}$/.test(String(periodo)))
            && new Set(aniosPeriodo).size === periodos.length;
        const salto = esMovil
            ? (periodos.length <= 5 ? 1 : Math.max(1, Math.ceil(periodos.length / 4)))
            : (esSerieAnual || periodos.length <= 14
                ? 1
                : Math.max(1, Math.ceil(periodos.length / 10)));
        periodos.forEach((periodo, indice) => {
            if (indice % salto !== 0 && indice !== periodos.length - 1) return;
            const x = margen.izquierda + (indice / Math.max(periodos.length - 1, 1)) * anchoPlot;
            contexto.save();
            contexto.translate(x, margen.superior + altoPlot + 18);
            contexto.rotate(-Math.PI / 6);
            const etiquetaEje = esSerieAnual ? String(periodo).slice(0, 4) : formatearPeriodoProduccion(periodo);
            contexto.fillText(etiquetaEje, 0, 0);
            contexto.restore();
        });
    };

    const actualizarPieGraficaProduccion = (elemento, intervalo, visible = true) => {
        if (!elemento) return;

        const etiqueta = elemento.querySelector("span") || elemento;
        etiqueta.textContent = textosPeriodoGraficaProduccion[intervalo]
            || "Datos mostrados de acuerdo con el intervalo seleccionado";
        elemento.hidden = !visible;
    };

    const ocultarPieGraficaProduccion = (elemento) => {
        if (elemento) elemento.hidden = true;
    };

    const actualizarResumenSeleccionProduccion = (elemento, formulario) => {
        if (!elemento) return;

        const campo = obtenerValoresSeleccionados(formulario, "campo")[0];
        const plataforma = obtenerValoresSeleccionados(formulario, "plataforma")[0];
        const pozo = obtenerValoresSeleccionados(formulario, "pozo")[0];
        const segmentos = [];

        if (campo) segmentos.push(`Campo: ${campo}`);
        if (plataforma) segmentos.push(`Plataforma: ${plataforma}`);
        if (pozo) segmentos.push(`Pozo: ${pozo}`);

        elemento.textContent = segmentos.join(" | ");
    };

    const limpiarResultadosProduccion = (tabla, canvas, leyenda, mensaje = "Selecciona filtros para consultar.") => {
        const thead = tabla.querySelector("thead");
        const tbody = tabla.querySelector("tbody");
        thead.innerHTML = "";
        tbody.innerHTML = "";
        if (leyenda) {
            leyenda.innerHTML = "";
            leyenda.hidden = true;
        }

        const contexto = canvas.getContext("2d");
        const rect = canvas.getBoundingClientRect();
        const escala = window.devicePixelRatio || 1;
        const esMovil = esVistaMovilProduccion();
        const anchoGrafica = esMovil
            ? Math.max(280, rect.width || canvas.clientWidth || 320)
            : Math.max(720, rect.width);
        const altoGrafica = esMovil ? 340 : 460;
        canvas.width = anchoGrafica * escala;
        canvas.height = altoGrafica * escala;
        contexto.scale(escala, escala);
        contexto.clearRect(0, 0, canvas.width / escala, canvas.height / escala);
        contexto.fillStyle = "#606060";
        contexto.font = "14px Arial";
        contexto.fillText(mensaje, 24, 48);
    };

    const validarSeleccionProduccion = (formulario) => {
        const nivel = formulario.nivel.value;
        const campos = obtenerValoresSeleccionados(formulario, "campo");
        const plataformas = obtenerValoresSeleccionados(formulario, "plataforma");
        const pozos = obtenerValoresSeleccionados(formulario, "pozo");

        if (campos.length > 1) {
            return "Selecciona un solo campo para consultar.";
        }
        if (nivel !== "total" && campos.length !== 1) {
            return "Selecciona un campo para consultar.";
        }
        if (nivel === "plataforma" && plataformas.length !== 1) {
            return "Selecciona una sola plataforma para consultar.";
        }
        if (nivel === "pozo" && plataformas.length !== 1) {
            return "Selecciona una plataforma antes de consultar por pozo.";
        }
        if (nivel === "pozo" && pozos.length !== 1) {
            return "Selecciona un solo pozo para consultar.";
        }

        return "";
    };

    const renderizarTablaProduccion = (tabla, filas, variables) => {
        const thead = tabla.querySelector("thead");
        const tbody = tabla.querySelector("tbody");
        const esMovil = esVistaMovilProduccion();
        const dimensiones = ["periodo", "campo", "plataforma", "pozo"]
            .filter((columna) => filas.some((fila) => fila[columna] !== undefined));
        const dimensionesVisibles = esMovil
            ? dimensiones.filter((columna) => columna === "periodo")
            : dimensiones;
        const columnas = [...dimensionesVisibles, ...variables];

        thead.innerHTML = `<tr>${columnas.map((columna) => {
            const claseVariable = coloresVariablesProduccion[columna]
                ? ` class="tabla-produccion-variable tabla-produccion-variable-${columna}"`
                : "";
            return `<th${claseVariable}>${etiquetasVariablesProduccion[columna] || columna.toUpperCase()}</th>`;
        }).join("")}</tr>`;

        tbody.innerHTML = filas.map((fila) => `<tr>${columnas.map((columna) => {
            const valor = fila[columna] ?? "";
            const texto = columna === "periodo"
                ? formatearPeriodoProduccion(valor)
                : typeof valor === "number" ? formatoNumero.format(valor) : valor;
            return `<td>${texto}</td>`;
        }).join("")}</tr>`).join("");
    };

    document.querySelectorAll("[data-produccion-interactiva]").forEach((panel) => {
        const formulario = panel.querySelector("[data-formulario-produccion]");
        const estado = panel.querySelector("[data-estado-produccion]");
        const tabla = panel.querySelector("[data-tabla-produccion]");
        const canvas = panel.querySelector("[data-grafica-produccion]");
        const selectorVariable = panel.querySelector("[data-variable-grafica]");
        const leyenda = panel.querySelector("[data-leyenda-produccion]");
        const tooltip = panel.querySelector("[data-tooltip-produccion]");
        const pieGrafica = panel.querySelector("[data-pie-grafica-produccion]");
        const resumenSeleccion = panel.querySelector("[data-resumen-seleccion-produccion]");
        let filasActuales = [];
        let variablesActuales = [...ordenVariablesGrafica];
        let temporizadorConsulta = null;

        const consultarProduccion = async () => {
            ocultarPieGraficaProduccion(pieGrafica);
            aplicarNivelProduccion(formulario);
            actualizarFiltrosProduccion(formulario);
            actualizarResumenSeleccionProduccion(resumenSeleccion, formulario);
            const errorSeleccion = validarSeleccionProduccion(formulario);
            if (errorSeleccion) {
                estado.textContent = errorSeleccion;
                filasActuales = [];
                limpiarResultadosProduccion(tabla, canvas, leyenda, errorSeleccion);
                return;
            }

            const parametros = new URLSearchParams();
            parametros.set("nivel", formulario.nivel.value);
            parametros.set("intervalo", formulario.intervalo.value);

            const filtrosActivos = filtrosProduccionPorNivel[formulario.nivel.value] || [];
            filtrosActivos.forEach((nombre) => {
                obtenerValoresSeleccionados(formulario, nombre).forEach((valor) => {
                    parametros.append(nombre, valor);
                });
            });

            variablesActuales = obtenerValoresSeleccionados(formulario, "variables");
            if (!variablesActuales.length) {
                variablesActuales = [...ordenVariablesGrafica];
            }
            variablesActuales.forEach((valor) => parametros.append("variables", valor));

            if (formulario.fecha_inicio.value) parametros.set("fecha_inicio", formulario.fecha_inicio.value);
            if (formulario.fecha_fin.value) parametros.set("fecha_fin", formulario.fecha_fin.value);

            estado.textContent = "Consultando producción...";
            const respuesta = await fetch(`/api/produccion?${parametros.toString()}`);
            const datos = await respuesta.json();

            if (!respuesta.ok) {
                estado.textContent = datos.error || "No se pudo consultar la producción.";
                return;
            }

            filasActuales = datos.filas;
            actualizarPieGraficaProduccion(pieGrafica, formulario.intervalo.value, filasActuales.length > 0);
            const notas = datos.notas?.length ? ` ${datos.notas.join(" ")}` : "";
            estado.textContent = `${filasActuales.length} filas encontradas.${notas}`;
            renderizarTablaProduccion(tabla, filasActuales, variablesActuales);
            renderizarLeyendaProduccion(leyenda, filasActuales, selectorVariable.value, variablesActuales);

            if (selectorVariable.value !== "todas" && !variablesActuales.includes(selectorVariable.value)) {
                selectorVariable.value = variablesActuales[0] || "todas";
            }
            dibujarGraficaProduccion(canvas, filasActuales, selectorVariable.value, variablesActuales);
        };

        const programarConsultaProduccion = () => {
            window.clearTimeout(temporizadorConsulta);
            temporizadorConsulta = window.setTimeout(consultarProduccion, 220);
        };

        formulario.querySelectorAll('[name="intervalo"], [name="fecha_inicio"], [name="fecha_fin"]').forEach((control) => {
            control.addEventListener("change", () => {
                ocultarPieGraficaProduccion(pieGrafica);
                programarConsultaProduccion();
            });
        });

        formulario.querySelectorAll('[name="campo"]').forEach((control) => {
            control.addEventListener("change", () => {
                const selectorPlataforma = formulario.querySelector('[name="plataforma"]');
                const selectorPozo = formulario.querySelector('[name="pozo"]');

                if (selectorPlataforma) selectorPlataforma.value = "";
                if (selectorPozo) selectorPozo.value = "";
                aplicarNivelProduccion(formulario, true);
                filtrarPlataformasProduccion(formulario);
                filtrarPozosProduccion(formulario);
                actualizarFiltrosProduccion(formulario);
                actualizarResumenSeleccionProduccion(resumenSeleccion, formulario);
                programarConsultaProduccion();
            });
        });

        formulario.querySelectorAll('[name="plataforma"]').forEach((control) => {
            control.addEventListener("change", () => {
                const selectorPozo = formulario.querySelector('[name="pozo"]');

                if (selectorPozo) selectorPozo.value = "";
                aplicarNivelProduccion(formulario, true);
                filtrarPozosProduccion(formulario);
                actualizarFiltrosProduccion(formulario);
                actualizarResumenSeleccionProduccion(resumenSeleccion, formulario);
                programarConsultaProduccion();
            });
        });

        formulario.querySelectorAll('[name="pozo"]').forEach((control) => {
            control.addEventListener("change", () => {
                aplicarNivelProduccion(formulario, true);
                actualizarFiltrosProduccion(formulario);
                actualizarResumenSeleccionProduccion(resumenSeleccion, formulario);
                programarConsultaProduccion();
            });
        });

        formulario.addEventListener("submit", (evento) => {
            evento.preventDefault();
            consultarProduccion();
        });

        selectorVariable.addEventListener("change", () => {
            renderizarLeyendaProduccion(leyenda, filasActuales, selectorVariable.value, variablesActuales);
            dibujarGraficaProduccion(canvas, filasActuales, selectorVariable.value, variablesActuales);
        });

        canvas.addEventListener("mousemove", (evento) => {
            if (!tooltip) return;

            const elemento = elementoGraficaEnPosicion(canvas, evento);
            if (!elemento) {
                tooltip.hidden = true;
                return;
            }

            tooltip.textContent = elemento.texto;
            posicionarTooltipProduccion(canvas, tooltip, elemento, evento);
        });

        canvas.addEventListener("mouseleave", () => {
            if (tooltip) tooltip.hidden = true;
        });

        aplicarNivelProduccion(formulario);
        actualizarFiltrosProduccion(formulario);
        actualizarResumenSeleccionProduccion(resumenSeleccion, formulario);
        consultarProduccion();
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
