<script>
	import * as XLSX from 'xlsx';
	const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

	let fechaInicial = $state('');
	let fechaFinal = $state('');
	let tipoReporte = $state('reservas');
	let estadoReserva = $state('');
	let consultaRealizada = $state(false);
	let cargando = $state(false);
	let mensajeError = $state('');
	let estadoConexion = $state('Sin conexión');
	let reporte = $state(null);
	let correo = $state('');
	let mensajeCorreo = $state('');
	let enviandoCorreo = $state(false);

	const formatoNumero = (valor) =>
		new Intl.NumberFormat('es-CO').format(Number(valor ?? 0));

	function fechaTexto(valor) {
		if (!valor) return '—';
		const texto = String(valor);
		return texto.includes('T') ? texto.slice(0, 10) : texto;
	}

	function valorCelda(valor) {
		if (valor === null || valor === undefined || valor === '') return '—';
		if (typeof valor === 'boolean') return valor ? 'Activo' : 'Inactivo';
		return String(valor);
	}

	function nombreTipo() {
		if (tipoReporte === 'espacios') return 'Uso de espacios';
		if (tipoReporte === 'recursos') return 'Recursos';
		return 'Reservas';
	}

	function columnasDetalle() {
		if (!reporte) return [];
		if (tipoReporte === 'reservas') {
			return [
				{ key: 'tipo', label: 'Tipo' },
				{ key: 'espacio', label: 'Espacio' },
				{ key: 'fecha_reserva', label: 'Fecha' },
				{ key: 'estado', label: 'Estado' },
				{ key: 'usuario', label: 'Usuario' }
			];
		}
		if (tipoReporte === 'espacios') {
			return [
				{ key: 'espacio', label: 'Espacio' },
				{ key: 'tipo', label: 'Tipo' },
				{ key: 'ubicacion_piso', label: 'Ubicación / piso' },
				{ key: 'total_reservas', label: 'Reservas' },
				{ key: 'aprobadas', label: 'Aprobadas' },
				{ key: 'pendientes', label: 'Pendientes' },
				{ key: 'estado', label: 'Estado' }
			];
		}
		return [
			{ key: 'recurso', label: 'Recurso' },
			{ key: 'categoria', label: 'Categoría' },
			{ key: 'estado_mantenimiento', label: 'Mantenimiento' },
			{ key: 'cantidad_asignada', label: 'Unidades asignadas' },
			{ key: 'espacios_asignados', label: 'Espacios asignados' },
			{ key: 'estado', label: 'Estado' }
		];
	}

	function valorIndicador(clave) {
		return reporte?.indicadores?.[clave] ?? 0;
	}

	function etiquetaIndicador(clave) {
		if (tipoReporte === 'recursos') {
			if (clave === 'total_reservas') return 'Unidades asignadas';
			if (clave === 'espacios_utilizados') return 'Espacios con recursos';
			if (clave === 'total_recursos') return 'Tipos de recursos';
		}
		if (tipoReporte === 'espacios') {
			if (clave === 'total_reservas') return 'Reservas registradas';
			if (clave === 'espacios_utilizados') return 'Espacios utilizados';
			if (clave === 'total_recursos') return 'Espacios activos';
		}
		if (clave === 'total_reservas') return 'Total de reservas';
		if (clave === 'espacios_utilizados') return 'Espacios utilizados';
		return 'Recursos activos';
	}

	async function consultarReporte(evento) {
		evento?.preventDefault();
		mensajeError = '';

		if (fechaInicial && fechaFinal && fechaFinal < fechaInicial) {
			mensajeError = 'La fecha final no puede ser anterior a la fecha inicial.';
			return;
		}
		if (!tipoReporte) {
			mensajeError = 'Selecciona un tipo de reporte para continuar.';
			return;
		}

		cargando = true;
		estadoConexion = 'Consultando…';

		try {
			const parametros = [
				`tipo_reporte=${encodeURIComponent(tipoReporte)}`,
				...(fechaInicial ? [`fecha_inicial=${encodeURIComponent(fechaInicial)}`] : []),
				...(fechaFinal ? [`fecha_final=${encodeURIComponent(fechaFinal)}`] : [])
				,...(estadoReserva && tipoReporte === 'reservas' ? [`estado_reserva=${encodeURIComponent(estadoReserva)}`] : [])
			].join('&');

			const respuesta = await fetch(`${API_BASE_URL}/reportes/?${parametros}`);
			const datos = await respuesta.json().catch(() => ({}));

			if (!respuesta.ok) {
				throw new Error(datos.detail || `Error al consultar el reporte (${respuesta.status}).`);
			}

			reporte = datos;
			consultaRealizada = true;
			estadoConexion = 'Conectado';
		} catch (error) {
			reporte = null;
			consultaRealizada = false;
			estadoConexion = 'Error de conexión';
			mensajeError = 'No fue posible consultar el reporte. Inténtalo nuevamente.';
		} finally {
			cargando = false;
		}
	}

	function limpiarFiltros() {
		fechaInicial = '';
		fechaFinal = '';
		tipoReporte = 'reservas';
		estadoReserva = '';
		consultaRealizada = false;
		mensajeError = '';
		reporte = null;
		estadoConexion = 'Sin conexión';
	}

	function totalSerie() {
		return Math.max(1, ...(reporte?.serie ?? []).map((item) => Number(item.total ?? 0)));
	}

	function exportarExcel() {
		if (!reporte) return;
		const filas = reporte.detalle.map((fila) => Object.fromEntries(columnasDetalle().map((c) => [c.label, fila[c.key]])));
		const libro = XLSX.utils.book_new();
		XLSX.utils.book_append_sheet(libro, XLSX.utils.json_to_sheet(filas), 'Reporte');
		XLSX.writeFile(libro, `reporte-${tipoReporte}-${new Date().toISOString().slice(0, 10)}.xlsx`);
	}

	async function enviarCorreo() {
		mensajeCorreo = '';
		if (!reporte || !correo.trim()) { mensajeCorreo = 'Consulta un reporte e ingresa un correo válido.'; return; }
		enviandoCorreo = true;
		try {
			const respuesta = await fetch(`${API_BASE_URL}/reportes/enviar`, {
				method: 'POST', headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ destinatario: correo.trim(), tipo_reporte: tipoReporte, fecha_inicial: fechaInicial || null, fecha_final: fechaFinal || null, estado_reserva: estadoReserva || null })
			});
			const data = await respuesta.json().catch(() => ({}));
			if (!respuesta.ok) throw new Error(data.detail || 'No fue posible enviar el reporte.');
			mensajeCorreo = 'Reporte enviado correctamente.';
		} catch (error) {
			mensajeCorreo = error instanceof TypeError
				? 'No fue posible conectar con el servicio de correo. Inténtalo nuevamente.'
				: error?.message || 'No fue posible enviar el reporte. Inténtalo nuevamente.';
		}
		finally { enviandoCorreo = false; }
	}
</script>

<svelte:head>
	<title>Sistema de Reservas CUL - Reportes</title>
	<meta name="description" content="Consulta y genera reportes del sistema de reservas." />
</svelte:head>

<div class="reportes-container">
	<header class="pagina-encabezado">
		<div>
			<span class="pagina-etiqueta">ANÁLISIS DEL SISTEMA</span>
			<h1>Reportes</h1>
			<p>Consulta y genera reportes del sistema de reservas universitarias.</p>
		</div>
	</header>

	<section class="panel filtros-panel">
		<div class="panel-encabezado">
			<div class="encabezado-icono" aria-hidden="true">☷</div>
			<div>
				<h2>Consultar reportes</h2>
				<p>Selecciona los criterios para consultar la información.</p>
			</div>
		</div>
		<form id="filtrosReporte" onsubmit={consultarReporte}>
			<div class="filtros-grid">
				<div class="campo">
					<label for="fechaInicial">Fecha inicial</label>
					<input id="fechaInicial" bind:value={fechaInicial} type="date" />
				</div>
				<div class="campo">
					<label for="fechaFinal">Fecha final</label>
					<input id="fechaFinal" bind:value={fechaFinal} type="date" min={fechaInicial || undefined} />
				</div>
				<div class="campo">
					<label for="tipoReporte">Tipo de reporte</label>
					<select id="tipoReporte" bind:value={tipoReporte}>
						<option value="">Seleccionar tipo de reporte</option>
						<option value="reservas">Reservas</option>
						<option value="espacios">Uso de espacios</option>
						<option value="recursos">Recursos</option>
					</select>
				</div>
				{#if tipoReporte === 'reservas'}<div class="campo"><label for="estadoReserva">Estado de la reserva</label><select id="estadoReserva" bind:value={estadoReserva}><option value="">Todos los estados</option><option value="Pendiente">Pendiente</option><option value="Aprobada">Aprobada</option><option value="Rechazada">Rechazada</option><option value="Cancelada">Cancelada</option></select></div>{/if}
			</div>
			{#if mensajeError}
				<div class="mensaje-error" role="alert"><span aria-hidden="true">⚠</span>{mensajeError}</div>
			{/if}
			<div class="filtros-acciones">
				<button type="button" class="btn-secundario" onclick={limpiarFiltros} disabled={cargando}>Limpiar filtros</button>
				<button type="submit" class="btn-principal" disabled={cargando}>
					<span aria-hidden="true">⌕</span>{cargando ? 'Consultando…' : 'Consultar reporte'}
				</button>
			</div>
		</form>
	</section>

	<section class="indicadores-grid" aria-label="Indicadores de reportes">
		{#each [
			{ key: 'total_reservas', icon: '▤', color: 'azul' },
			{ key: 'espacios_utilizados', icon: '▦', color: 'verde' },
			{ key: 'total_recursos', icon: '⚙', color: 'morado' }
		] as indicador (indicador.key)}
			<article class="indicador-card">
				<div class="indicador-superior">
					<span class={`indicador-icono ${indicador.color}`} aria-hidden="true">{indicador.icon}</span>
					<span class="indicador-etiqueta">{etiquetaIndicador(indicador.key).toUpperCase()}</span>
				</div>
				<div class="indicador-valor">{consultaRealizada ? formatoNumero(valorIndicador(indicador.key)) : '—'}</div>
				<p>{etiquetaIndicador(indicador.key)}</p>
				<span class="indicador-nota">{consultaRealizada ? 'Datos actualizados' : 'Consulta para cargar datos reales'}</span>
			</article>
		{/each}
	</section>

	<section class="graficos-grid">
		<article class="panel grafico-panel">
			<div class="panel-encabezado">
				<div><h2>{tipoReporte === 'recursos' ? 'Recursos por espacio' : 'Reservas por período'}</h2><p>{tipoReporte === 'recursos' ? 'Unidades asignadas por espacio.' : 'Distribución de los registros según las fechas seleccionadas.'}</p></div>
				<span class="grafico-etiqueta">{nombreTipo()}</span>
			</div>
			{#if consultaRealizada && (reporte?.serie?.length ?? 0) > 0}
				<div class="grafico-datos" aria-label="Gráfico de datos">
					{#each reporte.serie as item, indice (item.fecha ?? item.etiqueta ?? indice)}
						<div class="barra-item">
							<div class="barra-valor">{formatoNumero(item.total)}</div>
							<div class="barra-fondo"><div class="barra" style={`height: ${(Number(item.total ?? 0) / totalSerie()) * 100}%`}></div></div>
							<div class="barra-etiqueta">{fechaTexto(item.fecha ?? item.etiqueta)}</div>
						</div>
					{/each}
				</div>
			{:else}
				<div class="grafico-vacio">
					<div class="grafico-vacio-icono" aria-hidden="true">▥</div>
					<h3>{cargando ? 'Cargando información…' : 'Gráfico de reportes'}</h3>
					<p>{consultaRealizada ? 'No hay datos para los filtros seleccionados.' : 'Consulta un reporte para visualizar los datos reales.'}</p>
					<div class="grafico-lineas" aria-hidden="true"><span></span><span></span><span></span><span></span><span></span></div>
				</div>
			{/if}
		</article>

		<article class="panel grafico-panel">
			<div class="panel-encabezado"><div><h2>Distribución</h2><p>Resumen de la información consultada.</p></div></div>
			{#if consultaRealizada && (reporte?.distribucion?.length ?? 0) > 0}
				<div class="distribucion-lista">
					{#each reporte.distribucion as item, indice (item.etiqueta ?? indice)}
						<div class="distribucion-item">
							<div class="distribucion-texto"><span>{valorCelda(item.etiqueta)}</span><strong>{formatoNumero(item.total)}</strong></div>
							<div class="distribucion-barra-fondo"><div class="distribucion-barra" style={`width: ${(Number(item.total ?? 0) / Math.max(1, ...reporte.distribucion.map((x) => Number(x.total ?? 0)))) * 100}%`}></div></div>
						</div>
					{/each}
				</div>
			{:else}
				<div class="distribucion-vacia">
					<div class="distribucion-circulo" aria-hidden="true">—</div>
					<h3>{consultaRealizada ? 'Sin estadísticas disponibles' : 'Consulta pendiente'}</h3>
					<p>{consultaRealizada ? 'No hay datos de distribución para esta consulta.' : 'La distribución se calculará con datos reales del sistema.'}</p>
				</div>
			{/if}
		</article>
	</section>

	<section class="panel tabla-panel">
		<div class="panel-encabezado tabla-encabezado">
			<div><h2>Detalle del reporte</h2><p>{consultaRealizada ? `${formatoNumero(reporte?.total_registros)} registros encontrados.` : 'Consulta los resultados correspondientes a los filtros seleccionados.'}</p></div>
			{#if consultaRealizada}<div class="acciones-exportacion"><button type="button" onclick={exportarExcel}>Exportar Excel</button><button type="button" onclick={() => window.print()}>Guardar PDF</button></div>{/if}
		</div>
		<div class="tabla-contenedor">
			<table>
				<thead>
					<tr>
						{#each columnasDetalle() as columna (columna.key)}
							<th>{columna.label}</th>
						{/each}
					</tr>
				</thead>
				<tbody>
					{#if consultaRealizada && (reporte?.detalle?.length ?? 0) > 0}
						{#each reporte.detalle as fila, indice (fila.id_reserva ?? fila.id_espacio ?? fila.id_recurso ?? indice)}
							<tr>
								{#each columnasDetalle() as columna (columna.key)}
									<td>{columna.key.includes('fecha') ? fechaTexto(fila[columna.key]) : valorCelda(fila[columna.key])}</td>
								{/each}
							</tr>
						{/each}
					{:else}
						<tr><td colspan={Math.max(1, columnasDetalle().length)}>
							<div class="tabla-vacia">
								<div class="tabla-vacia-icono" aria-hidden="true">▤</div>
								<h3>{cargando ? 'Consultando reporte…' : consultaRealizada ? 'No hay registros' : 'No hay información para mostrar'}</h3>
								<p>{consultaRealizada ? 'No se encontraron registros para los criterios seleccionados.' : 'Selecciona los filtros y consulta para ver los resultados.'}</p>
							</div>
						</td></tr>
					{/if}
				</tbody>
			</table>
		</div>
	</section>
	{#if consultaRealizada}<section class="panel email-panel"><div class="email-copy"><h2>Enviar reporte por correo</h2><p>Se enviará el detalle como archivo CSV compatible con Excel.</p></div><form onsubmit={(e) => { e.preventDefault(); enviarCorreo(); }}><input type="email" bind:value={correo} placeholder="destinatario@institucion.edu" required/><button disabled={enviandoCorreo}>{enviandoCorreo ? 'Enviando…' : 'Enviar'}</button></form>{#if mensajeCorreo}<p class:correo-error={!mensajeCorreo.includes('correctamente')} class:correo-exito={mensajeCorreo.includes('correctamente')} class="correo-estado" role="status">{mensajeCorreo}</p>{/if}</section>{/if}
</div>

<style>
	.reportes-container {
		width: 100%;
		max-width: 1600px;
		margin: 0 auto;
		padding: 32px;
		box-sizing: border-box;
		color: #f8fafc;
	}
	.acciones-exportacion,.email-panel form{display:flex;gap:8px;align-items:center}.acciones-exportacion button,.email-panel button{background:#2563eb;color:white;border:0;border-radius:8px;padding:10px 13px;font-weight:700;cursor:pointer}.email-panel{box-sizing:border-box;width:100%;min-width:0;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,460px);align-items:center;gap:14px 24px;margin-top:18px}.email-copy{min-width:0}.email-copy h2{margin:0 0 6px;font-size:18px;line-height:1.35}.email-panel form{grid-column:2;min-width:0;width:100%}.email-panel input{flex:1;min-width:0;width:100%;padding:10px;border-radius:7px;border:1px solid #475569;background:#0f172a;color:white}.email-panel button{flex:none}.email-copy p,.correo-estado{margin:0;color:#94a3b8;line-height:1.5}.correo-estado{grid-column:1/-1;min-width:0;overflow-wrap:anywhere}.correo-error{color:#fecaca!important}.correo-exito{color:#86efac!important}@media(max-width:900px){.email-panel{grid-template-columns:minmax(0,1fr)}.email-panel form{grid-column:1}.correo-estado{grid-column:1}}@media(max-width:650px){.email-panel{gap:12px}.email-panel form{width:100%}}

	@media print {
		@page { margin: 14mm; }
		:global(html), :global(body) { background: #fff !important; color: #111 !important; }
		:global(.app-layout > :not(.app-contenido)) { display: none !important; }
		:global(.app-layout > .app-contenido > :not(.app-main)) { display: none !important; }
		:global(.app-main) { width: 100% !important; padding: 0 !important; }

		.reportes-container > :not(.tabla-panel) { display: none !important; }
		.reportes-container { width: 100% !important; max-width: none !important; margin: 0 !important; padding: 0 !important; }
		.tabla-panel {
			position: static !important;
			width: 100% !important;
			margin: 0 !important;
			padding: 0 !important;
			border: 0 !important;
			border-radius: 0 !important;
			background: #fff !important;
			color: #111 !important;
			box-shadow: none !important;
		}
		.tabla-encabezado { justify-content: flex-start !important; padding: 0 0 12px !important; }
		.tabla-encabezado h2, .tabla-encabezado p { color: #111 !important; }
		.tabla-encabezado p { margin: 4px 0 0 !important; }
		.tabla-panel .acciones-exportacion, .tabla-panel .estado-conexion { display: none !important; }
		.tabla-contenedor { width: 100% !important; overflow: visible !important; padding: 0 !important; }
		.tabla-contenedor table { width: 100% !important; font-size: 9pt !important; }
		.tabla-contenedor thead { display: table-header-group; background: #e5e7eb !important; }
		.tabla-contenedor th, .tabla-contenedor td { color: #111 !important; border-bottom: 1px solid #cbd5e1 !important; padding: 7px !important; white-space: normal !important; }
		.tabla-contenedor tr { break-inside: avoid; }
	}

	.pagina-encabezado {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 24px;
		margin-bottom: 28px;
	}

	.pagina-etiqueta {
		color: #60a5fa;
		font-size: 11px;
		font-weight: 750;
		letter-spacing: 1.2px;
	}

	.pagina-encabezado h1 {
		margin: 10px 0 6px;
		color: #f8fafc;
		font-size: 30px;
		font-weight: 800;
	}

	.pagina-encabezado p {
		margin: 0;
		color: #cbd5e1;
		font-size: 14px;
		line-height: 1.7;
	}

	.panel {
		overflow: hidden;
		margin-bottom: 24px;
		border: 1px solid #334155;
		border-radius: 12px;
		background: #1e293b;
	}

	.panel-encabezado {
		display: flex;
		align-items: center;
		gap: 14px;
		padding: 22px;
		border-bottom: 1px solid #334155;
	}

	.panel-encabezado h2 {
		margin: 0;
		color: #f8fafc;
		font-size: 16px;
		font-weight: 750;
	}

	.panel-encabezado p {
		margin: 7px 0 0;
		color: #b7c5d9;
		font-size: 12px;
		line-height: 1.7;
	}

	.encabezado-icono {
		display: grid;
		width: 42px;
		height: 42px;
		flex-shrink: 0;
		place-items: center;
		border: 1px solid #3b82f6;
		border-radius: 10px;
		background: #172b49;
		color: #93c5fd;
		font-size: 22px;
	}

	.btn-principal,
	.btn-secundario {
		display: inline-flex;
		min-height: 42px;
		align-items: center;
		justify-content: center;
		gap: 8px;
		padding: 10px 16px;
		border: 1px solid transparent;
		border-radius: 8px;
		font: inherit;
		font-size: 13px;
		font-weight: 700;
		cursor: pointer;
		transition:
			background-color 0.2s ease,
			border-color 0.2s ease;
	}

	.btn-principal {
		background: #2563eb;
		color: #ffffff;
	}

	.btn-principal:hover {
		background: #1d4ed8;
	}

	.btn-secundario {
		border-color: #475569;
		background: #334155;
		color: #f8fafc;
	}

	.btn-secundario:hover {
		background: #475569;
	}

	.filtros-panel form {
		padding: 24px;
	}

	.filtros-grid {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 20px;
	}

	.campo {
		display: flex;
		min-width: 0;
		flex-direction: column;
		gap: 9px;
	}

	.campo label {
		color: #e2e8f0;
		font-size: 13px;
		font-weight: 650;
	}

	.campo input,
	.campo select {
		width: 100%;
		min-height: 44px;
		padding: 11px 12px;
		border: 1px solid #475569;
		border-radius: 8px;
		outline: none;
		background: #0f172a;
		color: #f8fafc;
		font: inherit;
		font-size: 13px;
		box-sizing: border-box;
		color-scheme: dark;
	}

	:global(html[data-tema='claro']) .reportes-container .campo input[type='date'] {
		color-scheme: light;
	}

	.campo input:focus,
	.campo select:focus {
		border-color: #60a5fa;
		box-shadow: 0 0 0 3px rgb(59 130 246 / 18%);
	}

	.campo input::placeholder {
		color: #94a3b8;
		opacity: 1;
	}

	.filtros-acciones {
		display: flex;
		justify-content: flex-end;
		gap: 12px;
		margin-top: 24px;
		padding-top: 20px;
		border-top: 1px solid #334155;
	}

	.mensaje-error {
		display: flex;
		align-items: center;
		gap: 10px;
		margin-top: 20px;
		padding: 12px 14px;
		border: 1px solid #b91c1c;
		border-radius: 8px;
		background: #451a1a;
		color: #fecaca;
		font-size: 13px;
	}

	.indicadores-grid {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 20px;
		margin-bottom: 24px;
	}

	.indicador-card {
		padding: 22px;
		border: 1px solid #334155;
		border-radius: 12px;
		background: #1e293b;
	}

	.indicador-superior {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 12px;
	}

	.indicador-icono {
		display: grid;
		width: 44px;
		height: 44px;
		place-items: center;
		border-radius: 11px;
		font-size: 23px;
	}

	.indicador-icono.azul {
		border: 1px solid #1d4ed8;
		background: #172b49;
		color: #93c5fd;
	}

	.indicador-icono.verde {
		border: 1px solid #047857;
		background: #12352f;
		color: #6ee7b7;
	}

	.indicador-icono.morado {
		border: 1px solid #6d28d9;
		background: #30204f;
		color: #c4b5fd;
	}

	.indicador-etiqueta {
		color: #94a3b8;
		font-size: 10px;
		font-weight: 750;
		letter-spacing: 1px;
	}

	.indicador-valor {
		margin-top: 20px;
		color: #f8fafc;
		font-size: 30px;
		font-weight: 800;
	}

	.indicador-card > p {
		margin: 5px 0 12px;
		color: #e2e8f0;
		font-size: 13px;
		font-weight: 650;
	}

	.indicador-nota {
		color: #94a3b8;
		font-size: 11px;
	}

	.graficos-grid {
		display: grid;
		grid-template-columns: minmax(0, 1.7fr) minmax(280px, 1fr);
		gap: 20px;
	}

	.grafico-panel {
		margin-bottom: 24px;
	}

	.grafico-panel .panel-encabezado {
		justify-content: space-between;
	}

	.grafico-etiqueta {
		padding: 7px 10px;
		border: 1px solid #475569;
		border-radius: 7px;
		color: #cbd5e1;
		font-size: 11px;
		white-space: nowrap;
	}

	.grafico-vacio,
	.distribucion-vacia {
		display: flex;
		min-height: 290px;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 28px;
		text-align: center;
	}

	.grafico-vacio-icono {
		display: grid;
		width: 60px;
		height: 60px;
		place-items: center;
		margin-bottom: 17px;
		border: 1px solid #475569;
		border-radius: 14px;
		background: #172338;
		color: #93c5fd;
		font-size: 29px;
	}

	.grafico-vacio h3,
	.distribucion-vacia h3 {
		margin: 0;
		color: #f8fafc;
		font-size: 15px;
		font-weight: 750;
	}

	.grafico-vacio p,
	.distribucion-vacia p {
		max-width: 380px;
		margin: 9px 0 0;
		color: #b7c5d9;
		font-size: 12px;
		line-height: 1.7;
	}

	.grafico-lineas {
		display: flex;
		width: 100%;
		max-width: 330px;
		align-items: flex-end;
		justify-content: center;
		gap: 12px;
		height: 50px;
		margin-top: 25px;
		border-bottom: 1px solid #475569;
	}

	.grafico-lineas span {
		width: 30px;
		height: 18px;
		border: 1px solid #3b82f6;
		border-bottom: 0;
		border-radius: 5px 5px 0 0;
		background: #1d3b68;
		opacity: 0.65;
	}

	.grafico-lineas span:nth-child(2) {
		height: 32px;
	}

	.grafico-lineas span:nth-child(3) {
		height: 24px;
	}

	.grafico-lineas span:nth-child(4) {
		height: 42px;
	}

	.grafico-lineas span:nth-child(5) {
		height: 28px;
	}

	.distribucion-circulo {
		display: grid;
		width: 100px;
		height: 100px;
		place-items: center;
		margin-bottom: 22px;
		border: 10px solid #334155;
		border-right-color: #3b82f6;
		border-radius: 50%;
		background: #172338;
		color: #f8fafc;
		font-size: 24px;
		font-weight: 750;
	}

	.tabla-panel {
		margin-top: 0;
	}

	.tabla-encabezado {
		justify-content: space-between;
	}

	.estado-conexion {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		padding: 7px 10px;
		border: 1px solid #475569;
		border-radius: 20px;
		color: #cbd5e1;
		font-size: 11px;
		white-space: nowrap;
	}

	.estado-punto {
		width: 7px;
		height: 7px;
		border-radius: 50%;
		background: #f59e0b;
	}

	.tabla-contenedor {
		width: 100%;
		overflow-x: auto;
		padding: 16px 20px 20px;
	}

	.tabla-contenedor table {
		width: 100%;
		border-collapse: collapse;
		text-align: left;
	}

	.tabla-contenedor thead {
		background: #27364b;
	}

	.tabla-contenedor th {
		padding: 15px 14px;
		border-bottom: 1px solid #475569;
		color: #f8fafc;
		font-size: 12px;
		font-weight: 750;
		white-space: nowrap;
	}

	.tabla-vacia {
		display: flex;
		min-height: 220px;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 25px 15px;
		text-align: center;
	}

	.tabla-vacia-icono {
		display: grid;
		width: 56px;
		height: 56px;
		place-items: center;
		margin-bottom: 16px;
		border: 1px solid #475569;
		border-radius: 14px;
		background: #172338;
		color: #93c5fd;
		font-size: 27px;
	}

	.tabla-vacia h3 {
		margin: 0;
		color: #f8fafc;
		font-size: 15px;
		font-weight: 750;
	}

	.tabla-vacia p {
		max-width: 450px;
		margin: 9px 0 0;
		color: #b7c5d9;
		font-size: 12px;
		line-height: 1.7;
	}

	@media (max-width: 1000px) {
		.filtros-grid {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}

		.indicadores-grid {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}

		.graficos-grid {
			grid-template-columns: minmax(0, 1fr);
		}
	}

	@media (max-width: 650px) {
		.reportes-container {
			padding: 22px 16px;
		}

		.pagina-encabezado {
			align-items: stretch;
			flex-direction: column;
		}

		.pagina-encabezado h1 {
			font-size: 25px;
		}

		.filtros-panel form {
			padding: 18px;
		}

		.filtros-grid,
		.indicadores-grid {
			grid-template-columns: minmax(0, 1fr);
		}

		.filtros-acciones {
			flex-direction: column-reverse;
		}

		.filtros-acciones button {
			width: 100%;
		}

		.panel-encabezado {
			padding: 18px;
		}

		.grafico-panel .panel-encabezado {
			align-items: flex-start;
			flex-direction: column;
		}

		.tabla-encabezado {
			align-items: flex-start;
		}

		.estado-conexion {
			align-self: flex-start;
		}

		.tabla-contenedor {
			padding: 12px;
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.btn-principal,
		.btn-secundario {
			transition: none;
		}
	}

	.barra-item { display: flex; min-width: 48px; flex: 1; flex-direction: column; align-items: center; justify-content: flex-end; gap: 8px; }
	.grafico-datos { display: flex; min-height: 290px; align-items: stretch; gap: 12px; overflow-x: auto; padding: 24px; }
	.barra-valor { color: #e2e8f0; font-size: 11px; font-weight: 700; }
	.barra-fondo { display: flex; width: 100%; height: 190px; align-items: flex-end; justify-content: center; border-bottom: 1px solid #475569; background: linear-gradient(to top, rgb(51 65 85 / 25%) 1px, transparent 1px); background-size: 100% 25%; }
	.barra { width: min(38px, 75%); min-height: 2px; border-radius: 5px 5px 0 0; background: #3b82f6; }
	.barra-etiqueta { max-width: 85px; color: #cbd5e1; font-size: 10px; text-align: center; overflow-wrap: anywhere; }
	.distribucion-lista { display: flex; min-height: 290px; flex-direction: column; justify-content: center; gap: 20px; padding: 24px; }
	.distribucion-texto { display: flex; justify-content: space-between; gap: 12px; margin-bottom: 8px; color: #e2e8f0; font-size: 12px; }
	.distribucion-texto strong { color: #f8fafc; }
	.distribucion-barra-fondo { height: 8px; overflow: hidden; border-radius: 99px; background: #334155; }
	.distribucion-barra { height: 100%; border-radius: 99px; background: #3b82f6; }
	.tabla-contenedor tbody tr { border-bottom: 1px solid #334155; }
	.tabla-contenedor td { padding: 13px 14px; color: #cbd5e1; font-size: 12px; white-space: nowrap; }
	.estado-conexion.conectado { border-color: #047857; color: #6ee7b7; }
	.estado-conexion.conexion-error { border-color: #b91c1c; color: #fecaca; }
	.estado-conexion.conectado .estado-punto { background: #34d399; }
	.estado-conexion.conexion-error .estado-punto { background: #f87171; }
	.btn-principal:disabled, .btn-secundario:disabled { cursor: wait; opacity: 0.7; }
	:global(html[data-tema='claro'] .app-main .reportes-container .indicador-valor) { color: #334155 !important; }
	:global(html[data-tema='claro'] .app-main .reportes-container .barra-valor),
	:global(html[data-tema='claro'] .app-main .reportes-container .barra-etiqueta),
	:global(html[data-tema='claro'] .app-main .reportes-container .distribucion-texto span),
	:global(html[data-tema='claro'] .app-main .reportes-container .distribucion-texto strong),
	:global(html[data-tema='claro'] .app-main .reportes-container .grafico-etiqueta) {
		color: #334155 !important;
		font-family: inherit !important;
		font-weight: 600 !important;
	}

</style>
