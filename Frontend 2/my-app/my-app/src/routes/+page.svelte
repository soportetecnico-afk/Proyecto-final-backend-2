<script>
	import { onMount } from 'svelte';
	import { resolve } from '$app/paths';

	// Estado reactivo en Svelte 5
	let usuario = $state(null);

	onMount(() => {
		const sesion = localStorage.getItem('usuario_sesion');
		if (sesion) {
			try {
				usuario = JSON.parse(sesion);
			} catch (e) {
				console.error('Error al leer sesión', e);
			}
		} else {
			// Si no hay sesión iniciada, redirige al login
			window.location.href = '/login';
		}
	});

	// Catálogo de módulos con control de acceso por rol
	// Rol 1: Admin, Rol 3: Decano, Rol 6: Docente
	const todosLosModulos = [
		{
			nombre: 'Reservas',
			ruta: '/reservas',
			categoria: 'GESTIÓN ACADÉMICA',
			descripcion: 'Gestiona las reservas de espacios universitarios.',
			icono: '▦',
			claseIcono: 'icono-azul',
			rolesPermitidos: [1, 3, 6]
		},
		{
			nombre: 'Espacios',
			ruta: '/espacios',
			categoria: 'INFRAESTRUCTURA',
			descripcion: 'Consulta y administra los espacios físicos disponibles.',
			icono: '⌂',
			claseIcono: 'icono-verde',
			rolesPermitidos: [1, 3, 6]
		},
		{
			nombre: 'Recursos',
			ruta: '/recursos',
			categoria: 'EQUIPAMIENTO',
			descripcion: 'Consulta los recursos inventariados y su estado.',
			icono: '▣',
			claseIcono: 'icono-morado',
			rolesPermitidos: [1, 3, 6]
		},
		{
			nombre: 'Reportes',
			ruta: '/reportes',
			categoria: 'INFORMACIÓN',
			descripcion: 'Consulta los reportes y bitácoras de auditoría del sistema.',
			icono: '▥',
			claseIcono: 'icono-amarillo',
			rolesPermitidos: [1, 3] // Exclusivo para Administrador y Decano
		},
		{
			nombre: 'Usuarios',
			ruta: '/usuarios',
			categoria: 'ADMINISTRACIÓN',
			descripcion: 'Directorio institucional de usuarios y cargos.',
			icono: '♟',
			claseIcono: 'icono-cian',
			rolesPermitidos: [1, 3] // Exclusivo para Administrador y Decano
		},
		{
			nombre: 'Configuración',
			ruta: '/configuracion',
			categoria: 'SISTEMA',
			descripcion: 'Administra las opciones y parámetros generales de la plataforma.',
			icono: '⚙️',
			claseIcono: 'icono-gris',
			rolesPermitidos: [1] // Exclusivo para Administrador
		}
	];

	// Módulos derivados según el rol activo
	let modulosVisibles = $derived(
		usuario
			? todosLosModulos.filter((m) => m.rolesPermitidos.includes(usuario.id_rol))
			: todosLosModulos
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

		<h1>Sistema de Reservas CUL</h1>

		<h2>
			{#if usuario}
				Bienvenido, {usuario.nombre} ({usuario.rol || 'Usuario'})
			{:else}
				Gestión de Espacios Universitarios
			{/if}
		</h2>

		<p>
			Administra y consulta los espacios universitarios, los recursos disponibles y las reservas
			desde una plataforma centralizada y sincronizada con PostgreSQL.
		</p>
	</section>

	<!-- MÓDULOS -->
	<section class="modulos-seccion">
		<div class="modulos-encabezado">
			<div>
				<h2>Módulos autorizados</h2>
				<p>Accesos habilitados según tu perfil institucional en la base de datos.</p>
			</div>
		</div>

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
	</section>

	<!-- INFORMACIÓN INFERIOR -->
	<section class="informacion-panel">
		<div class="informacion-icono" aria-hidden="true">i</div>

		<div class="informacion-texto">
			<strong>Sesión institucional activa</strong>
			<p>
				Operando con permisos correspondientes al perfil asignado en la tabla de roles de PostgreSQL.
			</p>
		</div>
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

	.presentacion h2 {
		margin: 14px 0 0;
		color: #60a5fa;
		font-size: 17px;
		font-weight: 650;
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
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 20px;
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
		border: 1px solid #355d91;
		border-radius: 9px;
		background: #1e3a63;
		color: #eff6ff;
		font-size: 12px;
		font-weight: 700;
		transition:
			background-color 0.2s ease,
			border-color 0.2s ease;
	}

	.modulo-tarjeta:hover .modulo-accion {
		border-color: #4b83c7;
		background: #264b7b;
	}

	.modulo-accion span:last-child {
		font-size: 17px;
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

		.presentacion h2 {
			font-size: 15px;
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
</style>