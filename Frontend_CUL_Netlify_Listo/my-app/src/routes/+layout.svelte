<script>
	import { onMount } from 'svelte';
	import { afterNavigate } from '$app/navigation';
	import { page } from '$app/state';

	import Navbar from '$lib/components/layout/Navbar.svelte';
	import Sidebar from '$lib/components/layout/Sidebar.svelte';
	import Footer from '$lib/components/layout/Footer.svelte';
	

	let { children } = $props();
	let esLogin = $derived(page.url.pathname === '/login');
	let esTableroCompartido = $derived(page.url.pathname === '/tablero/vista');

	function verificarAcceso() {
		if (typeof window === 'undefined') return;

		const rutaActual = window.location.pathname;
		const sesion = localStorage.getItem('usuario_sesion');

		// Una ruta interna requiere una sesión.
		if (rutaActual !== '/login' && rutaActual !== '/tablero/vista' && !sesion) {
			window.location.replace('/login');
			return;
		}

		// Si ya inició sesión, no debe regresar al formulario de login.
		if (rutaActual === '/login' && sesion) {
			window.location.replace('/');
		}
	}

	onMount(() => {
		verificarAcceso();

		// Revalida al restaurar una página desde la caché del navegador.
		const alMostrarPagina = () => verificarAcceso();
		window.addEventListener('pageshow', alMostrarPagina);

		return () => window.removeEventListener('pageshow', alMostrarPagina);
	});

	// También protege las navegaciones internas y el botón Atrás/Adelante.
	afterNavigate(() => verificarAcceso());
</script>

{#if esTableroCompartido}
	{@render children()}
{:else if esLogin}
	<div class="login-layout">
		{@render children()}
	</div>
{:else}
	<div class="app-layout">
		<Navbar />
		<div class="app-contenido">
			<Sidebar />
			<main class="app-main">
				{@render children()}
			</main>
		</div>
		<Footer />
	</div>
{/if}

<style>
	:global(html),
	:global(body) {
		min-height: 100%;
		margin: 0;
		background: #0f172a !important;
		color: #f8fafc;
	}

	:global(*) { box-sizing: border-box; }

	.app-layout {
		display: flex;
		min-height: 100vh;
		flex-direction: column;
		background: #0f172a;
	}

	.app-contenido { display: flex; flex: 1; min-height: 0; }
	.app-main { flex: 1; width: 0; min-width: 0; padding: 26px; background: #0f172a; }
	.login-layout { width: 100%; min-height: 100vh; background: #0f172a; }

	:global(html[data-tema='claro']) {
		color-scheme: light;
		background: #f1f5fb;
	}

	:global(html[data-tema='claro'] body),
	:global(html[data-tema='claro'] .app-layout),
	:global(html[data-tema='claro'] .app-main) {
		background: #f1f5fb !important;
		color: #1e293b !important;
	}

	:global(html[data-tema='claro'] .sidebar) {
		background: #ffffff !important;
		color: #334155 !important;
		border-right: 1px solid #dbeafe;
		box-shadow: 4px 0 18px rgb(30 64 175 / 6%);
	}

	:global(html[data-tema='claro'] .sidebar-separador) { background: #dbeafe !important; }
	:global(html[data-tema='claro'] .sidebar-etiqueta) { color: #64748b !important; }
	:global(html[data-tema='claro'] .sidebar-enlace) { color: #334155 !important; }
	:global(html[data-tema='claro'] .sidebar-enlace:hover) { background: #eff6ff !important; color: #1d4ed8 !important; }
	:global(html[data-tema='claro'] .sidebar-enlace.activo) { background: #dbeafe !important; color: #1d4ed8 !important; }
	:global(html[data-tema='claro'] .sidebar-enlace.activo::before) { background: #2563eb !important; }

	:global(html[data-tema='claro'] .footer) {
		background: #ffffff !important;
		border-color: #dbeafe !important;
		color: #475569 !important;
	}
	:global(html[data-tema='claro'] .footer-identidad strong) { color: #1e3a8a !important; }
	:global(html[data-tema='claro'] .footer-identidad p),
	:global(html[data-tema='claro'] .footer-derechos) { color: #64748b !important; }
	:global(html[data-tema='claro'] .footer-logo) { border-color: #bfdbfe !important; color: #2563eb !important; }

	:global(html[data-tema='claro'] .app-main [class*='panel']),
	:global(html[data-tema='claro'] .app-main [class*='card']),
	:global(html[data-tema='claro'] .app-main [class*='tarjeta']),
	:global(html[data-tema='claro'] .app-main [class*='modal']:not([class*='fondo'])),
	:global(html[data-tema='claro'] .app-main .embed),
	:global(html[data-tema='claro'] .app-main .tabla-contenedor) {
		background-color: #ffffff !important;
		border-color: #dbeafe !important;
		color: #1e293b !important;
		box-shadow: 0 5px 20px rgb(30 64 175 / 5%);
	}

	:global(html[data-tema='claro'] .app-main :is(h1, h2, h3, h4, h5, h6, label, p, small, strong, th, td, .text-muted, .descripcion)) {
		color: #334155 !important;
	}
	:global(html[data-tema='claro'] .app-main :is(h1, h2, h3, h4, h5, h6)) { color: #123675 !important; }
	:global(html[data-tema='claro'] .app-main :is(.mensaje-error, .mensaje-error *, .alert-danger, .alert-danger *, .correo-error)) { color: #991b1b !important; }
	:global(html[data-tema='claro'] .app-main :is(.mensaje-exito, .mensaje-exito *, .alert-success, .alert-success *, .correo-exito)) { color: #166534 !important; }

	:global(html[data-tema='claro'] .app-main input:not([type='checkbox']):not([type='radio']),
		html[data-tema='claro'] .app-main select,
		html[data-tema='claro'] .app-main textarea) {
		background-color: #ffffff !important;
		border-color: #bfdbfe !important;
		color: #0f172a !important;
	}
	:global(html[data-tema='claro'] .app-main input::placeholder,
		html[data-tema='claro'] .app-main textarea::placeholder) { color: #94a3b8 !important; }
	:global(html[data-tema='claro'] .app-main #facultad) { color-scheme: light; }
	:global(html[data-tema='claro'] .app-main #facultad option) { background: #ffffff !important; color: #1e293b !important; }
	:global(html[data-tema='claro'] .app-main #rol) { color-scheme: light; }
	:global(html[data-tema='claro'] .app-main #rol option) { background: #ffffff !important; color: #1e293b !important; }
	:global(html[data-tema='claro'] .app-main #estadoUsuario) { color-scheme: light; }
	:global(html[data-tema='claro'] .app-main #estadoUsuario option) { background: #ffffff !important; color: #1e293b !important; }

	:global(html[data-tema='claro'] .app-main table) {
		--bs-table-bg: #ffffff;
		--bs-table-color: #334155;
		--bs-table-border-color: #dbeafe;
		--bs-table-hover-bg: #eff6ff;
		--bs-table-hover-color: #1e293b;
		color: #334155 !important;
		border-color: #dbeafe !important;
	}
	:global(html[data-tema='claro'] .app-main thead th) { background: #eaf2ff !important; color: #1d4ed8 !important; }
	:global(html[data-tema='claro'] .app-main tbody td) { background: #ffffff !important; color: #334155 !important; border-color: #e2e8f0 !important; }
	:global(html[data-tema='claro'] .app-main tbody tr:nth-child(even) td) { background: #f8fbff !important; }
	:global(html[data-tema='claro'] .app-main .roles-container .aviso) { background: #ffffff !important; }
	:global(html[data-tema='claro'] .app-main .roles-container .aviso h2) { color: #1e293b !important; }
	:global(html[data-tema='claro'] .app-main .roles-container .aviso p) { color: #475569 !important; }
	:global(html[data-tema='oscuro'] .app-main .roles-container .aviso) { background: #1e293b !important; }
	:global(html[data-tema='oscuro'] .app-main .roles-container .aviso h2) { color: #f8fafc !important; }
	:global(html[data-tema='oscuro'] .app-main .roles-container .aviso p) { color: #cbd5e1 !important; }
	:global(html[data-tema='claro'] .app-main .roles-container .estado) { background: #ffffff !important; border-color: #dbeafe !important; color: #475569 !important; }
	:global(html[data-tema='oscuro'] .app-main .roles-container .estado) { background: #1e293b !important; border-color: #334155 !important; color: #cbd5e1 !important; }
	:global(html[data-tema='claro'] .app-main .roles-container .aviso-inactivo) { background: #ffffff !important; border-color: #fecaca !important; color: #991b1b !important; }
	:global(html[data-tema='oscuro'] .app-main .roles-container .aviso-inactivo) { background: #3b1d29 !important; border-color: #7f1d1d !important; color: #fecaca !important; }
	:global(html[data-tema='claro'] .app-main .modal-permisos .contador) { background: #ffffff !important; border-color: #bfdbfe !important; color: #1d4ed8 !important; }
	:global(html[data-tema='claro'] .app-main .modal-permisos .modulo-item) { background: #ffffff !important; border-color: #dbeafe !important; color: #334155 !important; }
	:global(html[data-tema='claro'] .app-main .modal-permisos .modulo-item.habilitado) { background: #eff6ff !important; border-color: #93c5fd !important; }
	:global(html[data-tema='claro'] .app-main .modal-permisos .modulo-item.parcial) { background: #fff7ed !important; border-color: #f59e0b !important; }
	:global(html[data-tema='claro'] .app-main .modal-permisos .modulo-info strong) { color: #123675 !important; }
	:global(html[data-tema='claro'] .app-main .modal-permisos .modulo-info small) { color: #475569 !important; }
	:global(html[data-tema='claro'] .app-main .modal-permisos .modulo-control span.estado-off) { color: #475569 !important; }
	:global(html[data-tema='claro'] .app-main .modal-permisos .modulo-control span.estado-on),
	:global(html[data-tema='claro'] .app-main .modal-permisos .modulo-control span.estado-parcial) { color: #166534 !important; }
	:global(html[data-tema='claro'] .app-main .modal-permisos .modulo-sin-acceso) { color: #991b1b !important; }
	:global(html[data-tema='claro'] .app-main .modal-permisos .modulo-parcial) { color: #92400e !important; }
	:global(html[data-tema='claro'] .app-main .modal-permisos .modulo-sin-configurar) { color: #991b1b !important; }

	:global(html[data-tema='claro'] .app-main button:not(.btn-primary):not(.btn-principal):not(.btn-success):not(.btn-danger):not(.boton-primario):not([class*='estado'])) {
		background-color: #eff6ff;
		border-color: #bfdbfe;
		color: #1d4ed8;
	}
	:global(html[data-tema='claro'] .app-main button:not(:disabled):hover:not(.btn-primary):not(.btn-principal):not(.btn-success):not(.btn-danger):not(.boton-primario)) {
		background-color: #dbeafe;
	}

	:global(html[data-tema='claro'] .login-layout),
	:global(html[data-tema='claro'] .login-page) { background: #f1f5fb !important; }
	:global(html[data-tema='claro'] .login-presentacion) {
		background: linear-gradient(145deg, #ffffff, #eff6ff) !important;
		border-color: #dbeafe !important;
	}
	:global(html[data-tema='claro'] .login-presentacion :is(h1, strong)) { color: #123675 !important; }
	:global(html[data-tema='claro'] .login-presentacion :is(p, span)) { color: #475569 !important; }

	@media (max-width: 768px) {
		.app-contenido { flex-direction: column; }
		.app-main { width: 100%; padding: 16px; }
	}
</style>
