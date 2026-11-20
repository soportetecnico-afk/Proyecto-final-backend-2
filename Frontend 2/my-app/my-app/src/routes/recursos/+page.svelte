<script>
	import { onMount } from 'svelte';

	// Variables de estado
	let mostrarModal = $state(false);
	let recursosRaw = $state([]);
	let cargando = $state(true);
	let error = $state('');

	// Filtros reactivos
	let busqueda = $state('');
	let categoriaFiltro = $state('');
	let estadoFiltro = $state('');

	// Formulario de creación
	let nombreRecurso = $state('');
	let categoriaRecurso = $state('');
	let estadoMantenimiento = $state('');

	const opcionesCategoria = ['Tecnología', 'Mobiliario', 'Audiovisual', 'Laboratorio', 'Deportes', 'Equipos Médicos'];
	const opcionesEstado = ['Optimo', 'Requiere Reparacion', 'En Mantenimiento', 'Fuera de Servicio'];

	// Carga automática
	onMount(async () => {
		await cargarRecursos();
	});

	async function cargarRecursos() {
		cargando = true;
		error = '';
		try {
			const res = await fetch('http://127.0.0.1:8000/recursos/');
			if (!res.ok) throw new Error('No se pudo conectar con la API');
			recursosRaw = await res.json();
		} catch (e) {
			error = e.message;
		} finally {
			cargando = false;
		}
	}

	// Filtrado Reactivo (Mapeando el ID por el num)
	let recursos = $derived(
		recursosRaw
			.filter((r) => {
				const coincideTexto = !busqueda.trim() || r.nombre_recurso.toLowerCase().includes(busqueda.toLowerCase().trim());
				const coincideCat = !categoriaFiltro || r.categoria === categoriaFiltro;
				const coincideEst = !estadoFiltro || r.estado_mantenimiento === estadoFiltro;
				return coincideTexto && coincideCat && coincideEst;
			})
			.map((r, index) => ({
				...r,
				num: index + 1 // Correlativo respetando la norma sin mostrar ID
			}))
	);

	function abrirModal() {
		nombreRecurso = '';
		categoriaRecurso = '';
		estadoMantenimiento = '';
		mostrarModal = true;
	}

	async function guardarRecurso(evento) {
		evento.preventDefault();
		if (!nombreRecurso.trim() || !categoriaRecurso || !estadoMantenimiento) {
			alert('Complete los campos obligatorios');
			return;
		}

		try {
			const res = await fetch('http://127.0.0.1:8000/recursos/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					nombre_recurso: nombreRecurso.trim(),
					categoria: categoriaRecurso,
					estado_mantenimiento: estadoMantenimiento
				})
			});

			if (!res.ok) throw new Error('Error al guardar el recurso');
			
			alert('Recurso registrado exitosamente');
			mostrarModal = false;
			await cargarRecursos();
		} catch (e) {
			alert(e.message);
		}
	}
</script>

<svelte:head>
	<title>Sistema de Reservas CUL - Recursos</title>
	<meta name="description" content="Gestión de recursos universitarios" />
</svelte:head>

<div class="recursos-container container py-5">
	<!-- ENCABEZADO -->
	<div class="d-flex justify-content-between align-items-center recursos-encabezado mb-4">
		<div>
			<h1 class="fw-bold mb-1">Recursos</h1>
			<p class="descripcion mb-0">Consulta y gestiona los recursos disponibles.</p>
		</div>

		<button type="button" class="btn btn-primary" onclick={abrirModal}>
			+ Nuevo recurso
		</button>
	</div>

	<!-- FILTROS -->
	<div class="card panel-recursos mb-4 shadow-sm">
		<div class="card-body">
			<h5 class="fw-bold mb-3">Buscar recursos</h5>

			<div class="row g-3">
				<!-- Nombre -->
				<div class="col-md-5">
					<label for="buscarRecurso" class="form-label">Nombre del recurso</label>
					<input type="text" id="buscarRecurso" class="form-control" placeholder="Buscar recurso..." bind:value={busqueda} />
				</div>

				<!-- Categoría -->
				<div class="col-md-4">
					<label for="categoria" class="form-label">Categoría</label>
					<select id="categoria" class="form-select" bind:value={categoriaFiltro}>
						<option value="">Todas las categorías</option>
						{#each opcionesCategoria as cat}
							<option value={cat}>{cat}</option>
						{/each}
					</select>
				</div>

				<!-- Estado -->
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

	<!-- TABLA DE RECURSOS -->
	<div class="card panel-recursos shadow-sm">
		<div class="card-header py-3">
			<h5 class="fw-bold mb-0">Recursos registrados</h5>
		</div>

		<div class="card-body">
			{#if error}
				<div class="alert alert-danger">{error}</div>
			{/if}

			<div class="table-responsive">
				<table class="table-hover tabla-recursos mb-0 table align-middle">
					<thead>
						<tr>
							<th scope="col">#</th>
							<th scope="col">Nombre</th>
							<th scope="col">Categoría</th>
							<th scope="col">Estado de mantenimiento</th>
							<th scope="col">Activo</th>
						</tr>
					</thead>

					<tbody>
						{#if cargando}
							<tr><td colspan="5" class="text-center py-4 text-muted">Cargando datos...</td></tr>
						{:else if recursos.length === 0}
							<tr>
								<td colspan="5">
									<div class="estado-vacio text-center">
										<div class="empty-icon" aria-hidden="true">⚙️</div>
										<h5 class="fw-bold">No hay recursos encontrados</h5>
										<p class="mensaje-vacio mb-0">Modifica los filtros o agrega un recurso nuevo.</p>
									</div>
								</td>
							</tr>
						{:else}
							{#each recursos as rec}
								<tr>
									<td class="fw-bold text-secondary">{rec.num}</td>
									<td class="fw-semibold">{rec.nombre_recurso}</td>
									<td><span class="badge bg-secondary">{rec.categoria}</span></td>
									<td>
										<span class="badge {rec.estado_mantenimiento === 'Optimo' ? 'bg-success' : 'bg-warning'}">
											{rec.estado_mantenimiento || 'Optimo'}
										</span>
									</td>
									<td><span class="badge bg-primary">Sí</span></td>
								</tr>
							{/each}
						{/if}
					</tbody>
				</table>
			</div>
		</div>
	</div>
</div>

<!-- MODAL NUEVO RECURSO (Visible condicionalmente) -->
{#if mostrarModal}
<div class="modal fade show" tabindex="-1" style="display: block; background: rgba(0,0,0,0.5);">
	<div class="modal-dialog modal-dialog-centered">
		<div class="modal-content modal-recursos">
			<div class="modal-header">
				<h5 class="modal-title fw-bold">Nuevo recurso</h5>
				<button type="button" class="btn-close" onclick={() => mostrarModal = false}></button>
			</div>

			<div class="modal-body">
				<form onsubmit={guardarRecurso}>
					<div class="mb-3">
						<label for="nombreRecurso" class="form-label">Nombre del recurso</label>
						<input type="text" id="nombreRecurso" class="form-control" bind:value={nombreRecurso} placeholder="Ej: Proyector Epson 24X" required />
					</div>

					<div class="mb-3">
						<label for="categoriaRecurso" class="form-label">Categoría</label>
						<select id="categoriaRecurso" class="form-select" bind:value={categoriaRecurso} required>
							<option value="" disabled>Seleccionar categoría</option>
							{#each opcionesCategoria as cat}
								<option value={cat}>{cat}</option>
							{/each}
						</select>
					</div>

					<div class="mb-3">
						<label for="estadoRecurso" class="form-label">Estado de mantenimiento</label>
						<select id="estadoRecurso" class="form-select" bind:value={estadoMantenimiento} required>
							<option value="" disabled>Seleccionar estado</option>
							{#each opcionesEstado as est}
								<option value={est}>{est}</option>
							{/each}
						</select>
					</div>

					<div class="modal-footer px-0 pb-0 mt-4">
						<button type="button" class="btn btn-secondary" onclick={() => mostrarModal = false}>Cancelar</button>
						<button type="submit" class="btn btn-primary">Guardar recurso</button>
					</div>
				</form>
			</div>
		</div>
	</div>
</div>
{/if}

<style>
	/* Mantenemos tus estilos originales exactos */
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
	.recursos-container .form-control:focus, .recursos-container .form-select:focus { background-color: #0f172a; color: #ffffff; border-color: #3b82f6; box-shadow: 0 0 0 3px rgb(59 130 246 / 20%); }
	.recursos-container .form-select option { background-color: #0f172a; color: #f8fafc; }
	.recursos-container .tabla-recursos { --bs-table-bg: transparent; --bs-table-color: #e2e8f0; --bs-table-border-color: #334155; --bs-table-hover-bg: #2563eb; --bs-table-hover-color: #ffffff; color: #e2e8f0; border-color: #334155; }
	.recursos-container .tabla-recursos thead th { background-color: #273449; color: #f8fafc; border-color: #334155; font-weight: 700; padding: 13px 12px; white-space: nowrap; }
	.recursos-container .tabla-recursos tbody td { background-color: transparent; color: #e2e8f0; border-color: #334155; }
	.recursos-container .tabla-recursos tbody tr:hover td { --bs-table-bg-state: #2563eb; --bs-table-color-state: #ffffff; background-color: #2563eb !important; box-shadow: inset 0 0 0 9999px #2563eb !important; color: #ffffff !important; }
	.recursos-container .estado-vacio { padding: 40px 16px; }
	.recursos-container .empty-icon { margin-bottom: 20px; font-size: 3rem; opacity: 0.85; }
	.recursos-container .estado-vacio h5 { margin-bottom: 10px; color: #f8fafc; }
	.recursos-container .mensaje-vacio { color: #cbd5e1; }
	.recursos-container .btn-primary { background-color: #2563eb; border-color: #2563eb; color: #ffffff; font-weight: 600; border-radius: 7px; }
	.recursos-container .btn-primary:hover { background-color: #1d4ed8; border-color: #1d4ed8; }
	.modal-recursos { background-color: #1e293b; color: #f8fafc; border: 1px solid #334155; border-radius: 10px; }
	.modal-recursos .modal-header, .modal-recursos .modal-footer { border-color: #334155; }
	.modal-recursos .modal-title { color: #f8fafc; }
	.modal-recursos .form-label { color: #cbd5e1; }
	.modal-recursos .form-control, .modal-recursos .form-select { background-color: #0f172a; color: #f8fafc; border-color: #475569; }
	.modal-recursos .form-control::placeholder { color: #94a3b8; opacity: 1; }
	.modal-recursos .form-select option { background-color: #ffffff; color: #0f172a; }
	.modal-recursos .btn-close { filter: invert(1) grayscale(100%) brightness(200%); }
	@media (max-width: 768px) { .recursos-container { padding-top: 1.5rem !important; padding-bottom: 1.5rem !important; } .recursos-container .recursos-encabezado { align-items: flex-start !important; flex-direction: column; gap: 1rem; } .recursos-container .recursos-encabezado .btn { width: 100%; } .recursos-container .tabla-recursos { min-width: 650px; } }
</style>
