<script>
	import PageHeader from '$lib/components/ui/PageHeader.svelte';
	import BaseButton from '$lib/components/ui/BaseButton.svelte';
	import FormInput from '$lib/components/ui/FormInput.svelte';
	import FormSelect from '$lib/components/ui/FormSelect.svelte';
	import DataTable from '$lib/components/ui/DataTable.svelte';

	let mostrarFormulario = $state(false);
	let nombreCompleto = $state('');
	let correoElectronico = $state('');
	let telefono = $state('');
	let rol = $state('');
	let facultad = $state('');
	let estadoUsuario = $state('');

	let buscarNombre = $state('');
	let buscarCorreo = $state('');
	let buscarRol = $state('');

	let cargando = $state(false);
	let mensajeError = $state('');
	let mensajeExito = $state('');

	const opcionesRoles = [];
	const opcionesFacultades = [];

	const opcionesEstados = [
		{ valor: 'activo', etiqueta: 'Activo' },
		{ valor: 'inactivo', etiqueta: 'Inactivo' }
	];

	const columnas = [
		{ clave: 'id', etiqueta: 'ID' },
		{ clave: 'nombreCompleto', etiqueta: 'Nombre completo' },
		{ clave: 'correoElectronico', etiqueta: 'Correo electrónico' },
		{ clave: 'telefono', etiqueta: 'Teléfono' },
		{ clave: 'rol', etiqueta: 'Rol' },
		{ clave: 'facultad', etiqueta: 'Facultad' },
		{ clave: 'estadoUsuario', etiqueta: 'Estado' },
		{ clave: 'acciones', etiqueta: 'Acciones' }
	];

	// Los datos reales se cargarán desde FastAPI.
	const usuarios = $state([]);

	const usuariosFiltrados = $derived(
		usuarios.filter((usuario) => {
			const nombre = String(usuario.nombreCompleto ?? '').toLowerCase();
			const correo = String(usuario.correoElectronico ?? '').toLowerCase();
			const rolUsuario = String(usuario.rol ?? '').toLowerCase();

			return (
				nombre.includes(buscarNombre.trim().toLowerCase()) &&
				correo.includes(buscarCorreo.trim().toLowerCase()) &&
				(!buscarRol || rolUsuario === buscarRol.toLowerCase())
			);
		})
	);

	function limpiarFormulario() {
		nombreCompleto = '';
		correoElectronico = '';
		telefono = '';
		rol = '';
		facultad = '';
		estadoUsuario = '';
		mensajeError = '';
		mensajeExito = '';
	}

	function abrirFormulario() {
		limpiarFormulario();
		mostrarFormulario = true;
	}

	function cancelarFormulario() {
		limpiarFormulario();
		mostrarFormulario = false;
	}

	function guardarUsuario(evento) {
		evento.preventDefault();
		mensajeError = '';
		mensajeExito = '';

		if (
			!nombreCompleto.trim() ||
			!correoElectronico.trim() ||
			!rol ||
			!facultad ||
			!estadoUsuario
		) {
			mensajeError = 'Completa todos los campos obligatorios.';
			return;
		}

		mensajeExito =
			'Formulario validado. El registro estará disponible cuando conectemos el backend.';
	}
</script>

```svelte

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
		onAccion={() => {
			if (mostrarFormulario) {
				cancelarFormulario();
			} else {
				abrirFormulario();
			}
		}}
	/>

	{#if mostrarFormulario}
		<section class="panel">
			<div class="panel-encabezado">
				<div>
					<h2>Registrar usuario</h2>
					<p>Completa la información del usuario y configura su acceso.</p>
				</div>
			</div>

			<form class="formulario-contenido" onsubmit={guardarUsuario}>
				<div class="formulario-grid">
					<FormInput
						id="nombreCompleto"
						label="Nombre completo"
						bind:valor={nombreCompleto}
						placeholder="Ingrese el nombre completo"
						requerido
					/>

					<FormInput
						id="correoElectronico"
						label="Correo electrónico"
						tipo="email"
						bind:valor={correoElectronico}
						placeholder="Ingrese el correo electrónico"
						requerido
					/>

					<FormInput
						id="telefono"
						label="Teléfono"
						tipo="tel"
						bind:valor={telefono}
						placeholder="Ingrese el teléfono"
					/>

					<FormSelect
						id="rol"
						label="Rol"
						bind:valor={rol}
						opciones={opcionesRoles}
						placeholder="Seleccionar rol"
						requerido
					/>

					<FormSelect
						id="facultad"
						label="Facultad"
						bind:valor={facultad}
						opciones={opcionesFacultades}
						placeholder="Seleccionar facultad"
						requerido
					/>

					<FormSelect
						id="estadoUsuario"
						label="Estado"
						bind:valor={estadoUsuario}
						opciones={opcionesEstados}
						placeholder="Seleccionar estado"
						requerido
					/>
				</div>

				{#if mensajeError}
					<div class="mensaje-formulario mensaje-error" role="alert">
						{mensajeError}
					</div>
				{/if}

				{#if mensajeExito}
					<div class="mensaje-formulario mensaje-exito" role="status">
						{mensajeExito}
					</div>
				{/if}

				<div class="formulario-nota">
					<span aria-hidden="true">ⓘ</span>
					Los registros se habilitarán al conectar el formulario con FastAPI.
				</div>

				<div class="formulario-acciones">
					<BaseButton texto="Cancelar" variante="secundario" onClick={cancelarFormulario} />
					<BaseButton texto="Guardar usuario" variante="primario" tipo="submit" />
				</div>
			</form>
		</section>
	{/if}

	<section class="panel">
		<div class="panel-encabezado">
			<div>
				<h2>Buscar usuarios</h2>
				<p>Utiliza los filtros para localizar usuarios registrados.</p>
			</div>
		</div>

		<div class="filtros-grid">
			<FormInput
				id="buscarNombre"
				label="Nombre"
				bind:valor={buscarNombre}
				placeholder="Buscar por nombre..."
			/>

			<FormInput
				id="buscarCorreo"
				label="Correo electrónico"
				bind:valor={buscarCorreo}
				placeholder="Buscar por correo..."
			/>

			<FormSelect
				id="buscarRol"
				label="Rol"
				bind:valor={buscarRol}
				opciones={opcionesRoles}
				placeholder="Todos los roles"
			/>
		</div>
	</section>

	<section class="panel">
		<div class="panel-encabezado tabla-encabezado">
			<div>
				<h2>Usuarios registrados</h2>
				<p>Consulta la información y el estado de los usuarios.</p>
			</div>

		</div>

		<div class="tabla-contenedor">
			<DataTable
				{columnas}
				filas={usuariosFiltrados}
				{cargando}
				mensajeVacio="No hay usuarios cargados. Los registros aparecerán aquí cuando conectemos la base de datos."
			/>
		</div>
	</section>
</div>

<style>
	.usuarios-container {
		width: 100%;
		max-width: 1600px;
		margin: 0 auto;
		padding: 32px;
		box-sizing: border-box;
		color: #f8fafc;
	}

	.panel {
		width: 100%;
		margin-bottom: 24px;
		overflow: hidden;
		border: 1px solid #334155;
		border-radius: 12px;
		background: #1e293b;
		box-sizing: border-box;
	}

	.panel-encabezado {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 16px;
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
		color: #b7c5d9;
		font-size: 13px;
		line-height: 1.6;
	}

	.filtros-grid {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 20px;
		padding: 24px;
	}

	.formulario-contenido {
		padding: 24px;
	}

	.formulario-grid {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 22px;
	}

	.formulario-nota {
		display: flex;
		align-items: flex-start;
		gap: 10px;
		margin-top: 24px;
		padding: 14px;
		border: 1px solid #334155;
		border-radius: 8px;
		background: #172338;
		color: #cbd5e1;
		font-size: 12px;
		line-height: 1.7;
	}

	.formulario-nota span {
		color: #60a5fa;
		font-size: 17px;
	}

	.mensaje-formulario {
		margin-top: 20px;
		padding: 12px 14px;
		border: 1px solid #475569;
		border-radius: 8px;
		font-size: 13px;
		line-height: 1.6;
	}

	.mensaje-error {
		background: #451a1a;
		color: #fecaca;
	}

	.mensaje-exito {
		background: #143326;
		color: #bbf7d0;
	}

	.formulario-acciones {
		display: flex;
		justify-content: flex-end;
		gap: 12px;
		margin-top: 24px;
		padding-top: 20px;
		border-top: 1px solid #334155;
	}

	.estado-conexion {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		flex-shrink: 0;
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
		box-sizing: border-box;
	}

	@media (max-width: 1000px) {
		.filtros-grid {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}
	}

	@media (max-width: 650px) {
		.usuarios-container {
			padding: 22px 16px;
		}

		.panel-encabezado {
			align-items: flex-start;
			flex-direction: column;
			padding: 18px;
		}

		.filtros-grid,
		.formulario-grid {
			grid-template-columns: minmax(0, 1fr);
		}

		.filtros-grid,
		.formulario-contenido {
			padding: 18px;
		}

		.formulario-acciones {
			flex-direction: column-reverse;
		}

		.tabla-contenedor {
			padding: 12px;
		}

		.estado-conexion {
			align-self: flex-start;
		}
	}
</style>
