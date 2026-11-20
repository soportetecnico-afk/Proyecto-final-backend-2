<script>
	let {
		columnas = [],
		filas = [],
		mensajeVacio = 'No hay información disponible.',
		cargando = false
	} = $props();
</script>

<div class="tabla-contenedor">
	{#if cargando}
		<div class="tabla-mensaje" role="status">
			<span class="tabla-cargando" aria-hidden="true"></span>
			<p>Cargando información...</p>
		</div>
	{:else if filas.length === 0}
		<div class="tabla-mensaje">
			<div class="tabla-vacio-icono" aria-hidden="true">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					width="30"
					height="30"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="1.5"
					stroke-linecap="round"
					stroke-linejoin="round"
				>
					<rect x="3" y="4" width="18" height="16" rx="2"></rect>
					<path d="M3 10h18"></path>
					<path d="M9 4v16"></path>
				</svg>
			</div>

			<p>{mensajeVacio}</p>
		</div>
	{:else}
		<div class="tabla-scroll">
			<table>
				<thead>
					<tr>
						{#each columnas as columna (columna.clave)}
							<th scope="col">{columna.etiqueta}</th>
						{/each}
					</tr>
				</thead>

				<tbody>
					{#each filas as fila, indice (fila.id ?? indice)}
						<tr>
							{#each columnas as columna (columna.clave)}
								<td>
									{#if columna.render}
										{@render columna.render(fila, indice)}
									{:else}
										{fila[columna.clave] ?? '—'}
									{/if}
								</td>
							{/each}
						</tr>
					{/each}
				</tbody>
			</table>
		</div>

		<div class="tabla-pie">
			<span>
				Información disponible: {filas.length}
			</span>
		</div>
	{/if}
</div>

<style>
	.tabla-contenedor {
		width: 100%;
		min-width: 0;
		overflow: hidden;
		border: 1px solid #334155;
		border-radius: 12px;
		background: #1e293b;
	}

	.tabla-scroll {
		width: 100%;
		overflow-x: auto;
	}

	table {
		width: 100%;
		border-collapse: collapse;
		text-align: left;
		color: #dbe5f5;
		font-size: 13px;
	}

	thead {
		background: #172338;
	}

	th {
		padding: 15px 18px;
		border-bottom: 1px solid #334155;
		color: #94b8e8;
		font-size: 11px;
		font-weight: 700;
		letter-spacing: 0.7px;
		text-transform: uppercase;
		white-space: nowrap;
	}

	td {
		padding: 15px 18px;
		border-bottom: 1px solid #29364d;
		color: #dbe5f5;
		vertical-align: middle;
	}

	tbody tr {
		transition: background-color 0.15s ease;
	}

	tbody tr:hover {
		background: #26354a;
	}

	tbody tr:last-child td {
		border-bottom: none;
	}

	.tabla-mensaje {
		display: flex;
		min-height: 190px;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 12px;
		padding: 30px 20px;
		color: #94a3b8;
		text-align: center;
	}

	.tabla-mensaje p {
		margin: 0;
		font-size: 13px;
		line-height: 1.6;
	}

	.tabla-vacio-icono {
		display: grid;
		width: 54px;
		height: 54px;
		place-items: center;
		border: 1px solid #334155;
		border-radius: 14px;
		background: #172338;
		color: #7f9dc5;
	}

	.tabla-cargando {
		width: 28px;
		height: 28px;
		border: 3px solid #334155;
		border-top-color: #60a5fa;
		border-radius: 50%;
		animation: girar 0.8s linear infinite;
	}

	.tabla-pie {
		display: flex;
		align-items: center;
		justify-content: flex-end;
		min-height: 46px;
		padding: 12px 18px;
		border-top: 1px solid #334155;
		background: #172338;
		color: #94a3b8;
		font-size: 12px;
	}

	:global(html[data-tema='claro']) .tabla-pie {
		background: #ffffff;
		color: #64748b;
	}

	@keyframes girar {
		to {
			transform: rotate(360deg);
		}
	}

	@media (max-width: 600px) {
		th,
		td {
			padding: 12px;
		}

		table {
			font-size: 12px;
		}

		.tabla-pie {
			padding: 12px;
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.tabla-cargando {
			animation-duration: 2s;
		}
	}
</style>
