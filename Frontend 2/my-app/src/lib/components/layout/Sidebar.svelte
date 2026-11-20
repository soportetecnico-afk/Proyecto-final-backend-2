<script>
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { resolve } from '$app/paths';

	// Estado del usuario
	let usuario = $state(null);

	onMount(() => {
		const sesion = localStorage.getItem('usuario_sesion');

		if (sesion) {
			try {
				usuario = JSON.parse(sesion);
			} catch (e) {
				console.error('Error al recuperar la sesión:', e);
				usuario = null;
			}
		}
	});

	// Roles oficiales de PostgreSQL:
	// 1: Administrador
	// 3: Decano
	// 5: Docente

	function obtenerIdRol(usuarioActual) {
		const id = Number(
			usuarioActual?.id_rol ?? usuarioActual?.rol_id
		);

		if ([1, 3, 5].includes(id)) {
			return id;
		}

		const nombre = String(
			usuarioActual?.rol ??
			usuarioActual?.nombre_rol ??
			''
		).trim().toLowerCase();

		if (nombre === 'administrador') return 1;
		if (nombre === 'decano') return 3;
		if (nombre === 'docente') return 5;

		return null;
	}

	// Módulos disponibles según el perfil

	const modulos = [
		{
			nombre: 'Inicio',
			ruta: '/',
			icono: '⌂',
			roles: [1, 3, 5]
		},
		{
			nombre: 'Espacios',
			ruta: '/espacios',
			icono: '▦',
			roles: [1, 3, 5]
		},
		{
			nombre: 'Recursos',
			ruta: '/recursos',
			icono: '▣',
			roles: [1, 3, 5]
		},
		{
			nombre: 'Reservas',
			ruta: '/reservas',
			icono: '▤',
			roles: [1, 3, 5]
		},
		{
			nombre: 'Tablero',
			ruta: '/tablero',
			icono: '▥',
			roles: [1, 3]
		},
		{
			nombre: 'Reportes',
			ruta: '/reportes',
			icono: '▧',
			roles: [1, 3]
		},
		{
			nombre: 'Usuarios',
			ruta: '/usuarios',
			icono: '♙',
			roles: [1, 3]
		},
		{
			nombre: 'Roles y permisos',
			ruta: '/roles-permisos',
			icono: '🔐',
			roles: [1]
		}
	];

	// Filtrar módulos según el rol

	let rolActual = $derived(obtenerIdRol(usuario));

	let modulosVisibles = $derived(
		rolActual !== null
			? modulos.filter((modulo) =>
					modulo.roles.includes(rolActual)
				)
			: []
	);

	// Identificar módulo seleccionado

	function estaActivo(ruta) {
		if (ruta === '/') {
			return page.url.pathname === '/';
		}

		return (
			page.url.pathname === ruta ||
			page.url.pathname.startsWith(`${ruta}/`)
		);
	}
</script>

<aside class="sidebar">

	<div class="sidebar-separador"></div>

	<nav aria-label="Menú principal">

		<span class="sidebar-etiqueta">
			MENÚ PRINCIPAL
		</span>

		{#each modulosVisibles as modulo (modulo.ruta)}

			<a
				href={resolve(modulo.ruta)}
				class="sidebar-enlace"
				class:reservas-enlace={modulo.ruta === '/reservas'}
				class:activo={estaActivo(modulo.ruta)}
				aria-current={estaActivo(modulo.ruta) ? 'page' : undefined}
				title={modulo.nombre}
			>

				<span class="sidebar-icono" aria-hidden="true">
					{modulo.icono}
				</span>

				<span class="sidebar-texto">
					{modulo.nombre}
				</span>

			</a>

		{/each}

	</nav>

	<!-- Parte inferior del menú -->

	<div class="sidebar-pie">

		<span class="sidebar-texto">
			Portal universitario
		</span>

	</div>

</aside>

<style>

/* =========================================
   BARRA LATERAL
========================================= */

.sidebar {
	width: 68px;
	min-width: 68px;
	flex: 0 0 68px;

	/* Altura desde debajo del encabezado
	   hasta la parte inferior de la pantalla */

	height: calc(100vh - 56px);
	min-height: calc(100vh - 56px);

	align-self: stretch;
	flex-shrink: 0;

	display: flex;
	flex-direction: column;

	background: #111c31;
	color: #cbd5e1;

	padding: 20px 9px;

	box-sizing: border-box;

	overflow: hidden;
	white-space: nowrap;

	position: relative;
	z-index: 100;

	transition:
		width 0.3s ease,
		min-width 0.3s ease,
		flex-basis 0.3s ease,
		box-shadow 0.3s ease;
}

/* =========================================
   EXPANSIÓN AL PASAR EL CURSOR
========================================= */

.sidebar:hover,
.sidebar:focus-within {

	width: 240px;
	min-width: 240px;
	flex-basis: 240px;

	box-shadow: 8px 0 25px rgba(0, 0, 0, 0.25);

}

/* =========================================
   SEPARADOR
========================================= */

.sidebar-separador {

	height: 1px;
	min-height: 1px;

	background: rgba(255, 255, 255, 0.1);

	margin-bottom: 22px;

}

/* =========================================
   NAVEGACIÓN
========================================= */

.sidebar nav {

	display: flex;
	flex-direction: column;
	gap: 6px;

}

/* =========================================
   TÍTULO DEL MENÚ
========================================= */

.sidebar-etiqueta {

	display: block;

	margin: 0 10px 12px;

	color: #8493aa;

	font-size: 11px;
	font-weight: 700;
	letter-spacing: 1.2px;

	opacity: 0;

	transition: opacity 0.2s ease;

}

.sidebar:hover .sidebar-etiqueta,
.sidebar:focus-within .sidebar-etiqueta {

	opacity: 1;

}

/* =========================================
   ENLACES
========================================= */

.sidebar-enlace {

	position: relative;

	display: flex;
	align-items: center;

	gap: 12px;

	width: 100%;
	min-height: 42px;

	padding: 12px 14px;

	border-radius: 8px;

	box-sizing: border-box;

	color: #cbd5e1;
	text-decoration: none;

	font-size: 14px;
	font-weight: 500;

	transition:
		background-color 0.2s ease,
		color 0.2s ease;

}

.sidebar-enlace:hover {

	background: rgba(255, 255, 255, 0.08);

	color: #ffffff;

}

/* Módulo seleccionado */

.sidebar-enlace.activo {

	background: #2563eb;

	color: #ffffff;

	font-weight: 600;

}

:global(html[data-tema='claro']) .sidebar-enlace.reservas-enlace {
	color: #123675 !important;
}

:global(html[data-tema='claro']) .sidebar-enlace.reservas-enlace.activo {
	color: #ffffff !important;
}

.sidebar-enlace.activo::before {

	position: absolute;

	top: 8px;
	bottom: 8px;
	left: 0;

	width: 3px;

	border-radius: 0 3px 3px 0;

	background: #93c5fd;

	content: '';

}

/* =========================================
   ICONOS
========================================= */

.sidebar-icono {

	display: inline-flex;

	width: 22px;
	min-width: 22px;

	align-items: center;
	justify-content: center;

	font-size: 19px;
	line-height: 1;

}

/* =========================================
   TEXTO DE LOS MÓDULOS
========================================= */

.sidebar-texto {

	display: inline-block;

	width: 0;

	opacity: 0;

	overflow: hidden;

	transition:
		opacity 0.2s ease,
		width 0.3s ease;

}

.sidebar:hover .sidebar-texto,
.sidebar:focus-within .sidebar-texto {

	width: auto;

	opacity: 1;

}

/* =========================================
   PIE INFERIOR
========================================= */

.sidebar-pie {

	display: flex;
	align-items: center;

	gap: 9px;

	margin-top: auto;

	padding: 18px 10px 4px;

	color: #8493aa;

	font-size: 12px;

	flex-shrink: 0;

}

/* Indicador verde */

.indicador-conexion {

	width: 8px;
	height: 8px;

	min-width: 8px;

	border-radius: 50%;

	background: #22c55e;

}

/* =========================================
   DISPOSITIVOS MÓVILES
========================================= */

@media (max-width: 768px) {

	.sidebar {

		width: 100%;
		min-width: 100%;
		flex-basis: 100%;

		height: auto;
		min-height: auto;

		padding: 12px;

	}

	.sidebar-texto {

		width: auto;
		opacity: 1;

	}

	.sidebar-etiqueta {

		opacity: 1;

	}

	.sidebar-separador {

		margin-bottom: 12px;

	}

	.sidebar nav {

		gap: 4px;

	}

	.sidebar-enlace {

		padding: 10px 12px;

	}

	.sidebar-pie {

		margin-top: 18px;

	}

}

/* =========================================
   ACCESIBILIDAD
========================================= */

@media (prefers-reduced-motion: reduce) {

	.sidebar,
	.sidebar-texto,
	.sidebar-enlace {

		transition: none;

	}

}

</style>
