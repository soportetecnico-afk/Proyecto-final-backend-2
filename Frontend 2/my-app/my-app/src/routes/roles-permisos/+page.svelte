<script>
	import PageHeader from '$lib/components/ui/PageHeader.svelte';
	import BaseButton from '$lib/components/ui/BaseButton.svelte';

	let mostrarFormulario = $state(false);
	let nombreRol = $state('');
	let descripcionRol = $state('');
	let permisosSeleccionados = $state([]);

	const modulos = [
		'Inicio',
		'Espacios',
		'Recursos',
		'Reservas',
		'Reportes',
		'Usuarios',
		'Roles y permisos'
	];

	function limpiarFormulario() {
		nombreRol = '';
		descripcionRol = '';
		permisosSeleccionados = [];
		mostrarFormulario = false;
	}

	function alternarPermiso(modulo, seleccionado) {
		if (seleccionado) {
			if (!permisosSeleccionados.includes(modulo)) {
				permisosSeleccionados = [...permisosSeleccionados, modulo];
			}
		} else {
			permisosSeleccionados = permisosSeleccionados.filter((item) => item !== modulo);
		}
	}

	function guardarRolVisual(evento) {
		evento.preventDefault();

		// El formulario todavía no está conectado al backend.
		// No se guardan datos ni se simula un registro exitoso.
	}
</script>

<svelte:head>
	<title>Roles y permisos - Sistema de Reservas CUL</title>
	<meta
		name="description"
		content="Administración de roles y permisos del Sistema de Reservas CUL"
	/>
</svelte:head>

<div class="roles-container">
	<!-- ENCABEZADO -->
	<PageHeader
		etiqueta="ADMINISTRACIÓN DEL SISTEMA"
		titulo="Roles y permisos"
		descripcion="Gestiona los roles y organiza los permisos de acceso a los módulos del sistema."
	/>

	<!-- INFORMACIÓN -->
	<section class="panel-informativo">
		<div class="panel-icono" aria-hidden="true">ⓘ</div>

		<div>
			<h2>Control de acceso</h2>
			<p>
				Los roles permiten organizar los permisos que tendrá cada usuario dentro de la plataforma.
			</p>
		</div>
	</section>

	<!-- ACCIONES -->
	<section class="acciones-roles">
		<div>
			<h2>Administración de roles</h2>
			<p>Consulta y administra los roles de acceso.</p>
		</div>

		<BaseButton
			texto={mostrarFormulario ? 'Cancelar creación' : 'Crear rol'}
			onClick={() => (mostrarFormulario = !mostrarFormulario)}
		/>
	</section>

	<!-- FORMULARIO -->
	{#if mostrarFormulario}
		<section class="panel formulario-panel">
			<div class="panel-encabezado">
				<div>
					<h2>Crear nuevo rol</h2>
					<p>Define el nombre, la descripción y los permisos del rol.</p>
				</div>
			</div>

			<form onsubmit={guardarRolVisual}>
				<div class="formulario-campos">
					<div class="campo">
						<label for="nombreRol">Nombre del rol</label>

						<input
							id="nombreRol"
							bind:value={nombreRol}
							type="text"
							placeholder="Introduce el nombre del rol"
							required
						/>
					</div>

					<div class="campo">
						<label for="descripcionRol">Descripción</label>

						<textarea
							id="descripcionRol"
							bind:value={descripcionRol}
							rows="3"
							placeholder="Describe las responsabilidades del rol"></textarea>
					</div>
				</div>

				<!-- PERMISOS -->
				<div class="permisos-seccion">
					<h3>Permisos por módulo</h3>

					<p>Selecciona los módulos que podrá consultar o administrar este rol.</p>

					<div class="permisos-lista">
						{#each modulos as modulo (modulo)}
							<label class="permiso-opcion">
								<input
									type="checkbox"
									checked={permisosSeleccionados.includes(modulo)}
									onchange={(evento) => alternarPermiso(modulo, evento.currentTarget.checked)}
								/>

								<span class="permiso-indicador" aria-hidden="true"> ✓ </span>

								<span class="permiso-nombre">{modulo}</span>
							</label>
						{/each}
					</div>

					<div class="permisos-resumen">
						<span class="resumen-punto"></span>

						<span>
							{permisosSeleccionados.length}
							{permisosSeleccionados.length === 1 ? 'módulo seleccionado' : 'módulos seleccionados'}
						</span>
					</div>
				</div>

				<!-- ACCIONES DEL FORMULARIO -->
				<div class="formulario-acciones">
					<BaseButton texto="Cancelar" variante="secundario" onClick={limpiarFormulario} />

					<button class="boton-guardar" type="submit">
						<span aria-hidden="true">＋</span>
						Guardar rol
					</button>
				</div>
			</form>
		</section>
	{/if}

	<!-- LISTADO -->
	<section class="panel tabla-panel">
		<div class="panel-encabezado encabezado-listado">
			<div>
				<h2>Roles registrados</h2>
				<p>Listado de roles y opciones de administración.</p>
			</div>

			<span class="etiqueta-pendiente"> Conexión pendiente </span>
		</div>

		<!-- CABECERA DE LA TABLA -->
		<div class="tabla-contenedor">
			<table class="tabla-roles">
				<thead>
					<tr>
						<th scope="col">Rol</th>
						<th scope="col">Descripción</th>
						<th scope="col">Permisos</th>
						<th scope="col">Acciones</th>
					</tr>
				</thead>
			</table>

			<div class="tabla-vacia">
				<div class="tabla-vacia-icono" aria-hidden="true">♙</div>

				<h3>No hay roles cargados</h3>

				<p>Los roles aparecerán aquí cuando se conecte la base de datos.</p>

				<span class="estado-vacio"> Sin registros disponibles </span>
			</div>
		</div>
	</section>
</div>

<style>
	.roles-container {
		width: 100%;
		max-width: 1600px;
		margin: 0 auto;
		padding: 28px;
		box-sizing: border-box;
		color: #f1f5f9;
	}

	/* PANELES GENERALES */

	.panel {
		overflow: hidden;
		border: 1px solid #334155;
		border-radius: 13px;
		background: #1e293b;
	}

	.panel-informativo {
		display: flex;
		align-items: flex-start;
		gap: 14px;
		margin: 24px 0 32px;
		padding: 20px;
		border: 1px solid #334155;
		border-radius: 12px;
		background: #172338;
	}

	.panel-icono {
		display: grid;
		width: 38px;
		height: 38px;
		flex-shrink: 0;
		place-items: center;
		border: 1px solid #3b82f6;
		border-radius: 11px;
		background: #1d3558;
		color: #bfdbfe;
		font-size: 21px;
	}

	.panel-informativo h2 {
		margin: 0;
		color: #f8fafc;
		font-size: 15px;
		font-weight: 700;
	}

	.panel-informativo p {
		margin: 7px 0 0;
		color: #cbd5e1;
		font-size: 13px;
		line-height: 1.7;
	}

	/* ENCABEZADOS */

	.acciones-roles {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 20px;
		margin-bottom: 20px;
	}

	.acciones-roles h2,
	.panel-encabezado h2 {
		margin: 0;
		color: #f8fafc;
		font-size: 18px;
		font-weight: 750;
	}

	.acciones-roles p,
	.panel-encabezado p {
		margin: 7px 0 0;
		color: #cbd5e1;
		font-size: 13px;
		line-height: 1.6;
	}

	.panel-encabezado {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 16px;
		padding: 22px;
		border-bottom: 1px solid #334155;
		background: #202d40;
	}

	/* FORMULARIO */

	.formulario-panel {
		margin-bottom: 24px;
	}

	.formulario-panel form {
		padding: 24px;
	}

	.formulario-campos {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
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
	.campo textarea {
		width: 100%;
		min-height: 44px;
		padding: 12px;
		border: 1px solid #475569;
		border-radius: 9px;
		outline: none;
		background: #0f172a;
		color: #f8fafc;
		font-family: inherit;
		font-size: 13px;
		box-sizing: border-box;
		transition:
			border-color 0.2s ease,
			box-shadow 0.2s ease;
	}

	.campo textarea {
		resize: vertical;
	}

	.campo input::placeholder,
	.campo textarea::placeholder {
		color: #94a3b8;
		opacity: 1;
	}

	.campo input:focus,
	.campo textarea:focus {
		border-color: #60a5fa;
		box-shadow: 0 0 0 3px rgb(59 130 246 / 18%);
	}

	/* PERMISOS */

	.permisos-seccion {
		margin-top: 30px;
	}

	.permisos-seccion h3 {
		margin: 0;
		color: #f8fafc;
		font-size: 16px;
		font-weight: 700;
	}

	.permisos-seccion > p {
		margin: 8px 0 18px;
		color: #cbd5e1;
		font-size: 13px;
		line-height: 1.6;
	}

	.permisos-lista {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 12px;
	}

	.permiso-opcion {
		display: flex;
		align-items: center;
		gap: 11px;
		min-height: 54px;
		padding: 12px 14px;
		border: 1px solid #475569;
		border-radius: 10px;
		background: #172338;
		color: #e2e8f0;
		font-size: 13px;
		cursor: pointer;
		transition:
			border-color 0.2s ease,
			background-color 0.2s ease;
	}

	.permiso-opcion:hover {
		border-color: #64748b;
		background: #26364c;
	}

	.permiso-opcion:has(input:checked) {
		border-color: #60a5fa;
		background: #1e3a5f;
	}

	.permiso-opcion input {
		position: absolute;
		width: 1px;
		height: 1px;
		overflow: hidden;
		clip-path: inset(50%);
		white-space: nowrap;
	}

	.permiso-opcion:focus-within {
		outline: 2px solid #60a5fa;
		outline-offset: 2px;
	}

	.permiso-indicador {
		display: grid;
		width: 22px;
		height: 22px;
		flex-shrink: 0;
		place-items: center;
		border: 1px solid #64748b;
		border-radius: 6px;
		color: transparent;
		font-size: 13px;
		font-weight: 800;
	}

	.permiso-opcion:has(input:checked) .permiso-indicador {
		border-color: #60a5fa;
		background: #2563eb;
		color: #ffffff;
	}

	.permiso-nombre {
		font-weight: 600;
	}

	.permisos-resumen {
		display: flex;
		align-items: center;
		gap: 9px;
		margin-top: 18px;
		color: #cbd5e1;
		font-size: 12px;
	}

	.resumen-punto {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background: #60a5fa;
	}

	/* BOTONES */

	.formulario-acciones {
		display: flex;
		justify-content: flex-end;
		gap: 12px;
		margin-top: 28px;
		padding-top: 22px;
		border-top: 1px solid #334155;
	}

	.boton-guardar {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: 8px;
		min-height: 42px;
		padding: 10px 17px;
		border: 1px solid #3b82f6;
		border-radius: 8px;
		background: #2563eb;
		color: #ffffff;
		font-family: inherit;
		font-size: 13px;
		font-weight: 700;
		cursor: pointer;
		transition:
			background-color 0.2s ease,
			border-color 0.2s ease;
	}

	.boton-guardar:hover {
		border-color: #60a5fa;
		background: #1d4ed8;
	}

	.boton-guardar:focus-visible {
		outline: 2px solid #93c5fd;
		outline-offset: 3px;
	}

	/* TABLA */

	.tabla-panel {
		margin-bottom: 20px;
	}

	.encabezado-listado {
		min-height: 76px;
	}

	.etiqueta-pendiente {
		display: inline-flex;
		align-items: center;
		padding: 6px 10px;
		border: 1px solid #475569;
		border-radius: 20px;
		background: #172338;
		color: #cbd5e1;
		font-size: 11px;
		font-weight: 650;
		white-space: nowrap;
	}

	.tabla-contenedor {
		padding: 20px;
	}

	.tabla-roles {
		width: 100%;
		border-collapse: collapse;
		text-align: left;
	}

	.tabla-roles th {
		padding: 14px 16px;
		border-bottom: 1px solid #475569;
		background: #26364c;
		color: #f8fafc;
		font-size: 12px;
		font-weight: 750;
		white-space: nowrap;
	}

	.tabla-vacia {
		display: flex;
		min-height: 250px;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 30px 20px;
		text-align: center;
	}

	.tabla-vacia-icono {
		display: grid;
		width: 60px;
		height: 60px;
		place-items: center;
		margin-bottom: 18px;
		border: 1px solid #475569;
		border-radius: 16px;
		background: #172338;
		color: #93c5fd;
		font-size: 28px;
	}

	.tabla-vacia h3 {
		margin: 0;
		color: #f8fafc;
		font-size: 16px;
		font-weight: 750;
	}

	.tabla-vacia p {
		max-width: 430px;
		margin: 10px 0 0;
		color: #cbd5e1;
		font-size: 13px;
		line-height: 1.7;
	}

	.estado-vacio {
		margin-top: 17px;
		padding: 6px 10px;
		border: 1px solid #475569;
		border-radius: 7px;
		background: #172338;
		color: #cbd5e1;
		font-size: 11px;
	}

	/* RESPONSIVE */

	@media (max-width: 900px) {
		.permisos-lista {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}
	}

	@media (max-width: 650px) {
		.roles-container {
			padding: 20px 16px;
		}

		.panel-informativo {
			padding: 16px;
		}

		.acciones-roles {
			align-items: stretch;
			flex-direction: column;
		}

		.formulario-campos,
		.permisos-lista {
			grid-template-columns: minmax(0, 1fr);
		}

		.formulario-panel form {
			padding: 18px;
		}

		.formulario-acciones {
			align-items: stretch;
			flex-direction: column-reverse;
		}

		.encabezado-listado {
			align-items: flex-start;
			flex-direction: column;
		}

		.tabla-contenedor {
			overflow-x: auto;
			padding: 12px;
		}

		.tabla-roles {
			min-width: 540px;
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.permiso-opcion,
		.campo input,
		.campo textarea,
		.boton-guardar {
			transition: none;
		}
	}
</style>
