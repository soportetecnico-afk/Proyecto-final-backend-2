<script>
	let {
		titulo = 'Indicador',
		valor = '—',
		descripcion = '',
		icono = '▦',
		variante = 'azul'
	} = $props();
</script>

<article
	class="stat-card"
	class:verde={variante === 'verde'}
	class:amarillo={variante === 'amarillo'}
	class:rojo={variante === 'rojo'}
>
	<div class="stat-card-contenido">
		<div class="stat-card-texto">
			<span class="stat-card-titulo">{titulo}</span>
			<strong class="stat-card-valor">{valor}</strong>

			{#if descripcion}
				<span class="stat-card-descripcion">{descripcion}</span>
			{/if}
		</div>

		<div class="stat-card-icono" aria-hidden="true">
			{icono}
		</div>
	</div>
</article>

<style>
	.stat-card {
		min-width: 0;
		padding: 22px;
		border: 1px solid #334155;
		border-radius: 14px;
		background: #1e293b;
		box-shadow: 0 4px 12px rgb(0 0 0 / 8%);
		transition:
			border-color 0.2s ease,
			transform 0.2s ease;
	}

	.stat-card:hover {
		border-color: #4b6b96;
		transform: translateY(-2px);
	}

	.stat-card-contenido {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 16px;
	}

	.stat-card-texto {
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		gap: 9px;
		min-width: 0;
	}

	.stat-card-titulo {
		color: #b7c7df;
		font-size: 14px;
		font-weight: 500;
	}

	.stat-card-valor {
		color: #f8fafc;
		font-size: clamp(26px, 3vw, 34px);
		font-weight: 750;
		line-height: 1.2;
		overflow-wrap: anywhere;
	}

	.stat-card-descripcion {
		color: #94a3b8;
		font-size: 12px;
		line-height: 1.5;
	}

	.stat-card-icono {
		display: grid;
		place-items: center;
		width: 44px;
		height: 44px;
		flex-shrink: 0;
		border: 1px solid #3b82f6;
		border-radius: 12px;
		background: rgb(59 130 246 / 12%);
		color: #93c5fd;
		font-size: 22px;
	}

	.stat-card.verde .stat-card-icono {
		border-color: #16a34a;
		background: rgb(22 163 74 / 12%);
		color: #86efac;
	}

	.stat-card.amarillo .stat-card-icono {
		border-color: #ca8a04;
		background: rgb(202 138 4 / 12%);
		color: #fde047;
	}

	.stat-card.rojo .stat-card-icono {
		border-color: #dc2626;
		background: rgb(220 38 38 / 12%);
		color: #fca5a5;
	}

	@media (max-width: 480px) {
		.stat-card {
			padding: 18px;
		}
	}
</style>
