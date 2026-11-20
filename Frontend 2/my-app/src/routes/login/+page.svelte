<script>
	const API_BASE = 'http://127.0.0.1:8000';
	let usuario = $state('');
	let password = $state('');
	let mostrarPassword = $state(false);
	let error = $state('');
	let cargando = $state(false);

	async function iniciarSesion(evento) {
		evento.preventDefault();
		error = '';

		if (!usuario.trim() || !password) {
			error = 'Por favor ingresa tu usuario y contraseña.';
			return;
		}

		cargando = true;
		try {
			const res = await fetch(`${API_BASE}/usuarios/login`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ usuario: usuario.trim(), password })
			});

			const respuesta = await res.json().catch(() => ({}));
			if (!res.ok) throw new Error(respuesta.detail || 'No fue posible iniciar sesión.');
			if (!respuesta.access_token || !respuesta.usuario) {
				throw new Error('No fue posible iniciar sesión. Inténtalo nuevamente.');
			}

			localStorage.setItem('usuario_sesion', JSON.stringify(respuesta.usuario));
			localStorage.setItem('token_acceso', respuesta.access_token);
			window.location.href = '/';
		} catch (e) {
			error = e instanceof TypeError ? 'No fue posible iniciar sesión. Inténtalo nuevamente.' : e.message || 'No fue posible iniciar sesión. Inténtalo nuevamente.';
		} finally {
			cargando = false;
		}
	}
</script>

<svelte:head>
	<title>Iniciar sesión | Sistema de Reservas CUL</title>
	<meta
		name="description"
		content="Acceso al Sistema de Reservas y Gestión de Espacios Universitarios CUL."
	/>
</svelte:head>

<main class="login-page">
	<div class="login-layout">
		<!-- PANEL INFORMATIVO -->
		<section class="login-presentacion">
			<div class="marca-institucional">
				<div class="marca-logo">CUL</div>

				<div class="marca-texto">
					<strong>Sistema de Reservas</strong>
					<span>Gestión universitaria</span>
				</div>
			</div>

			<div class="presentacion-contenido">
				<span class="presentacion-etiqueta">
					<span class="indicador"></span>
					PORTAL UNIVERSITARIO
				</span>

				<h1>
					Tus espacios universitarios,
					<span>mejor organizados.</span>
				</h1>

				<p class="presentacion-descripcion">
					Accede a la plataforma de gestión de espacios universitarios y consulta las herramientas
					disponibles para organizar las actividades académicas.
				</p>

				<div class="presentacion-beneficios">
					<div class="beneficio">
						<div class="beneficio-icono" aria-hidden="true">▦</div>

						<div>
							<strong>Gestión de reservas</strong>
							<p>Organización de espacios universitarios.</p>
						</div>
					</div>

					<div class="beneficio">
						<div class="beneficio-icono verde" aria-hidden="true">⌂</div>

						<div>
							<strong>Espacios y recursos</strong>
							<p>Consulta centralizada de los recursos.</p>
						</div>
					</div>

					<div class="beneficio">
						<div class="beneficio-icono morado" aria-hidden="true">▥</div>

						<div>
							<strong>Información organizada</strong>
							<p>Acceso a los módulos del sistema.</p>
						</div>
					</div>
				</div>
			</div>

			<div class="presentacion-pie">
				<span>Plataforma de gestión universitaria</span>
				<span>© {new Date().getFullYear()} CUL</span>
			</div>
		</section>

		<!-- PANEL DE ACCESO -->
		<section class="login-acceso" aria-labelledby="titulo-login">
			<div class="login-formulario">
				<div class="login-encabezado">
					<div class="login-icono" aria-hidden="true">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							width="28"
							height="28"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="1.7"
							stroke-linecap="round"
							stroke-linejoin="round"
						>
							<rect x="3" y="11" width="18" height="10" rx="2"></rect>
							<path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
							<circle cx="12" cy="16" r="1"></circle>
						</svg>
					</div>

					<span class="login-etiqueta">ACCESO AL SISTEMA</span>

					<h2 id="titulo-login">Bienvenido</h2>

					<p>Ingresa tus credenciales para continuar.</p>
				</div>

				<!-- MENSAJE DE ERROR -->
				{#if error}
					<div class="mensaje-error mb-3">
						{error}
					</div>
				{/if}

				<form onsubmit={iniciarSesion}>
					<!-- USUARIO -->
					<div class="campo">
						<label for="usuario">Usuario</label>
						<div class="campo-contenedor">
							<span class="campo-icono" aria-hidden="true">
								<svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
									<circle cx="12" cy="8" r="4"></circle><path d="M5 21v-2a7 7 0 0 1 14 0v2"></path>
								</svg>
							</span>
							<input id="usuario" name="usuario" type="text" bind:value={usuario} placeholder="Ingresa tu usuario institucional" autocomplete="username" required />
						</div>
					</div>

					<!-- CONTRASEÑA -->
					<div class="campo">
						<div class="campo-encabezado">
							<label for="password">Contraseña</label>
						</div>

						<div class="campo-contenedor">
							<span class="campo-icono" aria-hidden="true">
								<svg
									xmlns="http://www.w3.org/2000/svg"
									width="19"
									height="19"
									viewBox="0 0 24 24"
									fill="none"
									stroke="currentColor"
									stroke-width="1.7"
									stroke-linecap="round"
									stroke-linejoin="round"
								>
									<rect x="3" y="11" width="18" height="10" rx="2"></rect>
									<path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
								</svg>
							</span>

							<input
								id="password"
								name="password"
								type={mostrarPassword ? 'text' : 'password'}
								bind:value={password}
								placeholder="Ingresa tu contraseña"
								autocomplete="current-password"
								required
							/>

							<button
								type="button"
								class="boton-ver-password"
								aria-label={mostrarPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
								aria-pressed={mostrarPassword}
								onclick={() => (mostrarPassword = !mostrarPassword)}
							>
								{#if mostrarPassword}
									Ocultar
								{:else}
									Mostrar
								{/if}
							</button>
						</div>
					</div>

					<!-- BOTÓN SUBMIT -->
					<button type="submit" class="boton-iniciar" disabled={cargando}>
						<span>{cargando ? 'Ingresando...' : 'Iniciar sesión'}</span>
						<span aria-hidden="true">→</span>
					</button>
				</form>

				<p class="login-nota">
					El acceso está reservado para los usuarios autorizados de la institución.
				</p>
			</div>

			<div class="acceso-pie">
				<span class="acceso-punto"></span>
				Interfaz de acceso al sistema
			</div>
		</section>
	</div>
</main>

<style>
	:global(body) {
		margin: 0;
		background: #0f172a;
	}

	:global(body > div),
	:global(body > #svelte) {
		min-height: 100%;
	}

	.mensaje-error {
		padding: 10px 14px;
		margin-bottom: 18px;
		border-radius: 8px;
		background-color: #fee2e2;
		border: 1px solid #fca5a5;
		color: #991b1b;
		font-size: 12px;
		font-weight: 600;
	}

	.login-page {
		display: flex;
		min-height: 100vh;
		align-items: center;
		justify-content: center;
		padding: 28px;
		background: radial-gradient(ellipse at 10% 10%, rgb(37 99 235 / 12%), transparent 42%), #0f172a;
	}

	.login-layout {
		display: grid;
		width: 100%;
		max-width: 1180px;
		min-height: 700px;
		grid-template-columns: 1fr 0.88fr;
		overflow: hidden;
		border: 1px solid #334155;
		border-radius: 22px;
		background: #111c31;
		box-shadow: 0 25px 70px rgb(0 0 0 / 25%);
	}

	/* PANEL INFORMATIVO */
	.login-presentacion {
		display: flex;
		flex-direction: column;
		justify-content: space-between;
		padding: 34px 42px 26px;
		background:
			radial-gradient(ellipse at 5% 100%, rgb(59 130 246 / 20%), transparent 45%),
			linear-gradient(145deg, #142b4b, #10203a 70%);
	}

	.marca-institucional {
		display: flex;
		align-items: center;
		gap: 13px;
	}

	.marca-logo {
		display: grid;
		width: 48px;
		height: 48px;
		flex-shrink: 0;
		place-items: center;
		border: 1px solid #60a5fa;
		border-radius: 13px;
		background: #2563eb;
		color: #fff;
		font-size: 16px;
		font-weight: 800;
	}

	.marca-texto {
		display: flex;
		flex-direction: column;
		gap: 5px;
	}

	.marca-texto strong {
		color: #f8fafc;
		font-size: 14px;
	}

	.marca-texto span {
		color: #a9c5eb;
		font-size: 12px;
	}

	.presentacion-contenido {
		max-width: 460px;
		margin: 45px 0;
	}

	.presentacion-etiqueta {
		display: inline-flex;
		align-items: center;
		gap: 9px;
		margin-bottom: 24px;
		padding: 8px 12px;
		border: 1px solid #345a91;
		border-radius: 30px;
		background: rgb(37 99 235 / 12%);
		color: #bfdbfe;
		font-size: 10px;
		font-weight: 700;
		letter-spacing: 1.3px;
	}

	.indicador {
		width: 7px;
		height: 7px;
		border-radius: 50%;
		background: #60a5fa;
	}

	.presentacion-contenido h1 {
		margin: 0;
		color: #f8fafc;
		font-size: clamp(32px, 3.4vw, 43px);
		font-weight: 800;
		letter-spacing: -1px;
		line-height: 1.2;
	}

	.presentacion-contenido h1 span {
		display: block;
		margin-top: 7px;
		color: #60a5fa;
	}

	.presentacion-descripcion {
		margin: 22px 0 0;
		color: #b7c7df;
		font-size: 14px;
		line-height: 1.9;
	}

	.presentacion-beneficios {
		display: flex;
		flex-direction: column;
		gap: 20px;
		margin-top: 36px;
	}

	.beneficio {
		display: flex;
		align-items: center;
		gap: 14px;
	}

	.beneficio-icono {
		display: grid;
		width: 44px;
		height: 44px;
		flex-shrink: 0;
		place-items: center;
		border: 1px solid #345a91;
		border-radius: 12px;
		background: rgb(37 99 235 / 15%);
		color: #93c5fd;
		font-size: 22px;
	}

	.beneficio-icono.verde {
		border-color: #166534;
		background: rgb(22 163 74 / 12%);
		color: #86efac;
	}

	.beneficio-icono.morado {
		border-color: #6d28d9;
		background: rgb(139 92 246 / 12%);
		color: #c4b5fd;
	}

	.beneficio strong {
		color: #f1f5f9;
		font-size: 13px;
	}

	.beneficio p {
		margin: 5px 0 0;
		color: #9fb3ce;
		font-size: 12px;
		line-height: 1.6;
	}

	.presentacion-pie {
		display: flex;
		justify-content: space-between;
		gap: 12px;
		padding-top: 20px;
		border-top: 1px solid #293e5c;
		color: #94a9c5;
		font-size: 11px;
	}

	/* FORMULARIO */
	.login-acceso {
		display: flex;
		flex-direction: column;
		justify-content: center;
		padding: 38px 42px 22px;
		background: #f8fafc;
	}

	.login-formulario {
		width: 100%;
		max-width: 390px;
		margin: auto;
	}

	.login-encabezado {
		margin-bottom: 32px;
	}

	.login-icono {
		display: grid;
		width: 52px;
		height: 52px;
		margin-bottom: 22px;
		place-items: center;
		border: 1px solid #bfdbfe;
		border-radius: 14px;
		background: #eff6ff;
		color: #2563eb;
	}

	.login-etiqueta {
		color: #2563eb;
		font-size: 10px;
		font-weight: 800;
		letter-spacing: 1.5px;
	}

	.login-encabezado h2 {
		margin: 10px 0 9px;
		color: #0f172a;
		font-size: 31px;
		font-weight: 800;
		letter-spacing: -0.7px;
	}

	.login-encabezado p {
		margin: 0;
		color: #64748b;
		font-size: 13px;
		line-height: 1.7;
	}

	.campo {
		margin-bottom: 22px;
	}

	.campo label {
		display: block;
		margin-bottom: 9px;
		color: #1e293b;
		font-size: 13px;
		font-weight: 700;
	}

	.campo-contenedor {
		display: flex;
		min-height: 49px;
		align-items: center;
		gap: 11px;
		padding: 0 13px;
		border: 1px solid #cbd5e1;
		border-radius: 10px;
		background: #fff;
		transition:
			border-color 0.2s ease,
			box-shadow 0.2s ease;
	}

	.campo-contenedor:focus-within {
		border-color: #3b82f6;
		box-shadow: 0 0 0 3px rgb(59 130 246 / 12%);
	}

	.campo-icono {
		display: flex;
		flex-shrink: 0;
		color: #64748b;
	}

	.campo-contenedor input {
		flex: 1;
		width: 100%;
		min-width: 0;
		height: 47px;
		padding: 0;
		border: none;
		outline: none;
		background: transparent;
		color: #0f172a;
		font-family: inherit;
		font-size: 13px;
	}

	.campo-contenedor input::placeholder {
		color: #94a3b8;
	}

	.campo-contenedor input:focus-visible {
		outline: none;
	}

	.boton-ver-password {
		flex-shrink: 0;
		padding: 5px 0 5px 5px;
		border: none;
		background: transparent;
		color: #2563eb;
		font-size: 11px;
		font-weight: 700;
		cursor: pointer;
	}

	.boton-ver-password:focus-visible {
		outline: 2px solid #2563eb;
		outline-offset: 3px;
		border-radius: 3px;
	}

	.boton-iniciar {
		position: relative;
		display: flex;
		width: 100%;
		min-height: 49px;
		align-items: center;
		justify-content: center;
		gap: 12px;
		margin-top: 28px;
		padding: 0 48px;
		border: 1px solid #2563eb;
		border-radius: 10px;
		background: #2563eb;
		color: #fff;
		font-family: inherit;
		font-size: 14px;
		font-weight: 700;
		cursor: pointer;
		transition:
			background-color 0.2s ease,
			transform 0.2s ease;
	}

	.boton-iniciar span:first-child {
		text-align: center;
	}

	.boton-iniciar:hover {
		transform: translateY(-1px);
		background: #1d4ed8;
	}

	.boton-iniciar:focus-visible {
		outline: 2px solid #2563eb;
		outline-offset: 3px;
	}

	.boton-iniciar span:last-child {
		position: absolute;
		right: 17px;
		font-size: 19px;
	}

	.login-nota {
		margin: 24px 0 0;
		color: #64748b;
		font-size: 11px;
		line-height: 1.8;
		text-align: center;
	}

	.acceso-pie {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 8px;
		margin-top: 30px;
		padding-top: 18px;
		border-top: 1px solid #e2e8f0;
		color: #64748b;
		font-size: 11px;
	}

	.acceso-punto {
		width: 7px;
		height: 7px;
		border-radius: 50%;
		background: #60a5fa;
	}

	/* RESPONSIVE */
	@media (max-width: 900px) {
		.login-page {
			padding: 18px;
		}

		.login-layout {
			max-width: 560px;
			grid-template-columns: 1fr;
		}

		.login-presentacion {
			padding: 28px;
		}

		.presentacion-contenido {
			margin: 38px 0;
		}

		.presentacion-contenido h1 {
			font-size: 34px;
		}

		.presentacion-beneficios {
			gap: 15px;
		}

		.login-acceso {
			padding: 35px 28px 22px;
		}
	}

	@media (max-width: 480px) {
		.login-page {
			padding: 0;
		}

		.login-layout {
			min-height: 100vh;
			border: none;
			border-radius: 0;
		}

		.login-presentacion {
			padding: 22px 20px;
		}

		.presentacion-contenido {
			margin: 32px 0;
		}

		.presentacion-contenido h1 {
			font-size: 30px;
		}

		.presentacion-descripcion {
			font-size: 13px;
		}

		.presentacion-pie {
			font-size: 10px;
		}

		.login-acceso {
			padding: 30px 20px 20px;
		}

		.login-encabezado h2 {
			font-size: 28px;
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.campo-contenedor,
		.boton-iniciar {
			transition: none;
		}

		.boton-iniciar:hover {
			transform: none;
		}
	}
</style>
