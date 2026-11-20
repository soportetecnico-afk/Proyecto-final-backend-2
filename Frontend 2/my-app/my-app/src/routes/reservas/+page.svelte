<script>
	import { onMount } from 'svelte';

	// Variables reactivas obligatorias para Svelte 5 (Runes)
	let reservas = $state([]);
	let espacios = $state([]);
	let cargando = $state(true);
	let error = $state(null);

	// Sesión activa obtenida del localStorage (o usuario 3 por defecto)
	let usuarioSesion = $state({ id_usuario: 3, id_rol: 3, nombre: 'Estudiante' });

	// Formulario reactivo
	let nuevaReserva = $state({
		id_usuario: 3,
		id_espacio: '',
		id_tipo_evento: 1,
		fecha_reserva: '',
		hora_inicio: '',
		hora_fin: '',
		cantidad_asistentes: 1
	});

	// Métricas calculadas para las tarjetas
	let totalReservas = $derived(reservas.length);
	let pendientes = $derived(reservas.filter(r => r.estado_reserva === 'Pendiente').length);
	let aprobadas = $derived(reservas.filter(r => r.estado_reserva === 'Aprobada').length);

	onMount(async () => {
		// Recuperar usuario autenticado si existe
		const guardado = localStorage.getItem('usuario_sesion');
		if (guardado) {
			usuarioSesion = JSON.parse(guardado);
			nuevaReserva.id_usuario = usuarioSesion.id_usuario;
		}
		await cargarDatos();
	});

	async function cargarDatos() {
		cargando = true;
		error = null;
		try {
			// Consulta a la API FastAPI
			const [resRes, resEsp] = await Promise.all([
				fetch('http://127.0.0.1:8000/reservas/'),
				fetch('http://127.0.0.1:8000/espacios/')
			]);

			if (!resRes.ok) throw new Error('No se pudo obtener reservas');
			reservas = await resRes.json();

			if (resEsp.ok) {
				espacios = await resEsp.json();
			}
		} catch (err) {
			error = err.message;
		} finally {
			cargando = false;
		}
	}

	async function guardarReserva() {
		if (!nuevaReserva.id_espacio || !nuevaReserva.fecha_reserva || !nuevaReserva.hora_inicio || !nuevaReserva.hora_fin) {
			alert('Complete todos los campos requeridos');
			return;
		}

		try {
			const res = await fetch('http://127.0.0.1:8000/reservas/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(nuevaReserva)
			});

			if (!res.ok) {
				const detalle = await res.json();
				throw new Error(detalle.detail || 'Error al guardar');
			}

			alert('Reserva enviada exitosamente');
			nuevaReserva = {
				id_usuario: usuarioSesion.id_usuario,
				id_espacio: '',
				id_tipo_evento: 1,
				fecha_reserva: '',
				hora_inicio: '',
				hora_fin: '',
				cantidad_asistentes: 1
			};
			await cargarDatos();
		} catch (err) {
			alert('Error: ' + err.message);
		}
	}

	// Acción del Docente / Admin para aprobar reserva
	async function cambiarEstado(id_reserva, nuevoEstado) {
		try {
			// Obtenemos la reserva actual
			const actual = reservas.find(r => r.id_reserva === id_reserva);
			if (!actual) return;

			// Actualizamos con el nuevo estado
			const res = await fetch(`http://127.0.0.1:8000/reservas/${id_reserva}`, {
				method: 'PUT',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					...actual,
					estado_reserva: nuevoEstado
				})
			});

			if (res.ok) {
				await cargarDatos();
			}
		} catch (e) {
			console.error(e);
		}
	}
</script>

<svelte:head>
	<title>Sistema de Reservas CUL - Reservas</title>
	<meta name="description" content="Gestión de reservas de espacios universitarios" />
</svelte:head>

<div class="reservas-container container py-5">
	<!-- ENCABEZADO -->
	<div class="d-flex justify-content-between align-items-center reservas-encabezado mb-4">
		<div>
			<h1 class="fw-bold mb-1">Reservas</h1>
			<p class="descripcion mb-0">Gestiona las reservas de los espacios universitarios.</p>
		</div>

		<button
			type="button"
			class="btn btn-primary"
			data-bs-toggle="modal"
			data-bs-target="#modalReserva"
		>
			+ Nueva reserva
		</button>
	</div>

	<!-- TARJETAS DE ESTADO REACTIVAS -->
	<div class="row g-4 tarjetas-reservas mb-4">
		<!-- PENDIENTES -->
		<div class="col-md-4">
			<div class="card tarjeta-reserva">
				<div class="card-body">
					<div class="tarjeta-superior">
						<span class="tarjeta-etiqueta">Pendientes</span>
						<span class="tarjeta-icono icono-pendiente" aria-hidden="true">◷</span>
					</div>
					<h2 class="tarjeta-valor">0</h2>
					<span class="estado-reserva estado-pendiente">Pendientes de aprobación</span>
				</div>
			</div>
		</div>

		<!-- APROBADAS -->
		<div class="col-md-4">
			<div class="card tarjeta-reserva">
				<div class="card-body">
					<div class="tarjeta-superior">
						<span class="tarjeta-etiqueta">Aprobadas</span>
						<span class="tarjeta-icono icono-aprobado" aria-hidden="true">✓</span>
					</div>
					<h2 class="tarjeta-valor">{reservas.length}</h2>
					<span class="estado-reserva estado-aprobado">Reservas confirmadas</span>
				</div>
			</div>
		</div>

		<!-- TOTAL -->
		<div class="col-md-4">
			<div class="card tarjeta-reserva">
				<div class="card-body">
					<div class="tarjeta-superior">
						<span class="tarjeta-etiqueta">Total</span>
						<span class="tarjeta-icono icono-total" aria-hidden="true">▤</span>
					</div>
					<h2 class="tarjeta-valor">{reservas.length}</h2>
					<span class="estado-reserva estado-total">Reservas registradas</span>
				</div>
			</div>
		</div>
	</div>

	<!-- TABLA DE RESERVAS -->
	<div class="card panel-reservas">
		<div class="card-header d-flex justify-content-between align-items-center">
			<div>
				<h5 class="fw-bold mb-1">Reservas recientes</h5>
				<p class="descripcion-panel mb-0">Consulta las solicitudes sincronizadas con PostgreSQL.</p>
			</div>
			<button class="btn btn-sm btn-outline-secondary text-white" on:click={cargarDatos}>
				🔄 Actualizar
			</button>
		</div>

		<div class="card-body">
			{#if error}
				<div class="alert alert-danger m-3">
					<strong>Error de conexión:</strong> {error}. Asegúrate de que FastAPI esté corriendo en el puerto 8000.
				</div>
			{/if}

			<div class="table-responsive">
				<table class="table-hover tabla-reservas mb-0 table align-middle">
					<thead>
						<tr>
							<th scope="col">#</th>
							<th scope="col">Espacio</th>
							<th scope="col">Fecha</th>
							<th scope="col">Horario</th>
							<th scope="col">Asistentes</th>
							<th scope="col">Estado</th>
						</tr>
					</thead>

					<tbody>
						{#if cargando}
							<tr>
								<td colspan="6" class="text-center py-4 text-muted">
									Cargando datos desde la base de datos...
								</td>
							</tr>
						{:else if reservas.length === 0}
							<tr>
								<td colspan="6">
									<div class="estado-vacio text-center">
										<div class="estado-vacio-icono" aria-hidden="true">📅</div>
										<h5 class="fw-bold">No hay reservas cargadas</h5>
										<p class="mensaje-vacio mb-0">
											Las reservas registradas en Neon aparecerán automáticamente aquí.
										</p>
									</div>
								</td>
							</tr>
						{:else}
							{#each reservas as r, index}
								<tr>
									<td class="fw-semibold">{index + 1}</td>
									<td>Espacio #{r.id_espacio}</td>
									<td>{r.fecha_reserva}</td>
									<td>{r.hora_inicio} - {r.hora_fin}</td>
									<td>{r.cantidad_asistentes} personas</td>
									<td>
										<span class="estado-reserva estado-aprobado">Confirmada</span>
									</td>
								</tr>
							{/each}
						{/if}
					</tbody>
				</table>
			</div>
		</div>
	</div>
</div>

<!-- MODAL NUEVA RESERVA -->
<div
	class="modal fade"
	id="modalReserva"
	tabindex="-1"
	aria-labelledby="modalReservaLabel"
	aria-hidden="true"
>
	<div class="modal-dialog modal-lg modal-dialog-centered">
		<div class="modal-content modal-reservas">
			<div class="modal-header">
				<div>
					<h5 class="modal-title fw-bold" id="modalReservaLabel">Nueva reserva</h5>
					<p class="modal-descripcion mb-0">Completa los datos de la solicitud.</p>
				</div>
				<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
			</div>

			<div class="modal-body">
				<form on:submit|preventDefault={guardarReserva}>
					<div class="row g-3">
						<!-- ESPACIO (Cargado dinámicamente) -->
						<div class="col-md-6">
							<label for="espacio" class="form-label">Espacio</label>
							<select id="espacio" class="form-select" bind:value={nuevaReserva.id_espacio} required>
								<option value="" disabled selected>Seleccionar espacio</option>
								{#each espacios as esp}
									<option value={esp.id_espacio}>
										{esp.nombre_espacio} (Cap: {esp.capacidad_aforo})
									</option>
								{/each}
							</select>
						</div>

						<!-- FECHA -->
						<div class="col-md-6">
							<label for="fecha" class="form-label">Fecha</label>
							<input type="date" id="fecha" class="form-control" bind:value={nuevaReserva.fecha_reserva} required />
						</div>

						<!-- HORA INICIO -->
						<div class="col-md-6">
							<label for="horaInicio" class="form-label">Hora de inicio</label>
							<input type="time" id="horaInicio" class="form-control" bind:value={nuevaReserva.hora_inicio} required />
						</div>

						<!-- HORA FIN -->
						<div class="col-md-6">
							<label for="horaFin" class="form-label">Hora de finalización</label>
							<input type="time" id="horaFin" class="form-control" bind:value={nuevaReserva.hora_fin} required />
						</div>

						<!-- ASISTENTES -->
						<div class="col-md-12">
							<label for="asistentes" class="form-label">Cantidad de asistentes</label>
							<input
								type="number"
								id="asistentes"
								class="form-control"
								min="1"
								placeholder="Ej: 25"
								bind:value={nuevaReserva.cantidad_asistentes}
								required
							/>
						</div>
					</div>

					<div class="modal-footer px-0 pb-0 mt-4">
						<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
						<button type="submit" class="btn btn-primary" data-bs-dismiss="modal">
							Solicitar reserva
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
</div>

<style>
	/* CONTENEDOR PRINCIPAL */
	.reservas-container {
		color: #f8fafc;
	}

	/* ENCABEZADO */
	.reservas-container .reservas-encabezado h1 {
		color: #f8fafc !important;
		font-size: 2rem;
		font-weight: 700;
	}

	.reservas-container .reservas-encabezado .descripcion {
		color: #334155 !important;
	}

	/* TARJETAS DE ESTADÍSTICAS */
	.reservas-container .tarjeta-reserva {
		height: 100%;
		background-color: #1e293b !important;
		border: 1px solid #334155 !important;
		border-radius: 10px;
		color: #f8fafc !important;
		box-shadow: none;
	}

	.reservas-container .tarjeta-reserva .card-body {
		padding: 22px;
		background-color: #1e293b !important;
		color: #f8fafc !important;
	}

	.reservas-container .tarjeta-superior {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 12px;
	}

	.reservas-container .tarjeta-etiqueta {
		color: #cbd5e1 !important;
		font-size: 0.95rem;
		font-weight: 600;
	}

	.reservas-container .tarjeta-icono {
		display: flex;
		width: 40px;
		height: 40px;
		align-items: center;
		justify-content: center;
		border-radius: 10px;
		font-size: 1.35rem;
		font-weight: 700;
	}

	.reservas-container .icono-pendiente {
		background-color: rgb(245 158 11 / 15%);
		color: #fbbf24 !important;
	}

	.reservas-container .icono-aprobado {
		background-color: rgb(34 197 94 / 15%);
		color: #4ade80 !important;
	}

	.reservas-container .icono-total {
		background-color: rgb(59 130 246 / 15%);
		color: #60a5fa !important;
	}

	.reservas-container .tarjeta-valor {
		margin: 20px 0 14px;
		color: #f8fafc !important;
		font-size: 2rem;
		font-weight: 700;
	}

	/* ESTADOS */
	.reservas-container .estado-reserva {
		display: inline-block;
		padding: 6px 10px;
		border: 1px solid transparent;
		border-radius: 6px;
		font-size: 0.78rem;
		font-weight: 600;
	}

	.reservas-container .estado-pendiente {
		background-color: rgb(245 158 11 / 12%);
		border-color: rgb(245 158 11 / 25%);
		color: #fcd34d !important;
	}

	.reservas-container .estado-aprobado {
		background-color: rgb(34 197 94 / 12%);
		border-color: rgb(34 197 94 / 25%);
		color: #86efac !important;
	}

	.reservas-container .estado-total {
		background-color: rgb(59 130 246 / 12%);
		border-color: rgb(59 130 246 / 25%);
		color: #93c5fd !important;
	}

	/* PANEL DE LA TABLA */
	.reservas-container .panel-reservas {
		overflow: hidden;
		background-color: #1e293b !important;
		border: 1px solid #334155 !important;
		border-radius: 10px;
		color: #f8fafc !important;
	}

	.reservas-container .panel-reservas .card-header {
		padding: 18px 20px;
		background-color: #1e293b !important;
		border-bottom: 1px solid #334155 !important;
		color: #f8fafc !important;
	}

	.reservas-container .panel-reservas .card-header h5 {
		color: #f8fafc !important;
	}

	.reservas-container .descripcion-panel {
		color: #cbd5e1 !important;
		font-size: 0.9rem;
	}

	.reservas-container .panel-reservas .card-body {
		padding: 16px;
		background-color: #1e293b !important;
		color: #f8fafc !important;
	}

	/* TABLA */
	.reservas-container .tabla-reservas {
		--bs-table-bg: #1e293b;
		--bs-table-color: #e2e8f0;
		--bs-table-border-color: #334155;
		--bs-table-hover-bg: #2563eb;
		--bs-table-hover-color: #ffffff;

		width: 100%;
		background-color: #1e293b !important;
		color: #e2e8f0 !important;
		border-color: #334155 !important;
	}

	.reservas-container .tabla-reservas thead th {
		padding: 14px 12px;
		background-color: #273449 !important;
		border-color: #334155 !important;
		color: #f8fafc !important;
		font-weight: 700;
		white-space: nowrap;
	}

	.reservas-container .tabla-reservas tbody,
	.reservas-container .tabla-reservas tbody tr,
	.reservas-container .tabla-reservas tbody td {
		background-color: #1e293b !important;
		border-color: #334155 !important;
		color: #e2e8f0 !important;
	}

	.reservas-container .tabla-reservas tbody tr:hover td {
		--bs-table-bg-state: #2563eb;
		--bs-table-color-state: #ffffff;
		background-color: #2563eb !important;
		box-shadow: inset 0 0 0 9999px #2563eb !important;
		color: #ffffff !important;
	}

	/* ESTADO VACÍO */
	.reservas-container .estado-vacio {
		padding: 42px 16px;
	}

	.reservas-container .estado-vacio-icono {
		margin-bottom: 18px;
		font-size: 2.8rem;
	}

	.reservas-container .estado-vacio h5 {
		margin-bottom: 10px;
		color: #f8fafc !important;
	}

	.reservas-container .mensaje-vacio {
		color: #cbd5e1 !important;
	}

	/* BOTONES */
	.reservas-container .btn-primary,
	.modal-reservas .btn-primary {
		background-color: #2563eb !important;
		border-color: #2563eb !important;
		color: #ffffff !important;
		font-weight: 600;
		border-radius: 7px;
	}

	.reservas-container .btn-primary:hover,
	.modal-reservas .btn-primary:hover {
		background-color: #1d4ed8 !important;
		border-color: #1d4ed8 !important;
	}

	/* MODAL */
	.modal-reservas {
		overflow: hidden;
		background-color: #1e293b !important;
		border: 1px solid #334155 !important;
		border-radius: 10px;
		color: #f8fafc !important;
	}

	.modal-reservas .modal-header,
	.modal-reservas .modal-footer {
		background-color: #1e293b !important;
		border-color: #334155 !important;
	}

	.modal-reservas .modal-title {
		color: #f8fafc !important;
	}

	.modal-reservas .modal-descripcion {
		margin-top: 5px;
		color: #cbd5e1 !important;
		font-size: 0.9rem;
	}

	.modal-reservas .modal-body {
		background-color: #1e293b !important;
	}

	.modal-reservas .form-label {
		color: #cbd5e1 !important;
		font-weight: 500;
	}

	.modal-reservas .form-control,
	.modal-reservas .form-select {
		background-color: #0f172a !important;
		border: 1px solid #475569 !important;
		border-radius: 7px;
		color: #f8fafc !important;
	}

	.modal-reservas .form-control:focus,
	.modal-reservas .form-select:focus {
		border-color: #3b82f6 !important;
		box-shadow: 0 0 0 3px rgb(59 130 246 / 20%);
	}

	.modal-reservas .form-control::placeholder {
		color: #94a3b8 !important;
		opacity: 1;
	}

	.modal-reservas .form-select option {
		background-color: #0f172a;
		color: #f8fafc;
	}

	.modal-reservas .btn-close {
		filter: invert(1) grayscale(100%) brightness(200%);
	}

	/* RESPONSIVE */
	@media (max-width: 768px) {
		.reservas-container {
			padding-top: 1.5rem !important;
			padding-bottom: 1.5rem !important;
		}

		.reservas-container .reservas-encabezado {
			align-items: flex-start !important;
			flex-direction: column;
			gap: 1rem;
		}

		.reservas-container .reservas-encabezado .btn {
			width: 100%;
		}

		.reservas-container .tabla-reservas {
			min-width: 750px;
		}
	}

	/* Fondo blanco para las tarjetas y la tabla de reservas */
	:global(html[data-tema='claro']) .reservas-container .tarjeta-reserva,
	:global(html[data-tema='claro']) .reservas-container .tarjeta-reserva .card-body,
	:global(html[data-tema='claro']) .reservas-container .panel-reservas,
	:global(html[data-tema='claro']) .reservas-container .panel-reservas .card-header,
	:global(html[data-tema='claro']) .reservas-container .panel-reservas .card-body,
	:global(html[data-tema='claro']) .reservas-container .tabla-reservas,
	:global(html[data-tema='claro']) .reservas-container .tabla-reservas tbody,
	:global(html[data-tema='claro']) .reservas-container .tabla-reservas tbody tr,
	:global(html[data-tema='claro']) .reservas-container .tabla-reservas tbody td {
		background-color: #ffffff !important;
		color: #1e293b !important;
	}

	:global(html[data-tema='claro']) .reservas-container .tabla-reservas thead th {
		background-color: #ffffff !important;
		color: #1e293b !important;
	}

	:global(html[data-tema='claro']) .reservas-container .tarjeta-etiqueta,
	:global(html[data-tema='claro']) .reservas-container .tarjeta-valor,
	:global(html[data-tema='claro']) .reservas-container .panel-reservas .card-header h5,
	:global(html[data-tema='claro']) .reservas-container .descripcion-panel,
	:global(html[data-tema='claro']) .reservas-container .estado-vacio h5,
	:global(html[data-tema='claro']) .reservas-container .mensaje-vacio {
		color: #1e293b !important;
	}

	:global(html[data-tema='claro']) .reservas-container .tabla-reservas tbody tr:hover td {
		--bs-table-bg-state: #2563eb !important;
		--bs-table-color-state: #ffffff !important;
		background-color: #2563eb !important;
		box-shadow: inset 0 0 0 9999px #2563eb !important;
		color: #ffffff !important;
	}

	.reservas-container .estado-pendiente {
		background-color: #fff1c2;
		border-color: #f59e0b;
		color: #92400e !important;
	}

	.reservas-container .estado-aprobado {
		background-color: #dcfce7;
		border-color: #16a34a;
		color: #166534 !important;
	}

	.reservas-container .estado-rechazado {
		background-color: #fee2e2;
		border-color: #ef4444;
		color: #b91c1c !important;
	}

	.reservas-container .estado-total {
		background-color: #dbeafe;
		border-color: #3b82f6;
		color: #1d4ed8 !important;
	}
</style>
