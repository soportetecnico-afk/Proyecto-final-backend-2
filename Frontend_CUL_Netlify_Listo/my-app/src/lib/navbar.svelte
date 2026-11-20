<script>
	import { onMount } from 'svelte';
	import { resolve } from '$app/paths';

	// Estado reactivo en Svelte 5
	let usuario = $state(null);

	onMount(() => {
		cargarSesion();
	});

	function cargarSesion() {
		const sesion = localStorage.getItem('usuario_sesion');
		if (sesion) {
			try {
				usuario = JSON.parse(sesion);
			} catch (e) {
				usuario = null;
			}
		} else {
			usuario = null;
		}
	}

	function cerrarSesion() {
		localStorage.removeItem('usuario_sesion');
		usuario = null;
		window.location.href = '/login';
	}
</script>

<nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm">
	<div class="container">
		<!-- Nombre del sistema -->
		<a class="navbar-brand fw-bold d-flex align-items-center gap-2" href={resolve('/')}>
			<span class="badge bg-white text-primary px-2 py-1 rounded-2">CUL</span>
			<span>Sistema de Reservas</span>
		</a>

		<!-- Botón para dispositivos pequeños -->
		<button
			class="navbar-toggler"
			type="button"
			data-bs-toggle="collapse"
			data-bs-target="#menuPrincipal"
			aria-controls="menuPrincipal"
			aria-expanded="false"
			aria-label="Abrir menú de navegación"
		>
			<span class="navbar-toggler-icon"></span>
		</button>

		<!-- Menú principal -->
		<div class="navbar-collapse collapse" id="menuPrincipal">
			<ul class="navbar-nav align-items-lg-center ms-auto">
				<li class="nav-item">
					<a class="nav-link" href={resolve('/')}> Inicio </a>
				</li>

				<li class="nav-item">
					<a class="nav-link" href={resolve('/reservas')}> Reservas </a>
				</li>

				<li class="nav-item">
					<a class="nav-link" href={resolve('/espacios')}> Espacios </a>
				</li>

				<li class="nav-item">
					<a class="nav-link" href={resolve('/recursos')}> Recursos </a>
				</li>

				<!-- CONDICIONAL SEGÚN ESTADO DE SESIÓN -->
				{#if usuario}
					<li class="nav-item ms-lg-3 mt-lg-0 mt-2 d-flex align-items-center gap-2">
						<div class="d-flex align-items-center gap-2 bg-primary-subtle px-3 py-1 rounded-pill border border-white-50">
							<span class="badge bg-white text-primary rounded-circle fw-bold" style="width: 26px; height: 26px; display: grid; place-items: center;">
								{usuario.nombre ? usuario.nombre.charAt(0).toUpperCase() : 'U'}
							</span>
							<div class="d-flex flex-column text-start">
								<span class="text-white fw-semibold small lh-1">{usuario.nombre}</span>
								<span class="text-white-50 small" style="font-size: 0.75rem;">{usuario.rol || 'Usuario'}</span>
							</div>
						</div>

						<button
							type="button"
							class="btn btn-outline-light btn-sm fw-semibold"
							onclick={cerrarSesion}
							title="Cerrar sesión"
						>
							Salir
						</button>
					</li>
				{:else}
					<li class="nav-item ms-lg-3 mt-lg-0 mt-2">
						<a class="btn btn-light text-primary fw-semibold" href={resolve('/login')}>
							Iniciar sesión
						</a>
					</li>
				{/if}
			</ul>
		</div>
	</div>
</nav>

<style>
	.navbar-brand span:first-child {
		font-size: 0.9rem;
		letter-spacing: 0.5px;
	}

	.nav-link {
		font-weight: 500;
		transition: color 0.2s ease;
	}

	.nav-link:hover {
		color: #ffffff !important;
	}
</style>