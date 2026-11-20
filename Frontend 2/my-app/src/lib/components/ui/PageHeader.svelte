<script>
	let {
		titulo = 'Página',
		descripcion = '',
		etiqueta = '',
		accionTexto = '',
		onAccion = undefined
	} = $props();
</script>

<section class="page-header">
	<div class="page-header-contenido">
		<div class="page-header-texto">
			{#if etiqueta}
				<span class="page-header-etiqueta">
					{etiqueta}
				</span>
			{/if}

			<h1>{titulo}</h1>

			{#if descripcion}
				<p>{descripcion}</p>
			{/if}
		</div>

		{#if accionTexto && onAccion}
			<button type="button" class="page-header-accion" onclick={onAccion}>
				<span aria-hidden="true">+</span>
				{accionTexto}
			</button>
		{/if}
	</div>
</section>

<style>
	.page-header {
		width: 100%;
		margin-bottom: 24px;
	}

	.page-header-contenido {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 20px;
	}

	.page-header-texto {
		min-width: 0;
	}

	.page-header-etiqueta {
		display: inline-block;
		margin-bottom: 8px;
		color: #60a5fa;
		font-size: 11px;
		font-weight: 700;
		letter-spacing: 1.5px;
		text-transform: uppercase;
	}

	.page-header h1 {
		margin: 0;
		color: #f8fafc;
		font-size: clamp(24px, 3vw, 32px);
		font-weight: 750;
		line-height: 1.25;
	}

	.page-header p {
		margin: 8px 0 0;
		color: #a9bad3;
		font-size: 15px;
		line-height: 1.6;
	}

	.page-header-accion {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: 8px;
		min-height: 44px;
		padding: 11px 18px;
		flex-shrink: 0;
		border: 1px solid #3b82f6;
		border-radius: 9px;
		background: #3b82f6;
		color: #ffffff;
		font-size: 14px;
		font-weight: 650;
		cursor: pointer;
		transition:
			background-color 0.2s ease,
			transform 0.2s ease;
	}

	.page-header-accion:hover {
		background: #2563eb;
		transform: translateY(-1px);
	}

	.page-header-accion:focus-visible {
		outline: 2px solid #93c5fd;
		outline-offset: 3px;
	}

	@media (max-width: 600px) {
		.page-header-contenido {
			align-items: flex-start;
			flex-direction: column;
		}

		.page-header-accion {
			width: 100%;
		}
	}
</style>
