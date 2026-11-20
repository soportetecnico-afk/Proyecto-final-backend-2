<script>
	let {
		abierto = $bindable(false),
		titulo = 'Confirmar acción',
		mensaje = '¿Estás seguro de que deseas continuar?',
		textoConfirmar = 'Confirmar',
		textoCancelar = 'Cancelar',
		variante = 'peligro',
		cargando = false,
		onConfirmar = undefined,
		onCancelar = undefined
	} = $props();

	function cancelar() {
		if (cargando) return;

		abierto = false;

		if (onCancelar) {
			onCancelar();
		}
	}

	function confirmar() {
		if (cargando) return;

		if (onConfirmar) {
			onConfirmar();
		}
	}

	function manejarTeclado(evento) {
		if (evento.key === 'Escape' && abierto && !cargando) {
			cancelar();
		}
	}
</script>

<svelte:window onkeydown={manejarTeclado} />

{#if abierto}
	<div
		class="confirm-fondo"
		role="presentation"
		onclick={(evento) => {
			if (evento.target === evento.currentTarget && !cargando) {
				cancelar();
			}
		}}
	>
		<div
			class="confirm-panel"
			class:panel-advertencia={variante === 'advertencia'}
			class:panel-info={variante === 'info'}
			role="alertdialog"
			aria-modal="true"
			aria-labelledby="confirm-titulo"
			aria-describedby="confirm-mensaje"
			tabindex="-1"
		>
			<div
				class="confirm-icono"
				class:icono-advertencia={variante === 'advertencia'}
				class:icono-info={variante === 'info'}
				aria-hidden="true"
			>
				{#if variante === 'advertencia'}
					!
				{:else if variante === 'info'}
					i
				{:else}
					×
				{/if}
			</div>

			<div class="confirm-textos">
				<h2 id="confirm-titulo">{titulo}</h2>
				<p id="confirm-mensaje">{mensaje}</p>
			</div>

			<div class="confirm-acciones">
				<button type="button" class="confirm-boton cancelar" onclick={cancelar} disabled={cargando}>
					{textoCancelar}
				</button>

				<button
					type="button"
					class="confirm-boton confirmar"
					class:confirm-advertencia={variante === 'advertencia'}
					class:confirm-info={variante === 'info'}
					onclick={confirmar}
					disabled={cargando}
				>
					{#if cargando}
						<span class="confirm-spinner" aria-hidden="true"></span>
						Procesando...
					{:else}
						{textoConfirmar}
					{/if}
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	.confirm-fondo {
		position: fixed;
		inset: 0;
		z-index: 1100;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 20px;
		overflow-y: auto;
		background: rgb(2 6 23 / 78%);
		backdrop-filter: blur(5px);
		animation: confirm-aparecer 0.18s ease-out;
	}

	.confirm-panel {
		display: flex;
		flex-direction: column;
		align-items: center;
		width: 100%;
		max-width: 440px;
		padding: 30px;
		border: 1px solid #334155;
		border-radius: 16px;
		outline: none;
		background: #1e293b;
		box-shadow: 0 24px 70px rgb(0 0 0 / 35%);
		text-align: center;
		animation: confirm-subir 0.2s ease-out;
	}

	.confirm-icono {
		display: grid;
		width: 58px;
		height: 58px;
		margin-bottom: 20px;
		place-items: center;
		border: 1px solid #991b1b;
		border-radius: 16px;
		background: rgb(239 68 68 / 12%);
		color: #fca5a5;
		font-size: 30px;
		font-weight: 500;
	}

	.confirm-icono.icono-advertencia {
		border-color: #854d0e;
		background: rgb(234 179 8 / 12%);
		color: #fde047;
	}

	.confirm-icono.icono-info {
		border-color: #1d4ed8;
		background: rgb(59 130 246 / 12%);
		color: #93c5fd;
	}

	.confirm-textos {
		width: 100%;
	}

	.confirm-textos h2 {
		margin: 0;
		color: #f8fafc;
		font-size: 20px;
		font-weight: 700;
		line-height: 1.4;
	}

	.confirm-textos p {
		margin: 12px 0 0;
		color: #a9bad3;
		font-size: 14px;
		line-height: 1.7;
		overflow-wrap: anywhere;
	}

	.confirm-acciones {
		display: flex;
		justify-content: center;
		gap: 12px;
		width: 100%;
		margin-top: 28px;
	}

	.confirm-boton {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: 8px;
		min-height: 44px;
		padding: 11px 18px;
		border: 1px solid transparent;
		border-radius: 9px;
		font-family: inherit;
		font-size: 13px;
		font-weight: 600;
		cursor: pointer;
		transition:
			background-color 0.2s ease,
			border-color 0.2s ease;
	}

	.confirm-boton.cancelar {
		border-color: #475569;
		background: #334155;
		color: #e2e8f0;
	}

	.confirm-boton.cancelar:hover:not(:disabled) {
		background: #475569;
	}

	.confirm-boton.confirmar {
		border-color: #dc2626;
		background: #dc2626;
		color: #fff;
	}

	.confirm-boton.confirmar:hover:not(:disabled) {
		background: #b91c1c;
	}

	.confirm-boton.confirmar.confirm-advertencia {
		border-color: #ca8a04;
		background: #a16207;
	}

	.confirm-boton.confirmar.confirm-advertencia:hover:not(:disabled) {
		background: #854d0e;
	}

	.confirm-boton.confirmar.confirm-info {
		border-color: #2563eb;
		background: #2563eb;
	}

	.confirm-boton.confirmar.confirm-info:hover:not(:disabled) {
		background: #1d4ed8;
	}

	.confirm-boton:disabled {
		cursor: not-allowed;
		opacity: 0.6;
	}

	.confirm-boton:focus-visible {
		outline: 2px solid #93c5fd;
		outline-offset: 3px;
	}

	.confirm-spinner {
		width: 15px;
		height: 15px;
		border: 2px solid rgb(255 255 255 / 35%);
		border-top-color: #fff;
		border-radius: 50%;
		animation: confirm-girar 0.7s linear infinite;
	}

	@keyframes confirm-aparecer {
		from {
			opacity: 0;
		}

		to {
			opacity: 1;
		}
	}

	@keyframes confirm-subir {
		from {
			opacity: 0;
			transform: translateY(8px);
		}

		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	@keyframes confirm-girar {
		to {
			transform: rotate(360deg);
		}
	}

	@media (max-width: 480px) {
		.confirm-panel {
			padding: 24px 18px;
		}

		.confirm-acciones {
			flex-direction: column-reverse;
		}

		.confirm-boton {
			width: 100%;
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.confirm-fondo,
		.confirm-panel,
		.confirm-spinner {
			animation: none;
		}
	}
</style>
