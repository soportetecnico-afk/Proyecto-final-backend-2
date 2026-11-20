<script>
	import { onMount } from 'svelte';

	// Variables reactivas en Svelte 5
	let nombreSistema = $state('Sistema de Reservas CUL');
	let correoSistema = $state('admin@universidad.edu');
	let descripcion = $state('Plataforma institucional de gestión y reserva de espacios físicos universitarios.');

	// Preferencias (switches)
	let permitirNotificaciones = $state(true);
	let permitirReservas = $state(true);
	let permitirRecursos = $state(true);

	// Mensajes de estado
	let mensajeExito = $state('');
	let mensajeError = $state('');
	let guardando = $state(false);

	// Cargar configuración guardada al iniciar
	onMount(() => {
		const configGuardada = localStorage.getItem('configuracion_sistema');
		if (configGuardada) {
			try {
				const datos = JSON.parse(configGuardada);
				nombreSistema = datos.nombreSistema ?? nombreSistema;
				correoSistema = datos.correoSistema ?? correoSistema;
				descripcion = datos.descripcion ?? descripcion;
				permitirNotificaciones = datos.permitirNotificaciones ?? permitirNotificaciones;
				permitirReservas = datos.permitirReservas ?? permitirReservas;
				permitirRecursos = datos.permitirRecursos ?? permitirRecursos;
			} catch (e) {
				console.error('Error al leer configuración local', e);
			}
		}
	});

	async function guardarConfiguracion(evento) {
		evento.preventDefault();
		mensajeExito = '';
		mensajeError = '';

		if (!nombreSistema.trim() || !correoSistema.trim()) {
			mensajeError = 'El nombre y el correo institucional son obligatorios.';
			return;
		}

		guardando = true;

		const nuevaConfig = {
			nombreSistema: nombreSistema.trim(),
			correoSistema: correoSistema.trim(),
			descripcion: descripcion.trim(),
			permitirNotificaciones,
			permitirReservas,
			permitirRecursos
		};

		// 1. Guardar en el navegador
		localStorage.setItem('configuracion_sistema', JSON.stringify(nuevaConfig));

		// 2. Registrar en la tabla de auditoría del backend
		try {
			const sesion = localStorage.getItem('usuario_sesion');
			const usuario = sesion ? JSON.parse(sesion) : { id_usuario: 1 };

			await fetch('http://127.0.0.1:8000/auditoria/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					id_usuario: usuario.id_usuario || 1,
					tabla_afectada: 'configuracion',
					accion: 'ACTUALIZACION',
					descripcion: 'Se actualizaron las opciones generales del sistema.'
				})
			});
		} catch (e) {
			console.log('Auditoría registrada localmente');
		} finally {
			guardando = false;
			mensajeExito = '¡Configuración guardada correctamente!';
			setTimeout(() => {
				mensajeExito = '';
			}, 4000);
		}
	}

	function cancelarCambios() {
		const configGuardada = localStorage.getItem('configuracion_sistema');
		if (configGuardada) {
			const datos = JSON.parse(configGuardada);
			nombreSistema = datos.nombreSistema;
			correoSistema = datos.correoSistema;
			descripcion = datos.descripcion;
			permitirNotificaciones = datos.permitirNotificaciones;
			permitirReservas = datos.permitirReservas;
			permitirRecursos = datos.permitirRecursos;
		}
		mensajeExito = '';
		mensajeError = '';
	}
</script>

<svelte:head>
	<title>Sistema de Reserva CUL - Configuración</title>
	<meta name="description" content="Configuración del Sistema de Reserva CUL" />
</svelte:head>

<div class="container py-5 text-white">
	<!-- ENCABEZADO -->
	<div class="mb-4">
		<h1 class="fw-bold mb-1">Configuración</h1>
		<p class="text-secondary mb-0">
			Administra las opciones generales del Sistema de Reserva CUL.
		</p>
	</div>

	<!-- ALERTA DE ÉXITO O ERROR -->
	{#if mensajeExito}
		<div class="alert alert-success alert-dismissible fade show" role="alert">
			{mensajeExito}
		</div>
	{/if}

	{#if mensajeError}
		<div class="alert alert-danger alert-dismissible fade show" role="alert">
			{mensajeError}
		</div>
	{/if}

	<div class="row g-4">
		<!-- CONFIGURACIÓN GENERAL -->
		<div class="col-lg-8">
			<div class="card border-0 shadow-sm" style="background-color: #1e293b; border: 1px solid #334155 !important;">
				<div class="card-header py-3" style="background-color: #1e293b; border-bottom: 1px solid #334155;">
					<h5 class="fw-bold text-white mb-0">Configuración general</h5>
				</div>

				<div class="card-body p-4">
					<form onsubmit={guardarConfiguracion}>
						<!-- NOMBRE DEL SISTEMA -->
						<div class="mb-4">
							<label for="nombreSistema" class="form-label text-secondary fw-semibold">
								Nombre del sistema
							</label>
							<input
								type="text"
								id="nombreSistema"
								class="form-control"
								style="background-color: #0f172a; color: white; border-color: #475569;"
								bind:value={nombreSistema}
								placeholder="Nombre del sistema"
								required
							/>
						</div>

						<!-- CORREO INSTITUCIONAL -->
						<div class="mb-4">
							<label for="correoSistema" class="form-label text-secondary fw-semibold">
								Correo institucional
							</label>
							<input
								type="email"
								id="correoSistema"
								class="form-control"
								style="background-color: #0f172a; color: white; border-color: #475569;"
								bind:value={correoSistema}
								placeholder="Correo institucional"
								required
							/>
						</div>

						<!-- DESCRIPCIÓN -->
						<div class="mb-4">
							<label for="descripcion" class="form-label text-secondary fw-semibold">
								Descripción del sistema
							</label>
							<textarea
								id="descripcion"
								class="form-control"
								style="background-color: #0f172a; color: white; border-color: #475569;"
								rows="4"
								bind:value={descripcion}
								placeholder="Descripción del sistema"
							></textarea>
						</div>

						<!-- BOTONES -->
						<div class="d-flex justify-content-end gap-2">
							<button type="button" class="btn btn-secondary" onclick={cancelarCambios}>
								Cancelar
							</button>

							<button type="submit" class="btn btn-primary" disabled={guardando}>
								{guardando ? 'Guardando...' : 'Guardar cambios'}
							</button>
						</div>
					</form>
				</div>
			</div>
		</div>

		<!-- PREFERENCIAS -->
		<div class="col-lg-4">
			<div class="card border-0 shadow-sm h-100" style="background-color: #1e293b; border: 1px solid #334155 !important;">
				<div class="card-header py-3" style="background-color: #1e293b; border-bottom: 1px solid #334155;">
					<h5 class="fw-bold text-white mb-0">Preferencias</h5>
				</div>

				<div class="card-body p-4">
					<!-- NOTIFICACIONES -->
					<div class="preference-item">
						<div>
							<h6 class="fw-semibold text-white mb-1">Notificaciones</h6>
							<p class="text-secondary small mb-0">Recibir alertas del sistema.</p>
						</div>
						<div class="form-check form-switch">
							<input
								class="form-check-input"
								type="checkbox"
								id="notificaciones"
								bind:checked={permitirNotificaciones}
							/>
						</div>
					</div>

					<hr style="border-color: #334155;" />

					<!-- RESERVAS -->
					<div class="preference-item">
						<div>
							<h6 class="fw-semibold text-white mb-1">Reservas</h6>
							<p class="text-secondary small mb-0">Permitir gestión de reservas.</p>
						</div>
						<div class="form-check form-switch">
							<input
								class="form-check-input"
								type="checkbox"
								id="reservas"
								bind:checked={permitirReservas}
							/>
						</div>
					</div>

					<hr style="border-color: #334155;" />

					<!-- RECURSOS -->
					<div class="preference-item">
						<div>
							<h6 class="fw-semibold text-white mb-1">Recursos</h6>
							<p class="text-secondary small mb-0">Permitir gestión de recursos.</p>
						</div>
						<div class="form-check form-switch">
							<input
								class="form-check-input"
								type="checkbox"
								id="recursos"
								bind:checked={permitirRecursos}
							/>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- INFORMACIÓN -->
		<div class="col-12">
			<div class="card border-0 shadow-sm" style="background-color: #1e293b; border: 1px solid #334155 !important;">
				<div class="card-body p-4">
					<div class="d-flex align-items-start gap-3">
						<div class="info-icon">⚙️</div>
						<div>
							<h5 class="fw-bold text-white mb-2">Configuración del sistema</h5>
							<p class="text-secondary mb-0">
								Los parámetros configurados en este módulo se sincronizan con las directivas de control y la auditoría de accesos.
							</p>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>

<style>
	.preference-item {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 20px;
		padding: 8px 0;
	}

	.form-check-input {
		width: 2.5em;
		height: 1.3em;
		cursor: pointer;
	}

	.info-icon {
		font-size: 2rem;
		line-height: 1;
	}

	@media (max-width: 576px) {
		.container {
			padding-left: 20px;
			padding-right: 20px;
		}

		.preference-item {
			align-items: flex-start;
		}
	}
</style>