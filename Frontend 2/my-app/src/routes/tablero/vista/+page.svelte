<script>
	import { onMount } from 'svelte';
	const API = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
	let datos = $state(null);
	let mensaje = $state('Cargando tablero…');
	const fmt = (n) => new Intl.NumberFormat('es-CO').format(Number(n ?? 0));
	const max = $derived(Math.max(1, ...(datos?.serie ?? []).map((x) => Number(x.total ?? 0))));
	onMount(() => {
		const sincronizarTema = () => {
			document.documentElement.dataset.tema = localStorage.getItem('tema_apariencia') || 'oscuro';
		};
		sincronizarTema();
		window.addEventListener('storage', sincronizarTema);
		return () => window.removeEventListener('storage', sincronizarTema);
	});
	onMount(async () => {
		try { const q = new URLSearchParams(location.search); const r = await fetch(`${API}/reportes/tablero?${q}`); const d = await r.json(); if(!r.ok) throw new Error(d.detail); datos=d; mensaje=''; }
		catch { mensaje='No fue posible cargar el tablero. Inténtalo nuevamente.'; }
	});
</script>
<svelte:head><title>Tablero compartido</title></svelte:head>
{#if datos}<main><h1>Actividad de reservas</h1><div class="kpis"><div><small>RESERVAS</small><strong>{fmt(datos.indicadores.total_reservas)}</strong></div><div><small>ESPACIOS UTILIZADOS</small><strong>{fmt(datos.indicadores.espacios_utilizados)}</strong></div><div><small>ASISTENTES</small><strong>{fmt(datos.indicadores.total_asistentes)}</strong></div></div><h2>Reservas por fecha</h2><div class="chart">{#each datos.serie as x (x.fecha)}<div><b>{fmt(x.total)}</b><i style={`height:${Math.max(4,Number(x.total)/max*100)}%`}></i><small>{String(x.fecha).slice(0,10)}</small></div>{:else}<p>No hay reservas en el período.</p>{/each}</div><h2>Distribución por estado</h2>{#each datos.distribucion as x (x.etiqueta)}<p class="row">{x.etiqueta}<b>{fmt(x.total)}</b></p>{/each}</main>{:else}<p class="loading">{mensaje}</p>{/if}
<style> :global(html[data-tema='oscuro']){color-scheme:dark;scrollbar-color:#64748b #0f172a}:global(html[data-tema='claro']){color-scheme:light;scrollbar-color:#94a3b8 #f1f5f9}:global(body){margin:0;background:#0f172a;color:#e2e8f0;font:14px system-ui}main{padding:20px}h1{font-size:22px}.kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.kpis div{background:#1e293b;border-radius:10px;padding:13px}.kpis small{color:#a78bfa;font-size:10px;font-weight:800}.kpis strong{display:block;font-size:26px;margin-top:8px}.chart{height:240px;display:flex;align-items:end;gap:10px;overflow:auto;background:#1e293b;border-radius:10px;padding:14px}.chart>div{height:100%;min-width:40px;display:flex;align-items:center;justify-content:end;flex-direction:column;gap:6px}.chart i{width:24px;min-height:3px;background:#38bdf8;border-radius:5px 5px 0 0}.chart small{color:#94a3b8;font-size:9px}.row{display:flex;justify-content:space-between;background:#1e293b;padding:10px;border-radius:8px}.loading{padding:24px;color:#94a3b8}:global(html[data-tema='claro'] body){background:#ffffff!important;color:#1e293b!important}:global(html[data-tema='claro'] main){background:#ffffff;color:#1e293b}:global(html[data-tema='claro'] .kpis div),:global(html[data-tema='claro'] .chart),:global(html[data-tema='claro'] .row){background:#ffffff;color:#1e293b}:global(html[data-tema='claro'] .chart small){color:#1e293b!important;font-size:11px!important;font-weight:500!important}:global(html[data-tema='claro'] .loading){color:#475569}</style>
