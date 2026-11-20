<script>
	let {
		texto = 'Botón',
		variante = 'primario',
		tipo = 'button',
		deshabilitado = false,
		onClick = undefined
	} = $props();
</script>

<button
	type={tipo}
	class="base-button"
	class:primario={variante === 'primario'}
	class:secundario={variante === 'secundario'}
	class:exito={variante === 'exito'}
	class:peligro={variante === 'peligro'}
	class:contorno={variante === 'contorno'}
	disabled={deshabilitado}
	onclick={onClick}
>
	{#if variante === 'primario'}
		<span class="boton-icono" aria-hidden="true">+</span>
	{/if}

	<span>{texto}</span>
</button>

<style>
	.base-button {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: 8px;
		min-height: 42px;
		padding: 10px 16px;
		border: 1px solid transparent;
		border-radius: 9px;
		font-family: inherit;
		font-size: 14px;
		font-weight: 600;
		cursor: pointer;
		transition:
			background-color 0.2s ease,
			border-color 0.2s ease,
			transform 0.2s ease;
	}

	.base-button:hover:not(:disabled) {
		transform: translateY(-1px);
	}

	.base-button:focus-visible {
		outline: 2px solid #93c5fd;
		outline-offset: 3px;
	}

	.primario {
		border-color: #3b82f6;
		background: #3b82f6;
		color: #ffffff;
	}

	.primario:hover:not(:disabled) {
		background: #2563eb;
	}

	.secundario {
		border-color: #475569;
		background: #334155;
		color: #f8fafc;
	}

	.secundario:hover:not(:disabled) {
		background: #475569;
	}

	.exito {
		border-color: #15803d;
		background: #15803d;
		color: #ffffff;
	}

	.exito:hover:not(:disabled) {
		background: #166534;
	}

	.peligro {
		border-color: #dc2626;
		background: #dc2626;
		color: #ffffff;
	}

	.peligro:hover:not(:disabled) {
		background: #b91c1c;
	}

	.contorno {
		border-color: #64748b;
		background: transparent;
		color: #e2e8f0;
	}

	.contorno:hover:not(:disabled) {
		background: #1e293b;
	}

	.base-button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
		transform: none;
	}

	.boton-icono {
		font-size: 19px;
		line-height: 1;
	}

	@media (max-width: 480px) {
		.base-button {
			min-height: 44px;
		}
	}
</style>
