<script>
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { resolve } from '$app/paths';

	// Estado reactivo en Svelte 5
	let usuario = $state(null);

	onMount(() => {
		const sesion = localStorage.getItem('usuario_sesion');
		if (sesion) {
			try {
				usuario = JSON.parse(sesion);
			} catch (e) {
				usuario = null;
			}
		}
	});

	// Catálogo de módulos con control de visibilidad por rol:
	// Rol 1: Administrador, Rol 3: Decano, Rol 6: Docente
	const modulos = [
		{ nombre: 'Inicio', ruta: '/', icono: '⌂', roles: [1, 3, 6] },
		{ nombre: 'Espacios', ruta: '/espacios', icono: '▦', roles: [1, 3, 6] },
		{ nombre: 'Recursos', ruta: '/recursos', icono: '▣', roles: [1, 3, 6] },
		{ nombre: 'Reservas', ruta: '/reservas', icono: '▤', roles: [1, 3, 6] },
		{ nombre: 'Reportes', ruta: '/reportes', icono: '▥', roles: [1, 3] },
		{ nombre: 'Usuarios', ruta: '/usuarios', icono: '♙', roles: [1, 3] },
		{ nombre: 'Roles y permisos', ruta: '/roles-permisos', icono: '🔐', roles: [1] },
		{ nombre: 'Configuración', ruta: '/configuracion', icono: '⚙', roles: [1] }
	];

	// Filtrado reactivo de módulos según el rol de la sesión activa
	let modulosVisibles = $derived(
		usuario && usuario.id_rol
			? modulos.filter((m) => m.roles.includes(usuario.id_rol))
			: modulos
	);

	function estaActivo(ruta) {
		if (ruta === '/') {
			return page.url.pathname === '/';
		}
		return page.url.pathname === ruta || page.url.pathname.startsWith(`${ruta}/`);
	}
</script>

<aside class="sidebar">
	<div class="sidebar-separador"></div>

	<nav aria-label="Menú principal">
		<span class="sidebar-etiqueta">MENÚ PRINCIPAL</span>

		{#each modulosVisibles as modulo (modulo.ruta)}
			<a
				href={resolve(modulo.ruta)}
				class="sidebar-enlace"
				class:reservas-enlace={modulo.ruta === '/reservas'}
				class:activo={estaActivo(modulo.ruta)}
				aria-current={estaActivo(modulo.ruta) ? 'page' : undefined}
			>
				<span class="sidebar-icono" aria-hidden="true">{modulo.icono}</span>
				<span>{modulo.nombre}</span>
			</a>
		{/each}
	</nav>

	<div class="sidebar-pie">
		<span class="indicador-conexion"></span>
		<span>Portal universitario</span>
	</div>
</aside>

<style>
	.sidebar {
		width: 240px;
		min-width: 240px;
		min-height: 100%;
		display: flex;
		flex-direction: column;
		background: #111c31;
		color: #cbd5e1;
		padding: 20px 14px;
		box-sizing: border-box;
	}

	.sidebar-separador {
		height: 1px;
		background: rgba(255, 255, 255, 0.1);
		margin-bottom: 22px;
	}

	.sidebar nav {
		display: flex;
		flex-direction: column;
		gap: 6px;
	}

	.sidebar-etiqueta {
		display: block;
		margin: 0 10px 12px;
		color: #8493aa;
		font-size: 11px;
		font-weight: 700;
		letter-spacing: 1.2px;
	}

	.sidebar-enlace {
		position: relative;
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 12px 14px;
		border-radius: 8px;
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

	.sidebar-icono {
		display: inline-flex;
		width: 22px;
		min-width: 22px;
		align-items: center;
		justify-content: center;
		font-size: 19px;
		line-height: 1;
	}

	.sidebar-pie {
		display: flex;
		align-items: center;
		gap: 9px;
		margin-top: auto;
		padding: 18px 10px 4px;
		color: #8493aa;
		font-size: 12px;
	}

	.indicador-conexion {
		width: 8px;
		height: 8px;
		min-width: 8px;
		border-radius: 50%;
		background: #22c55e;
	}

	@media (max-width: 768px) {
		.sidebar {
			width: 100%;
			min-width: 0;
			min-height: auto;
			padding: 12px;
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
</style>
