<script>
	import { onMount } from 'svelte';
	import { resolve } from '$app/paths';

	let usuario = $state(null);

	onMount(() => {
		const sesion = localStorage.getItem('usuario_sesion');

		if (!sesion) {
			window.location.href = '/login';
			return;
		}

		try {
			usuario = JSON.parse(sesion);
		} catch (error) {
			console.error('Error al leer la sesión:', error);
			localStorage.removeItem('usuario_sesion');
			window.location.href = '/login';
		}
	});

	// Catálogo de módulos. Los permisos se validan tanto por ID como por nombre del rol.
	const todosLosModulos = [
		{
			nombre: 'Reservas',
			ruta: '/reservas',
			categoria: 'GESTIÓN ACADÉMICA',
			descripcion: 'Gestiona y consulta las reservas de espacios universitarios.',
			icono: '▦',
			claseIcono: 'icono-azul',
			rolesPermitidos: ['administrador', 'decano', 'docente']
		},
		{
			nombre: 'Espacios',
			ruta: '/espacios',
			categoria: 'INFRAESTRUCTURA',
			descripcion: 'Consulta los espacios físicos disponibles.',
			icono: '⌂',
			claseIcono: 'icono-verde',
			rolesPermitidos: ['administrador', 'decano', 'docente']
		},
		{
			nombre: 'Recursos',
			ruta: '/recursos',
			categoria: 'EQUIPAMIENTO',
			descripcion: 'Consulta y administra los recursos inventariados y su estado.',
			icono: '▣',
			claseIcono: 'icono-morado',
			rolesPermitidos: ['administrador', 'decano', 'docente']
		},
		{
			nombre: 'Reportes',
			ruta: '/reportes',
			categoria: 'INFORMACIÓN',
			descripcion: 'Consulta los reportes y las bitácoras de auditoría del sistema.',
			icono: '▥',
			claseIcono: 'icono-amarillo',
			rolesPermitidos: ['administrador', 'decano']
		},
		{
			nombre: 'Usuarios',
			ruta: '/usuarios',
			categoria: 'ADMINISTRACIÓN',
			descripcion: 'Directorio institucional de usuarios y cargos.',
			icono: '♟',
			claseIcono: 'icono-cian',
			rolesPermitidos: ['administrador', 'decano']
		}
	];

	function normalizarTexto(valor) {
		return String(valor ?? '')
			.normalize('NFD')
			.replace(/[\u0300-\u036f]/g, '')
			.toLowerCase()
			.trim();
	}

	function obtenerRolUsuario(datos) {
		if (!datos) return '';

		// Primero se identifica el rol por su nombre, si la sesión lo proporciona.
		const nombreRol = normalizarTexto(
			datos.rol ?? datos.nombre_rol ?? datos.tipo_rol ?? datos.nombreRol ?? ''
		);

		if (nombreRol.includes('docente') || nombreRol.includes('profesor')) return 'docente';
		if (nombreRol.includes('decano')) return 'decano';
		if (
			nombreRol.includes('administrador') ||
			nombreRol === 'admin' ||
			nombreRol.includes('superadmin')
		) return 'administrador';

		// Si no viene el nombre del rol, se utiliza el identificador de la sesión.
		const idRol = Number(datos.id_rol ?? datos.rol_id ?? datos.idRol ?? datos.role_id);

		if (idRol === 1) return 'administrador';
		if (idRol === 3) return 'decano';
		if (idRol === 6) return 'docente';

		return '';
	}

	let rolActual = $derived(obtenerRolUsuario(usuario));

	let modulosVisibles = $derived(
		todosLosModulos.filter((modulo) => modulo.rolesPermitidos.includes(rolActual))
	);
</script>

<svelte:head>
	<title>Inicio - Sistema de Reservas CUL</title>
	<meta name="description" content="Sistema de Reservas y Gestión de Espacios Universitarios CUL" />
</svelte:head>

<div class="inicio-container">
	<!-- PRESENTACIÓN -->
	<section class="presentacion">
		<div class="presentacion-etiqueta">
			<span class="indicador"></span>
			PORTAL UNIVERSITARIO
		</div>

		<h1>
			{#if usuario}
				Bienvenido, {usuario.nombre || usuario.nombre_completo || usuario.nombres || 'Usuario'}
			{:else}
				Gestión de Espacios Universitarios
			{/if}
		</h1>

	</section>

	<!-- MÓDULOS -->
	<section class="modulos-seccion">
		<div class="modulos-encabezado">
			<div>
				<h2>Accesos Rápidos</h2>
			</div>
		</div>

		{#if modulosVisibles.length > 0}
		<div class="modulos-grid">
			{#each modulosVisibles as modulo}
				<a href={resolve(modulo.ruta)} class="modulo-tarjeta">
					<div class="modulo-superior">
						<div class="modulo-icono {modulo.claseIcono}" aria-hidden="true">{modulo.icono}</div>
						<span class="modulo-flecha" aria-hidden="true">↗</span>
					</div>

					<span class="modulo-categoria">{modulo.categoria}</span>

					<h3>{modulo.nombre}</h3>

					<p>{modulo.descripcion}</p>

					<div class="modulo-accion">
						<span>Acceder</span>
						<span aria-hidden="true">→</span>
					</div>
				</a>
			{/each}
		</div>
		{:else}
			<div class="sin-modulos" role="status">
				No se pudo identificar tu perfil de acceso. Cierra sesión e ingresa nuevamente.
			</div>
		{/if}
	</section>

</div>

<style>
	:global(body) {
		margin: 0;
		background: #0f172a;
		color: #f8fafc;
		font-family:
			system-ui,
			-apple-system,
			BlinkMacSystemFont,
			'Segoe UI',
			sans-serif;
	}

	.inicio-container {
		width: 100%;
		max-width: 1800px;
		margin: 0 auto;
		padding: 32px;
		box-sizing: border-box;
	}

	.presentacion {
		display: flex;
		flex-direction: column;
		align-items: center;
		margin: 8px auto 44px;
		text-align: center;
	}

	.presentacion-etiqueta {
		display: inline-flex;
		align-items: center;
		gap: 9px;
		margin-bottom: 22px;
		padding: 9px 15px;
		border: 1px solid #334155;
		border-radius: 30px;
		background: #172338;
		color: #bfdbfe;
		font-size: 10px;
		font-weight: 800;
		letter-spacing: 1.3px;
	}

	:global(html[data-tema='claro']) .presentacion-etiqueta {
		background: #ffffff;
		color: #2563eb;
	}

	.indicador {
		width: 7px;
		height: 7px;
		border-radius: 50%;
		background: #60a5fa;
	}

	.presentacion h1 {
		margin: 0;
		color: #f8fafc;
		font-size: clamp(28px, 3vw, 40px);
		font-weight: 800;
		letter-spacing: -1px;
		line-height: 1.2;
	}

	:global(html[data-tema='claro'] .app-main .inicio-container .presentacion h1) {
		color: #2563eb !important;
	}


	.presentacion > p {
		max-width: 720px;
		margin: 16px 0 0;
		color: #cbd5e1;
		font-size: 13px;
		line-height: 1.9;
	}

	.modulos-seccion {
		width: 100%;
	}

	.modulos-encabezado {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 22px;
	}

	.modulos-encabezado h2 {
		margin: 0;
		color: #f8fafc;
		font-size: 20px;
		font-weight: 750;
	}

	.modulos-encabezado p {
		margin: 7px 0 0;
		color: #a9bad3;
		font-size: 12px;
	}

	.modulos-grid {
		display: grid;
		/* Seis columnas permiten centrar la segunda fila sin cambiar
		   el ancho visual de las tarjetas de la primera fila. */
		grid-template-columns: repeat(6, minmax(0, 1fr));
		gap: 20px;
	}

	.modulos-grid > .modulo-tarjeta {
		grid-column: span 2;
	}

	/* Cuando hay cinco módulos, centra las dos tarjetas de la segunda fila. */
	.modulos-grid > .modulo-tarjeta:nth-child(4) {
		grid-column: 2 / span 2;
	}

	.modulos-grid > .modulo-tarjeta:nth-child(5) {
		grid-column: 4 / span 2;
	}

	.modulo-tarjeta {
		display: flex;
		min-width: 0;
		min-height: 218px;
		flex-direction: column;
		padding: 22px;
		border: 1px solid #334155;
		border-radius: 14px;
		background: #1e293b;
		color: inherit;
		text-decoration: none;
		box-sizing: border-box;
		transition:
			transform 0.2s ease,
			border-color 0.2s ease,
			background-color 0.2s ease,
			box-shadow 0.2s ease;
	}

	.modulo-tarjeta:hover {
		transform: translateY(-3px);
		border-color: #4b75a8;
		background: #223149;
		box-shadow: 0 12px 26px rgb(0 0 0 / 15%);
	}

	.modulo-tarjeta:focus-visible {
		outline: 2px solid #60a5fa;
		outline-offset: 4px;
	}

	.modulo-superior {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 22px;
	}

	.modulo-icono {
		display: grid;
		width: 48px;
		height: 48px;
		flex-shrink: 0;
		place-items: center;
		border: 1px solid;
		border-radius: 12px;
		font-size: 25px;
		font-weight: 700;
	}

	.icono-azul {
		border-color: #3b82f6;
		background: rgb(59 130 246 / 12%);
		color: #60a5fa;
	}

	.icono-verde {
		border-color: #16a34a;
		background: rgb(22 163 74 / 12%);
		color: #4ade80;
	}

	.icono-morado {
		border-color: #8b5cf6;
		background: rgb(139 92 246 / 12%);
		color: #c4b5fd;
	}

	.icono-amarillo {
		border-color: #ca8a04;
		background: rgb(202 138 4 / 12%);
		color: #facc15;
	}

	.icono-cian {
		border-color: #0891b2;
		background: rgb(8 145 178 / 12%);
		color: #67e8f9;
	}

	.icono-gris {
		border-color: #64748b;
		background: rgb(100 116 139 / 15%);
		color: #cbd5e1;
	}

	.modulo-flecha {
		display: grid;
		width: 34px;
		height: 34px;
		place-items: center;
		border: 1px solid #334155;
		border-radius: 9px;
		color: #93c5fd;
		font-size: 17px;
		transition:
			background-color 0.2s ease,
			border-color 0.2s ease;
	}

	.modulo-tarjeta:hover .modulo-flecha {
		border-color: #3b82f6;
		background: #1d3b68;
	}

	.modulo-categoria {
		margin-bottom: 10px;
		color: #93b9e9;
		font-size: 10px;
		font-weight: 800;
		letter-spacing: 1px;
	}

	.modulo-tarjeta h3 {
		margin: 0;
		color: #f8fafc;
		font-size: 17px;
		font-weight: 750;
	}

	.modulo-tarjeta > p {
		margin: 10px 0 20px;
		color: #cbd5e1;
		font-size: 12px;
		line-height: 1.7;
	}

	.modulo-accion {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 12px;
		min-height: 46px;
		margin-top: auto;
		padding: 0 13px;
		border: 1px solid #bfdbfe;
		border-radius: 9px;
		background: #ffffff;
		color: #1d4ed8;
		font-size: 12px;
		font-weight: 700;
		transition:
			background-color 0.2s ease,
			border-color 0.2s ease;
	}

	.modulo-tarjeta:hover .modulo-accion {
		border-color: #93c5fd;
		background: #eff6ff;
		color: #1e40af;
	}

	.modulo-accion span:last-child {
		font-size: 17px;
	}

	:global(html[data-tema='oscuro']) .inicio-container .modulo-accion {
		border-color: #334155;
		background: #1e293b;
		color: #f8fafc;
	}

	:global(html[data-tema='oscuro']) .inicio-container .modulo-tarjeta:hover .modulo-accion {
		border-color: #475569;
		background: #263449;
		color: #ffffff;
	}

	.informacion-panel {
		display: flex;
		align-items: flex-start;
		gap: 14px;
		margin-top: 24px;
		padding: 20px;
		border: 1px solid #334155;
		border-radius: 12px;
		background: #172338;
	}

	.informacion-icono {
		display: grid;
		width: 34px;
		height: 34px;
		flex-shrink: 0;
		place-items: center;
		border: 1px solid #3b82f6;
		border-radius: 50%;
		color: #93c5fd;
		font-size: 16px;
		font-weight: 700;
	}

	.informacion-texto strong {
		color: #f8fafc;
		font-size: 12px;
	}

	.informacion-texto p {
		margin: 7px 0 0;
		color: #a9bad3;
		font-size: 12px;
		line-height: 1.6;
	}

	@media (max-width: 1100px) {
		.inicio-container {
			padding: 24px;
		}

		.modulos-grid {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}

		.modulos-grid > .modulo-tarjeta,
		.modulos-grid > .modulo-tarjeta:nth-child(4),
		.modulos-grid > .modulo-tarjeta:nth-child(5) {
			grid-column: auto;
		}
	}

	@media (max-width: 650px) {
		.inicio-container {
			padding: 20px 16px;
		}

		.presentacion {
			margin-bottom: 32px;
		}

		.presentacion h1 {
			font-size: 29px;
		}


		.modulos-grid {
			grid-template-columns: minmax(0, 1fr);
			gap: 14px;
		}

		.modulo-tarjeta {
			min-height: 205px;
			padding: 20px;
		}

		.informacion-panel {
			padding: 16px;
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.modulo-tarjeta,
		.modulo-flecha,
		.modulo-accion {
			transition: none;
		}
	}


	.sin-modulos {
		padding: 20px;
		border: 1px solid #475569;
		border-radius: 12px;
		background: #172338;
		color: #cbd5e1;
		font-size: 13px;
		text-align: center;
	}
</style>
