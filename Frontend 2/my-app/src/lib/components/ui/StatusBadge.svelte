<script>
	let { estado = '', etiqueta = '', variante = 'auto' } = $props();

	const variantesValidas = [
		'pendiente',
		'aprobada',
		'rechazada',
		'activa',
		'inactiva',
		'cancelada',
		'neutral'
	];

	const obtenerVariante = () => {
		if (variante !== 'auto' && variantesValidas.includes(variante)) {
			return variante;
		}

		const normalizado = String(estado)
			.trim()
			.toLowerCase()
			.normalize('NFD')
			.replace(/[\u0300-\u036f]/g, '');

		const equivalencias = {
			pendiente: 'pendiente',
			aprobada: 'aprobada',
			aprobado: 'aprobada',
			rechazada: 'rechazada',
			rechazado: 'rechazada',
			activa: 'activa',
			activo: 'activa',
			inactiva: 'inactiva',
			inactivo: 'inactiva',
			cancelada: 'cancelada',
			cancelado: 'cancelada'
		};

		return equivalencias[normalizado] ?? 'neutral';
	};
</script>

<span
	class="status-badge"
	class:pendiente={obtenerVariante() === 'pendiente'}
	class:aprobada={obtenerVariante() === 'aprobada'}
	class:rechazada={obtenerVariante() === 'rechazada'}
	class:activa={obtenerVariante() === 'activa'}
	class:inactiva={obtenerVariante() === 'inactiva'}
	class:cancelada={obtenerVariante() === 'cancelada'}
	class:neutral={obtenerVariante() === 'neutral'}
>
	<span class="status-punto" aria-hidden="true"></span>
	{etiqueta || estado || 'Sin estado'}
</span>

<style>
	.status-badge {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: 7px;
		width: fit-content;
		max-width: 100%;
		padding: 6px 10px;
		border: 1px solid transparent;
		border-radius: 999px;
		font-size: 12px;
		font-weight: 600;
		line-height: 1.3;
		overflow-wrap: anywhere;
	}

	.status-punto {
		width: 7px;
		height: 7px;
		flex-shrink: 0;
		border-radius: 50%;
		background: currentColor;
	}

	.pendiente {
		border-color: #854d0e;
		background: rgb(234 179 8 / 12%);
		color: #fde047;
	}

	.aprobada {
		border-color: #166534;
		background: rgb(34 197 94 / 12%);
		color: #86efac;
	}

	.rechazada {
		border-color: #991b1b;
		background: rgb(239 68 68 / 12%);
		color: #fca5a5;
	}

	.activa {
		border-color: #1d4ed8;
		background: rgb(59 130 246 / 12%);
		color: #93c5fd;
	}

	.inactiva {
		border-color: #475569;
		background: rgb(148 163 184 / 10%);
		color: #cbd5e1;
	}

	.cancelada {
		border-color: #9a3412;
		background: rgb(249 115 22 / 12%);
		color: #fdba74;
	}

	.neutral {
		border-color: #475569;
		background: rgb(148 163 184 / 10%);
		color: #cbd5e1;
	}
</style>
