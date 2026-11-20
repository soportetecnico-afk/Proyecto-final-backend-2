<script>
	import { onMount } from 'svelte';

	const API_BASE = 'http://127.0.0.1:8000';

	let reservas = $state([]);
	let espacios = $state([]);
	let cargando = $state(true);
	let error = $state(null);
	let usuarioSesion = $state(null);
	let tokenAcceso = '';
	let puedeCrearReserva = $state(false);
	let mostrarFormularioReserva = $state(false);
	let puedeGestionarReservas = $state(false);
	let reservaSeleccionada = $state(null);
	let mostrarFormularioRechazo = $state(false);
	let motivoRechazo = $state('');
	let procesandoDecision = $state(false);
	let notificacion = $state({ tipo: '', mensaje: '' });
	let temporizadorNotificacion;
	let filtroReservas = $state('todas');

	function mostrarNotificacion(tipo, mensaje) {
		notificacion = { tipo, mensaje };
		if (temporizadorNotificacion) clearTimeout(temporizadorNotificacion);
		temporizadorNotificacion = setTimeout(() => {
			notificacion = { tipo: '', mensaje: '' };
		}, 5500);
	}

	function cerrarNotificacion() {
		if (temporizadorNotificacion) clearTimeout(temporizadorNotificacion);
		notificacion = { tipo: '', mensaje: '' };
	}

	function normalizar(valor) {
		return String(valor ?? '')
			.normalize('NFD')
			.replace(/[\u0300-\u036f]/g, '')
			.trim()
			.toLowerCase();
	}

	function esDocente() {
		return Number(usuarioSesion?.id_rol) === 5 || normalizar(
			usuarioSesion?.nombre_rol ?? usuarioSesion?.rol
		) === 'docente';
	}

	function comprobarPermisos() {
		const idRol = Number(usuarioSesion?.id_rol);
		const nombreRol = normalizar(usuarioSesion?.nombre_rol ?? usuarioSesion?.rol);
		puedeGestionarReservas = [1, 3].includes(idRol) || ['administrador', 'decano'].includes(nombreRol);
		// Los tres perfiles oficiales pueden crear solicitudes de reserva.
		puedeCrearReserva = [1, 3, 5].includes(idRol) || ['administrador', 'decano', 'docente'].includes(nombreRol);
	}

	let nuevaReserva = $state({
		id_usuario: null,
		id_espacio: '',
		id_tipo_evento: 1,
		fecha_reserva: '',
		hora_inicio: '',
		hora_fin: '',
		cantidad_asistentes: 1
	});

	// El usuario elige la duración; la hora final se calcula para conservar
	// la compatibilidad con el modelo y la base de datos actuales.
	let duracionHoras = $state('2');
	let horaFinCalculada = $derived(calcularHoraFin(nuevaReserva.hora_inicio, duracionHoras));

	function calcularHoraFin(horaInicio, duracion) {
		if (!horaInicio || !duracion) return '';
		const [horas, minutos] = horaInicio.split(':').map(Number);
		if (!Number.isInteger(horas) || !Number.isInteger(minutos)) return '';
		const total = horas * 60 + minutos + Number(duracion) * 60;
		if (total >= 24 * 60) return '';
		return `${String(Math.floor(total / 60)).padStart(2, '0')}:${String(total % 60).padStart(2, '0')}`;
	}

	// Capacidad máxima del espacio seleccionado, consultada desde /espacios/.
	let espacioSeleccionado = $derived(
		espacios.find((espacio) => Number(espacio.id_espacio ?? espacio.id) === Number(nuevaReserva.id_espacio)) ?? null
	);
	let capacidadMaxima = $derived(
		Number(espacioSeleccionado?.capacidad_aforo ?? espacioSeleccionado?.capacidad ?? 0)
	);
	let excedeCapacidad = $derived(
		capacidadMaxima > 0 && Number(nuevaReserva.cantidad_asistentes) > capacidadMaxima
	);

	// Devuelve la fecha local en formato YYYY-MM-DD (el formato que exige input[type=date]).
	function obtenerFechaLocalISO() {
		const ahora = new Date();
		const anio = ahora.getFullYear();
		const mes = String(ahora.getMonth() + 1).padStart(2, '0');
		const dia = String(ahora.getDate()).padStart(2, '0');
		return `${anio}-${mes}-${dia}`;
	}

	// Abre el selector nativo en navegadores compatibles; si no existe showPicker,
	// el input conserva su comportamiento nativo y permite escribir el valor.
	function abrirSelectorFechaHora(event) {
		const input = event.currentTarget;
		if (typeof input.showPicker === 'function') {
			try {
				input.showPicker();
			} catch {
				// Algunos navegadores bloquean showPicker; se mantiene el control nativo.
			}
		}
	}

	let totalReservas = $derived(reservas.length);
	let pendientes = $derived(reservas.filter((r) => normalizar(r.estado_reserva) === 'pendiente').length);
	let aprobadas = $derived(reservas.filter((r) => ['aprobada', 'aprobado', 'confirmada', 'confirmado'].includes(normalizar(r.estado_reserva))).length);
	let rechazadas = $derived(reservas.filter((r) => ['rechazada', 'rechazado'].includes(normalizar(r.estado_reserva))).length);
	let reservasFiltradas = $derived(
		filtroReservas === 'pendientes'
			? reservas.filter((r) => normalizar(r.estado_reserva) === 'pendiente')
			: filtroReservas === 'aprobadas'
				? reservas.filter((r) => ['aprobada', 'aprobado', 'confirmada', 'confirmado'].includes(normalizar(r.estado_reserva)))
				: filtroReservas === 'rechazadas'
					? reservas.filter((r) => ['rechazada', 'rechazado'].includes(normalizar(r.estado_reserva)))
					: reservas
	);

	function encabezadosAutenticados() {
		if (!tokenAcceso) throw new Error('Tu sesión no está autenticada. Cierra sesión e ingresa nuevamente.');
		return { Authorization: `Bearer ${tokenAcceso}` };
	}

	onMount(async () => {
		try {
			const guardado = localStorage.getItem('usuario_sesion');
			tokenAcceso = localStorage.getItem('token_acceso') ?? '';
			if (!guardado || !tokenAcceso) {
				localStorage.removeItem('usuario_sesion');
				localStorage.removeItem('token_acceso');
				window.location.replace('/login');
				return;
			}
			usuarioSesion = JSON.parse(guardado);
			if (!usuarioSesion?.id_usuario || !usuarioSesion?.id_rol) {
				throw new Error('La información de tu sesión está incompleta. Inicia sesión nuevamente.');
			}
			nuevaReserva.id_usuario = usuarioSesion.id_usuario;
			comprobarPermisos();
			await cargarDatos();
		} catch (e) {
			error = e.message;
			cargando = false;
		}
	});

	async function cargarDatos() {
		cargando = true;
		error = null;
		try {
			const headers = encabezadosAutenticados();
			const [resRes, resEsp] = await Promise.all([
				fetch(`${API_BASE}/reservas/`, { headers }),
				fetch(`${API_BASE}/espacios/`, { headers })
			]);

			if (resRes.status === 401) {
				localStorage.removeItem('usuario_sesion');
				localStorage.removeItem('token_acceso');
				window.location.replace('/login');
				return;
			}
			if (!resRes.ok) {
				const detalle = await resRes.json().catch(() => ({}));
				throw new Error(detalle.detail || 'No se pudieron obtener las reservas.');
			}
			reservas = await resRes.json();
			if (resEsp.ok) {
				const datosEspacios = await resEsp.json();
				espacios = Array.isArray(datosEspacios)
					? datosEspacios
					: datosEspacios?.data ?? datosEspacios?.espacios ?? [];
			}
		} catch (e) {
			error = e.message || 'Error al consultar las reservas.';
		} finally {
			cargando = false;
		}
	}

	async function guardarReserva() {
		comprobarPermisos();
		if (!puedeCrearReserva) {
			mostrarNotificacion('advertencia', 'Tu perfil no tiene permiso para crear reservas desde este módulo.');
			return;
		}
		if (!nuevaReserva.id_espacio || !nuevaReserva.fecha_reserva || !nuevaReserva.hora_inicio || !duracionHoras) {
			mostrarNotificacion('advertencia', 'Completa todos los campos requeridos para registrar la reserva.');
			return;
		}
		if (nuevaReserva.fecha_reserva < obtenerFechaLocalISO()) {
			mostrarNotificacion('advertencia', 'La fecha de la reserva no puede ser anterior al día de hoy.');
			return;
		}
		if (!horaFinCalculada) {
			mostrarNotificacion('advertencia', 'La duración seleccionada termina después de la medianoche. Selecciona una hora de inicio más temprana.');
			return;
		}
		if (!Number.isInteger(Number(nuevaReserva.cantidad_asistentes)) || Number(nuevaReserva.cantidad_asistentes) < 1) {
			mostrarNotificacion('advertencia', 'La cantidad de asistentes debe ser un número entero mayor que cero.');
			return;
		}
		if (capacidadMaxima > 0 && Number(nuevaReserva.cantidad_asistentes) > capacidadMaxima) {
			mostrarNotificacion(
				'advertencia',
				`No es posible crear la reserva: el público supera la capacidad permitida de «${espacioSeleccionado?.nombre_espacio ?? espacioSeleccionado?.nombre ?? 'este espacio'}». Capacidad máxima: ${capacidadMaxima} personas.`
			);
			return;
		}
		try {
			const res = await fetch(`${API_BASE}/reservas/`, {
				method: 'POST',
				headers: { ...encabezadosAutenticados(), 'Content-Type': 'application/json' },
				body: JSON.stringify({ ...nuevaReserva, hora_fin: horaFinCalculada })
			});
			if (!res.ok) {
				const detalle = await res.json().catch(() => ({}));
				throw new Error(detalle.detail || 'Error al guardar la reserva.');
			}
			mostrarFormularioReserva = false;
			mostrarNotificacion('exito', 'La reserva fue enviada exitosamente y quedó pendiente de aprobación.');
			nuevaReserva = {
				id_usuario: usuarioSesion.id_usuario,
				id_espacio: '', id_tipo_evento: 1, fecha_reserva: '',
				hora_inicio: '', hora_fin: '', cantidad_asistentes: 1
			};
			duracionHoras = '2';
			await cargarDatos();
		} catch (e) {
			mostrarNotificacion('error', 'No fue posible guardar la reserva. Inténtalo nuevamente.');
		}
	}

	function abrirDetalleReserva(reserva) {
		reservaSeleccionada = reserva;
		mostrarFormularioRechazo = false;
		motivoRechazo = '';
	}

	function cerrarDetalleReserva() {
		if (procesandoDecision) return;
		reservaSeleccionada = null;
		mostrarFormularioRechazo = false;
		motivoRechazo = '';
	}

	async function resolverReserva(decision) {
		if (!puedeGestionarReservas || !reservaSeleccionada || procesandoDecision) return;

		const motivo = motivoRechazo.trim();
		if (decision === 'Rechazada' && !motivo) {
			mostrarNotificacion('advertencia', 'Debes escribir el motivo por el cual se rechaza la reserva.');
			return;
		}

		procesandoDecision = true;
		error = null;
		try {
			const res = await fetch(
				`${API_BASE}/reservas/${reservaSeleccionada.id_reserva}/decision`,
				{
					method: 'PATCH',
					headers: { ...encabezadosAutenticados(), 'Content-Type': 'application/json' },
					body: JSON.stringify({
						decision,
						motivo_rechazo: decision === 'Rechazada' ? motivo : null
					})
				}
			);

			const respuesta = await res.json().catch(() => ({}));
			if (!res.ok) throw new Error(respuesta.detail || 'No fue posible procesar la solicitud.');

			procesandoDecision = false;
			cerrarDetalleReserva();
			await cargarDatos();
			mostrarNotificacion(
				'exito',
				decision === 'Confirmada'
					? 'La reserva fue aprobada correctamente.'
					: 'La reserva fue rechazada y el motivo quedó registrado.'
			);
		} catch (e) {
			mostrarNotificacion('error', 'No fue posible registrar la decisión. Inténtalo nuevamente.');
		} finally {
			procesandoDecision = false;
		}
	}

	function esPendiente(estado) {
		return normalizar(estado) === 'pendiente';
	}

	function esRechazada(estado) {
		return ['rechazada', 'rechazado'].includes(normalizar(estado));
	}

	function esAprobada(estado) {
		return ['aprobada', 'aprobado', 'confirmada', 'confirmado'].includes(normalizar(estado));
	}

	function obtenerNombreEspacio(reserva) {
		// Algunas respuestas de la API incluyen el nombre directamente en la reserva.
		const nombreDirecto = reserva?.nombre_espacio
			?? reserva?.espacio_nombre
			?? reserva?.nombre_del_espacio
			?? reserva?.espacio?.nombre_espacio
			?? reserva?.espacio?.nombre
			?? reserva?.espacio?.descripcion;
		if (typeof nombreDirecto === 'string' && nombreDirecto.trim()) return nombreDirecto.trim();

		// Si la reserva solo trae el ID, se busca el nombre en el catálogo /espacios/.
		const idEspacio = reserva?.id_espacio
			?? reserva?.espacio_id
			?? reserva?.espacio?.id_espacio
			?? reserva?.espacio?.id;
		const listaEspacios = Array.isArray(espacios)
			? espacios
			: Array.isArray(espacios?.data)
				? espacios.data
				: Array.isArray(espacios?.espacios)
					? espacios.espacios
					: [];
		const espacio = listaEspacios.find((item) =>
			Number(item?.id_espacio ?? item?.espacio_id ?? item?.id) === Number(idEspacio)
		);
		const nombre = espacio?.nombre_espacio
			?? espacio?.espacio_nombre
			?? espacio?.nombre
			?? espacio?.descripcion;
		return nombre || `Nombre del espacio no disponible (ID ${idEspacio ?? 'N/D'})`;
	}

	function obtenerComentarioReserva(reserva) {
		if (esRechazada(reserva?.estado_reserva)) {
			return reserva?.motivo_rechazo || reserva?.detalle_rechazo || 'Motivo no registrado';
		}
		if (esAprobada(reserva?.estado_reserva)) return 'Aprobada';
		return '—';
	}

	function etiquetaEstado(estado) {
		const valor = normalizar(estado);
		if (['aprobada', 'aprobado', 'confirmada', 'confirmado'].includes(valor)) return 'Confirmada';
		if (valor === 'pendiente') return 'Pendiente';
		if (['rechazada', 'rechazado', 'cancelada', 'cancelado'].includes(valor)) return 'Rechazada';
		return estado || 'Sin estado';
	}

	function claseEstado(estado) {
		const valor = normalizar(estado);
		if (['aprobada', 'aprobado', 'confirmada', 'confirmado'].includes(valor)) return 'estado-aprobado';
		if (valor === 'pendiente') return 'estado-pendiente';
		return 'estado-rechazado';
	}
</script>

<svelte:head>
	<title>Sistema de Reservas CUL - Reservas</title>
	<meta name="description" content="Gestión de reservas de espacios universitarios" />
</svelte:head>

<div class="reservas-container container py-5">
	{#if notificacion.mensaje}
		<div class="notificacion-pagina notificacion-{notificacion.tipo}" role={notificacion.tipo === 'error' ? 'alert' : 'status'} aria-live="polite">
			<span class="notificacion-icono" aria-hidden="true">{notificacion.tipo === 'exito' ? '✓' : notificacion.tipo === 'advertencia' ? '!' : '×'}</span>
			<p>{notificacion.mensaje}</p>
			<button type="button" aria-label="Cerrar notificación" onclick={cerrarNotificacion}>×</button>
		</div>
	{/if}
	<!-- ENCABEZADO -->
	<div class="d-flex justify-content-between align-items-center reservas-encabezado mb-4">
		<div>
			<h1 class="fw-bold mb-1">Reservas</h1>
			<p class="descripcion mb-0">Gestiona las reservas de los espacios universitarios.</p>
		</div>
		{#if puedeCrearReserva}
			<button type="button" class="btn btn-primary btn-nueva-reserva" onclick={() => (mostrarFormularioReserva = !mostrarFormularioReserva)}>
				{mostrarFormularioReserva ? '× Cancelar' : '+ Nueva reserva'}
			</button>
		{/if}
	</div>

	{#if puedeCrearReserva && mostrarFormularioReserva}
		<div class="card formulario-nueva-reserva mb-4">
			<div class="card-header">
				<h5 class="fw-bold mb-1">Registrar nueva reserva</h5>
				<p class="descripcion-panel mb-0">Completa los datos para enviar la solicitud. La reserva quedará pendiente de aprobación.</p>
			</div>
			<div class="card-body">
				<form onsubmit={(event) => { event.preventDefault(); guardarReserva(); }}>
					<div class="row g-3">
						<div class="col-12 col-md-6">
							<label class="form-label" for="espacioReserva">Espacio <span aria-hidden="true">*</span></label>
							<select id="espacioReserva" class="form-select" bind:value={nuevaReserva.id_espacio} required>
								<option value="">Selecciona un espacio</option>
								{#each espacios as espacio}
									<option value={String(espacio.id_espacio ?? espacio.id)}>{espacio.nombre_espacio ?? espacio.nombre ?? espacio.descripcion ?? `Espacio ${espacio.id_espacio ?? espacio.id}`}</option>
								{/each}
							</select>
							{#if espacios.length === 0}<small class="ayuda-formulario">No hay espacios disponibles para seleccionar.</small>{/if}
						</div>
						<div class="col-12 col-md-6">
							<label class="form-label" for="fechaReserva">Fecha <span aria-hidden="true">*</span></label>
							<input id="fechaReserva" class="form-control campo-fecha-hora" type="date" bind:value={nuevaReserva.fecha_reserva} min={obtenerFechaLocalISO()} onclick={abrirSelectorFechaHora} required />
						</div>
						<div class="col-12 col-md-4">
							<label class="form-label" for="horaInicioReserva">Hora de inicio <span aria-hidden="true">*</span></label>
							<input id="horaInicioReserva" class="form-control campo-fecha-hora" type="time" step="60" bind:value={nuevaReserva.hora_inicio} onclick={abrirSelectorFechaHora} required />
						</div>
						<div class="col-12 col-md-4">
							<label class="form-label" for="duracionReserva">Duración del evento <span aria-hidden="true">*</span></label>
							<select id="duracionReserva" class="form-select" bind:value={duracionHoras} required>
								{#each [1, 2, 3, 4, 5, 6, 7, 8] as horas}
									<option value={String(horas)}>{horas} {horas === 1 ? 'hora' : 'horas'}</option>
								{/each}
							</select>
							{#if horaFinCalculada}<small class="ayuda-formulario">Finaliza a las {horaFinCalculada}.</small>{/if}
						</div>
						<div class="col-12 col-md-4">
							<label class="form-label" for="asistentesReserva">Cantidad de asistentes <span aria-hidden="true">*</span></label>
							<input id="asistentesReserva" class="form-control" type="number" min="1" max={capacidadMaxima || undefined} bind:value={nuevaReserva.cantidad_asistentes} required />
							{#if capacidadMaxima > 0}
								<small class="ayuda-formulario">Aforo máximo del espacio: {capacidadMaxima} personas.</small>
							{/if}
						</div>
					</div>
					<div class="aviso-formulario mt-3">La solicitud se registrará a tu nombre y quedará en estado <strong>Pendiente</strong> hasta que el administrador la revise.</div>
					<div class="d-flex justify-content-end gap-2 mt-3">
						<button type="button" class="btn btn-outline-light" onclick={() => (mostrarFormularioReserva = false)}>Cancelar</button>
						<button type="submit" class="btn btn-primary" disabled={cargando || espacios.length === 0 || excedeCapacidad}>Enviar solicitud</button>
					</div>
				</form>
			</div>
		</div>
	{/if}

	<!-- TARJETAS DE ESTADO: funcionan como filtros del listado -->
	<div class="row g-4 tarjetas-reservas mb-4">
		<div class="col-12 col-sm-6 col-xl-3">
			<button type="button" class="card tarjeta-reserva tarjeta-filtro w-100 text-start {filtroReservas === 'pendientes' ? 'filtro-activo' : ''}"
				aria-pressed={filtroReservas === 'pendientes'} onclick={() => (filtroReservas = 'pendientes')}>
				<div class="card-body">
					<div class="tarjeta-superior"><span class="tarjeta-etiqueta">Pendientes</span><span class="tarjeta-icono icono-pendiente" aria-hidden="true">◷</span></div>
					<h2 class="tarjeta-valor">{pendientes}</h2>
					<span class="estado-reserva estado-pendiente">Pendientes de aprobación</span>
				</div>
			</button>
		</div>
		<div class="col-12 col-sm-6 col-xl-3">
			<button type="button" class="card tarjeta-reserva tarjeta-filtro w-100 text-start {filtroReservas === 'aprobadas' ? 'filtro-activo' : ''}"
				aria-pressed={filtroReservas === 'aprobadas'} onclick={() => (filtroReservas = 'aprobadas')}>
				<div class="card-body">
					<div class="tarjeta-superior"><span class="tarjeta-etiqueta">Aprobadas</span><span class="tarjeta-icono icono-aprobado" aria-hidden="true">✓</span></div>
					<h2 class="tarjeta-valor">{aprobadas}</h2>
					<span class="estado-reserva estado-aprobado">Reservas confirmadas</span>
				</div>
			</button>
		</div>
		<div class="col-12 col-sm-6 col-xl-3">
			<button type="button" class="card tarjeta-reserva tarjeta-filtro w-100 text-start {filtroReservas === 'rechazadas' ? 'filtro-activo' : ''}"
				aria-pressed={filtroReservas === 'rechazadas'} onclick={() => (filtroReservas = 'rechazadas')}>
				<div class="card-body">
					<div class="tarjeta-superior"><span class="tarjeta-etiqueta">Rechazadas</span><span class="tarjeta-icono icono-rechazado" aria-hidden="true">×</span></div>
					<h2 class="tarjeta-valor">{rechazadas}</h2>
					<span class="estado-reserva estado-rechazado">Reservas no aprobadas</span>
				</div>
			</button>
		</div>
		<div class="col-12 col-sm-6 col-xl-3">
			<button type="button" class="card tarjeta-reserva tarjeta-filtro w-100 text-start {filtroReservas === 'todas' ? 'filtro-activo' : ''}"
				aria-pressed={filtroReservas === 'todas'} onclick={() => (filtroReservas = 'todas')}>
				<div class="card-body">
					<div class="tarjeta-superior"><span class="tarjeta-etiqueta">Todas las reservas</span><span class="tarjeta-icono icono-total" aria-hidden="true">▤</span></div>
					<h2 class="tarjeta-valor">{totalReservas}</h2>
					<span class="estado-reserva estado-total">Consulta todas las reservas</span>
				</div>
			</button>
		</div>
	</div>

	<!-- TABLA DE RESERVAS -->
	<div class="card panel-reservas">
		<div class="card-header d-flex justify-content-between align-items-center">
			<div>
				<h5 class="fw-bold mb-1">{filtroReservas === 'pendientes' ? 'Reservas pendientes' : filtroReservas === 'aprobadas' ? 'Reservas aprobadas' : filtroReservas === 'rechazadas' ? 'Reservas rechazadas' : 'Todas las reservas'}</h5>
				<p class="descripcion-panel mb-0">{esDocente() ? "Consulta únicamente las reservas que has realizado." : "Consulta las solicitudes de reserva."}</p>
			</div>
			<div class="d-flex align-items-center gap-2">
				<button type="button" class="btn btn-sm btn-outline-secondary text-white" onclick={cargarDatos}>
					🔄 Actualizar
				</button>
			</div>
		</div>

		<div class="card-body">
			{#if error}
				<div class="alert alert-danger m-3">
					<strong>No fue posible cargar las reservas.</strong> Inténtalo nuevamente.
				</div>
			{/if}

			<div class="table-responsive">
				<table class="table-hover tabla-reservas mb-0 table align-middle">
					<thead>
						<tr>
							<th scope="col">#</th>
							{#if puedeGestionarReservas}<th scope="col">Solicitante</th>{/if}
							<th scope="col">Espacio</th>
							<th scope="col">Fecha</th>
							<th scope="col">Horario</th>
							<th scope="col">Asistentes</th>
							<th scope="col">Estado</th>
							<th scope="col">Comentario</th>
							{#if puedeGestionarReservas}<th scope="col">Acciones</th>{/if}
						</tr>
					</thead>

					<tbody>
						{#if cargando}
							<tr>
								<td colspan={puedeGestionarReservas ? 9 : 7} class="text-center py-4 text-muted">
									Cargando reservas...
								</td>
							</tr>
						{:else if reservasFiltradas.length === 0}
							<tr>
								<td colspan={puedeGestionarReservas ? 9 : 7}>
									<div class="estado-vacio text-center">
										<div class="estado-vacio-icono" aria-hidden="true">📅</div>
										<h5 class="fw-bold">{esDocente() ? "Todavía no has realizado reservas" : "No hay reservas cargadas"}</h5>
										<p class="mensaje-vacio mb-0">
											{esDocente() ? "Cuando registres una reserva, aparecerá en este listado." : "Las reservas aparecerán aquí cuando haya solicitudes registradas."}
										</p>
									</div>
								</td>
							</tr>
						{:else}
							{#each reservasFiltradas as r, index}
								<tr>
									<td class="fw-semibold">{index + 1}</td>
									{#if puedeGestionarReservas}<td>{r.nombre_solicitante || `Usuario #${r.id_usuario}`}</td>{/if}
									<td>{obtenerNombreEspacio(r)}</td>
									<td>{r.fecha_reserva}</td>
									<td>{r.hora_inicio} - {r.hora_fin}</td>
									<td>{r.cantidad_asistentes} personas</td>
									<td>
										<span class="estado-reserva {claseEstado(r.estado_reserva)}">{etiquetaEstado(r.estado_reserva)}</span>
									</td>
							<td class="detalle-rechazo">
								{obtenerComentarioReserva(r)}
							</td>
									{#if puedeGestionarReservas}
										<td>
										<button type="button" class="btn btn-sm btn-outline-info"
											onclick={() => abrirDetalleReserva(r)}>
											Revisar
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


<!-- Modal de revisión para Administrador y Decano -->
{#if puedeGestionarReservas && reservaSeleccionada}
	<div class="modal-revision-fondo" role="presentation">
		<dialog open class="modal-revision" aria-labelledby="tituloRevision">
			<header class="modal-revision-header">
				<div>
					<h2 id="tituloRevision">Revisar reserva #{reservaSeleccionada.id_reserva}</h2>
					<p>Consulta la solicitud y decide si se aprueba o se rechaza.</p>
				</div>
				<button class="btn-cerrar-revision" type="button" aria-label="Cerrar" onclick={cerrarDetalleReserva}>×</button>
			</header>
			<div class="modal-revision-body">
				<div class="detalle-reserva-grid">
					<div><span>Solicitante</span><strong>{reservaSeleccionada.nombre_solicitante || `Usuario #${reservaSeleccionada.id_usuario}`}</strong>{#if reservaSeleccionada.correo_solicitante}<small>{reservaSeleccionada.correo_solicitante}</small>{/if}</div>
					<div><span>Espacio</span><strong>{obtenerNombreEspacio(reservaSeleccionada)}</strong></div>
					<div><span>Fecha</span><strong>{reservaSeleccionada.fecha_reserva}</strong></div>
					<div><span>Horario</span><strong>{reservaSeleccionada.hora_inicio} - {reservaSeleccionada.hora_fin}</strong></div>
					<div><span>Asistentes</span><strong>{reservaSeleccionada.cantidad_asistentes} personas</strong></div>
					<div><span>Estado actual</span><strong><span class="estado-reserva {claseEstado(reservaSeleccionada.estado_reserva)}">{etiquetaEstado(reservaSeleccionada.estado_reserva)}</span></strong></div>
				</div>
				{#if normalizar(reservaSeleccionada.estado_reserva) === 'rechazada' && reservaSeleccionada.motivo_rechazo}
					<div class="motivo-registrado">
						<strong>Motivo del rechazo</strong>
						<p>{reservaSeleccionada.motivo_rechazo}</p>
					</div>
				{/if}
				{#if esPendiente(reservaSeleccionada.estado_reserva)}
					{#if mostrarFormularioRechazo}
						<div class="formulario-rechazo">
							<label for="motivoRechazo" class="form-label">Motivo del rechazo <span aria-hidden="true">*</span></label>
							<textarea id="motivoRechazo" class="form-control" rows="4" bind:value={motivoRechazo}
								maxlength="1000" placeholder="Explica por qué no se puede aprobar esta reserva..." required></textarea>
							<small>El motivo quedará guardado y podrá consultarse posteriormente.</small>
						</div>
					{/if}
				{:else}
					<div class="aviso-decision">Esta reserva ya fue gestionada. No es posible cambiar nuevamente su decisión desde esta pantalla.</div>
				{/if}
			</div>
			<footer class="modal-revision-footer">
				<button type="button" class="btn btn-secondary" onclick={cerrarDetalleReserva} disabled={procesandoDecision}>Cerrar</button>
				{#if esPendiente(reservaSeleccionada.estado_reserva)}
					{#if mostrarFormularioRechazo}
						<button type="button" class="btn btn-danger" onclick={() => resolverReserva('Rechazada')} disabled={procesandoDecision || !motivoRechazo.trim()}>
							{procesandoDecision ? 'Procesando...' : 'Confirmar rechazo'}
						</button>
						<button type="button" class="btn btn-outline-light" onclick={() => { mostrarFormularioRechazo = false; motivoRechazo = ''; }} disabled={procesandoDecision}>Volver</button>
					{:else}
						<button type="button" class="btn btn-danger" onclick={() => mostrarFormularioRechazo = true}>Rechazar</button>
						<button type="button" class="btn btn-success" onclick={() => resolverReserva('Confirmada')} disabled={procesandoDecision}>
							{procesandoDecision ? 'Procesando...' : 'Aprobar reserva'}
						</button>
					{/if}
				{/if}
			</footer>
		</dialog>
	</div>
{/if}

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

	.reservas-container .tarjeta-filtro {
		font: inherit;
		cursor: pointer;
		transition: border-color 0.18s ease, transform 0.18s ease, box-shadow 0.18s ease;
	}

	.reservas-container .tarjeta-filtro:hover {
		border-color: #60a5fa !important;
		transform: translateY(-2px);
	}

	.reservas-container .tarjeta-filtro.filtro-activo {
		border: 2px solid #3b82f6 !important;
		box-shadow: 0 0 0 2px rgb(59 130 246 / 12%);
	}

	.reservas-container .tarjeta-filtro:focus-visible {
		outline: 2px solid #93c5fd;
		outline-offset: 3px;
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

	.reservas-container .icono-rechazado {
		background-color: rgb(239 68 68 / 15%);
		color: #f87171 !important;
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

	.reservas-container .estado-rechazado {
		background-color: rgb(239 68 68 / 12%);
		border-color: rgb(239 68 68 / 25%);
		color: #fca5a5 !important;
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

	/* NOTIFICACIÓN FLOTANTE: independiente del contenido de la página */
	.notificacion-pagina {
		position: fixed; top: 20px; right: 20px; z-index: 5000;
		display: flex; align-items: center; gap: 12px;
		width: min(520px, calc(100vw - 40px)); margin: 0; padding: 14px 16px;
		border: 1px solid; border-radius: 10px;
		box-shadow: 0 14px 38px rgb(0 0 0 / 42%);
		backdrop-filter: blur(10px);
		animation: aparecer-notificacion .22s ease-out;
	}
	.notificacion-pagina p { flex: 1; margin: 0; font-size: .92rem; line-height: 1.45; }
	.notificacion-pagina > button { border: 0; background: transparent; color: inherit; font-size: 1.35rem; line-height: 1; opacity: .8; cursor: pointer; }
	.notificacion-icono { display: grid; width: 28px; height: 28px; flex: 0 0 28px; place-items: center; border: 1px solid currentColor; border-radius: 50%; font-weight: 800; }
	.notificacion-exito { color: #86efac; background: #123629; border-color: #166534; }
	.notificacion-error { color: #fca5a5; background: #451a1a; border-color: #b91c1c; }
	.notificacion-advertencia { color: #fcd34d; background: #422006; border-color: #a16207; }
	@keyframes aparecer-notificacion { from { opacity: 0; transform: translateY(-6px); } to { opacity: 1; transform: translateY(0); } }

	/* FORMULARIO DE CREACIÓN DE RESERVAS */
	.reservas-container .formulario-nueva-reserva {
		background: #1e293b !important;
		border: 1px solid #334155 !important;
		border-radius: 10px;
		color: #f8fafc !important;
	}
	.reservas-container .formulario-nueva-reserva .card-header {
		padding: 18px 20px;
		background: #1e293b !important;
		border-bottom: 1px solid #334155 !important;
		color: #f8fafc !important;
	}
	.reservas-container .formulario-nueva-reserva .card-body { padding: 20px; }
	.reservas-container .formulario-nueva-reserva .form-label { display: block; margin-bottom: 7px; color: #e2e8f0; font-weight: 600; }
	.reservas-container .formulario-nueva-reserva .form-control,
	.reservas-container .formulario-nueva-reserva .form-select {
		min-height: 42px;
		background-color: #0f172a;
		border: 1px solid #475569;
		color: #f8fafc;
	}
	/* Mantiene activos los controles nativos de calendario y reloj en Chrome/Edge. */
	.reservas-container .formulario-nueva-reserva input.campo-fecha-hora {
		position: relative;
		z-index: 2;
		pointer-events: auto !important;
		appearance: auto;
		-webkit-appearance: auto;
		color-scheme: dark;
		cursor: pointer;
		min-height: 42px;
		touch-action: manipulation;
	}
	.reservas-container .formulario-nueva-reserva input.campo-fecha-hora::-webkit-calendar-picker-indicator {
		opacity: 1;
		cursor: pointer;
		filter: invert(1);
		padding: 4px;
	}
	.reservas-container .formulario-nueva-reserva .form-control:focus,
	.reservas-container .formulario-nueva-reserva .form-select:focus {
		background-color: #0f172a;
		border-color: #3b82f6;
		color: #f8fafc;
		box-shadow: 0 0 0 3px rgb(59 130 246 / 18%);
	}
	.reservas-container .ayuda-formulario { display: block; margin-top: 6px; color: #fbbf24; }
	.reservas-container .aviso-formulario { padding: 12px 14px; border: 1px solid #334155; border-radius: 8px; background: #172338; color: #cbd5e1; font-size: .88rem; }
	.reservas-container .btn-nueva-reserva { white-space: nowrap; }

	/* MODAL DE REVISIÓN DE RESERVAS */
	.modal-revision-fondo {
		position: fixed; inset: 0; z-index: 2000; display: flex;
		align-items: center; justify-content: center; padding: 20px;
		background: rgb(2 6 23 / 78%); backdrop-filter: blur(3px);
	}
	.modal-revision {
		position: relative; margin: 0; padding: 0; max-width: none; width: min(720px, 100%); max-height: min(90vh, 850px); overflow-y: auto;
		border: 1px solid #475569; border-radius: 14px;
		background: #1e293b; color: #f8fafc; box-shadow: 0 24px 70px rgb(0 0 0 / 45%);
	}
	.modal-revision-header, .modal-revision-footer {
		display: flex; align-items: center; justify-content: space-between;
		gap: 12px; padding: 18px 22px; border-bottom: 1px solid #334155;
	}
	.modal-revision-header h2 { margin: 0; font-size: 1.2rem; color: #f8fafc; }
	.modal-revision-header p { margin: 6px 0 0; color: #cbd5e1; font-size: .88rem; }
	.btn-cerrar-revision { border: 0; background: transparent; color: #cbd5e1; font-size: 1.8rem; line-height: 1; cursor: pointer; }
	.modal-revision-body { padding: 22px; }
	.detalle-reserva-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
	.detalle-reserva-grid > div { padding: 13px; border: 1px solid #334155; border-radius: 9px; background: #172338; }
	.detalle-reserva-grid span:not(.estado-reserva) { display: block; margin-bottom: 6px; color: #94a3b8; font-size: .78rem; }
	.detalle-reserva-grid strong { color: #f8fafc; font-size: .92rem; }
	.detalle-reserva-grid small { display: block; margin-top: 5px; color: #94a3b8; font-size: .78rem; }
	.motivo-registrado, .aviso-decision { margin-top: 18px; padding: 14px; border-radius: 9px; border: 1px solid #475569; background: #172338; }
	.motivo-registrado strong { color: #fca5a5; }
	.motivo-registrado p { margin: 7px 0 0; color: #e2e8f0; white-space: pre-wrap; }
	.aviso-decision { color: #cbd5e1; font-size: 1rem; font-weight: 700; }
	:global(html[data-tema='claro']) .modal-revision .aviso-decision { color: #334155 !important; }
	:global(html[data-tema='claro']) .modal-revision .detalle-reserva-grid > div,
	:global(html[data-tema='claro']) .modal-revision .motivo-registrado,
	:global(html[data-tema='claro']) .modal-revision .aviso-decision {
		border-color: #dbeafe !important;
		background: #ffffff !important;
	}
	.formulario-rechazo { margin-top: 18px; }
	.formulario-rechazo label { color: #f8fafc; }
	.formulario-rechazo textarea { background: #0f172a; border: 1px solid #475569; color: #f8fafc; }
	.formulario-rechazo textarea:focus { background: #0f172a; color: #f8fafc; border-color: #3b82f6; box-shadow: 0 0 0 3px rgb(59 130 246 / 20%); }
	.formulario-rechazo small { display: block; margin-top: 7px; color: #94a3b8; }
	.modal-revision-footer { justify-content: flex-end; flex-wrap: wrap; border-top: 1px solid #334155; border-bottom: 0; }
	@media (max-width: 600px) {
		.detalle-reserva-grid { grid-template-columns: 1fr; }
		.notificacion-pagina { top: 12px; right: 12px; width: calc(100vw - 24px); padding: 12px; }
	}


	/* DETALLE DEL MOTIVO DE RECHAZO EN LA TABLA */
	.reservas-container .detalle-rechazo {
		min-width: 220px;
		max-width: 360px;
		color: #fecaca;
		font-size: .85rem;
		white-space: normal;
		 overflow-wrap: anywhere;
	}
	.reservas-container .detalle-no-aplica {
		color: #94a3b8;
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
