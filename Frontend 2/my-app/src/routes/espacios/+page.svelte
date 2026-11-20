<script>
	import { onMount } from 'svelte';
	import PageHeader from '$lib/components/ui/PageHeader.svelte';
	import BaseButton from '$lib/components/ui/BaseButton.svelte';
	import FormInput from '$lib/components/ui/FormInput.svelte';
	import FormSelect from '$lib/components/ui/FormSelect.svelte';
	import DataTable from '$lib/components/ui/DataTable.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';

	// Estados reactivos con Svelte 5 (Runes)
	let mostrarModal = $state(false);
	let busqueda = $state('');
	let tipoSeleccionado = $state('');
	let facultadSeleccionada = $state('');

	let nombreEspacio = $state('');
	let tipoNuevoEspacio = $state('');
	let capacidad = $state('');
	let ubicacion = $state('');
	let facultadNueva = $state('');
	let disponibilidadSabado = $state('');

	let cargando = $state(true);
	let mensajeError = $state('');
	let mensajeExito = $state('');
	let conectadoBD = $state(false);

	// Control visual de permisos: el docente no puede crear espacios.
	let puedeCrearEspacios = $state(false);

	function normalizarTexto(valor) {
		return String(valor ?? '')
			.normalize('NFD')
			.replace(/[\u0300-\u036f]/g, '')
			.trim()
			.toLowerCase();
	}

	function buscarRolEnObjeto(objeto, profundidad = 0) {
		if (!objeto || typeof objeto !== 'object' || profundidad > 5) return '';
		const camposRol = [
			'rol', 'role', 'nombre_rol', 'nombreRol', 'tipo_usuario',
			'tipoUsuario', 'perfil', 'nombre_perfil', 'nombrePerfil'
		];

		for (const [clave, valor] of Object.entries(objeto)) {
			if (camposRol.includes(clave) && typeof valor === 'string' && valor.trim()) {
				return valor;
			}
		}
		for (const valor of Object.values(objeto)) {
			if (valor && typeof valor === 'object') {
				const encontrado = buscarRolEnObjeto(valor, profundidad + 1);
				if (encontrado) return encontrado;
			}
		}
		return '';
	}

	function comprobarPermisoCrearEspacios() {
		// Por defecto se oculta la acción hasta identificar un perfil autorizado.
		puedeCrearEspacios = false;
		try {
			const valores = [];
			const preferidas = [
				'usuario_sesion', 'usuario', 'user', 'usuarioActual',
				'currentUser', 'user_session', 'sesion'
			];

			for (const clave of preferidas) {
				const valor = localStorage.getItem(clave);
				if (valor) valores.push({ clave, valor });
			}
			for (let i = 0; i < localStorage.length; i++) {
				const clave = localStorage.key(i);
				if (!clave) continue;
				const valor = localStorage.getItem(clave);
				if (valor && !valores.some((item) => item.clave === clave)) {
					valores.push({ clave, valor });
				}
			}

			let rol = '';
			for (const item of valores) {
				const claveNormalizada = normalizarTexto(item.clave);
				const textoNormalizado = normalizarTexto(item.valor);
				if (/(^|_)(rol|role|perfil)(_|$)/.test(claveNormalizada) &&
					/^(administrador|admin|decano|docente)$/.test(textoNormalizado)) {
					rol = textoNormalizado;
					break;
				}
				try {
					rol = normalizarTexto(buscarRolEnObjeto(JSON.parse(item.valor)));
					if (rol) break;
				} catch {
					// Ignorar valores de almacenamiento que no sean JSON.
				}
			}
			puedeCrearEspacios = ['administrador', 'admin', 'decano'].includes(rol);
		} catch (error) {
			console.error('No fue posible comprobar el rol de la sesión:', error);
			puedeCrearEspacios = false;
		}
	}

	// Arrays reactivos para recibir los datos de PostgreSQL (Neon)
	let tiposEspacio = $state([]);
	let facultades = $state([]);
	let espaciosRaw = $state([]);

	const opcionesSabado = [
		{ valor: 'true', etiqueta: 'Sí' },
		{ valor: 'false', etiqueta: 'No' }
	];

	// Columnas adaptadas a las reglas del parcial (se usa 'num' correlativo en lugar de ID)
	const columnas = [
		{ clave: 'num', etiqueta: '#' },
		{ clave: 'nombre', etiqueta: 'Nombre' },
		{ clave: 'tipo', etiqueta: 'Tipo' },
		{ clave: 'capacidad', etiqueta: 'Capacidad' },
		{ clave: 'ubicacion', etiqueta: 'Ubicación' },
		{ clave: 'facultad', etiqueta: 'Facultad' },
		{ clave: 'acciones', etiqueta: 'Acciones' }
	];

	// Carga automática al montar el componente en el navegador
	onMount(async () => {
		comprobarPermisoCrearEspacios();
		await cargarTodo();
	});

	async function cargarTodo() {
		cargando = true;
		mensajeError = '';
		conectadoBD = false;

		try {
			// Cada endpoint se consulta por separado para que un fallo en facultades
			// no impida cargar los tipos de espacios ni la lista de espacios.
			const [resEspacios, resTipos, resFacultades] = await Promise.allSettled([
				fetch('http://127.0.0.1:8000/espacios/'),
				fetch('http://127.0.0.1:8000/tipos-espacio/'),
				fetch('http://127.0.0.1:8000/facultades/')
			]);

			// ESPACIOS
			if (resEspacios.status === 'fulfilled' && resEspacios.value.ok) {
				const datosEspacios = await resEspacios.value.json();
				espaciosRaw = Array.isArray(datosEspacios) ? datosEspacios : [];
				conectadoBD = true;
			} else {
				espaciosRaw = [];
				const detalle = resEspacios.status === 'rejected'
					? resEspacios.reason?.message
					: `HTTP ${resEspacios.value.status}`;
				throw new Error(`No se pudo cargar la lista de espacios. ${detalle || ''}`.trim());
			}

			// TIPOS DE ESPACIO
			if (resTipos.status === 'fulfilled' && resTipos.value.ok) {
				const datosTipos = await resTipos.value.json();
				if (!Array.isArray(datosTipos)) {
					throw new Error('La respuesta de tipos de espacio no tiene el formato esperado.');
				}
				tiposEspacio = [
					{ valor: '', etiqueta: 'Todos los tipos' },
					...datosTipos
						.filter((t) => t.estado === true || t.estado === 'true' || t.estado === 1)
						.map((t) => ({
							valor: String(t.id_tipo_espacio),
							etiqueta: t.nombre_tipo
						}))
				];
			} else {
				tiposEspacio = [];
				const detalle = resTipos.status === 'rejected'
					? resTipos.reason?.message
					: `HTTP ${resTipos.value.status}`;
				mensajeError = `No se pudieron cargar los tipos de espacio. ${detalle || ''}`.trim();
			}

			// FACULTADES
			if (resFacultades.status === 'fulfilled' && resFacultades.value.ok) {
				const datosFac = await resFacultades.value.json();
				if (Array.isArray(datosFac)) {
					facultades = [
						{ valor: '', etiqueta: 'Todas las facultades' },
						...datosFac.map((f) => ({
							valor: String(f.id_facultad),
							etiqueta: f.nombre_facultad
						}))
					];
				} else {
					facultades = [];
					mensajeError = mensajeError || 'La respuesta de facultades no tiene el formato esperado.';
				}
			} else {
				facultades = [];
				if (!mensajeError) {
					const detalle = resFacultades.status === 'rejected'
						? resFacultades.reason?.message
						: `HTTP ${resFacultades.value.status}`;
					mensajeError = `No se pudieron cargar las facultades. ${detalle || ''}`.trim();
				}
			}
		} catch (err) {
			mensajeError = 'No fue posible cargar los espacios. Inténtalo nuevamente.';
			conectadoBD = false;
		} finally {
			cargando = false;
		}
	}

	// FILTRADO REACTIVO DINÁMICO (CORREGIDO PARA RESTAURAR LA LISTA COMPLETA)
	let espacios = $derived(
		espaciosRaw
			.filter((esp) => {
				// 1. Filtro por texto de búsqueda
				const textoLimpio = busqueda.trim().toLowerCase();
				const coincideTexto =
					!textoLimpio ||
					esp.nombre_espacio.toLowerCase().includes(textoLimpio) ||
					esp.ubicacion_piso.toLowerCase().includes(textoLimpio);

				// 2. Filtro por Tipo de Espacio (limpio para detectar opción por defecto)
				const tipoLimpio = String(tipoSeleccionado || '').trim();
				const coincideTipo =
					!tipoLimpio ||
					tipoLimpio === 'null' ||
					tipoLimpio === 'undefined' ||
					String(esp.id_tipo_espacio) === tipoLimpio;

				// 3. Filtro por Facultad
				const facultadLimpia = String(facultadSeleccionada || '').trim();
				const coincideFacultad =
					!facultadLimpia ||
					facultadLimpia === 'null' ||
					facultadLimpia === 'undefined' ||
					String(esp.id_facultad) === facultadLimpia;

				return coincideTexto && coincideTipo && coincideFacultad;
			})
			.map((esp, index) => {
				const tipoObj = tiposEspacio.find((t) => t.valor === String(esp.id_tipo_espacio));
				const facObj = facultades.find((f) => f.valor === String(esp.id_facultad));

				return {
					id: esp.id_espacio,
					num: index + 1, // Correlativo respetando la norma sin exponer IDs
					nombre: esp.nombre_espacio,
					tipo: tipoObj ? tipoObj.etiqueta : 'General',
					capacidad: `${esp.capacidad_aforo} personas`,
					ubicacion: esp.ubicacion_piso,
					facultad: facObj ? facObj.etiqueta : 'Institucional'
				};
			})
	);

	function abrirModal() {
		comprobarPermisoCrearEspacios();
		if (!puedeCrearEspacios) return;

		mensajeError = '';
		mensajeExito = '';
		mostrarModal = true;
	}

	function cerrarModal() {
		mostrarModal = false;
		mensajeError = '';

		nombreEspacio = '';
		tipoNuevoEspacio = '';
		capacidad = '';
		ubicacion = '';
		facultadNueva = '';
		disponibilidadSabado = '';
	}

	async function guardarEspacio(evento) {
		evento.preventDefault();
		comprobarPermisoCrearEspacios();
		if (!puedeCrearEspacios) {
			mostrarModal = false;
			mensajeError = 'Tu perfil no tiene permiso para registrar espacios.';
			return;
		}

		mensajeError = '';
		mensajeExito = '';

		if (
			!nombreEspacio.trim() ||
			!tipoNuevoEspacio ||
			!capacidad ||
			!ubicacion.trim() ||
			!facultadNueva ||
			!disponibilidadSabado
		) {
			mensajeError = 'Completa todos los campos obligatorios.';
			return;
		}

		const capacidadNumerica = Number(capacidad);

		if (!Number.isInteger(capacidadNumerica) || capacidadNumerica <= 0) {
			mensajeError = 'La capacidad debe ser un número entero mayor que cero.';
			return;
		}

		cargando = true;

		try {
			// Persistencia real vía POST a FastAPI y PostgreSQL en Neon
			const respuesta = await fetch('http://127.0.0.1:8000/espacios/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					nombre_espacio: nombreEspacio.trim(),
					capacidad_aforo: capacidadNumerica,
					ubicacion_piso: ubicacion.trim(),
					id_tipo_espacio: Number(tipoNuevoEspacio),
					id_facultad: Number(facultadNueva),
					permite_sabado: disponibilidadSabado === 'true'
				})
			});

			if (!respuesta.ok) {
				const errorApi = await respuesta.json();
				throw new Error(errorApi.detail || 'Error al guardar el espacio');
			}

			mensajeExito = '¡Espacio registrado con éxito!';
			await cargarTodo(); // Refresca la tabla automáticamente
			cerrarModal();
		} catch (err) {
			mensajeError = 'No fue posible guardar el espacio. Inténtalo nuevamente.';
		} finally {
			cargando = false;
		}
	}
</script>

<svelte:head>
	<title>Sistema de Reservas CUL - Espacios</title>
	<meta name="description" content="Consulta y gestión de espacios universitarios" />
</svelte:head>

<div class="espacios-container">
	{#if puedeCrearEspacios}
		<PageHeader
			etiqueta="GESTIÓN DE INFRAESTRUCTURA"
			titulo="Espacios"
			descripcion="Consulta y gestiona los espacios universitarios disponibles."
			accionTexto="Nuevo espacio"
			onAccion={abrirModal}
		/>
	{:else}
		<PageHeader
			etiqueta="GESTIÓN DE INFRAESTRUCTURA"
			titulo="Espacios"
			descripcion="Consulta y gestiona los espacios universitarios disponibles."
		/>
	{/if}

	<!-- FILTROS -->
	<section class="panel filtros-panel">
		<div class="panel-encabezado">
			<div>
				<h2>Buscar espacios</h2>
				<p>Utiliza los filtros para localizar los espacios registrados.</p>
			</div>
		</div>

		<div class="filtros-grid">
			<FormInput
				id="buscarEspacio"
				label="Nombre o Ubicación"
				bind:valor={busqueda}
				placeholder="Buscar espacio..."
			/>

			<FormSelect
				id="tipoFiltro"
				label="Tipo de espacio"
				bind:valor={tipoSeleccionado}
				opciones={tiposEspacio}
				placeholder="Todos los tipos"
			/>

			<FormSelect
				id="facultadFiltro"
				label="Facultad"
				bind:valor={facultadSeleccionada}
				opciones={facultades}
				placeholder="Todas las facultades"
			/>
		</div>
	</section>

	<!-- TABLA -->
	<section class="panel tabla-panel">
		<div class="panel-encabezado tabla-encabezado">
			<div>
				<h2>Espacios registrados</h2>
				<p>Consulta los espacios disponibles en el sistema.</p>
			</div>

		</div>

		<div class="tabla-contenido">
			<DataTable
				{columnas}
				filas={espacios}
				{cargando}
				mensajeVacio="No se encontraron espacios que coincidan con los filtros aplicados."
			/>
		</div>
	</section>
</div>

<!-- MODAL DE CREACIÓN -->
<Modal
	bind:abierto={mostrarModal}
	titulo="Nuevo espacio"
	descripcion="Completa la información del espacio universitario."
	onCerrar={cerrarModal}
	ancho="grande"
	clasePanel="modal-espacios"
>
	<form class="formulario-espacio" onsubmit={guardarEspacio}>
		<div class="formulario-grid">
			<FormInput
				id="nombreEspacio"
				label="Nombre del espacio"
				bind:valor={nombreEspacio}
				placeholder="Ingrese el nombre"
				requerido
			/>

			<FormSelect
				id="tipoNuevoEspacio"
				label="Tipo de espacio"
				bind:valor={tipoNuevoEspacio}
				opciones={tiposEspacio}
				placeholder="Seleccionar tipo"
				requerido
			/>

			<FormInput
				id="capacidadEspacio"
				label="Capacidad"
				tipo="number"
				bind:valor={capacidad}
				placeholder="Ingrese la capacidad"
				requerido
			/>

			<FormInput
				id="ubicacionEspacio"
				label="Ubicación"
				bind:valor={ubicacion}
				placeholder="Ingrese la ubicación"
				requerido
			/>

			<FormSelect
				id="facultadNueva"
				label="Facultad"
				bind:valor={facultadNueva}
				opciones={facultades}
				placeholder="Seleccionar facultad"
				requerido
			/>

			<FormSelect
				id="disponibilidadSabado"
				label="Disponibilidad los sábados"
				bind:valor={disponibilidadSabado}
				opciones={opcionesSabado}
				placeholder="Seleccionar opción"
				requerido
			/>
		</div>

		{#if mensajeError}
			<div class="mensaje mensaje-error" role="alert">
				{mensajeError}
			</div>
		{/if}

		{#if mensajeExito}
			<div class="mensaje mensaje-exito" role="status">
				{mensajeExito}
			</div>
		{/if}

		<div class="formulario-acciones">
			<BaseButton texto="Cancelar" variante="secundario" onClick={cerrarModal} />

			<BaseButton texto="Guardar espacio" variante="primario" tipo="submit" />
		</div>
	</form>
</Modal>

<style>
	.espacios-container {
		width: 100%;
		max-width: 1600px;
		margin: 0 auto;
		padding: 28px;
		box-sizing: border-box;
	}

	.panel {
		width: 100%;
		overflow: hidden;
		border: 1px solid #334155;
		border-radius: 13px;
		background: #1e293b;
		box-sizing: border-box;
	}

	.filtros-panel {
		margin-bottom: 24px;
	}

	.panel-encabezado {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 20px;
		padding: 22px;
		border-bottom: 1px solid #334155;
	}

	.panel-encabezado h2 {
		margin: 0;
		color: #f8fafc;
		font-size: 17px;
		font-weight: 750;
	}

	.panel-encabezado p {
		margin: 7px 0 0;
		color: #a9bad3;
		font-size: 13px;
		line-height: 1.6;
	}

	.filtros-grid {
		display: grid;
		grid-template-columns: 1.4fr 1fr 1fr;
		gap: 20px;
		padding: 22px;
	}

	.tabla-encabezado {
		border-bottom: 1px solid #334155;
	}

	.estado-conexion {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		flex-shrink: 0;
		padding: 8px 11px;
		border: 1px solid #475569;
		border-radius: 20px;
		color: #cbd5e1;
		font-size: 11px;
	}

	.estado-punto {
		width: 7px;
		height: 7px;
		border-radius: 50%;
		background: #fbbf24;
	}

	.estado-punto.activo {
		background: #22c55e;
	}

	.tabla-contenido {
		padding: 20px;
	}

	.formulario-espacio {
		display: flex;
		flex-direction: column;
		gap: 24px;
	}

	:global(html[data-tema='oscuro'] .app-main .modal-panel.modal-espacios) {
		border-color: #334155 !important;
		background: #1e293b !important;
		color: #dbe5f5 !important;
	}

	:global(html[data-tema='oscuro'] .app-main .modal-panel.modal-espacios .modal-encabezado) {
		border-color: #334155 !important;
		background: #172338 !important;
	}

	:global(html[data-tema='oscuro'] .app-main .modal-panel.modal-espacios .modal-contenido) {
		background: #1e293b !important;
		color: #dbe5f5 !important;
	}

	:global(html[data-tema='claro'] .app-main #tipoNuevoEspacio),
	:global(html[data-tema='claro'] .app-main #facultadNueva),
	:global(html[data-tema='claro'] .app-main #disponibilidadSabado) {
		color-scheme: light;
	}

	:global(html[data-tema='claro'] .app-main #tipoNuevoEspacio option),
	:global(html[data-tema='claro'] .app-main #facultadNueva option),
	:global(html[data-tema='claro'] .app-main #disponibilidadSabado option) {
		background: #ffffff !important;
		color: #1e293b !important;
	}

	:global(html[data-tema='oscuro'] .app-main #tipoNuevoEspacio),
	:global(html[data-tema='oscuro'] .app-main #facultadNueva),
	:global(html[data-tema='oscuro'] .app-main #disponibilidadSabado) {
		color-scheme: dark;
	}

	:global(html[data-tema='oscuro'] .app-main #tipoNuevoEspacio option),
	:global(html[data-tema='oscuro'] .app-main #facultadNueva option),
	:global(html[data-tema='oscuro'] .app-main #disponibilidadSabado option) {
		background: #172338 !important;
		color: #f8fafc !important;
	}

	.formulario-grid {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 22px;
	}

	.formulario-nota {
		padding: 13px 15px;
		border: 1px solid #334155;
		border-radius: 9px;
		background: #172338;
		color: #a9bad3;
		font-size: 12px;
		line-height: 1.6;
	}

	.mensaje {
		padding: 13px 15px;
		border-radius: 9px;
		font-size: 13px;
		line-height: 1.6;
	}

	.mensaje-error {
		border: 1px solid #7f1d1d;
		background: #451a1a;
		color: #fecaca;
	}

	.mensaje-exito {
		border: 1px solid #166534;
		background: #14532d;
		color: #bbf7d0;
	}

	.formulario-acciones {
		display: flex;
		justify-content: flex-end;
		gap: 12px;
		padding-top: 20px;
		border-top: 1px solid #334155;
	}

	@media (max-width: 900px) {
		.filtros-grid {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}
	}

	@media (max-width: 600px) {
		.espacios-container {
			padding: 20px 16px;
		}

		.filtros-grid,
		.formulario-grid {
			grid-template-columns: minmax(0, 1fr);
		}

		.panel-encabezado {
			align-items: flex-start;
			flex-direction: column;
			padding: 18px;
		}

		.tabla-contenido {
			padding: 12px;
		}

		.formulario-acciones {
			flex-direction: column-reverse;
		}
	}
</style>
