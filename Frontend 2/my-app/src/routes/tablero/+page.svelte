<script>
	import { onMount } from 'svelte';

	const API = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
	let inicio = $state('');
	let fin = $state('');
	let reporte = $state(null);
	let cargando = $state(false);
	let error = $state('');
	let marcoSrc = $state('/tablero/vista');
	let marcoIframe = $state(null);

	function sincronizarTemaIframe() {
		const tema = document.documentElement.dataset.tema || localStorage.getItem('tema_apariencia') || 'oscuro';
		const documentoIframe = marcoIframe?.contentDocument;
		if (documentoIframe) documentoIframe.documentElement.dataset.tema = tema;
	}

	onMount(() => {
		const observadorTema = new MutationObserver(sincronizarTemaIframe);
		observadorTema.observe(document.documentElement, { attributes: true, attributeFilter: ['data-tema'] });
		sincronizarTemaIframe();
		return () => observadorTema.disconnect();
	});

	const numero = (v) => new Intl.NumberFormat('es-CO').format(Number(v ?? 0));
	const maximo = $derived(Math.max(1, ...(reporte?.serie ?? []).map((x) => Number(x.total ?? 0))));

	async function consultar() {
		cargando = true;
		error = '';
		try {
			const q = new URLSearchParams({ tipo_reporte: 'reservas' });
			if (inicio) q.set('fecha_inicial', inicio);
			if (fin) q.set('fecha_final', fin);
			const res = await fetch(`${API}/reportes/?${q}`);
			const data = await res.json();
			if (!res.ok) throw new Error(data.detail || 'No fue posible cargar los datos.');
			reporte = data;
			const embed = new URLSearchParams();
			if (inicio) embed.set('fecha_inicial', inicio);
			if (fin) embed.set('fecha_final', fin);
			marcoSrc = `/tablero/vista${embed.size ? `?${embed}` : ''}`;
		} catch (e) {
			error = 'No fue posible cargar el tablero. Inténtalo nuevamente.';
		} finally { cargando = false; }
	}

	function compartir() {
		navigator.clipboard?.writeText(new URL(marcoSrc, location.origin).href)
			.then(() => alert('Enlace del tablero copiado. Comparte este iframe: ' + `<iframe src="${new URL(marcoSrc, location.origin).href}" width="100%" height="700"></iframe>`))
			.catch(() => {});
	}
</script>

<svelte:head><title>Tablero | Reservas CUL</title><meta name="description" content="Indicadores y gráficos de uso de espacios universitarios." /></svelte:head>

<main class="page">
	<header><div><span class="eyebrow">ANÁLISIS INSTITUCIONAL</span><h1>Tablero de reservas</h1><p>Indicadores de ocupación y actividad de los espacios.</p></div><button class="share" onclick={compartir}>Compartir iframe</button></header>
	<form class="filters" onsubmit={(e) => { e.preventDefault(); consultar(); }}>
		<label>Desde<input type="date" bind:value={inicio} /></label><label>Hasta<input type="date" bind:value={fin} min={inicio || undefined} /></label>
		<button disabled={cargando}>{cargando ? 'Consultando…' : 'Aplicar filtros'}</button>
	</form>
	{#if error}<p class="error" role="alert">{error}</p>{/if}
	{#if reporte}
		<section class="cards" aria-label="Indicadores">
			<article><span>RESERVAS</span><strong>{numero(reporte.indicadores.total_reservas)}</strong><small>Registros en el período</small></article>
			<article><span>ESPACIOS UTILIZADOS</span><strong>{numero(reporte.indicadores.espacios_utilizados)}</strong><small>Espacios con reservas</small></article>
			<article><span>ASISTENTES</span><strong>{numero(reporte.indicadores.total_asistentes)}</strong><small>Asistencia estimada</small></article>
		</section>
		<section class="charts">
			<article class="panel"><h2>Reservas por fecha</h2><p>Barras según el período consultado.</p><div class="bars">{#each reporte.serie as x (x.fecha)}<div class="barCol"><b>{numero(x.total)}</b><div class="bar" style={`height:${Math.max(4, Number(x.total) / maximo * 100)}%`}></div><small>{String(x.fecha).slice(0,10)}</small></div>{:else}<p>No hay reservas en este período.</p>{/each}</div></article>
			<article class="panel"><h2>Estados de reserva</h2><p>Distribución de los registros.</p><div class="legend">{#each reporte.distribucion as x, i (x.etiqueta)}<div><span class:green={i === 0} class:purple={i > 0}></span>{x.etiqueta}<b>{numero(x.total)}</b></div>{:else}<p>No hay datos para mostrar.</p>{/each}</div></article>
		</section>
	{:else}<section class="empty">Aplica los filtros para cargar indicadores reales desde el sistema.</section>{/if}
	<section class="embed"><div><h2>Vista para compartir</h2><p>El tablero se publica dentro de este módulo mediante iframe. El enlace puede incorporarse a otra página.</p></div><iframe bind:this={marcoIframe} onload={sincronizarTemaIframe} title="Vista compartible del tablero" src={marcoSrc} loading="lazy"></iframe></section>
</main>

<style>
	.page{max-width:1450px;margin:auto;color:#e2e8f0}header{display:flex;justify-content:space-between;align-items:center;margin-bottom:22px}.eyebrow{color:#a78bfa;font-size:11px;font-weight:800;letter-spacing:.14em}h1{font-size:30px;margin:8px 0}header p,.panel p,.embed p{color:#94a3b8;margin:4px 0}.share,.filters button{border:0;border-radius:9px;background:#7c3aed;color:white;font-weight:700;padding:12px 16px;cursor:pointer}.filters{display:flex;align-items:end;gap:14px;background:#172033;padding:16px;border-radius:14px;margin:20px 0}.filters label{display:grid;gap:7px;color:#cbd5e1;font-size:13px}.filters input{color:#e2e8f0;background:#0f172a;border:1px solid #334155;padding:10px;border-radius:8px}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:18px 0}.cards article,.panel,.embed,.empty{background:#172033;border:1px solid #26344b;border-radius:14px;padding:20px}.cards span{color:#94a3b8;font-size:11px;font-weight:800}.cards strong{display:block;font-size:32px;margin:10px 0}.cards small{color:#94a3b8}.charts{display:grid;grid-template-columns:2fr 1fr;gap:16px}.panel h2,.embed h2{font-size:17px;margin:0 0 6px}.bars{height:250px;display:flex;align-items:end;gap:12px;overflow-x:auto;padding:20px 4px 0}.barCol{height:100%;min-width:46px;display:flex;flex-direction:column;align-items:center;justify-content:end;gap:7px}.bar{width:28px;min-height:3px;background:linear-gradient(#38bdf8,#2563eb);border-radius:7px 7px 2px 2px}.barCol small{font-size:10px;color:#94a3b8;white-space:nowrap}.legend{display:grid;gap:16px;margin-top:26px}.legend div{display:flex;align-items:center;gap:9px}.legend span{width:12px;height:12px;border-radius:3px;background:#f87171}.legend span.green{background:#34d399}.legend span.purple{background:#a78bfa}.legend b{margin-left:auto}.embed{margin-top:18px;display:grid;gap:14px}.embed iframe{width:100%;height:460px;border:1px solid #334155;border-radius:10px;background:#0f172a}.embed code{display:block;white-space:normal;overflow-wrap:anywhere;padding:12px;background:#0f172a;color:#a5b4fc;border-radius:8px}.error{background:#7f1d1d;color:#fee2e2;padding:12px;border-radius:8px}.empty{color:#94a3b8}.filters button:disabled{opacity:.65}@media(max-width:800px){header{align-items:flex-start;gap:12px;flex-direction:column}.cards{grid-template-columns:1fr}.charts{grid-template-columns:1fr}.filters{align-items:stretch;flex-direction:column}.filters label,.filters input{width:100%}.embed iframe{height:400px}}
	:global(html[data-tema='claro'] .page) { background: #ffffff; color: #1e293b; padding: 24px; border-radius: 14px; }
	:global(html[data-tema='claro'] .page header p), :global(html[data-tema='claro'] .page .panel p), :global(html[data-tema='claro'] .page .embed p) { color: #475569; }
	:global(html[data-tema='claro'] .page .filters), :global(html[data-tema='claro'] .page .cards article), :global(html[data-tema='claro'] .page .panel), :global(html[data-tema='claro'] .page .embed), :global(html[data-tema='claro'] .page .empty) { background: #ffffff; color: #1e293b; }
	:global(html[data-tema='claro'] .page .filters label), :global(html[data-tema='claro'] .page .cards span), :global(html[data-tema='claro'] .page .cards small), :global(html[data-tema='claro'] .page .barCol small) { color: #475569; }
	:global(html[data-tema='claro'] .page .filters input) { background: #ffffff; color: #1e293b; }
	:global(html[data-tema='claro'] .page .embed iframe), :global(html[data-tema='claro'] .page .embed code) { background: #ffffff; color: #334155; }
	:global(html[data-tema='oscuro'] .page) { background: transparent; color: #e2e8f0; }
	:global(html[data-tema='oscuro'] .page .filters), :global(html[data-tema='oscuro'] .page .cards article), :global(html[data-tema='oscuro'] .page .panel), :global(html[data-tema='oscuro'] .page .embed), :global(html[data-tema='oscuro'] .page .empty) { background: #1e293b; border-color: #334155; color: #e2e8f0; }
	:global(html[data-tema='oscuro'] .page .filters input), :global(html[data-tema='oscuro'] .page .embed iframe), :global(html[data-tema='oscuro'] .page .embed code) { background: #0f172a; color: #e2e8f0; }
</style>
