<script>
	import { onMount } from 'svelte';

	const API_URL = 'http://127.0.0.1:8000';

	// Estado de la página
	let mostrarModal = $state(false);
	let recursosRaw = $state([]);
	let cargando = $state(true);
	let guardandoEstado = $state({});
	let estadosEditados = $state({});
	let error = $state('');
	let mensaje = $state('');
	let usuarioActual = $state(null);

	// Filtros
	let busqueda = $state('');
	let categoriaFiltro = $state('');
	let estadoFiltro = $state('');

	// Formulario de creación
	let nombreRecurso = $state('');
	let categoriaRecurso = $state('');
	let estadoMantenimiento = $state('');

	const opcionesCategoria = [
		'Tecnología',
		'Mobiliario',
		'Audiovisual',
		'Laboratorio',
		'Deportes',
		'Equipos Médicos'
	];

	const opcionesEstado = [
		'Optimo',
		'Requiere Reparacion',
		'En Mantenimiento',
		'Fuera de Servicio'
	];

	// En la base de datos: Administrador = id_rol 1.
	let esAdministrador = $derived(Number(usuarioActual?.id_rol) === 1);

	onMount(async () => {
		const sesion = localStorage.getItem('usuario_sesion');
		if (sesion) {
			try {
				usuarioActual = JSON.parse(sesion);
			} catch {
				usuarioActual = null;
			}
		}

		await cargarRecursos();
	});

	async function leerErrorRespuesta(res, mensajePredeterminado) {
		try {
			const data = await res.json();
			return data.detail || data.mensaje || mensajePredeterminado;
		} catch {
			return mensajePredeterminado;
		}
	}

	async function cargarRecursos() {
		cargando = true;
		error = '';
		try {
			const res = await fetch(`${API_URL}/recursos/`);
			if (!res.ok) throw new Error(await leerErrorRespuesta(res, 'No se pudieron cargar los recursos.'));

			const data = await res.json();
			recursosRaw = Array.isArray(data) ? data : [];
			estadosEditados = {};
		} catch (e) {
			error = 'No fue posible cargar los recursos. Inténtalo nuevamente.';
		} finally {
			cargando = false;
		}
	}

	let recursos = $derived(
		recursosRaw
			.filter((r) => {
				const nombre = (r.nombre_recurso || '').toLowerCase();
				const coincideTexto = !busqueda.trim() || nombre.includes(busqueda.toLowerCase().trim());
				const coincideCat = !categoriaFiltro || r.categoria === categoriaFiltro;
				const coincideEst = !estadoFiltro || r.estado_mantenimiento === estadoFiltro;
				return coincideTexto && coincideCat && coincideEst;
			})
			.map((r, index) => ({ ...r, num: index + 1 }))
	);

	function abrirModal() {
		if (!esAdministrador) return;

		nombreRecurso = '';
		categoriaRecurso = '';
		estadoMantenimiento = '';
		mensaje = '';
		error = '';
		mostrarModal = true;
	}

	async function guardarRecurso(evento) {
		evento.preventDefault();
		if (!esAdministrador) {
			error = 'No tienes permisos para registrar recursos.';
			return;
		}

		if (!nombreRecurso.trim() || !categoriaRecurso || !estadoMantenimiento) {
			error = 'Complete los campos obligatorios.';
			return;
		}

		try {
			const res = await fetch(`${API_URL}/recursos/`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					nombre_recurso: nombreRecurso.trim(),
					categoria: categoriaRecurso,
					estado_mantenimiento: estadoMantenimiento
				})
			});

			if (!res.ok) throw new Error(await leerErrorRespuesta(res, 'Error al guardar el recurso.'));

			mostrarModal = false;
			mensaje = 'Recurso registrado exitosamente.';
			await cargarRecursos();
		} catch (e) {
			error = 'No fue posible guardar el recurso. Inténtalo nuevamente.';
		}
	}

	function obtenerEstadoSeleccionado(recurso) {
		return estadosEditados[recurso.id_recurso] ?? recurso.estado_mantenimiento ?? 'Optimo';
	}

	async function guardarEstadoRecurso(recurso) {
		if (!esAdministrador) return;

		const id = recurso.id_recurso;
		const nuevoEstado = obtenerEstadoSeleccionado(recurso);
		if (!id) {
			error = 'El recurso no contiene un identificador válido.';
			return;
		}
		if (nuevoEstado === recurso.estado_mantenimiento) {
			mensaje = 'No hay cambios en el estado del recurso.';
			return;
		}

		guardandoEstado[id] = true;
		error = '';
		mensaje = '';
		try {
			// El endpoint PUT existente recibe el objeto Recurso completo.
			const res = await fetch(`${API_URL}/recursos/${id}`, {
				method: 'PUT',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					nombre_recurso: recurso.nombre_recurso,
					categoria: recurso.categoria,
					estado_mantenimiento: nuevoEstado
				})
			});

			if (!res.ok) throw new Error(await leerErrorRespuesta(res, 'No se pudo actualizar el estado del recurso.'));

			mensaje = `Estado del recurso «${recurso.nombre_recurso}» actualizado correctamente.`;
			await cargarRecursos();
		} catch (e) {
			error = 'No fue posible actualizar el estado. Inténtalo nuevamente.';
		} finally {
			guardandoEstado[id] = false;
		}
	}
</script>

<svelte:head>
	<title>Sistema de Reservas CUL - Recursos</title>
	<meta name="description" content="Gestión de recursos universitarios" />
</svelte:head>

<div class="recursos-container container py-5">
	<div class="d-flex justify-content-between align-items-center recursos-encabezado mb-4">
		<div>
			<h1 class="fw-bold mb-1">Recursos</h1>
			<p class="descripcion mb-0">Consulta y gestiona los recursos disponibles.</p>
		</div>

		{#if esAdministrador}
			<button type="button" class="btn btn-primary" onclick={abrirModal}>+ Nuevo recurso</button>
		{/if}
	</div>

	{#if error}
		<div class="alert alert-danger" role="alert">{error}</div>
	{/if}
	{#if mensaje}
		<div class="alert alert-success" role="status">{mensaje}</div>
	{/if}

	<div class="card panel-recursos mb-4 shadow-sm">
		<div class="card-body">
			<h5 class="fw-bold mb-3">Buscar recursos</h5>
			<div class="row g-3">
				<div class="col-md-5">
					<label for="buscarRecurso" class="form-label">Nombre del recurso</label>
					<input type="text" id="buscarRecurso" class="form-control" placeholder="Buscar recurso..." bind:value={busqueda} />
				</div>
				<div class="col-md-4">
					<label for="categoria" class="form-label">Categoría</label>
					<select id="categoria" class="form-select" bind:value={categoriaFiltro}>
						<option value="">Todas las categorías</option>
						{#each opcionesCategoria as cat}
							<option value={cat}>{cat}</option>
						{/each}
					</select>
				</div>
				<div class="col-md-3">
					<label for="estado" class="form-label">Estado</label>
					<select id="estado" class="form-select" bind:value={estadoFiltro}>
						<option value="">Todos los estados</option>
						{#each opcionesEstado as est}
							<option value={est}>{est}</option>
						{/each}
					</select>
				</div>
			</div>
		</div>
	</div>

	<div class="card panel-recursos shadow-sm">
		<div class="card-header py-3 d-flex justify-content-between align-items-center">
			<h5 class="fw-bold mb-0">Recursos registrados</h5>
			<button type="button" class="btn btn-outline-light btn-sm" onclick={cargarRecursos} disabled={cargando}>↻ Actualizar</button>
		</div>

		<div class="card-body">
			<div class="table-responsive">
				<table class="table-hover tabla-recursos mb-0 table align-middle">
					<thead>
						<tr>
							<th scope="col">#</th>
							<th scope="col">Nombre</th>
							<th scope="col">Categoría</th>
							<th scope="col">Estado de mantenimiento</th>
							<th scope="col">Activo</th>
							{#if esAdministrador}<th scope="col">Acciones</th>{/if}
						</tr>
					</thead>
					<tbody>
						{#if cargando}
							<tr><td colspan={esAdministrador ? 6 : 5} class="text-center py-4 text-muted">Cargando datos...</td></tr>
						{:else if recursos.length === 0}
							<tr>
								<td colspan={esAdministrador ? 6 : 5}>
									<div class="estado-vacio text-center">
										<div class="empty-icon" aria-hidden="true">⚙️</div>
										<h5 class="fw-bold">No hay recursos encontrados</h5>
										<p class="mensaje-vacio mb-0">Modifica los filtros o agrega un recurso nuevo.</p>
									</div>
								</td>
							</tr>
						{:else}
							{#each recursos as rec (rec.id_recurso)}
								<tr>
									<td class="fw-bold text-secondary">{rec.num}</td>
									<td class="fw-semibold">{rec.nombre_recurso}</td>
									<td><span class="badge bg-secondary">{rec.categoria}</span></td>
									<td>
										{#if esAdministrador}
											<select
												class="form-select form-select-sm estado-select"
												aria-label={`Cambiar estado de ${rec.nombre_recurso}`}
												value={obtenerEstadoSeleccionado(rec)}
												onchange={(e) => (estadosEditados[rec.id_recurso] = e.currentTarget.value)}
											>
												{#each opcionesEstado as est}
													<option value={est}>{est}</option>
												{/each}
											</select>
										{:else}
											<span class="badge {rec.estado_mantenimiento === 'Optimo' ? 'bg-success' : rec.estado_mantenimiento === 'Fuera de Servicio' ? 'bg-danger' : 'bg-warning text-dark'}">
												{rec.estado_mantenimiento || 'Optimo'}
											</span>
										{/if}
									</td>
									<td><span class="badge bg-primary">{rec.estado ? 'Sí' : 'No'}</span></td>
									{#if esAdministrador}
										<td>
											<button
												type="button"
												class="btn btn-primary btn-sm"
												disabled={!!guardandoEstado[rec.id_recurso] || obtenerEstadoSeleccionado(rec) === rec.estado_mantenimiento}
												onclick={() => guardarEstadoRecurso(rec)}
											>
												{guardandoEstado[rec.id_recurso] ? 'Guardando...' : 'Guardar'}
											</button>
										</td>
									{/if}
								</tr>
							{/each}
						{/if}
					</tbody>
				</table>
			</div>
		</div>
	</div>
</div>

{#if mostrarModal}
	<div class="modal fade show modal-fondo" role="presentation" onclick={(e) => e.target === e.currentTarget && (mostrarModal = false)}>
		<div class="modal-dialog modal-dialog-centered">
			<div class="modal-content modal-recursos">
				<div class="modal-header">
					<h5 class="modal-title fw-bold">Nuevo recurso</h5>
					<button type="button" class="btn-close" aria-label="Cerrar" onclick={() => (mostrarModal = false)}></button>
				</div>
				<div class="modal-body">
					<form onsubmit={guardarRecurso}>
						<div class="mb-3">
							<label for="nombreRecurso" class="form-label">Nombre del recurso</label>
							<input type="text" id="nombreRecurso" class="form-control" bind:value={nombreRecurso} placeholder="Ej: Proyector Epson" required />
						</div>
						<div class="mb-3">
							<label for="categoriaRecurso" class="form-label">Categoría</label>
							<select id="categoriaRecurso" class="form-select" bind:value={categoriaRecurso} required>
								<option value="" disabled>Seleccionar categoría</option>
								{#each opcionesCategoria as cat}<option value={cat}>{cat}</option>{/each}
							</select>
						</div>
						<div class="mb-3">
							<label for="estadoRecurso" class="form-label">Estado de mantenimiento</label>
							<select id="estadoRecurso" class="form-select" bind:value={estadoMantenimiento} required>
								<option value="" disabled>Seleccionar estado</option>
								{#each opcionesEstado as est}<option value={est}>{est}</option>{/each}
							</select>
						</div>
						<div class="modal-footer px-0 pb-0 mt-4">
							<button type="button" class="btn btn-secondary" onclick={() => (mostrarModal = false)}>Cancelar</button>
							<button type="submit" class="btn btn-primary">Guardar recurso</button>
						</div>
					</form>
				</div>
			</div>
		</div>
	</div>
{/if}

<style>
	.recursos-container { color: #f8fafc; }
	.recursos-container .recursos-encabezado h1 { color: #f8fafc; font-size: 2rem; font-weight: 700; }
	.recursos-container .descripcion { color: #cbd5e1; }
	.recursos-container .panel-recursos { background-color: #1e293b; border: 1px solid #334155; border-radius: 10px; overflow: hidden; }
	.recursos-container .panel-recursos .card-body { background-color: #1e293b; }
	.recursos-container .panel-recursos .card-header { background-color: #1e293b; border-bottom: 1px solid #334155; }
	.recursos-container .panel-recursos h5 { color: #f8fafc; }
	.recursos-container .form-label { color: #cbd5e1; font-weight: 500; }
	.recursos-container .form-control, .recursos-container .form-select { background-color: #0f172a; color: #f8fafc; border: 1px solid #475569; border-radius: 7px; }
	.recursos-container .form-control::placeholder { color: #94a3b8; opacity: 1; }
	.recursos-container .form-control:focus, .recursos-container .form-select:focus { background-color: #0f172a; color: #fff; border-color: #3b82f6; box-shadow: 0 0 0 3px rgb(59 130 246 / 20%); }
	.recursos-container .form-select option { background-color: #0f172a; color: #f8fafc; }
	.recursos-container .tabla-recursos { --bs-table-bg: transparent; --bs-table-color: #e2e8f0; --bs-table-border-color: #334155; --bs-table-hover-bg: #2563eb; --bs-table-hover-color: #fff; color: #e2e8f0; border-color: #334155; }
	.recursos-container .tabla-recursos thead th { background-color: #273449; color: #f8fafc; border-color: #334155; font-weight: 700; padding: 13px 12px; white-space: nowrap; }
	.recursos-container .tabla-recursos tbody td { background-color: transparent; color: #e2e8f0; border-color: #334155; }
	.recursos-container .tabla-recursos tbody tr:hover td { --bs-table-bg-state: #2563eb; --bs-table-color-state: #ffffff; background-color: #2563eb !important; box-shadow: inset 0 0 0 9999px #2563eb !important; color: #ffffff !important; }
	:global(html[data-tema='claro'] .app-main .recursos-container .tabla-recursos) { --bs-table-hover-bg: #2563eb !important; --bs-table-hover-color: #ffffff !important; }
	:global(html[data-tema='claro'] .app-main .recursos-container .tabla-recursos tbody tr:hover td) { --bs-table-bg-state: #2563eb !important; --bs-table-color-state: #ffffff !important; background-color: #2563eb !important; box-shadow: inset 0 0 0 9999px #2563eb !important; color: #ffffff !important; }
	.recursos-container .estado-select { min-width: 175px; }
	.recursos-container .estado-vacio { padding: 40px 16px; }
	.recursos-container .empty-icon { margin-bottom: 20px; font-size: 3rem; opacity: .85; }
	.recursos-container .estado-vacio h5 { margin-bottom: 10px; color: #f8fafc; }
	.recursos-container .mensaje-vacio { color: #cbd5e1; }
	.recursos-container .btn-primary { background-color: #2563eb; border-color: #2563eb; color: #fff; font-weight: 600; border-radius: 7px; }
	.recursos-container .btn-primary:hover { background-color: #1d4ed8; border-color: #1d4ed8; }
	.modal-fondo { display: block; position: fixed; inset: 0; z-index: 1050; overflow-y: auto; background: rgb(2 6 23 / 70%); }
	.modal-recursos { background-color: #1e293b; color: #f8fafc; border: 1px solid #334155; border-radius: 10px; }
	.modal-recursos .modal-header, .modal-recursos .modal-footer { border-color: #334155; }
	.modal-recursos .modal-title { color: #f8fafc; }
	.modal-recursos .form-label { color: #cbd5e1; }
	.modal-recursos .form-control, .modal-recursos .form-select { background-color: #0f172a; color: #f8fafc; border-color: #475569; }
	.modal-recursos .form-control::placeholder { color: #94a3b8; opacity: 1; }
	.modal-recursos .form-select option { background-color: #ffffff; color: #0f172a; }
	.modal-recursos .btn-close { filter: invert(1) grayscale(100%) brightness(200%); }
	:global(html[data-tema='claro'] .app-main) .recursos-container .form-select,
	:global(html[data-tema='claro'] .app-main) .modal-recursos .form-select { color-scheme: light; }
	:global(html[data-tema='claro'] .app-main) .recursos-container .form-select option,
	:global(html[data-tema='claro'] .app-main) .modal-recursos .form-select option { background-color: #ffffff !important; color: #1e293b !important; }
	:global(html[data-tema='oscuro'] .app-main) .recursos-container .form-select,
	:global(html[data-tema='oscuro'] .app-main) .modal-recursos .form-select { color-scheme: dark; }
	:global(html[data-tema='oscuro'] .app-main) .recursos-container .form-select option,
	:global(html[data-tema='oscuro'] .app-main) .modal-recursos .form-select option { background-color: #0f172a !important; color: #f8fafc !important; }
	@media (max-width: 768px) {
		.recursos-container { padding-top: 1.5rem !important; padding-bottom: 1.5rem !important; }
		.recursos-container .recursos-encabezado { align-items: flex-start !important; flex-direction: column; gap: 1rem; }
		.recursos-container .recursos-encabezado .btn { width: 100%; }
		.recursos-container .tabla-recursos { min-width: 780px; }
	}
</style>
