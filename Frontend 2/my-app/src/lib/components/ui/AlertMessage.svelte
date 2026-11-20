<script>
	let { tipo = 'info', titulo = '', mensaje = '', visible = true, onCerrar = undefined } = $props();

	const tiposValidos = ['exito', 'error', 'advertencia', 'info'];

	let tipoActual = $derived(tiposValidos.includes(tipo) ? tipo : 'info');

	const iconos = {
		exito: '✓',
		error: '!',
		advertencia: '⚠',
		info: 'i'
	};

	function cerrarAlerta() {
		if (onCerrar) {
			onCerrar();
		}
	}
</script>

{#if visible}
	<div
		class="alert-message"
		class:alert-exito={tipoActual === 'exito'}
		class:alert-error={tipoActual === 'error'}
		class:alert-advertencia={tipoActual === 'advertencia'}
		class:alert-info={tipoActual === 'info'}
		role={tipoActual === 'error' || tipoActual === 'advertencia' ? 'alert' : 'status'}
	>
		<div class="alert-icono" aria-hidden="true">
			{iconos[tipoActual]}
		</div>

		<div class="alert-contenido">
			{#if titulo}
				<strong class="alert-titulo">{titulo}</strong>
			{/if}

			{#if mensaje}
				<p class="alert-mensaje">{mensaje}</p>
			{/if}
		</div>

		{#if onCerrar}
			<button type="button" class="alert-cerrar" aria-label="Cerrar mensaje" onclick={cerrarAlerta}>
				×
			</button>
		{/if}
	</div>
{/if}

<style>
	.alert-message {
		display: flex;
		align-items: flex-start;
		gap: 12px;
		width: 100%;
		padding: 15px 16px;
		border: 1px solid transparent;
		border-radius: 10px;
	}

	.alert-icono {
		display: grid;
		width: 28px;
		height: 28px;
		flex-shrink: 0;
		place-items: center;
		border: 1px solid currentColor;
		border-radius: 50%;
		font-size: 14px;
		font-weight: 800;
	}

	.alert-contenido {
		flex: 1;
		min-width: 0;
		padding-top: 2px;
	}

	.alert-titulo {
		display: block;
		margin-bottom: 4px;
		font-size: 14px;
		font-weight: 700;
		line-height: 1.5;
	}

	.alert-mensaje {
		margin: 0;
		font-size: 13px;
		line-height: 1.6;
		overflow-wrap: anywhere;
	}

	.alert-exito {
		border-color: #166534;
		background: rgb(22 163 74 / 10%);
		color: #86efac;
	}

	.alert-error {
		border-color: #991b1b;
		background: rgb(239 68 68 / 10%);
		color: #fca5a5;
	}

	.alert-advertencia {
		border-color: #854d0e;
		background: rgb(234 179 8 / 10%);
		color: #fde047;
	}

	.alert-info {
		border-color: #1d4ed8;
		background: rgb(59 130 246 / 10%);
		color: #93c5fd;
	}

	.alert-cerrar {
		display: grid;
		width: 30px;
		height: 30px;
		flex-shrink: 0;
		place-items: center;
		border: none;
		border-radius: 6px;
		background: transparent;
		color: inherit;
		font-size: 23px;
		cursor: pointer;
		opacity: 0.8;
	}

	.alert-cerrar:hover {
		background: rgb(255 255 255 / 8%);
		opacity: 1;
	}

	.alert-cerrar:focus-visible {
		outline: 2px solid currentColor;
		outline-offset: 2px;
	}

	@media (max-width: 480px) {
		.alert-message {
			gap: 10px;
			padding: 13px;
		}
	}
</style>
