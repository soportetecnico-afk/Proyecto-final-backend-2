<script>
	let {
		filtros = [],
		valores = $bindable({}),
		titulo = 'Filtros',
		onAplicar = undefined,
		onLimpiar = undefined,
		deshabilitado = false
	} = $props();

	function actualizarFiltro(clave, valor) {
		valores = {
			...valores,
			[clave]: valor
		};
	}

	function aplicarFiltros(evento) {
		evento.preventDefault();

		if (onAplicar) {
			onAplicar({ ...valores });
		}
	}

	function limpiarFiltros() {
		const nuevosValores = {};

		for (const filtro of filtros) {
			nuevosValores[filtro.clave] = '';
		}

		valores = nuevosValores;

		if (onLimpiar) {
			onLimpiar();
		}
	}
</script>

<section class="filter-bar">
	<div class="filter-encabezado">
		<div class="filter-titulo-contenedor">
			<span class="filter-icono" aria-hidden="true">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					width="19"
					height="19"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="1.8"
					stroke-linecap="round"
					stroke-linejoin="round"
				>
					<path d="M4 6h16"></path>
					<path d="M7 12h10"></path>
					<path d="M10 18h4"></path>
				</svg>
			</span>

			<h2>{titulo}</h2>
		</div>

		<button type="button" class="filter-limpiar" onclick={limpiarFiltros} disabled={deshabilitado}>
			Limpiar filtros
		</button>
	</div>

	<form class="filter-formulario" onsubmit={aplicarFiltros}>
		<div class="filter-campos">
			{#each filtros as filtro (filtro.clave)}
				<div class="filter-campo">
					<label for={`filtro-${filtro.clave}`}>
						{filtro.etiqueta}
					</label>

					{#if filtro.tipo === 'select'}
						<select
							id={`filtro-${filtro.clave}`}
							value={valores[filtro.clave] ?? ''}
							onchange={(evento) => actualizarFiltro(filtro.clave, evento.currentTarget.value)}
							disabled={deshabilitado}
						>
							<option value="">
								{filtro.placeholder ?? 'Todas las opciones'}
							</option>

							{#each filtro.opciones ?? [] as opcion (opcion.valor)}
								<option value={opcion.valor}>
									{opcion.etiqueta}
								</option>
							{/each}
						</select>
					{:else}
						<input
							id={`filtro-${filtro.clave}`}
							type={filtro.tipo ?? 'text'}
							value={valores[filtro.clave] ?? ''}
							placeholder={filtro.placeholder ?? ''}
							onchange={(evento) => actualizarFiltro(filtro.clave, evento.currentTarget.value)}
							disabled={deshabilitado}
						/>
					{/if}
				</div>
			{/each}
		</div>

		<div class="filter-acciones">
			<button type="submit" class="filter-aplicar" disabled={deshabilitado}>
				Aplicar filtros
			</button>
		</div>
	</form>
</section>

<style>
	.filter-bar {
		width: 100%;
		min-width: 0;
		padding: 20px;
		border: 1px solid #334155;
		border-radius: 12px;
		background: #1e293b;
	}

	.filter-encabezado {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 16px;
		margin-bottom: 20px;
	}

	.filter-titulo-contenedor {
		display: flex;
		align-items: center;
		gap: 10px;
	}

	.filter-icono {
		display: grid;
		width: 36px;
		height: 36px;
		flex-shrink: 0;
		place-items: center;
		border: 1px solid #334155;
		border-radius: 9px;
		background: #172338;
		color: #93c5fd;
	}

	.filter-titulo-contenedor h2 {
		margin: 0;
		color: #f8fafc;
		font-size: 15px;
		font-weight: 700;
	}

	.filter-limpiar {
		padding: 8px 10px;
		border: 1px solid transparent;
		border-radius: 7px;
		background: transparent;
		color: #93c5fd;
		font-family: inherit;
		font-size: 12px;
		font-weight: 600;
		cursor: pointer;
	}

	.filter-limpiar:hover:not(:disabled) {
		border-color: #334155;
		background: #172338;
	}

	.filter-formulario {
		display: flex;
		flex-direction: column;
		gap: 18px;
	}

	.filter-campos {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 16px;
	}

	.filter-campo {
		display: flex;
		flex-direction: column;
		gap: 8px;
		min-width: 0;
	}

	.filter-campo label {
		color: #cbd5e1;
		font-size: 12px;
		font-weight: 600;
	}

	.filter-campo input,
	.filter-campo select {
		width: 100%;
		min-width: 0;
		min-height: 42px;
		padding: 10px 12px;
		border: 1px solid #3b4b63;
		border-radius: 8px;
		outline: none;
		background: #172338;
		color: #f8fafc;
		font-family: inherit;
		font-size: 13px;
		transition:
			border-color 0.2s ease,
			box-shadow 0.2s ease;
	}

	.filter-campo input::placeholder {
		color: #8293ac;
	}

	.filter-campo input:focus,
	.filter-campo select:focus {
		border-color: #60a5fa;
		box-shadow: 0 0 0 3px rgb(59 130 246 / 15%);
	}

	.filter-campo input:disabled,
	.filter-campo select:disabled {
		cursor: not-allowed;
		opacity: 0.6;
	}

	.filter-campo option {
		background: #172338;
		color: #f8fafc;
	}

	.filter-acciones {
		display: flex;
		justify-content: flex-end;
	}

	.filter-aplicar {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		min-height: 40px;
		padding: 10px 16px;
		border: 1px solid #3b82f6;
		border-radius: 8px;
		background: #3b82f6;
		color: #fff;
		font-family: inherit;
		font-size: 12px;
		font-weight: 600;
		cursor: pointer;
		transition: background-color 0.2s ease;
	}

	.filter-aplicar:hover:not(:disabled) {
		background: #2563eb;
	}

	.filter-aplicar:disabled,
	.filter-limpiar:disabled {
		cursor: not-allowed;
		opacity: 0.5;
	}

	.filter-aplicar:focus-visible,
	.filter-limpiar:focus-visible {
		outline: 2px solid #60a5fa;
		outline-offset: 3px;
	}

	@media (max-width: 900px) {
		.filter-campos {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}
	}

	@media (max-width: 600px) {
		.filter-bar {
			padding: 16px;
		}

		.filter-encabezado {
			align-items: flex-start;
		}

		.filter-campos {
			grid-template-columns: minmax(0, 1fr);
		}

		.filter-acciones,
		.filter-aplicar {
			width: 100%;
		}
	}
</style>
