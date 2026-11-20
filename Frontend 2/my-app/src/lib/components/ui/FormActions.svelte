<script>
	let {
		textoGuardar = 'Guardar',
		textoCancelar = 'Cancelar',
		mostrarCancelar = true,
		mostrarLimpiar = false,
		textoLimpiar = 'Limpiar',
		cargando = false,
		deshabilitado = false,
		onGuardar = undefined,
		onCancelar = undefined,
		onLimpiar = undefined
	} = $props();
</script>

<div class="form-actions">
	<div class="form-actions-secundarias">
		{#if mostrarLimpiar}
			<button
				type="button"
				class="form-actions-boton limpiar"
				onclick={onLimpiar}
				disabled={cargando || deshabilitado}
			>
				{textoLimpiar}
			</button>
		{/if}

		{#if mostrarCancelar}
			<button
				type="button"
				class="form-actions-boton cancelar"
				onclick={onCancelar}
				disabled={cargando || deshabilitado}
			>
				{textoCancelar}
			</button>
		{/if}
	</div>

	<button
		type="submit"
		class="form-actions-boton guardar"
		onclick={onGuardar}
		disabled={cargando || deshabilitado}
	>
		{#if cargando}
			<span class="form-actions-spinner" aria-hidden="true"></span>
			Procesando...
		{:else}
			<span class="form-actions-icono" aria-hidden="true">✓</span>
			{textoGuardar}
		{/if}
	</button>
</div>

<style>
	.form-actions {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 16px;
		width: 100%;
		padding-top: 20px;
		border-top: 1px solid #334155;
	}

	.form-actions-secundarias {
		display: flex;
		align-items: center;
		gap: 10px;
	}

	.form-actions-boton {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: 8px;
		min-height: 42px;
		padding: 10px 16px;
		border: 1px solid transparent;
		border-radius: 9px;
		font-family: inherit;
		font-size: 13px;
		font-weight: 600;
		cursor: pointer;
		transition:
			background-color 0.2s ease,
			border-color 0.2s ease,
			transform 0.2s ease;
	}

	.form-actions-boton:hover:not(:disabled) {
		transform: translateY(-1px);
	}

	.form-actions-boton:focus-visible {
		outline: 2px solid #60a5fa;
		outline-offset: 3px;
	}

	.form-actions-boton:disabled {
		cursor: not-allowed;
		opacity: 0.5;
		transform: none;
	}

	.form-actions-boton.limpiar,
	.form-actions-boton.cancelar {
		border-color: #475569;
		background: #334155;
		color: #e2e8f0;
	}

	.form-actions-boton.limpiar:hover:not(:disabled),
	.form-actions-boton.cancelar:hover:not(:disabled) {
		background: #475569;
	}

	.form-actions-boton.guardar {
		border-color: #2563eb;
		background: #2563eb;
		color: #fff;
	}

	.form-actions-boton.guardar:hover:not(:disabled) {
		background: #1d4ed8;
	}

	.form-actions-icono {
		font-size: 15px;
		font-weight: 800;
	}

	.form-actions-spinner {
		width: 15px;
		height: 15px;
		border: 2px solid rgb(255 255 255 / 35%);
		border-top-color: #fff;
		border-radius: 50%;
		animation: form-actions-girar 0.7s linear infinite;
	}

	@keyframes form-actions-girar {
		to {
			transform: rotate(360deg);
		}
	}

	@media (max-width: 600px) {
		.form-actions {
			align-items: stretch;
			flex-direction: column-reverse;
		}

		.form-actions-secundarias {
			display: grid;
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}

		.form-actions-boton {
			width: 100%;
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.form-actions-spinner {
			animation: none;
		}
	}
</style>
