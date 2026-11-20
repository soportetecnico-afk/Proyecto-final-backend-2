<script>
    import { onMount } from 'svelte';
    import PageHeader from '$lib/components/ui/PageHeader.svelte';

    const API_BASE = 'http://127.0.0.1:8000';

    let roles = $state([]);
    let modulos = $state([]);
    let asignaciones = $state([]);
    let rolSeleccionadoId = $state(null);
    let cargando = $state(true);
    let cargandoPermisos = $state(false);
    let guardandoRol = $state(false);
    let mostrarFormulario = $state(false);
    let mostrarModalPermisos = $state(false);
    let nombreRol = $state('');
    let descripcionRol = $state('');
    let error = $state('');
    let exito = $state('');
    let procesandoModulos = $state([]);
    let procesandoRoles = $state([]);

    // PostgreSQL puede serializar booleanos como true/false o como t/f,
    // según la ruta o el cursor utilizado. Se normalizan en un solo lugar.
    function esBooleanoActivo(valor) {
        if (valor === true || valor === 1) return true;
        if (valor === false || valor === 0 || valor == null) return false;
        return ['true', 't', '1', 'yes', 'si', 'sí'].includes(
            String(valor).trim().toLowerCase()
        );
    }

    function rolActivo(rol) {
        return esBooleanoActivo(rol?.estado);
    }

    // Los permisos visibles deben coincidir con los módulos principales del Sidebar.
    // Cada módulo visual agrupa uno o varios registros reales de la tabla "modulo".
    // Así se conservan las asignaciones existentes en PostgreSQL sin duplicar registros.
    const GRUPOS_MODULOS = [
        {
            id: 'inicio',
            nombre: 'Inicio',
            descripcion: 'Acceso al panel principal del sistema.',
            rutas: ['/dashboard'],
            nombres: ['dashboard principal']
        },
        {
            id: 'espacios',
            nombre: 'Espacios',
            descripcion: 'Aulas, laboratorios y canchas.',
            rutas: ['/espacios/aulas', '/espacios/laboratorios', '/espacios/canchas'],
            nombres: ['catalogo de aulas', 'catalogo de laboratorios', 'catalogo de canchas']
        },
        {
            id: 'recursos',
            nombre: 'Recursos',
            descripcion: 'Inventario y mantenimiento de equipos.',
            rutas: ['/recursos/tecnologia', '/recursos/medicina', '/mantenimiento'],
            nombres: ['inventario de computadores', 'inventario de equipos medicos', 'mantenimiento de equipos']
        },
        {
            id: 'reservas',
            nombre: 'Reservas',
            descripcion: 'Calendario, solicitudes, asistencia y eventos.',
            rutas: ['/calendario', '/aprobaciones', '/mis-reservas', '/checkin', '/notificaciones', '/tipos-evento'],
            nombres: [
                'calendario academico',
                'aprobacion de reservas',
                'mis clases y reservas',
                'registro de asistencia (check-in)',
                'notificaciones',
                'tipos de eventos academicos'
            ]
        },
        {
            id: 'reportes',
            nombre: 'Reportes',
            descripcion: 'Informes de ocupación y auditoría.',
            rutas: ['/reportes/ocupacion', '/auditoria'],
            nombres: ['reportes de ocupacion', 'auditoria de accesos']
        },
        {
            id: 'usuarios',
            nombre: 'Usuarios',
            descripcion: 'Directorio, facultades y perfil de usuario.',
            rutas: ['/usuarios', '/facultades', '/perfil'],
            nombres: ['gestion de usuarios', 'gestion de facultades', 'mi perfil']
        },
        {
            id: 'roles-permisos',
            nombre: 'Roles y permisos',
            descripcion: 'Administración de perfiles y configuración de acceso.',
            rutas: ['/roles', '/configuracion'],
            nombres: ['gestion de roles', 'configuracion del sistema']
        }
    ];

    function normalizarTexto(valor) {
        return String(valor ?? '')
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .trim()
            .toLowerCase();
    }

    function perteneceAlGrupo(modulo, grupo) {
        const ruta = normalizarTexto(modulo.ruta_url).replace(/\/$/, '');
        const nombre = normalizarTexto(modulo.nombre);
        return grupo.rutas.includes(ruta) || grupo.nombres.includes(nombre);
    }

    function modulosDelGrupo(grupo) {
        return modulos.filter((modulo) => perteneceAlGrupo(modulo, grupo));
    }

    // El backend devuelve permiso_activo según modulosxrol.estado.
    // No basta con que exista una fila: también debe estar habilitada.
    function permisoActivo(asignacion) {
        const estado = asignacion?.permiso_activo ?? asignacion?.estado;
        return esBooleanoActivo(estado);
    }

    function grupoTieneAcceso(grupo) {
        const lista = modulosDelGrupo(grupo);
        return lista.length > 0 && lista.every((modulo) => permisoActivo(asignacionDe(modulo.id_modulo)));
    }

    function grupoTieneAccesoParcial(grupo) {
        const lista = modulosDelGrupo(grupo);
        return lista.some((modulo) => permisoActivo(asignacionDe(modulo.id_modulo))) && !grupoTieneAcceso(grupo);
    }

    function cantidadGruposHabilitados() {
        // Cuenta secciones con al menos un permiso activo, incluidas las parciales.
        return GRUPOS_MODULOS.filter((grupo) => {
            const lista = modulosDelGrupo(grupo);
            return lista.some((modulo) => permisoActivo(asignacionDe(modulo.id_modulo)));
        }).length;
    }

    function marcarPermisoParcial(elemento, parcial) {
        elemento.indeterminate = parcial;
        return {
            update(nuevoValor) {
                elemento.indeterminate = nuevoValor;
            }
        };
    }

    const rolSeleccionado = $derived(roles.find((rol) => Number(rol.id_rol) === Number(rolSeleccionadoId)) ?? null);

    onMount(() => { cargarDatos(); });

    async function respuestaApi(url, opciones = {}) {
        const respuesta = await fetch(url, {
            ...opciones,
            headers: { 'Content-Type': 'application/json', ...(opciones.headers ?? {}) }
        });
        const texto = await respuesta.text();
        let datos = {};
        try { datos = texto ? JSON.parse(texto) : {}; } catch { datos = { detail: texto }; }
        if (!respuesta.ok) {
            const detalle = datos.detail ?? datos.mensaje ?? `Error HTTP ${respuesta.status}`;
            throw new Error(typeof detalle === 'string' ? detalle : JSON.stringify(detalle));
        }
        return datos;
    }

    async function cargarDatos() {
        cargando = true;
        error = '';
        try {
            const [datosRoles, datosModulos] = await Promise.all([
                respuestaApi(`${API_BASE}/roles/`),
                respuestaApi(`${API_BASE}/modulos/`)
            ]);
            roles = Array.isArray(datosRoles) ? datosRoles : [];
            // Se conserva el catálogo completo para asociar cada módulo secundario
            // con una de las siete secciones principales del menú lateral.
            modulos = Array.isArray(datosModulos) ? datosModulos : [];
            if (rolSeleccionadoId && !roles.some((rol) => Number(rol.id_rol) === Number(rolSeleccionadoId))) {
                rolSeleccionadoId = null;
                asignaciones = [];
            }
        } catch (e) {
            error = 'No fue posible cargar los roles y módulos. Inténtalo nuevamente.';
        } finally {
            cargando = false;
        }
    }

    async function seleccionarRol(rol) {
        rolSeleccionadoId = Number(rol.id_rol);
        mostrarModalPermisos = true;
        asignaciones = [];
        cargandoPermisos = true;
        error = '';
        exito = '';
        try {
            const datos = await respuestaApi(`${API_BASE}/modulos-roles/rol/${rol.id_rol}`);

            if (!Array.isArray(datos)) {
                throw new Error('No se recibieron los permisos esperados.');
            }

            // Este endpoint ya devuelve el catálogo completo de módulos junto con
            // permiso_activo. Usamos la misma respuesta para pintar y validar,
            // evitando comparar dos consultas que puedan quedar desincronizadas.
            const datosNormalizados = datos.map((fila) => {
                // Compatibilidad con respuestas JSON en forma de objeto y con
                // respuestas antiguas en forma de arreglo/tupla.
                const item = Array.isArray(fila)
                    ? {
                        id_modulo: fila[0],
                        nombre: fila[1],
                        ruta_url: fila[2],
                        modulo_activo: fila[3],
                        id_modulosxrol: fila[4],
                        id_rol: fila[5],
                        permiso_activo: fila[6]
                    }
                    : fila;

                return {
                    ...item,
                    id_modulo: Number(item.id_modulo),
                    modulo_activo: esBooleanoActivo(item.modulo_activo),
                    permiso_activo: esBooleanoActivo(item.permiso_activo)
                };
            });

            modulos = datosNormalizados.filter((item) => item.modulo_activo);
            asignaciones = datosNormalizados;
        } catch (e) {
            error = `No fue posible consultar los permisos de ${rol.nombre ?? rol.nombre_rol}. Inténtalo nuevamente.`;
        } finally {
            cargandoPermisos = false;
        }
    }

    function cerrarModalPermisos() {
        mostrarModalPermisos = false;
        rolSeleccionadoId = null;
        asignaciones = [];
        error = '';
        exito = '';
    }

    function manejarTecla(evento) {
        if (evento.key === 'Escape' && mostrarModalPermisos) {
            cerrarModalPermisos();
        }
    }

    function asignacionDe(moduloId) {
        return asignaciones.find((item) => Number(item.id_modulo) === Number(moduloId));
    }

    async function cambiarPermisoGrupo(grupo, conceder) {
        if (!rolSeleccionadoId || !rolSeleccionado || !rolActivo(rolSeleccionado)) {
            error = 'No puedes modificar permisos de un perfil inactivo. Actívalo primero.';
            return;
        }

        const lista = modulosDelGrupo(grupo);
        if (lista.length === 0) {
            error = `No hay módulos asociados a ${grupo.nombre}.`;
            return;
        }

        if (procesandoModulos.includes(grupo.id)) return;
        procesandoModulos = [...procesandoModulos, grupo.id];
        error = '';
        exito = '';

        try {
            // Cada tarjeta representa una sección del menú y puede agrupar
            // varios módulos reales. El endpoint actualiza el booleano estado.
            for (const modulo of lista) {
                const asignacion = asignacionDe(modulo.id_modulo);
                const estadoActual = permisoActivo(asignacion);
                if (estadoActual === conceder) continue;

                await respuestaApi(
                    `${API_BASE}/modulos-roles/rol/${rolSeleccionadoId}/modulo/${modulo.id_modulo}`,
                    {
                        method: 'PATCH',
                        body: JSON.stringify({ estado: conceder })
                    }
                );
            }

            const actualizadas = await respuestaApi(`${API_BASE}/modulos-roles/rol/${rolSeleccionadoId}`);
            asignaciones = Array.isArray(actualizadas) ? actualizadas : [];

            exito = conceder
                ? `Se concedió el acceso a ${grupo.nombre}.`
                : `Se retiró el acceso a ${grupo.nombre}.`;
        } catch (e) {
            // Recargar el estado real por si alguna operación del grupo sí alcanzó a guardarse.
            try {
                const actualizadas = await respuestaApi(`${API_BASE}/modulos-roles/rol/${rolSeleccionadoId}`);
                asignaciones = Array.isArray(actualizadas) ? actualizadas : [];
            } catch {
                // Se conserva el error original.
            }
            error = `No fue posible actualizar el permiso de ${grupo.nombre}. Inténtalo nuevamente.`;
        } finally {
            procesandoModulos = procesandoModulos.filter((id) => id !== grupo.id);
        }
    }


    async function cambiarEstadoRol(rol) {
        const activo = rolActivo(rol);
        if (activo && Number(rol.id_rol) === 1) {
            error = 'El perfil Administrador principal no se puede desactivar.';
            return;
        }

        const accion = activo ? 'desactivar' : 'activar';
        const nombre = rol.nombre ?? rol.nombre_rol ?? 'este perfil';
        if (!confirm(`¿Seguro que deseas ${accion} el perfil "${nombre}"?`)) return;

        const id = Number(rol.id_rol);
        if (procesandoRoles.includes(id)) return;
        procesandoRoles = [...procesandoRoles, id];
        error = '';
        exito = '';

        try {
            await respuestaApi(`${API_BASE}/roles/${id}/estado`, {
                method: 'PATCH',
                body: JSON.stringify({ estado: !activo })
            });
            await cargarDatos();

            const actualizado = roles.find((item) => Number(item.id_rol) === id);
            if (actualizado && Number(rolSeleccionadoId) === id) {
                await seleccionarRol(actualizado);
            }
            exito = `El perfil "${nombre}" quedó ${activo ? 'inactivo' : 'activo'} correctamente.`;
        } catch (e) {
            error = `No fue posible ${accion} el perfil. Inténtalo nuevamente.`;
        } finally {
            procesandoRoles = procesandoRoles.filter((item) => item !== id);
        }
    }

    async function crearRol(evento) {
        evento.preventDefault();
        if (!nombreRol.trim()) return;
        guardandoRol = true;
        error = '';
        exito = '';
        try {
            const nuevo = await respuestaApi(`${API_BASE}/roles/`, {
                method: 'POST',
                body: JSON.stringify({ nombre: nombreRol.trim(), descripcion: descripcionRol.trim() || null })
            });
            await cargarDatos();
            const idNuevo = nuevo.id_rol ?? nuevo.id;
            limpiarFormulario();
            if (idNuevo) {
                const rolNuevo = roles.find((rol) => Number(rol.id_rol) === Number(idNuevo));
                if (rolNuevo) await seleccionarRol(rolNuevo);
            }
            exito = 'El perfil se creó correctamente. Ahora puedes asignarle los módulos permitidos.';
        } catch (e) {
            error = 'No fue posible crear el perfil. Inténtalo nuevamente.';
        } finally {
            guardandoRol = false;
        }
    }

    function limpiarFormulario() {
        nombreRol = '';
        descripcionRol = '';
        mostrarFormulario = false;
    }
</script>

<svelte:window onkeydown={manejarTecla} />

<svelte:head>
    <title>Roles y permisos - Sistema de Reservas CUL</title>
    <meta name="description" content="Administración de perfiles y permisos de acceso a los módulos." />
</svelte:head>

<div class="roles-container">
    <PageHeader etiqueta="ADMINISTRACIÓN DEL SISTEMA" titulo="Roles y permisos"
        descripcion="Crea perfiles y controla a qué módulos puede acceder cada uno." />

    <section class="aviso">
        <span class="aviso-icono">ⓘ</span>
        <div>
            <h2>Administración de perfiles</h2>
            <p>Consulta los perfiles existentes, crea nuevos y asigna o retira permisos para módulos como Reservas, Espacios, Recursos y Usuarios.</p>
        </div>
    </section>

    {#if error}<div class="mensaje error" role="alert">{error}</div>{/if}
    {#if exito}<div class="mensaje exito" role="status">{exito}</div>{/if}

    <div class="encabezado-lista">
        <div>
            <h2>Perfiles del sistema</h2>
            <p>{roles.length} perfil{roles.length === 1 ? '' : 'es'} registrado{roles.length === 1 ? '' : 's'}.</p>
        </div>
        <div class="acciones">
            <button class="boton-secundario" onclick={cargarDatos} disabled={cargando}>Actualizar</button>
            <button class="boton-primario" onclick={() => { mostrarFormulario = !mostrarFormulario; error = ''; }}>
                {mostrarFormulario ? 'Cancelar' : '+ Crear perfil'}
            </button>
        </div>
    </div>

    {#if mostrarFormulario}
        <section class="panel formulario-panel">
            <div class="panel-titulo">
                <h2>Crear nuevo perfil</h2>
                <p>Después de crearlo, selecciona los módulos a los que tendrá acceso.</p>
            </div>
            <form onsubmit={crearRol}>
                <div class="campos">
                    <label>
                        <span>Nombre del perfil *</span>
                        <input bind:value={nombreRol} maxlength="80" placeholder="Ej. Coordinador académico" required />
                    </label>
                    <label>
                        <span>Descripción</span>
                        <textarea bind:value={descripcionRol} rows="3" maxlength="250" placeholder="Describe las funciones de este perfil"></textarea>
                    </label>
                </div>
                <div class="form-acciones">
                    <button type="button" class="boton-secundario" onclick={limpiarFormulario}>Cancelar</button>
                    <button type="submit" class="boton-primario" disabled={guardandoRol}>{guardandoRol ? 'Guardando...' : 'Guardar perfil'}</button>
                </div>
            </form>
        </section>
    {/if}

    {#if cargando}
        <div class="estado">Consultando perfiles y módulos...</div>
    {:else if roles.length === 0}
        <div class="estado">No hay perfiles registrados.</div>
    {:else}
        <div class="perfiles-grid">
            {#each roles as rol (rol.id_rol)}
                <article class="perfil-card" class:seleccionado={Number(rolSeleccionadoId) === Number(rol.id_rol)}>
                    <div class="perfil-top">
                        <span class="perfil-icono">♙</span>
                        <span class="estado-perfil" class:inactivo={!rolActivo(rol)}>
                            {rolActivo(rol) ? 'Activo' : 'Inactivo'}
                        </span>
                    </div>
                    <h3>{rol.nombre ?? rol.nombre_rol}</h3>
                    <p>{rol.descripcion || 'Sin descripción registrada.'}</p>
                    <button class="boton-permisos" onclick={() => seleccionarRol(rol)}>
                        {Number(rolSeleccionadoId) === Number(rol.id_rol) ? 'Perfil seleccionado' : 'Gestionar permisos'}
                        <span>→</span>
                    </button>
                    <button
                        class="boton-estado-rol"
                        class:activar={!rolActivo(rol)}
                        onclick={() => cambiarEstadoRol(rol)}
                        disabled={procesandoRoles.includes(Number(rol.id_rol)) || (Number(rol.id_rol) === 1 && rolActivo(rol))}
                        title={Number(rol.id_rol) === 1 && rolActivo(rol) ? 'El administrador principal no se puede desactivar' : ''}
                    >
                        {procesandoRoles.includes(Number(rol.id_rol))
                            ? 'Procesando...'
                            : rolActivo(rol) ? 'Desactivar perfil' : 'Activar perfil'}
                    </button>
                </article>
            {/each}
        </div>
    {/if}

    {#if mostrarModalPermisos && rolSeleccionado}
        <div class="modal-overlay">
            <dialog open class="modal-permisos" aria-labelledby="titulo-modal-permisos">
                <header class="modal-header">
                    <div>
                        <span class="etiqueta-panel">CONFIGURACIÓN DE ACCESO</span>
                        <h2 id="titulo-modal-permisos">Permisos de: {rolSeleccionado.nombre ?? rolSeleccionado.nombre_rol}</h2>
                        <p>Activa los módulos que este perfil puede consultar o utilizar. Desactiva los que no debe tener disponibles.</p>
                        {#if !rolActivo(rolSeleccionado)}
                            <p class="aviso-inactivo">Este perfil está inactivo. Actívalo para poder modificar sus permisos y permitir el acceso a sus usuarios.</p>
                        {/if}
                    </div>
                    <button type="button" class="boton-cerrar-modal" onclick={cerrarModalPermisos} aria-label="Cerrar ventana">×</button>
                </header>

                <div class="modal-contador">
                    <span class="contador">{cantidadGruposHabilitados()} / {GRUPOS_MODULOS.length} módulos habilitados</span>
                </div>

                {#if cargandoPermisos}
                    <div class="estado modal-estado">Consultando permisos...</div>
                {:else if modulos.length === 0}
                    <div class="estado modal-estado">No hay módulos registrados.</div>
                {:else}
                    <div class="modulos-lista">
                        {#each GRUPOS_MODULOS as grupo (grupo.id)}
                            {@const listaGrupo = modulosDelGrupo(grupo)}
                            {@const asignado = grupoTieneAcceso(grupo)}
                            {@const parcial = grupoTieneAccesoParcial(grupo)}
                            <label class="modulo-item" class:habilitado={asignado} class:parcial>
                                <div class="modulo-info">
                                    <span class="modulo-icono">▦</span>
                                    <div>
                                        <strong>{grupo.nombre}</strong>
                                        <small>{grupo.descripcion}</small>
                                        {#if listaGrupo.length === 0}
                                            <small class="modulo-sin-configurar">Sin módulos internos asociados</small>
                                        {:else if parcial}
                                            <small class="modulo-parcial">{listaGrupo.filter((modulo) => permisoActivo(asignacionDe(modulo.id_modulo))).length} de {listaGrupo.length} funciones habilitadas</small>
                                        {:else if !asignado}
                                            <small class="modulo-sin-acceso">0 de {listaGrupo.length} funciones habilitadas</small>
                                        {/if}
                                    </div>
                                </div>
                                <div class="modulo-control">
                                    <span class:estado-on={asignado || parcial} class:estado-parcial={parcial} class:estado-off={!asignado && !parcial}>
                                        {asignado ? '✓ Acceso' : parcial ? '✓ Acceso parcial' : 'Sin acceso'}
                                    </span>
                                    <input type="checkbox" checked={asignado}
                                        use:marcarPermisoParcial={parcial}
                                        disabled={!rolActivo(rolSeleccionado) || listaGrupo.length === 0 || procesandoModulos.includes(grupo.id)}
                                        onchange={(evento) => cambiarPermisoGrupo(grupo, evento.currentTarget.checked)}
                                        aria-label={`Permitir ${grupo.nombre} para ${rolSeleccionado.nombre ?? rolSeleccionado.nombre_rol}`} />
                                </div>
                            </label>
                        {/each}
                    </div>
                {/if}

                {#if error}
                    <div class="mensaje error modal-mensaje" role="alert">{error}</div>
                {/if}
                {#if exito}
                    <div class="mensaje exito modal-mensaje" role="status">{exito}</div>
                {/if}

                <footer class="modal-footer">
                    <span class="ayuda-modal">Los cambios de permisos se guardan directamente en el sistema.</span>
                    <button type="button" class="boton-secundario" onclick={cerrarModalPermisos}>Cancelar</button>
                </footer>
            </dialog>
        </div>
    {/if}
</div>

<style>
    .roles-container { width: 100%; max-width: 1600px; margin: 0 auto; padding: 28px; box-sizing: border-box; color: #f1f5f9; }
    .aviso, .panel, .estado { border: 1px solid #334155; border-radius: 12px; background: #1e293b; }
    .aviso { display: flex; gap: 14px; align-items: flex-start; margin: 24px 0 28px; padding: 20px; background: #1e293b; }
    .aviso-icono { color: #60a5fa; font-size: 22px; }
    .aviso h2, .encabezado-lista h2, .panel h2 { margin: 0; color: #f8fafc; font-size: 16px; }
    .aviso p, .encabezado-lista p, .panel p { margin: 7px 0 0; color: #cbd5e1; font-size: 13px; line-height: 1.6; }
    .encabezado-lista { display: flex; justify-content: space-between; align-items: center; gap: 16px; margin-bottom: 16px; }
    .acciones, .form-acciones { display: flex; align-items: center; gap: 10px; }
    button { font: inherit; cursor: pointer; }
    button:disabled { opacity: .6; cursor: wait; }
    .boton-primario, .boton-secundario { border-radius: 8px; padding: 10px 16px; color: #f8fafc; }
    .boton-primario { border: 1px solid #3b82f6; background: #2563eb; }
    .boton-primario:hover { background: #1d4ed8; }
    .boton-secundario { border: 1px solid #64748b; background: transparent; }
    .perfiles-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; }
    .perfil-card { display: flex; min-height: 220px; flex-direction: column; padding: 22px; border: 1px solid #334155; border-radius: 13px; background: #1e293b; }
    .perfil-card.seleccionado { border-color: #3b82f6; box-shadow: 0 0 0 1px #3b82f6; }
    .perfil-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; }
    .perfil-icono { display: grid; width: 42px; height: 42px; place-items: center; border: 1px solid #3b82f6; border-radius: 11px; background: #172f52; color: #93c5fd; font-size: 22px; }
    .estado-perfil { border-radius: 20px; padding: 5px 10px; background: #064e3b; color: #6ee7b7; font-size: 11px; }
    .estado-perfil.inactivo { background: #7f1d1d; color: #fecaca; }
    .boton-estado-rol { width: 100%; margin-top: 9px; padding: 8px 11px; border: 1px solid #7f1d1d; border-radius: 8px; background: #3b1d29; color: #fecaca; font-size: 12px; }
    .boton-estado-rol:hover:not(:disabled) { background: #572333; }
    .boton-estado-rol.activar { border-color: #047857; background: #064e3b; color: #a7f3d0; }
    .boton-estado-rol:disabled { opacity: .55; cursor: not-allowed; }
    .aviso-inactivo { margin-top: 10px !important; padding: 9px 11px; border: 1px solid #7f1d1d; border-radius: 7px; background: #3b1d29; color: #fecaca !important; }
    .modulo-sin-acceso { color: #fca5a5 !important; font-size: 13px !important; font-weight: 700; }
    .perfil-card h3 { margin: 0 0 9px; color: #f8fafc; font-size: 17px; }
    .perfil-card p { min-height: 40px; margin: 0 0 12px; color: #cbd5e1; font-size: 13px; line-height: 1.6; }
    .boton-permisos { display: flex; justify-content: space-between; align-items: center; width: 100%; margin-top: auto; padding: 10px 12px; border: 1px solid #3b82f6; border-radius: 8px; background: #1e3a5f; color: #eff6ff; text-align: left; }
    .boton-permisos:hover { background: #244a78; }
    .modal-overlay { position: fixed; inset: 0; z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 24px; background: rgba(2, 6, 23, .78); backdrop-filter: blur(5px); }
    .modal-permisos { position: relative; inset: auto; display: flex; box-sizing: border-box; flex: 0 1 auto; width: min(1240px, 96vw); max-width: none; max-height: min(90vh, 900px); height: auto; margin: auto; padding: 0; flex-direction: column; overflow: hidden; border: 1px solid #475569; border-radius: 14px; background: #1e293b; color: #f8fafc; box-shadow: 0 24px 70px rgba(0, 0, 0, .48); }
    .modal-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 20px; padding: 22px 24px 16px; border-bottom: 1px solid #334155; }
    .modal-header h2 { margin: 0; color: #f8fafc; font-size: 21px; }
    .modal-header p { margin: 8px 0 0; color: #cbd5e1; font-size: 14px; line-height: 1.55; }
    .boton-cerrar-modal { flex: 0 0 auto; width: 36px; height: 36px; border: 1px solid #475569; border-radius: 8px; background: #172338; color: #cbd5e1; font-size: 24px; line-height: 1; }
    .boton-cerrar-modal:hover { background: #334155; color: #fff; }
    .modal-contador { display: flex; justify-content: flex-end; padding: 16px 26px 0; }
    .modal-permisos .modulos-lista { overflow-y: auto; min-height: 0; padding: 18px 24px; }
    .modal-estado { margin: 18px 24px; }
    .modal-mensaje { margin: 0 24px 12px; }
    .modal-footer { display: flex; justify-content: space-between; align-items: center; gap: 16px; padding: 16px 24px; border-top: 1px solid #334155; background: #172338; }
    .ayuda-modal { color: #cbd5e1; font-size: 14px; line-height: 1.55; font-weight: 400; }
    .formulario-panel form { padding: 20px 22px; }
    .campos { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
    .campos label { display: flex; flex-direction: column; gap: 8px; color: #e2e8f0; font-size: 13px; }
    input:not([type="checkbox"]), textarea { width: 100%; box-sizing: border-box; padding: 11px 12px; border: 1px solid #475569; border-radius: 7px; outline: none; background: #0f172a; color: #f8fafc; }
    input:focus, textarea:focus { border-color: #3b82f6; }
    textarea { resize: vertical; }
    .form-acciones { justify-content: flex-end; margin-top: 18px; }
    .etiqueta-panel { display: block; margin-bottom: 8px; color: #60a5fa; font-size: 10px; font-weight: 800; letter-spacing: .12em; }
    .contador { white-space: nowrap; border: 1px solid #4774a8; border-radius: 22px; padding: 12px 18px; background: #172f52; color: #dbeafe; font-size: 17px; font-weight: 800; line-height: 1.4; }
    .modulos-lista { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; padding: 20px 22px; }
    .modulo-item { display: flex; justify-content: space-between; align-items: center; gap: 18px; min-width: 0; min-height: 104px; padding: 20px; border: 1px solid #334155; border-radius: 9px; background: #172338; cursor: pointer; }
    .modulo-item.habilitado { border-color: #2563eb; background: #1b3150; }
    .modulo-item.parcial { border-color: #d97706; background: #332817; }
    .modulo-parcial { color: #fbbf24 !important; font-size: 13px !important; font-weight: 700; }
    .modulo-sin-configurar { color: #fca5a5 !important; font-size: 13px !important; font-weight: 700; }
    .modulo-info, .modulo-control { display: flex; align-items: center; gap: 14px; }
    .modulo-info { min-width: 0; }
    .modulo-info div { display: flex; min-width: 0; flex-direction: column; gap: 6px; }
    .modulo-info strong { color: #f8fafc; font-size: 18px; line-height: 1.35; font-weight: 700; }
    .modulo-info small { overflow: hidden; color: #cbd5e1; font-size: 14px; line-height: 1.45; text-overflow: ellipsis; white-space: normal; }
    .modulo-icono { display: grid; width: 42px; height: 42px; flex: 0 0 42px; place-items: center; border: 1px solid #475569; border-radius: 8px; color: #93c5fd; }
    .modulo-control { flex: 0 0 auto; }
    .modulo-control span { color: #cbd5e1; font-size: 14px; font-weight: 600; white-space: nowrap; }
    .modulo-control span.estado-on { color: #4ade80; font-weight: 800; }
    .modulo-control span.estado-parcial { color: #4ade80; font-weight: 800; }
    .modulo-control span.estado-off { color: #cbd5e1; }
    .modulo-control input { width: 21px; height: 21px; accent-color: #2563eb; cursor: pointer; }
    .estado { padding: 24px; color: #cbd5e1; }
    .mensaje { margin: 14px 0; padding: 12px 16px; border-radius: 8px; font-size: 13px; }
    .mensaje.error { border: 1px solid #ef4444; background: #451a1a; color: #fecaca; }
    .mensaje.exito { border: 1px solid #059669; background: #064e3b; color: #a7f3d0; }
    @media (max-width: 1000px) { .perfiles-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .modulos-lista { grid-template-columns: 1fr; } }
    @media (max-width: 650px) {
        .roles-container { padding: 18px; }
        .perfiles-grid, .campos { grid-template-columns: 1fr; }
        .encabezado-lista { align-items: flex-start; flex-direction: column; }
        .acciones { width: 100%; }
        .acciones button { flex: 1; }
        .modal-overlay { align-items: center; justify-content: center; padding: 12px; }
        .modal-permisos { width: 100%; max-height: 94vh; border-radius: 13px; }
        .modal-header { padding: 17px; }
        .modal-contador { padding: 12px 17px 0; }
        .modal-permisos .modulos-lista { grid-template-columns: 1fr; padding: 14px 17px; }
        .modal-footer { align-items: stretch; flex-direction: column; padding: 14px 17px; }
        .modal-footer button { width: 100%; }
        .modulo-item { align-items: flex-start; flex-direction: column; }
        .modulo-control { align-self: flex-end; }
    }
</style>
