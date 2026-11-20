<script>
	import { onMount } from 'svelte';
	import { resolve } from '$app/paths';

	// Estado reactivo en Svelte 5
	let usuario = $state({
		nombre: 'Usuario',
		rol: 'Sesión del sistema',
		inicial: 'U'
	});

	onMount(() => {
		cargarSesion();
	});

	function cargarSesion() {
		const sesionGuardada = localStorage.getItem('usuario_sesion');
		if (sesionGuardada) {
			try {
				const datos = JSON.parse(sesionGuardada);
				const nombre = datos.nombre || datos.nombre_usuario || 'Usuario';
				let rol = datos.rol || datos.nombre_rol;

				if (!rol) {
					if (datos.id_rol === 1) rol = 'Administrador';
					else if (datos.id_rol === 3) rol = 'Decano';
					else if (datos.id_rol === 6) rol = 'Docente';
					else rol = 'Institucional';
				}

				usuario = {
					nombre: nombre,
					rol: rol,
					inicial: nombre.charAt(0).toUpperCase()
				};
			} catch (e) {
				console.error('Error al procesar la sesión:', e);
			}
		}
	}

	function cerrarSesion() {
		localStorage.removeItem('usuario_sesion');
		window.location.href = '/login';
	}
</script>

<header class="topbar">
	<div class="topbar-identidad">
		<a href={resolve('/')} style="text-decoration: none;">
			<span class="topbar-logo">CUL</span>
		</a>

		<div class="topbar-titulo">
			<h1>Sistema de Reservas</h1>
			<span>Gestión de Espacios Universitarios</span>
		</div>
	</div>

	<div class="topbar-acciones">
		<div class="topbar-usuario">
			<div class="usuario-avatar" aria-hidden="true">{usuario.inicial}</div>

			<div class="usuario-informacion">
				<strong>{usuario.nombre}</strong>
				<span>{usuario.rol}</span>
			</div>
		</div>

		<button
			type="button"
			class="btn-cerrar-sesion"
			aria-label="Cerrar sesión"
			onclick={cerrarSesion}
		>
			<span aria-hidden="true">↪</span>
			<span>Cerrar sesión</span>
		</button>
	</div>
</header>

<style>
	.topbar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 24px;
		width: 100%;
		min-height: 88px;
		padding: 16px 28px;
		background: #2563eb;
		color: #ffffff;
		border-bottom: 1px solid #3b82f6;
		box-shadow: 0 4px 14px rgb(0 0 0 / 12%);
	}

	.topbar-identidad {
		display: flex;
		align-items: center;
		gap: 14px;
		min-width: 0;
	}

	.topbar-logo {
		display: grid;
		place-items: center;
		width: 48px;
		height: 48px;
		flex-shrink: 0;
		border: 2px solid rgb(255 255 255 / 80%);
		border-radius: 12px;
		color: #ffffff;
		font-size: 18px;
		font-weight: 800;
	}

	.topbar-titulo {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.topbar-titulo h1 {
		margin: 0;
		color: #ffffff;
		font-size: 19px;
		font-weight: 700;
	}

	.topbar-titulo span {
		color: #dbeafe;
		font-size: 12px;
	}

	.topbar-acciones {
		display: flex;
		align-items: center;
		justify-content: flex-end;
		gap: 24px;
	}

	.topbar-usuario {
		display: flex;
		align-items: center;
		gap: 10px;
	}

	.usuario-avatar {
		display: grid;
		place-items: center;
		width: 42px;
		height: 42px;
		flex-shrink: 0;
		border-radius: 50%;
		background: #ffffff;
		color: #2563eb;
		font-size: 16px;
		font-weight: 800;
	}

	.usuario-informacion {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.usuario-informacion strong {
		color: #ffffff;
		font-size: 13px;
	}

	.usuario-informacion span {
		color: #dbeafe;
		font-size: 12px;
	}

	.btn-cerrar-sesion {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: 8px;
		min-height: 42px;
		padding: 10px 14px;
		border: 1px solid rgb(255 255 255 / 45%);
		border-radius: 9px;
		background: rgb(255 255 255 / 12%);
		color: #ffffff;
		font-size: 13px;
		font-weight: 600;
		cursor: pointer;
		transition:
			background-color 0.2s ease,
			border-color 0.2s ease;
	}

	.btn-cerrar-sesion:hover {
		border-color: #ffffff;
		background: #dc2626;
	}

	.btn-cerrar-sesion:focus-visible {
		outline: 2px solid #ffffff;
		outline-offset: 3px;
	}

	@media (max-width: 768px) {
		.topbar {
			align-items: flex-start;
			flex-direction: column;
			gap: 18px;
			padding: 18px;
		}

		.topbar-acciones {
			justify-content: space-between;
			width: 100%;
			gap: 12px;
		}

		.topbar-titulo h1 {
			font-size: 17px;
		}
	}

	@media (max-width: 420px) {
		.topbar-titulo span {
			max-width: 210px;
			line-height: 1.4;
		}

		.usuario-informacion span {
			max-width: 120px;
			overflow-wrap: anywhere;
		}

		.btn-cerrar-sesion {
			padding: 9px 10px;
			font-size: 12px;
		}
	}
</style>