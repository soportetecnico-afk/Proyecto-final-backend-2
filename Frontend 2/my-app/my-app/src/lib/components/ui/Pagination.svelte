<script>
	let {
		paginaActual = $bindable(1),
		totalPaginas = 1,
		totalRegistros = 0,
		registrosPorPagina = 10,
		deshabilitado = false,
		onCambiarPagina = undefined
	} = $props();

	let paginasVisibles = $derived.by(() => {
		const total = Math.max(1, Number(totalPaginas) || 1);
		const actual = Math.min(total, Math.max(1, Number(paginaActual) || 1));

		const inicio = Math.max(1, actual - 2);
		const fin = Math.min(total, actual + 2);

		const paginas = [];

		for (let pagina = inicio; pagina <= fin; pagina++) {
			paginas.push(pagina);
		}

		return paginas;
	});

	let inicioRegistro = $derived(
		totalRegistros === 0 ? 0 : (paginaActual - 1) * registrosPorPagina + 1
	);

	let finRegistro = $derived(Math.min(paginaActual * registrosPorPagina, totalRegistros));

	function cambiarPagina(nuevaPagina) {
		const total = Math.max(1, Number(totalPaginas) || 1);

		if (deshabilitado || nuevaPagina < 1 || nuevaPagina > total || nuevaPagina === paginaActual) {
			return;
		}

		paginaActual = nuevaPagina;

		if (onCambiarPagina) {
			onCambiarPagina(nuevaPagina);
		}
	}
</script>

{#if totalPaginas > 0}
	<nav class="pagination" aria-label="Paginación de resultados">
		<div class="pagination-informacion">
			<span>
				Mostrando
				<strong>{inicioRegistro}–{finRegistro}</strong>
				de
				<strong>{totalRegistros}</strong>
				registros
			</span>
		</div>

		<div class="pagination-controles">
			<button
				type="button"
				class="pagination-flecha"
				aria-label="Página anterior"
				disabled={deshabilitado || paginaActual <= 1}
				onclick={() => cambiarPagina(paginaActual - 1)}
			>
				‹
			</button>

			{#if paginasVisibles[0] > 1}
				<button
					type="button"
					class="pagination-numero"
					onclick={() => cambiarPagina(1)}
					disabled={deshabilitado}
				>
					1
				</button>

				{#if paginasVisibles[0] > 2}
					<span class="pagination-puntos">…</span>
				{/if}
			{/if}

			{#each paginasVisibles as pagina (pagina)}
				<button
					type="button"
					class="pagination-numero"
					class:activo={pagina === paginaActual}
					aria-current={pagina === paginaActual ? 'page' : undefined}
					aria-label={`Página ${pagina}`}
					disabled={deshabilitado}
					onclick={() => cambiarPagina(pagina)}
				>
					{pagina}
				</button>
			{/each}

			{#if paginasVisibles[paginasVisibles.length - 1] < totalPaginas}
				{#if paginasVisibles[paginasVisibles.length - 1] < totalPaginas - 1}
					<span class="pagination-puntos">…</span>
				{/if}

				<button
					type="button"
					class="pagination-numero"
					onclick={() => cambiarPagina(totalPaginas)}
					disabled={deshabilitado}
				>
					{totalPaginas}
				</button>
			{/if}

			<button
				type="button"
				class="pagination-flecha"
				aria-label="Página siguiente"
				disabled={deshabilitado || paginaActual >= totalPaginas}
				onclick={() => cambiarPagina(paginaActual + 1)}
			>
				›
			</button>
		</div>
	</nav>
{/if}

<style>
	.pagination {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 20px;
		width: 100%;
		padding: 16px 0;
	}

	.pagination-informacion {
		color: #94a3b8;
		font-size: 12px;
		line-height: 1.6;
	}

	.pagination-informacion strong {
		color: #dbe5f5;
		font-weight: 600;
	}

	.pagination-controles {
		display: flex;
		align-items: center;
		justify-content: flex-end;
		gap: 5px;
	}

	.pagination-numero,
	.pagination-flecha {
		display: grid;
		min-width: 34px;
		height: 34px;
		flex-shrink: 0;
		place-items: center;
		border: 1px solid #334155;
		border-radius: 8px;
		background: #1e293b;
		color: #cbd5e1;
		font-family: inherit;
		font-size: 12px;
		cursor: pointer;
		transition:
			background-color 0.2s ease,
			border-color 0.2s ease;
	}

	.pagination-numero:hover:not(:disabled),
	.pagination-flecha:hover:not(:disabled) {
		border-color: #3b82f6;
		background: #263b59;
		color: #fff;
	}

	.pagination-numero.activo {
		border-color: #3b82f6;
		background: #2563eb;
		color: #fff;
		font-weight: 700;
	}

	.pagination-numero:disabled,
	.pagination-flecha:disabled {
		cursor: not-allowed;
		opacity: 0.4;
	}

	.pagination-numero:focus-visible,
	.pagination-flecha:focus-visible {
		outline: 2px solid #60a5fa;
		outline-offset: 2px;
	}

	.pagination-puntos {
		padding: 0 3px;
		color: #94a3b8;
		font-size: 13px;
	}

	@media (max-width: 600px) {
		.pagination {
			align-items: flex-start;
			flex-direction: column;
			gap: 12px;
		}

		.pagination-controles {
			justify-content: flex-start;
			flex-wrap: wrap;
		}
	}
</style>
