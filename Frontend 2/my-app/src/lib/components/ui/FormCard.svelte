<script>
	let { titulo = 'Formulario', descripcion = '', etiqueta = '', children } = $props();
</script>

<section class="form-card">
	<header class="form-card-encabezado">
		<div class="form-card-identidad">
			{#if etiqueta}
				<span class="form-card-etiqueta">{etiqueta}</span>
			{/if}

			<h2>{titulo}</h2>

			{#if descripcion}
				<p>{descripcion}</p>
			{/if}
		</div>
	</header>

	<div class="form-card-contenido">
		{@render children?.()}
	</div>
</section>

<style>
	.form-card {
		width: 100%;
		min-width: 0;
		overflow: hidden;
		border: 1px solid #334155;
		border-radius: 14px;
		background: #1e293b;
		box-shadow: 0 4px 16px rgb(0 0 0 / 8%);
	}

	.form-card-encabezado {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 20px;
		padding: 22px 24px;
		border-bottom: 1px solid #334155;
		background: #172338;
	}

	.form-card-identidad {
		min-width: 0;
	}

	.form-card-etiqueta {
		display: inline-block;
		margin-bottom: 7px;
		color: #60a5fa;
		font-size: 10px;
		font-weight: 700;
		letter-spacing: 1.3px;
		text-transform: uppercase;
	}

	.form-card-identidad h2 {
		margin: 0;
		color: #f8fafc;
		font-size: 18px;
		font-weight: 700;
		line-height: 1.4;
	}

	.form-card-identidad p {
		margin: 6px 0 0;
		color: #94a3b8;
		font-size: 13px;
		line-height: 1.6;
	}

	.form-card-contenido {
		padding: 24px;
		color: #dbe5f5;
	}

	@media (max-width: 600px) {
		.form-card-encabezado {
			padding: 18px;
		}

		.form-card-contenido {
			padding: 18px;
		}

		.form-card-identidad h2 {
			font-size: 16px;
		}
	}
</style>
