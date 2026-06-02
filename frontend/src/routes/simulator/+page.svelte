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
	let sidebarOpen = $state(true);

	async function run() {
		loading = true;
		error = null;
		try {
			const req = { current_rate: currentRate, horizon_months: horizonMonths, n_paths: nPaths, use_calibrated: true };
			result = model === 'vasicek' ? await api.simulateVasicek(req) : await api.simulateCIR(req);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Simulation failed';
		} finally {
			loading = false;
		}
	}

	onMount(run);

	const td = $derived(result?.terminal_distribution);
</script>

<svelte:head><title>Simulator — Quantara</title></svelte:head>

<div class="page">

	<!-- ── Page header ───────────────────────────────────────── -->
	<div class="page-head">
		<div>
			<div class="data-label" style="margin-bottom:0.375rem">Rate Path Simulator</div>
			<h1 style="font-size:clamp(1.5rem,3vw,2.25rem)">10,000 possible futures</h1>
		</div>
		{#if result}
			<div class="head-stat">
				<div class="data-label">Median terminal</div>
				<div class="stat-number">{result.terminal_distribution.p50.toFixed(2)}%</div>
			</div>
			<div class="head-stat">
				<div class="data-label">Range (p5 – p95)</div>
				<div class="stat-number">
					{result.terminal_distribution.p5.toFixed(2)} – {result.terminal_distribution.p95.toFixed(2)}%
				</div>
			</div>
			<div class="head-stat">
				<div class="data-label">P(rate rises)</div>
				<div class="stat-number" class:up={result.prob_increase > 0.5} class:down={result.prob_increase <= 0.5}>
					{(result.prob_increase * 100).toFixed(1)}%
				</div>
			</div>
		{/if}
	</div>

	<hr />

	<div class="layout">

		<!-- ── Sidebar ─────────────────────────────────────────── -->
		<aside class="sidebar" class:collapsed={!sidebarOpen}>
			<button class="sidebar-toggle" onclick={() => sidebarOpen = !sidebarOpen} title="Toggle panel">
				{sidebarOpen ? '‹' : '›'}
			</button>

			{#if sidebarOpen}
				<div class="controls">
					<div class="ctrl-section">
						<div class="ctrl-section-title">Parameters</div>

						<div class="ctrl-row">
							<label class="label" for="rate">Starting Rate</label>
							<div class="rate-input-wrap">
								<input id="rate" type="number" min="0" max="25" step="0.25"
									bind:value={currentRate} class="input" />
								<span class="rate-suffix mono">%</span>
							</div>
						</div>

						<div class="ctrl-row">
							<label class="label" for="horizon">
								Horizon
								<span class="mono" style="float:right;color:var(--ink)">{horizonMonths}mo</span>
							</label>
							<input id="horizon" type="range" min="1" max="24"
								bind:value={horizonMonths} class="range-input" />
							<div class="range-labels">
								<span class="faint mono">1 month</span>
								<span class="faint mono">24 months</span>
							</div>
						</div>

						<div class="ctrl-row">
							<label class="label" for="paths">Paths</label>
							<select id="paths" bind:value={nPaths} class="input">
								<option value={1000}>1,000</option>
								<option value={5000}>5,000</option>
								<option value={10000}>10,000</option>
								<option value={25000}>25,000</option>
								<option value={50000}>50,000</option>
							</select>
						</div>
					</div>

					<div class="ctrl-section">
						<div class="ctrl-section-title">Model</div>
						<div class="model-pills">
							<button class="pill" class:active={model === 'cir'} onclick={() => model = 'cir'}>
								CIR
								<span class="pill-sub">r ≥ 0</span>
							</button>
							<button class="pill" class:active={model === 'vasicek'} onclick={() => model = 'vasicek'}>
								Vasicek
								<span class="pill-sub">constant σ</span>
							</button>
						</div>
					</div>

					<button class="run-btn" onclick={run} disabled={loading}>
						{loading ? 'Simulating…' : 'Run →'}
					</button>

					{#if result}
						<ModelParams {result} />
					{/if}
				</div>
			{/if}
		</aside>

		<!-- ── Main chart area ────────────────────────────────── -->
		<main class="chart-area">
			{#if error}
				<div class="error-box">{error}</div>
			{:else if loading}
				<div class="loading-center">
					<div class="loading-line"></div>
					<p class="mono" style="font-size:0.8125rem;color:var(--ink-soft);margin-top:1rem">
						Simulating {nPaths.toLocaleString()} paths…
					</p>
				</div>
			{:else if result}
				<div class="chart-head">
					<div>
						<div class="data-label">Rate paths — {model.toUpperCase()} model</div>
						<div style="font-size:0.8125rem;color:var(--ink-soft);margin-top:0.25rem">
							Percentile bands: 5th / 25th / median / 75th / 95th
						</div>
					</div>
					<div style="display:flex;gap:0.5rem;align-items:center">
						{#if result.cache_hit}
							<span class="tag tag-up">cached</span>
						{/if}
						<span class="tag mono">{result.computation_time_ms.toFixed(0)}ms</span>
					</div>
				</div>

				<FanChart data={result.paths_summary} timeAxis={result.time_axis} height={400} />

				<!-- Stats grid -->
				{#if td}
					<div class="stats-grid">
						{#each [
							{ l: 'Mean', v: td.mean.toFixed(2)+'%' },
							{ l: 'Std dev', v: '±'+td.std.toFixed(2)+'%' },
							{ l: '5th pct', v: td.p5.toFixed(2)+'%', cls: 'down' },
							{ l: '25th pct', v: td.p25.toFixed(2)+'%' },
							{ l: 'Median', v: td.p50.toFixed(2)+'%', accent: true },
							{ l: '75th pct', v: td.p75.toFixed(2)+'%' },
							{ l: '95th pct', v: td.p95.toFixed(2)+'%', cls: 'up' },
							{ l: 'P(rises)', v: (result.prob_increase*100).toFixed(1)+'%' },
						] as s}
							<div class="stat-cell">
								<div class="data-label">{s.l}</div>
								<div class="stat-val mono" class:up={s.cls === 'up'} class:down={s.cls === 'down'} class:accent={s.accent}>{s.v}</div>
							</div>
						{/each}
					</div>
				{/if}

				<!-- Terminal distribution -->
				<div class="dist-section">
					<div class="data-label" style="margin-bottom:0.25rem">Terminal rate distribution</div>
					<div style="font-size:0.8125rem;color:var(--ink-soft);margin-bottom:1rem">
						Where rates land at month {horizonMonths} across all paths
					</div>
					{#if td}
						<TerminalDistribution data={td} height={140} />
					{/if}
				</div>
			{:else}
				<div class="loading-center">
					<p class="faint">Configure and run a simulation.</p>
				</div>
			{/if}
		</main>

	</div>
</div>

<style>
	.page { max-width: 1320px; margin: 0 auto; padding-bottom: 4rem; }

	.page-head {
		padding: 2rem 2rem 1.5rem;
		display: flex;
		align-items: flex-end;
		gap: 3rem;
		flex-wrap: wrap;
	}

	.head-stat { display: flex; flex-direction: column; gap: 0.25rem; }

	.layout {
		display: grid;
		grid-template-columns: 260px 1fr;
		min-height: 600px;
	}

	/* Sidebar */
	.sidebar {
		border-right: 1px solid var(--rule);
		position: relative;
		transition: width 0.2s;
	}

	.sidebar.collapsed { width: 28px; }

	.sidebar-toggle {
		position: absolute;
		top: 1rem;
		right: -14px;
		z-index: 10;
		width: 28px;
		height: 28px;
		background: var(--surface);
		border: 1px solid var(--rule);
		border-radius: 50%;
		cursor: pointer;
		font-size: 0.875rem;
		color: var(--ink-soft);
		display: flex;
		align-items: center;
		justify-content: center;
		transition: color 0.15s;
	}

	.sidebar-toggle:hover { color: var(--ink); }

	.controls {
		padding: 1.5rem 1.25rem;
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
		overflow: hidden;
	}

	.ctrl-section { display: flex; flex-direction: column; gap: 1rem; }

	.ctrl-section-title {
		font-size: 0.6875rem;
		text-transform: uppercase;
		letter-spacing: 0.12em;
		color: var(--ink-faint);
		font-family: var(--font-mono);
		padding-bottom: 0.5rem;
		border-bottom: 1px solid var(--rule);
	}

	.ctrl-row { display: flex; flex-direction: column; gap: 0.375rem; }

	.rate-input-wrap { position: relative; }
	.rate-suffix {
		position: absolute;
		right: 0.75rem;
		top: 50%;
		transform: translateY(-50%);
		color: var(--ink-soft);
		font-size: 0.875rem;
		pointer-events: none;
	}

	.range-input {
		width: 100%;
		accent-color: var(--accent);
		cursor: pointer;
	}

	.range-labels {
		display: flex;
		justify-content: space-between;
		font-size: 0.625rem;
		margin-top: 0.25rem;
	}

	.model-pills { display: flex; gap: 0.5rem; }

	.pill {
		flex: 1;
		padding: 0.625rem 0.5rem;
		border: 1px solid var(--rule);
		border-radius: var(--radius-sm);
		background: var(--surface);
		cursor: pointer;
		font-family: var(--font-mono);
		font-size: 0.8125rem;
		color: var(--ink-soft);
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 2px;
		transition: all 0.15s;
	}

	.pill-sub { font-size: 0.5625rem; color: var(--ink-faint); }

	.pill.active {
		border-color: var(--accent);
		background: var(--accent-tint);
		color: var(--accent);
	}

	.pill.active .pill-sub { color: var(--accent); opacity: 0.7; }

	.run-btn {
		width: 100%;
		padding: 0.75rem;
		background: var(--ink);
		color: var(--paper);
		border: none;
		border-radius: var(--radius-sm);
		font-family: var(--font-sans);
		font-size: 0.9375rem;
		font-weight: 500;
		cursor: pointer;
		transition: opacity 0.15s, transform 0.1s;
	}

	.run-btn:hover:not(:disabled) { opacity: 0.85; transform: translateY(-1px); }
	.run-btn:disabled { opacity: 0.45; cursor: not-allowed; }

	/* Chart area */
	.chart-area { padding: 1.5rem 2rem; display: flex; flex-direction: column; gap: 1.5rem; }

	.chart-head {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
	}

	.stats-grid {
		display: grid;
		grid-template-columns: repeat(8, 1fr);
		border: 1px solid var(--rule);
		border-radius: var(--radius-sm);
		overflow: hidden;
	}

	.stat-cell {
		padding: 0.875rem 1rem;
		border-right: 1px solid var(--rule);
		display: flex;
		flex-direction: column;
		gap: 0.375rem;
	}

	.stat-cell:last-child { border-right: none; }

	.stat-val {
		font-size: 1rem;
		color: var(--ink);
	}

	.stat-val.up { color: var(--up); }
	.stat-val.down { color: var(--down); }
	.stat-val.accent { color: var(--accent); font-weight: 500; }

	.dist-section { border-top: 1px solid var(--rule); padding-top: 1.5rem; }

	/* States */
	.loading-center {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 400px;
	}

	.error-box {
		color: var(--down);
		font-size: 0.875rem;
		padding: 1.5rem;
		border: 1px solid var(--down);
		border-radius: var(--radius-sm);
		background: color-mix(in srgb, var(--down) 6%, transparent);
	}

	@media (max-width: 900px) {
		.layout { grid-template-columns: 1fr; }
		.sidebar { border-right: none; border-bottom: 1px solid var(--rule); }
		.sidebar-toggle { display: none; }
		.stats-grid { grid-template-columns: repeat(4, 1fr); }
		.stat-cell:nth-child(4) { border-right: none; }
		.stat-cell:nth-child(n+5) { border-top: 1px solid var(--rule); }
	}
</style>
