<script lang="ts">
	import '../app.css';
	import Nav from '$lib/components/Nav.svelte';
	import { theme } from '$lib/stores/theme';
	import { onMount } from 'svelte';

	let { children } = $props();

	onMount(() => {
		theme.init();
	});
</script>

<svelte:head>
	<title>Quantara — RBI Rate Path Simulator</title>
</svelte:head>

<Nav />

<main>
	{@render children()}
</main>

<style>
	main {
		min-height: calc(100vh - 56px);
		background-color: var(--bg);
	}
</style>
