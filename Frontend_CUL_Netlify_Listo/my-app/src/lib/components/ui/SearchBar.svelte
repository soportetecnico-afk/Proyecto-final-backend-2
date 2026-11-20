<script>
	let {
		valor = $bindable(''),
		placeholder = 'Buscar...',
		etiqueta = 'Buscar',
		deshabilitado = false,
		onBuscar = undefined,
		onLimpiar = undefined
	} = $props();

	function manejarEnvio(evento) {
		evento.preventDefault();

		if (onBuscar) {
			onBuscar(valor.trim());
		}
	}

	function limpiarBusqueda() {
		valor = '';

		if (onLimpiar) {
			onLimpiar();
		}
	}
</script>

<form class="search-bar" onsubmit={manejarEnvio}>
	<label class="search-label" for="campo-busqueda">
		{etiqueta}
	</label>

	<div class="search-contenedor">
		<span class="search-icono" aria-hidden="true">
			<svg
				xmlns="http://www.w3.org/2000/svg"
				width="20"
				height="20"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="1.8"
				stroke-linecap="round"
				stroke-linejoin="round"
			>
				<circle cx="11" cy="11" r="7"></circle>
				<path d="m20 20-4-4"></path>
			</svg>
		</span>

		<input
			id="campo-busqueda"
			type="search"
			bind:value={valor}
			{placeholder}
			disabled={deshabilitado}
			class="search-input"
			autocomplete="off"
		/>

		{#if valor}
			<button
				type="button"
				class="search-limpiar"
				onclick={limpiarBusqueda}
				aria-label="Limpiar búsqueda"
				disabled={deshabilitado}
			>
				×
			</button>
		{/if}

		<button type="submit" class="search-boton" disabled={deshabilitado}> Buscar </button>
	</div>
</form>

<style>
	.search-bar {
		display: flex;
		flex-direction: column;
		gap: 9px;
		width: 100%;
		min-width: 0;
	}

	.search-label {
		color: #dbe5f5;
		font-size: 13px;
		font-weight: 600;
	}

	.search-contenedor {
		display: flex;
		align-items: center;
		gap: 10px;
		width: 100%;
		min-height: 46px;
		padding: 5px 6px 5px 13px;
		border: 1px solid #3b4b63;
		border-radius: 10px;
		background: #172338;
		transition:
			border-color 0.2s ease,
			box-shadow 0.2s ease;
	}

	.search-contenedor:focus-within {
		border-color: #60a5fa;
		box-shadow: 0 0 0 3px rgb(59 130 246 / 15%);
	}

	.search-icono {
		display: grid;
		place-items: center;
		flex-shrink: 0;
		color: #94a3b8;
	}

	.search-input {
		flex: 1;
		width: 100%;
		min-width: 0;
		padding: 7px 0;
		border: none;
		outline: none;
		background: transparent;
		color: #f8fafc;
		font-family: inherit;
		font-size: 14px;
	}

	.search-input::placeholder {
		color: #8293ac;
	}

	.search-input:disabled {
		cursor: not-allowed;
		opacity: 0.6;
	}

	.search-input::-webkit-search-cancel-button {
		display: none;
	}

	.search-limpiar {
		display: grid;
		place-items: center;
		width: 30px;
		height: 30px;
		flex-shrink: 0;
		border: none;
		border-radius: 6px;
		background: transparent;
		color: #94a3b8;
		font-size: 22px;
		cursor: pointer;
	}

	.search-limpiar:hover:not(:disabled) {
		background: #334155;
		color: #fff;
	}

	.search-boton {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		min-height: 34px;
		padding: 8px 14px;
		flex-shrink: 0;
		border: 1px solid #3b82f6;
		border-radius: 7px;
		background: #3b82f6;
		color: #fff;
		font-family: inherit;
		font-size: 12px;
		font-weight: 600;
		cursor: pointer;
		transition: background-color 0.2s ease;
	}

	.search-boton:hover:not(:disabled) {
		background: #2563eb;
	}

	.search-boton:disabled,
	.search-limpiar:disabled {
		cursor: not-allowed;
		opacity: 0.5;
	}

	.search-boton:focus-visible,
	.search-limpiar:focus-visible {
		outline: 2px solid #93c5fd;
		outline-offset: 2px;
	}

	@media (max-width: 480px) {
		.search-contenedor {
			gap: 7px;
			padding-left: 10px;
		}

		.search-boton {
			padding: 8px 10px;
		}
	}
</style>
