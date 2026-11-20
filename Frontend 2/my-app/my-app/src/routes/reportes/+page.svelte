<script>
	let fechaInicial = $state('');
	let fechaFinal = $state('');
	let tipoReporte = $state('');

	let consultaRealizada = $state(false);
	let mensajeError = $state('');

	function consultarReporte(evento) {
		evento.preventDefault();
		mensajeError = '';

		if (fechaInicial && fechaFinal && fechaFinal < fechaInicial) {
			mensajeError = 'La fecha final no puede ser anterior a la fecha inicial.';
			return;
		}

		// La consulta real se implementará al conectar el backend.
		consultaRealizada = true;
	}

	function limpiarFiltros() {
		fechaInicial = '';
		fechaFinal = '';
		tipoReporte = '';
		consultaRealizada = false;
		mensajeError = '';
	}
</script>

<svelte:head>
	<title>Sistema de Reservas CUL - Reportes</title>
	<meta name="description" content="Consulta y genera reportes del sistema de reservas." />
</svelte:head>

<div class="reportes-container">
	<!-- ENCABEZADO -->
	<header class="pagina-encabezado">
		<div>
			<span class="pagina-etiqueta">ANÁLISIS DEL SISTEMA</span>
			<h1>Reportes</h1>
			<p>Consulta y genera reportes del sistema de reservas universitarias.</p>
		</div>

		<button
			type="button"
			class="btn-principal"
			onclick={() => document.getElementById('filtrosReporte')?.requestSubmit()}
		>
			<span aria-hidden="true">↗</span>
			Generar reporte
		</button>
	</header>

	<!-- FILTROS -->
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
					<input
						id="fechaFinal"
						bind:value={fechaFinal}
						type="date"
						min={fechaInicial || undefined}
					/>
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
			</div>

			{#if mensajeError}
				<div class="mensaje-error" role="alert">
					<span aria-hidden="true">⚠</span>
					{mensajeError}
				</div>
			{/if}

			<div class="filtros-acciones">
				<button type="button" class="btn-secundario" onclick={limpiarFiltros}>
					Limpiar filtros
				</button>

				<button type="submit" class="btn-principal">
					<span aria-hidden="true">⌕</span>
					Consultar reporte
				</button>
			</div>
		</form>
	</section>

	<!-- INDICADORES -->
	<section class="indicadores-grid" aria-label="Indicadores de reportes">
		<article class="indicador-card">
			<div class="indicador-superior">
				<span class="indicador-icono azul" aria-hidden="true">▤</span>
				<span class="indicador-etiqueta">RESERVAS</span>
			</div>

			<div class="indicador-valor">—</div>
			<p>Total de reservas</p>
			<span class="indicador-nota">Pendiente de conexión</span>
		</article>

		<article class="indicador-card">
			<div class="indicador-superior">
				<span class="indicador-icono verde" aria-hidden="true">▦</span>
				<span class="indicador-etiqueta">ESPACIOS</span>
			</div>

			<div class="indicador-valor">—</div>
			<p>Espacios utilizados</p>
			<span class="indicador-nota">Pendiente de conexión</span>
		</article>

		<article class="indicador-card">
			<div class="indicador-superior">
				<span class="indicador-icono morado" aria-hidden="true">⚙</span>
				<span class="indicador-etiqueta">RECURSOS</span>
			</div>

			<div class="indicador-valor">—</div>
			<p>Recursos asignados</p>
			<span class="indicador-nota">Pendiente de conexión</span>
		</article>
	</section>

	<!-- GRÁFICOS -->
	<section class="graficos-grid">
		<article class="panel grafico-panel">
			<div class="panel-encabezado">
				<div>
					<h2>Reservas por período</h2>
					<p>Distribución de las reservas según las fechas seleccionadas.</p>
				</div>

				<span class="grafico-etiqueta">Por período</span>
			</div>

			<div class="grafico-vacio">
				<div class="grafico-vacio-icono" aria-hidden="true">▥</div>
				<h3>Gráfico de reservas</h3>
				<p>La información gráfica aparecerá cuando se conecte el módulo con el backend.</p>
				<div class="grafico-lineas" aria-hidden="true">
					<span></span>
					<span></span>
					<span></span>
					<span></span>
					<span></span>
				</div>
			</div>
		</article>

		<article class="panel grafico-panel">
			<div class="panel-encabezado">
				<div>
					<h2>Distribución</h2>
					<p>Resumen de la información consultada.</p>
				</div>
			</div>

			<div class="distribucion-vacia">
				<div class="distribucion-circulo" aria-hidden="true">—</div>
				<h3>Sin estadísticas disponibles</h3>
				<p>Los indicadores se calcularán con datos reales del sistema.</p>
			</div>
		</article>
	</section>

	<!-- DETALLE -->
	<section class="panel tabla-panel">
		<div class="panel-encabezado tabla-encabezado">
			<div>
				<h2>Detalle del reporte</h2>
				<p>Consulta los resultados correspondientes a los filtros seleccionados.</p>
			</div>

		</div>

		<div class="tabla-contenedor">
			<table>
				<thead>
					<tr>
						<th>ID</th>
						<th>Tipo</th>
						<th>Espacio</th>
						<th>Fecha</th>
						<th>Estado</th>
					</tr>
				</thead>

				<tbody>
					<tr>
						<td colspan="5">
							<div class="tabla-vacia">
								<div class="tabla-vacia-icono" aria-hidden="true">▤</div>

								<h3>
									{consultaRealizada ? 'Consulta preparada' : 'No hay información para mostrar'}
								</h3>

								<p>
									{consultaRealizada
										? 'Los resultados aparecerán cuando se conecte la consulta con el backend.'
										: 'Selecciona los filtros y consulta para preparar el reporte.'}
								</p>
							</div>
						</td>
					</tr>
				</tbody>
			</table>
		</div>
	</section>
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

		.pagina-encabezado .btn-principal {
			width: 100%;
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
</style>
