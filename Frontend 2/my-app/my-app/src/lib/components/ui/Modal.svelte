<script>
	let {
		abierto = $bindable(false),
		titulo = 'Ventana',
		descripcion = '',
		ancho = 'mediano',
		onCerrar = undefined,
		children
	} = $props();

	function cerrarModal() {
		abierto = false;

		if (onCerrar) {
			onCerrar();
		}
	}

	function manejarTeclado(evento) {
		if (evento.key === 'Escape' && abierto) {
			cerrarModal();
		}
	}
</script>

<svelte:window onkeydown={manejarTeclado} />

{#if abierto}
	<div
		class="modal-fondo"
		role="presentation"
		onclick={(evento) => {
			if (evento.target === evento.currentTarget) {
				cerrarModal();
			}
		}}
	>
		<div
			class="modal-panel"
			class:modal-pequeno={ancho === 'pequeno'}
			class:modal-grande={ancho === 'grande'}
			role="dialog"
			aria-modal="true"
			aria-labelledby="modal-titulo"
			aria-describedby={descripcion ? 'modal-descripcion' : undefined}
			tabindex="-1"
		>
			<header class="modal-encabezado">
				<div class="modal-titulos">
					<h2 id="modal-titulo">{titulo}</h2>

					{#if descripcion}
						<p id="modal-descripcion">{descripcion}</p>
					{/if}
				</div>

				<button
					type="button"
					class="modal-cerrar"
					aria-label="Cerrar ventana"
					onclick={cerrarModal}
				>
					×
				</button>
			</header>

			<div class="modal-contenido">
				{@render children?.()}
			</div>
		</div>
	</div>
{/if}

<style>
	.modal-fondo {
		position: fixed;
		inset: 0;
		z-index: 1000;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 24px;
		overflow-y: auto;
		background: rgb(2 6 23 / 75%);
		backdrop-filter: blur(5px);
		animation: aparecer 0.18s ease-out;
	}

	.modal-panel {
		display: flex;
		flex-direction: column;
		width: 100%;
		max-width: 560px;
		max-height: calc(100vh - 48px);
		overflow: hidden;
		border: 1px solid #334155;
		border-radius: 16px;
		outline: none;
		background: #1e293b;
		box-shadow: 0 24px 70px rgb(0 0 0 / 35%);
		animation: subir 0.2s ease-out;
	}

	.modal-panel.modal-pequeno {
		max-width: 400px;
	}

	.modal-panel.modal-grande {
		max-width: 800px;
	}

	.modal-encabezado {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 20px;
		padding: 24px;
		border-bottom: 1px solid #334155;
		background: #172338;
	}

	.modal-titulos {
		min-width: 0;
	}

	.modal-titulos h2 {
		margin: 0;
		color: #f8fafc;
		font-size: 20px;
		font-weight: 700;
		line-height: 1.4;
	}

	.modal-titulos p {
		margin: 7px 0 0;
		color: #94a3b8;
		font-size: 13px;
		line-height: 1.6;
	}

	.modal-cerrar {
		display: grid;
		width: 36px;
		height: 36px;
		flex-shrink: 0;
		place-items: center;
		border: 1px solid #475569;
		border-radius: 9px;
		background: #1e293b;
		color: #cbd5e1;
		font-size: 25px;
		line-height: 1;
		cursor: pointer;
		transition:
			background-color 0.2s ease,
			color 0.2s ease;
	}

	.modal-cerrar:hover {
		background: #334155;
		color: #fff;
	}

	.modal-cerrar:focus-visible {
		outline: 2px solid #60a5fa;
		outline-offset: 3px;
	}

	.modal-contenido {
		padding: 24px;
		overflow-y: auto;
		color: #dbe5f5;
	}

	@keyframes aparecer {
		from {
			opacity: 0;
		}

		to {
			opacity: 1;
		}
	}

	@keyframes subir {
		from {
			opacity: 0;
			transform: translateY(10px);
		}

		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	@media (max-width: 600px) {
		.modal-fondo {
			align-items: flex-end;
			padding: 12px;
		}

		.modal-panel {
			max-height: calc(100vh - 24px);
			border-radius: 16px;
		}

		.modal-encabezado {
			padding: 20px;
		}

		.modal-contenido {
			padding: 20px;
		}

		.modal-titulos h2 {
			font-size: 18px;
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.modal-fondo,
		.modal-panel {
			animation: none;
		}
	}
</style>
