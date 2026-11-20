<script>
	import { page } from '$app/state';

	import Navbar from '$lib/components/layout/Navbar.svelte';
	import Sidebar from '$lib/components/layout/Sidebar.svelte';
	import Footer from '$lib/components/layout/Footer.svelte';

	let { children } = $props();

	let esLogin = $derived(page.url.pathname === '/login');
</script>

{#if esLogin}
	<div class="login-layout">
		{@render children()}
	</div>
{:else}
	<div class="app-layout">
		<Navbar />

		<div class="app-contenido">
			<Sidebar />

			<main class="app-main">
				{@render children()}
			</main>
		</div>

		<Footer />
	</div>
{/if}

<style>
	:global(html),
	:global(body) {
		min-height: 100%;
		margin: 0;
		background: #0f172a !important;
		color: #f8fafc;
	}

	:global(*) {
		box-sizing: border-box;
	}

	.app-layout {
		display: flex;
		min-height: 100vh;
		flex-direction: column;
		background: #0f172a;
	}

	.app-contenido {
		display: flex;
		flex: 1;
		min-height: 0;
	}

	.app-main {
		flex: 1;
		width: 0;
		min-width: 0;
		padding: 26px;
		background: #0f172a;
	}

	.login-layout {
		width: 100%;
		min-height: 100vh;
		background: #0f172a;
	}

	@media (max-width: 768px) {
		.app-contenido {
			flex-direction: column;
		}

		.app-main {
			width: 100%;
			padding: 16px;
		}
	}
</style>