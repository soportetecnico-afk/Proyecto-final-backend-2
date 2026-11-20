<script>

    import { onMount, tick } from 'svelte';

    import PageHeader from '$lib/components/ui/PageHeader.svelte';

    import BaseButton from '$lib/components/ui/BaseButton.svelte';

    import FormInput from '$lib/components/ui/FormInput.svelte';

    import FormSelect from '$lib/components/ui/FormSelect.svelte';

    import DataTable from '$lib/components/ui/DataTable.svelte';

    const API_BASE = 'http://127.0.0.1:8000';

    let mostrarFormulario = $state(false);

    let usuarioSesion = $state(null);

    let tokenAcceso = '';

    let usuarioEditandoId = $state(null);

    let nombreCompleto = $state('');

    let correoElectronico = $state('');

    let password = $state('');

    let telefono = $state('');

    let rol = $state('');

    let facultad = $state('');

    let estadoUsuario = $state('activo');

    let buscarNombre = $state('');

    let buscarCorreo = $state('');

    let buscarRol = $state('');

    let usuarios = $state([]);

    let roles = $state([]);

    let facultades = $state([]);

    let cargando = $state(true);

    let guardando = $state(false);

    let conectado = $state(false);

    let mensajeError = $state('');

    let mensajeExito = $state('');

    const opcionesEstados = [

        { valor: 'activo', etiqueta: 'Activo' },

        { valor: 'inactivo', etiqueta: 'Inactivo' }

    ];

    function normalizar(valor) {
        return String(valor ?? '')
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .trim()
            .toLowerCase();
    }

    const esDecano = $derived(
        Number(usuarioSesion?.id_rol) === 3 || normalizar(usuarioSesion?.nombre_rol ?? usuarioSesion?.rol) === 'decano'
    );

    const opcionesRoles = $derived(
        roles
            .filter((item) => !esDecano || Boolean(usuarioEditandoId) || normalizar(item.nombre ?? item.nombre_rol) === 'docente')
            .map((item) => ({ valor: String(item.id_rol), etiqueta: item.nombre ?? item.nombre_rol ?? `Rol ${item.id_rol}` }))
    );

    const opcionesFacultades = $derived([

        { valor: 'null', etiqueta: 'Sin facultad' },

        ...facultades.map((item) => ({

            valor: String(item.id_facultad),

            etiqueta: item.nombre_facultad ?? item.nombre ?? `Facultad ${item.id_facultad}`

        }))

    ]);

    const columnas = [

        { clave: 'id', etiqueta: '#' },

        { clave: 'nombreCompleto', etiqueta: 'Nombre completo' },

        { clave: 'correoElectronico', etiqueta: 'Correo electrónico' },

        { clave: 'telefono', etiqueta: 'Teléfono' },

        { clave: 'rolNombre', etiqueta: 'Rol' },

        { clave: 'facultadNombre', etiqueta: 'Facultad' },

        { clave: 'estadoTexto', etiqueta: 'Estado' },

        { clave: 'acciones', etiqueta: 'Acciones' }

    ];

    const usuariosFiltrados = $derived(

        usuarios.filter((usuario) => {

            const nombre = String(usuario.nombreCompleto ?? '').toLowerCase();

            const correo = String(usuario.correoElectronico ?? '').toLowerCase();


            return nombre.includes(buscarNombre.trim().toLowerCase()) &&

                correo.includes(buscarCorreo.trim().toLowerCase()) &&

                (!buscarRol || String(usuario.id_rol) === buscarRol);

        })

    );

    onMount(() => {

        try {
            usuarioSesion = JSON.parse(localStorage.getItem('usuario_sesion') ?? 'null');
            tokenAcceso = localStorage.getItem('token_acceso') ?? '';
        } catch {
            usuarioSesion = null;
            tokenAcceso = '';
        }

        cargarDatos();

    });

    async function leerRespuesta(respuesta) {

        const texto = await respuesta.text();

        let datos;

        try {

            datos = texto ? JSON.parse(texto) : null;

        } catch {

            datos = texto;

        }

        if (!respuesta.ok) {

            const detalle = typeof datos === 'object' && datos !== null ? datos.detail : null;

            throw new Error(detalle || `Error HTTP ${respuesta.status}`);

        }

        return datos;

    }

    function mapearUsuarios(datos) {

        return (Array.isArray(datos) ? datos : []).map((item) => {

            const rolEncontrado = roles.find((r) => Number(r.id_rol) === Number(item.id_rol));

            const facultadEncontrada = facultades.find((f) => Number(f.id_facultad) === Number(item.id_facultad));

            const activo = item.estado === true || item.estado === 'true' || item.estado === 1;

            return {

                id: item.id_usuario,

                id_usuario: item.id_usuario,

                nombreCompleto: item.nombre_completo ?? '',

                correoElectronico: item.correo_electronico ?? '',

                telefono: item.telefono ?? '',

                id_rol: item.id_rol,

                rolNombre: item.nombre_rol ?? rolEncontrado?.nombre ?? rolEncontrado?.nombre_rol ?? `Rol ${item.id_rol ?? ''}`,

                id_facultad: item.id_facultad,

                facultadNombre: item.nombre_facultad ?? facultadEncontrada?.nombre_facultad ?? facultadEncontrada?.nombre ?? 'Sin facultad',

                estado: activo,

                estadoTexto: activo ? 'Activo' : 'Inactivo',

                acciones: 'Editar'

            };

        });

    }

    async function cargarDatos() {

        cargando = true;

        mensajeError = '';

        try {

            const [respuestaUsuarios, respuestaRoles, respuestaFacultades] = await Promise.all([

                fetch(`${API_BASE}/usuarios/`),

                fetch(`${API_BASE}/roles/`),

                fetch(`${API_BASE}/facultades/`)

            ]);

            const [datosUsuarios, datosRoles, datosFacultades] = await Promise.all([

                leerRespuesta(respuestaUsuarios),

                leerRespuesta(respuestaRoles),

                leerRespuesta(respuestaFacultades)

            ]);

            const rolesPermitidos = new Set(['administrador', 'decano', 'docente']);
            roles = (Array.isArray(datosRoles) ? datosRoles : []).filter((item) =>
                rolesPermitidos.has(String(item.nombre ?? item.nombre_rol ?? '').trim().toLowerCase())
            );

            facultades = Array.isArray(datosFacultades) ? datosFacultades : [];

            usuarios = mapearUsuarios(datosUsuarios);

            conectado = true;

        } catch (error) {

            conectado = false;

            mensajeError = 'No se pudieron cargar los usuarios. Inténtalo nuevamente.';

            console.error('Error cargando el módulo Usuarios:', error);

        } finally {

            cargando = false;

        }

    }

    function limpiarFormulario() {

        nombreCompleto = '';

        correoElectronico = '';

        password = '';

        telefono = '';

        rol = '';

        facultad = '';

        estadoUsuario = 'activo';

        mensajeError = '';

        mensajeExito = '';

    }

    async function desplazarAlFormulario() {

        // Espera a que Svelte muestre el formulario. Al abrir Crear o Editar,
        // vuelve al inicio de la página para que también se vea el encabezado
        // general de Usuarios y el encabezado del formulario.
        await tick();

        requestAnimationFrame(() => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });

    }

    function abrirFormulario() {

        limpiarFormulario();

        usuarioEditandoId = null;

        mostrarFormulario = true;

        desplazarAlFormulario();

    }

    function cancelarFormulario() {

        limpiarFormulario();

        mostrarFormulario = false;

    }

    function editarUsuario(usuario) {

        if (!usuario) {

            mensajeError = 'No fue posible identificar el usuario que deseas editar.';

            return;

        }

        const id = usuario.id_usuario ?? usuario.id;

        if (id === null || id === undefined) {

            mensajeError = 'El registro seleccionado no contiene un ID de usuario válido.';

            return;

        }

        mensajeError = '';

        mensajeExito = '';

        usuarioEditandoId = id;

        password = '';

        nombreCompleto = usuario.nombreCompleto ?? usuario.nombre_completo ?? '';

        correoElectronico = usuario.correoElectronico ?? usuario.correo_electronico ?? '';

        telefono = usuario.telefono ?? '';

        rol = usuario.id_rol !== null && usuario.id_rol !== undefined ? String(usuario.id_rol) : '';

        facultad = usuario.id_facultad !== null && usuario.id_facultad !== undefined ? String(usuario.id_facultad) : 'null';

        estadoUsuario = (

            usuario.estado === true ||

            usuario.estado === 'true' ||

            usuario.estado === 1 ||

            usuario.estadoTexto === 'Activo'

        ) ? 'activo' : 'inactivo';

        mostrarFormulario = true;

        desplazarAlFormulario();

    }

    async function guardarUsuario(evento) {

        evento.preventDefault();

        mensajeError = '';

        mensajeExito = '';

        if (!nombreCompleto.trim() || !correoElectronico.trim() || !rol || !estadoUsuario) {

            mensajeError = 'Completa los campos obligatorios: nombre, correo, rol y estado.';

            return;

        }

        if (!usuarioEditandoId && esDecano) {
            const rolSeleccionado = roles.find((item) => Number(item.id_rol) === Number(rol));
            if (normalizar(rolSeleccionado?.nombre ?? rolSeleccionado?.nombre_rol) !== 'docente') {
                mensajeError = 'Como Decano, solo puedes crear usuarios con el rol Docente.';
                return;
            }
        }

        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correoElectronico.trim())) {

            mensajeError = 'Ingresa un correo electrónico válido.';

            return;

        }

        if ((!usuarioEditandoId && password.length < 8) || (usuarioEditandoId && password.length > 0 && password.length < 8)) {

            mensajeError = 'La contraseña debe tener al menos 8 caracteres. Si estás editando, déjala vacía para conservar la actual.';

            return;

        }

        guardando = true;

        try {

            const payload = {

                nombre_completo: nombreCompleto.trim(),

                correo_electronico: correoElectronico.trim(),

                telefono: telefono.trim() || null,

                id_rol: Number(rol),

                id_facultad: !facultad || facultad === 'null' ? null : Number(facultad),

                estado: estadoUsuario === 'activo',

                ...(password.length > 0 ? { password } : {})

            };

            const respuesta = await fetch(usuarioEditandoId ? `${API_BASE}/usuarios/${usuarioEditandoId}` : `${API_BASE}/usuarios/`, {

                method: usuarioEditandoId ? 'PUT' : 'POST',

                headers: {
                    'Content-Type': 'application/json',
                    Accept: 'application/json',
                    ...(tokenAcceso ? { Authorization: `Bearer ${tokenAcceso}` } : {})
                },

                body: JSON.stringify(payload)

            });

            const resultado = await leerRespuesta(respuesta);

            mensajeExito = resultado?.mensaje ?? (usuarioEditandoId ? 'Usuario actualizado correctamente.' : 'Usuario registrado correctamente.');

            await cargarDatos();

            if (conectado) {

                limpiarFormulario();

                mostrarFormulario = false;

            }

        } catch (error) {

            mensajeError = 'No fue posible guardar el usuario. Inténtalo nuevamente.';

            console.error('Error guardando usuario:', error);

        } finally {

            guardando = false;

        }

    }

</script>

<svelte:head>

    <title>Sistema de Reservas CUL - Usuarios</title>

    <meta name="description" content="Gestión de usuarios del Sistema de Reservas CUL" />

</svelte:head>

<div class="usuarios-container">

    <PageHeader

        etiqueta="ADMINISTRACIÓN DEL SISTEMA"

        titulo="Usuarios"

        descripcion="Administra los usuarios y organiza su acceso al Sistema de Reservas CUL."

        accionTexto={mostrarFormulario ? 'Cancelar creación' : 'Nuevo usuario'}

        onAccion={() => (mostrarFormulario ? cancelarFormulario() : abrirFormulario())}

    />

    {#if mensajeError}

        <div class="mensaje-formulario mensaje-error" role="alert">{mensajeError}</div>

    {/if}

    {#if mostrarFormulario}

        <section class="panel formulario-panel">

            <div class="panel-encabezado"><div><h2>{usuarioEditandoId ? 'Editar usuario' : 'Registrar usuario'}</h2><p>{usuarioEditandoId ? 'Actualiza la información del usuario seleccionado.' : 'Completa la información del usuario y configura su acceso.'}</p></div></div>

            <form class="formulario-contenido" onsubmit={guardarUsuario}>

                <div class="formulario-grid">

                    <FormInput id="nombreCompleto" label="Nombre completo" bind:valor={nombreCompleto} placeholder="Ingrese el nombre completo" requerido />

                    <FormInput id="correoElectronico" label="Correo electrónico" tipo="email" bind:valor={correoElectronico} placeholder="Ingrese el correo electrónico" requerido />

                    <FormInput
                        id="password"
                        label={usuarioEditandoId ? 'Cambiar contraseña (opcional)' : 'Contraseña de acceso'}
                        tipo="password"
                        bind:valor={password}
                        placeholder={usuarioEditandoId ? 'Dejar vacío para mantener la actual' : 'Mínimo 8 caracteres'}
                        mensajeAyuda={usuarioEditandoId ? 'Si escribes una nueva contraseña, se actualizará de forma segura. Si lo dejas vacío, se conservará la contraseña actual.' : 'Esta contraseña permitirá al usuario iniciar sesión y se guardará de forma segura.'}
                        requerido={!usuarioEditandoId}
                    />

                    <FormInput id="telefono" label="Teléfono" tipo="tel" bind:valor={telefono} placeholder="Ingrese el teléfono" />

                    <FormSelect id="rol" label="Rol" bind:valor={rol} opciones={opcionesRoles} placeholder="Seleccionar rol" requerido deshabilitado={cargando || opcionesRoles.length === 0} />

                    <FormSelect id="facultad" label="Facultad" bind:valor={facultad} opciones={opcionesFacultades} placeholder="Seleccionar facultad" deshabilitado={cargando || opcionesFacultades.length === 0} />

                    <FormSelect id="estadoUsuario" label="Estado" bind:valor={estadoUsuario} opciones={opcionesEstados} placeholder="Seleccionar estado" requerido />

                </div>

                {#if mensajeExito}<div class="mensaje-formulario mensaje-exito" role="status">{mensajeExito}</div>{/if}

                <div class="formulario-acciones">

                    <BaseButton texto="Cancelar" variante="secundario" onClick={cancelarFormulario} />

                    <BaseButton texto={guardando ? 'Guardando...' : usuarioEditandoId ? 'Guardar cambios' : 'Guardar usuario'} variante="primario" tipo="submit" deshabilitado={guardando || !conectado} />

                </div>

            </form>

        </section>

    {/if}

    <section class="panel">

        <div class="panel-encabezado"><div><h2>Buscar usuarios</h2><p>Utiliza los filtros para localizar usuarios registrados.</p></div><BaseButton texto="Actualizar" variante="contorno" onClick={cargarDatos} deshabilitado={cargando} /></div>

        <div class="filtros-grid">

            <FormInput id="buscarNombre" label="Nombre" bind:valor={buscarNombre} placeholder="Buscar por nombre..." />

            <FormInput id="buscarCorreo" label="Correo electrónico" bind:valor={buscarCorreo} placeholder="Buscar por correo..." />

            <div class="filtro-rol-field">
                <label for="buscarRol" class="filtro-rol-label">Rol</label>
                <select id="buscarRol" bind:value={buscarRol} class="filtro-rol-select">
                    <option value="">Todos los roles</option>
                    {#each opcionesRoles as opcion (opcion.valor)}
                        <option value={opcion.valor}>{opcion.etiqueta}</option>
                    {/each}
                </select>
            </div>

        </div>

    </section>

    <section class="panel">

        <div class="panel-encabezado tabla-encabezado">

            <div><h2>Usuarios registrados</h2><p>Consulta la información y el estado de los usuarios.</p></div>

        </div>

        <div class="tabla-contenedor">

            <DataTable {columnas} filas={usuariosFiltrados} {cargando} onEditar={editarUsuario} mensajeVacio={conectado ? 'No hay usuarios que coincidan con la búsqueda.' : 'No se pudieron cargar los usuarios. Inténtalo nuevamente.'} />

        </div>

    </section>

</div>

<style>

    .usuarios-container{width:100%;max-width:1600px;margin:0 auto;padding:32px;box-sizing:border-box;color:#f8fafc}.panel{width:100%;margin-bottom:24px;overflow:hidden;border:1px solid #334155;border-radius:12px;background:#1e293b;box-sizing:border-box}.formulario-panel{scroll-margin-top:88px}.panel-encabezado{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:22px;border-bottom:1px solid #334155}.panel-encabezado h2{margin:0;color:#f8fafc;font-size:17px;font-weight:750}.panel-encabezado p{margin:7px 0 0;color:#b7c5d9;font-size:13px;line-height:1.6}.filtros-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;padding:24px}.filtro-rol-field{display:flex;flex-direction:column;gap:8px;min-width:0}.filtro-rol-label{color:#dbe5f5;font-size:13px;font-weight:600}.filtro-rol-select{width:100%;min-height:44px;padding:11px 36px 11px 13px;border:1px solid #3b4b63;border-radius:9px;outline:none;background-color:#172338;color:#f8fafc;font-family:inherit;font-size:14px;cursor:pointer;transition:border-color .2s ease,box-shadow .2s ease}.filtro-rol-select:focus{border-color:#60a5fa;box-shadow:0 0 0 3px rgb(59 130 246 / 15%)}.filtro-rol-select option{background:#172338;color:#f8fafc}.formulario-contenido{padding:24px}.formulario-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px}.formulario-nota{display:flex;align-items:flex-start;gap:10px;margin-top:24px;padding:14px;border:1px solid #334155;border-radius:8px;background:#172338;color:#cbd5e1;font-size:12px;line-height:1.7}.formulario-nota span{color:#60a5fa;font-size:17px}.mensaje-formulario{margin:16px 24px;padding:12px 14px;border:1px solid #475569;border-radius:8px;font-size:13px;line-height:1.6}.formulario-contenido .mensaje-formulario{margin:20px 0 0}.mensaje-error{border-color:#7f1d1d;background:#451a1a;color:#fecaca}.mensaje-exito{border-color:#166534;background:#143326;color:#bbf7d0}.formulario-acciones{display:flex;justify-content:flex-end;gap:12px;margin-top:24px;padding-top:20px;border-top:1px solid #334155}.estado-conexion{display:inline-flex;align-items:center;gap:8px;flex-shrink:0;padding:7px 10px;border:1px solid #475569;border-radius:20px;color:#cbd5e1;font-size:11px;white-space:nowrap}.estado-conexion.conectado{border-color:#166534;color:#bbf7d0}.estado-punto{width:7px;height:7px;border-radius:50%;background:#f59e0b}.estado-conexion.conectado .estado-punto{background:#22c55e}.tabla-contenedor{width:100%;overflow-x:auto;padding:16px 20px 20px;box-sizing:border-box}@media(max-width:1000px){.filtros-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:650px){.usuarios-container{padding:22px 16px}.panel-encabezado{align-items:flex-start;flex-direction:column;padding:18px}.filtros-grid,.formulario-grid{grid-template-columns:minmax(0,1fr)}.filtros-grid,.formulario-contenido{padding:18px}.formulario-acciones{flex-direction:column-reverse}.tabla-contenedor{padding:12px}.estado-conexion{align-self:flex-start}}

</style>
