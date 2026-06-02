<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import FanChart from '$lib/components/FanChart.svelte';
	import TerminalDistribution from '$lib/components/TerminalDistribution.svelte';
	import ModelParams from '$lib/components/ModelParams.svelte';
	import type { SimulationResponse } from '$lib/api/types';

	let model = $state<'vasicek' | 'cir'>('cir');
	let currentRate = $state(5.75);
	let horizonMonths = $state(12);
	let nPaths = $state(10000);
	let loading = $state(false);
	let error = $state<string | null>(null);
	let result = $state<SimulationResponse | null>(null);

	async function runSimulation() {
		loading = true;
		error = null;
		try {
			const req = {
				current_rate: currentRate,
				horizon_months: horizonMonths,
				n_paths: nPaths,
				use_calibrated: true
			};
			result = model === 'vasicek'
				? await api.simulateVasicek(req)
				: await api.simulateCIR(req);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Simulation failed';
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		runSimulation();
	});

	const td = $derived(result?.terminal_distribution);
</script>

<svelte:head>
	<title>Simulator — Quantara</title>
</svelte:head>

<div class="page">
	<div class="page-header">
		<div class="page-eyebrow">Rate Path Simulator</div>
		<h1>10,000 possible futures</h1>
		<p class="page-sub">Stochastic simulation of RBI repo rate paths using MLE-calibrated parameters from historical data.</p>
	</div>

	<hr class="section-rule" />

	<div class="simulator-layout">
		<!-- Left: controls -->
		<aside class="controls-panel">
			<div class="control-group">
				<label class="ctrl-label" for="rate-input">Current Rate (%)</label>
				<input
					id="rate-input"
					type="number"
					min="0" max="25" step="0.25"
					bind:value={currentRate}
					class="ctrl-input mono"
				/>
			</div>

			<div class="control-group">
				<label class="ctrl-label" for="horizon-input">Horizon (months)</label>
				<input
					id="horizon-input"
					type="range"
					min="1" max="24"
					bind:value={horizonMonths}
					class="ctrl-range"
				/>
				<span class="ctrl-range-val mono">{horizonMonths} months</span>
			</div>

			<div class="control-group">
				<label class="ctrl-label" for="paths-input">Number of Paths</label>
				<select id="paths-input" bind:value={nPaths} class="ctrl-select mono">
					<option value={1000}>1,000</option>
					<option value={5000}>5,000</option>
					<option value={10000}>10,000</option>
					<option value={25000}>25,000</option>
					<option value={50000}>50,000</option>
				</select>
			</div>

			<div class="control-group">
				<div class="ctrl-label">Model</div>
				<div class="model-toggle">
					<button
						class="toggle-btn"
						class:active={model === 'cir'}
						onclick={() => (model = 'cir')}
					>CIR</button>
					<button
						class="toggle-btn"
						class:active={model === 'vasicek'}
						onclick={() => (model = 'vasicek')}
					>Vasicek</button>
				</div>
			</div>

			<button class="run-btn" onclick={runSimulation} disabled={loading}>
				{loading ? 'Simulating…' : 'Run Simulation'}
			</button>

			{#if result}
				<ModelParams {result} />
			{/if}
		</aside>

		<!-- Main: chart -->
		<div class="chart-panel">
			{#if error}
				<div class="error-msg">{error}</div>
			{:else if loading}
				<div class="loading-state">
					<div class="loading-bar"></div>
					<span class="loading-text mono">Simulating {nPaths.toLocaleString()} paths…</span>
				</div>
			{:else if result}
				<div class="chart-header">
					<h2 class="chart-title">Rate paths — next {horizonMonths} months</h2>
					{#if result.cache_hit}
						<span class="cache-badge mono">cached</span>
					{/if}
				</div>

				<FanChart
					data={result.paths_summary}
					timeAxis={result.time_axis}
					model={result.model}
					height={420}
				/>

				<!-- Stats strip -->
				{#if td}
					<div class="stats-strip">
						<div class="stat">
							<span class="stat-label">Mean terminal</span>
							<span class="stat-val mono">{td.mean.toFixed(2)}%</span>
						</div>
						<div class="stat">
							<span class="stat-label">Std dev</span>
							<span class="stat-val mono">±{td.std.toFixed(2)}%</span>
						</div>
						<div class="stat">
							<span class="stat-label">5th pct</span>
							<span class="stat-val mono down">{td.p5.toFixed(2)}%</span>
						</div>
						<div class="stat">
							<span class="stat-label">95th pct</span>
							<span class="stat-val mono up">{td.p95.toFixed(2)}%</span>
						</div>
						<div class="stat">
							<span class="stat-label">P(rate rises)</span>
							<span class="stat-val mono">{(result.prob_increase * 100).toFixed(1)}%</span>
						</div>
						<div class="stat">
							<span class="stat-label">P(rate falls)</span>
							<span class="stat-val mono">{(result.prob_decrease * 100).toFixed(1)}%</span>
						</div>
					</div>
				{/if}

				<hr class="section-rule mt-6" />

				<div class="dist-section">
					<h3 class="dist-title">Terminal rate distribution</h3>
					<p class="dist-sub">Where rates land at month {horizonMonths}, across all paths</p>
					{#if td}
						<TerminalDistribution data={td} height={160} />
					{/if}
				</div>
			{:else}
				<div class="empty-state">Configure parameters and run a simulation.</div>
			{/if}
		</div>
	</div>
</div>

<style>
	.page {
		max-width: 1280px;
		margin: 0 auto;
		padding: 0 2rem 4rem;
	}

	.page-header {
		padding: 3rem 0 2rem;
	}

	.page-eyebrow {
		font-family: var(--font-mono);
		font-size: 0.6875rem;
		text-transform: uppercase;
		letter-spacing: 0.12em;
		color: var(--accent);
		margin-bottom: 0.75rem;
	}

	.page-header h1 {
		font-size: clamp(1.75rem, 3vw, 2.5rem);
		margin-bottom: 0.75rem;
	}

	.page-sub {
		font-size: 0.9375rem;
		color: var(--text-muted);
		max-width: 580px;
		line-height: 1.6;
	}

	.simulator-layout {
		display: grid;
		grid-template-columns: 280px 1fr;
		gap: 3rem;
		margin-top: 2.5rem;
	}

	/* Controls */
	.controls-panel {
		display: flex;
		flex-direction: column;
		gap: 1.25rem;
	}

	.control-group {
		display: flex;
		flex-direction: column;
		gap: 0.375rem;
	}

	.ctrl-label {
		font-size: 0.6875rem;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--text-faint);
		font-family: var(--font-mono);
	}

	.ctrl-input,
	.ctrl-select {
		background-color: var(--surface);
		border: 1px solid var(--border);
		color: var(--text-primary);
		padding: 0.5rem 0.75rem;
		font-size: 1rem;
		font-family: var(--font-mono);
		border-radius: 2px;
		outline: none;
		width: 100%;
		transition: border-color 0.15s;
	}

	.ctrl-input:focus,
	.ctrl-select:focus {
		border-color: var(--accent);
	}

	.ctrl-range {
		accent-color: var(--accent);
		width: 100%;
	}

	.ctrl-range-val {
		font-size: 0.875rem;
		color: var(--text-primary);
		text-align: right;
	}

	.model-toggle {
		display: flex;
		border: 1px solid var(--border);
		border-radius: 2px;
		overflow: hidden;
	}

	.toggle-btn {
		flex: 1;
		padding: 0.5rem;
		background: var(--surface);
		border: none;
		cursor: pointer;
		font-family: var(--font-mono);
		font-size: 0.875rem;
		color: var(--text-muted);
		transition: background-color 0.15s, color 0.15s;
	}

	.toggle-btn.active {
		background-color: var(--accent);
		color: white;
	}

	.run-btn {
		background-color: var(--ink, #1A2332);
		color: var(--paper, #F8F5F0);
		border: none;
		padding: 0.75rem;
		font-size: 0.875rem;
		font-weight: 500;
		cursor: pointer;
		border-radius: 2px;
		transition: opacity 0.15s;
		margin-top: 0.5rem;
	}

	:global(.dark) .run-btn {
		background-color: var(--color-dark-text);
		color: var(--color-dark-bg);
	}

	.run-btn:hover:not(:disabled) {
		opacity: 0.85;
	}

	.run-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	/* Chart panel */
	.chart-panel {
		min-height: 500px;
	}

	.chart-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 1rem;
	}

	.chart-title {
		font-family: var(--font-display);
		font-size: 1.125rem;
	}

	.cache-badge {
		font-size: 0.6875rem;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--color-up);
		border: 1px solid var(--color-up);
		padding: 2px 8px;
		border-radius: 2px;
	}

	.stats-strip {
		display: grid;
		grid-template-columns: repeat(6, 1fr);
		gap: 0;
		border: 1px solid var(--border);
		margin-top: 1.5rem;
	}

	.stat {
		padding: 0.875rem 1rem;
		border-right: 1px solid var(--border);
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.stat:last-child {
		border-right: none;
	}

	.stat-label {
		font-size: 0.625rem;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--text-faint);
		font-family: var(--font-mono);
	}

	.stat-val {
		font-size: 1.125rem;
		color: var(--text-primary);
	}

	.stat-val.up { color: var(--color-up); }
	.stat-val.down { color: var(--color-down); }

	.mt-6 { margin-top: 1.5rem; }

	.dist-section {
		margin-top: 1.5rem;
	}

	.dist-title {
		font-family: var(--font-display);
		font-size: 1rem;
		margin-bottom: 0.25rem;
	}

	.dist-sub {
		font-size: 0.8125rem;
		color: var(--text-muted);
		margin-bottom: 1rem;
	}

	/* States */
	.loading-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 420px;
		gap: 1rem;
	}

	.loading-bar {
		width: 200px;
		height: 2px;
		background-color: var(--border);
		position: relative;
		overflow: hidden;
	}

	.loading-bar::after {
		content: '';
		position: absolute;
		top: 0;
		left: -100%;
		width: 100%;
		height: 100%;
		background-color: var(--accent);
		animation: slide 1.2s ease-in-out infinite;
	}

	@keyframes slide {
		to { left: 100%; }
	}

	.loading-text {
		font-size: 0.8125rem;
		color: var(--text-muted);
	}

	.error-msg {
		color: var(--color-down);
		font-size: 0.875rem;
		padding: 2rem;
		border: 1px solid var(--color-down);
		border-radius: 2px;
	}

	.empty-state {
		color: var(--text-faint);
		font-size: 0.875rem;
		padding: 4rem 0;
		text-align: center;
	}

	@media (max-width: 900px) {
		.simulator-layout {
			grid-template-columns: 1fr;
		}

		.stats-strip {
			grid-template-columns: repeat(3, 1fr);
		}

		.stat {
			border-bottom: 1px solid var(--border);
		}
	}
</style>
