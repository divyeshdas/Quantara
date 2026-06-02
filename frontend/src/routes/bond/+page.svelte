<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { api } from '$lib/api/client';
	import type { BondResponse } from '$lib/api/types';

	let faceValue = $state(1000);
	let couponRate = $state(7.25);
	let maturityYears = $state(10);
	let currentRate = $state(5.75);
	let model = $state<'vasicek' | 'cir'>('cir');
	let loading = $state(false);
	let error = $state<string | null>(null);
	let result = $state<BondResponse | null>(null);

	let scatterContainer: HTMLDivElement;
	let scatterChart: ReturnType<typeof import('echarts')['init']> | null = null;

	async function calculate() {
		loading = true;
		error = null;
		try {
			result = await api.bondPrice({
				face_value: faceValue,
				coupon_rate: couponRate,
				maturity_years: maturityYears,
				current_rate: currentRate,
				model,
				horizon_months: 12,
				n_paths: 10000,
				frequency: 2
			});
			await renderScatter();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Calculation failed';
		} finally {
			loading = false;
		}
	}

	async function renderScatter() {
		if (!result || !scatterContainer) return;
		const echarts = await import('echarts');
		if (!scatterChart) {
			scatterChart = echarts.init(scatterContainer, undefined, { renderer: 'svg' });
		}

		const accent = getComputedStyle(document.documentElement)
			.getPropertyValue('--color-accent').trim() || '#C17D3C';
		const textColor = getComputedStyle(document.documentElement)
			.getPropertyValue('--text-muted').trim() || '#4A5568';
		const gridColor = getComputedStyle(document.documentElement)
			.getPropertyValue('--border').trim() || '#D8D2C8';

		const data = result.terminal_rates_sample.map((r, i) => [r, result.price_sample[i]]);

		scatterChart.setOption({
			animation: false,
			grid: { top: 20, right: 20, bottom: 48, left: 60 },
			xAxis: {
				type: 'value' as const,
				name: 'Terminal rate (%)',
				nameLocation: 'middle',
				nameGap: 32,
				axisLabel: { fontFamily: 'JetBrains Mono, monospace', fontSize: 10, color: textColor },
				axisLine: { lineStyle: { color: gridColor } },
				splitLine: { lineStyle: { color: gridColor, type: 'dashed' as const, opacity: 0.5 } }
			},
			yAxis: {
				type: 'value' as const,
				name: 'Bond price (₹)',
				nameLocation: 'middle',
				nameGap: 48,
				axisLabel: {
					fontFamily: 'JetBrains Mono, monospace', fontSize: 10, color: textColor,
					formatter: (v: number) => v.toFixed(0)
				},
				axisLine: { show: false },
				splitLine: { lineStyle: { color: gridColor, type: 'dashed' as const, opacity: 0.5 } }
			},
			tooltip: {
				trigger: 'item',
				formatter: (p: { value: number[] }) =>
					`Rate: ${p.value[0].toFixed(2)}%<br/>Price: ₹${p.value[1].toFixed(2)}`
			},
			series: [{
				type: 'scatter',
				data,
				symbolSize: 3,
				itemStyle: { color: accent, opacity: 0.35 }
			}]
		});
	}

	onMount(() => {
		calculate();
	});

	onDestroy(() => {
		scatterChart?.dispose();
	});

	const pd = $derived(result?.price_distribution);
</script>

<svelte:head>
	<title>Bond Pricing — Quantara</title>
</svelte:head>

<div class="page">
	<div class="page-header">
		<div class="page-eyebrow">Bond Price Sensitivity</div>
		<h1>Duration risk,<br />quantified</h1>
		<p class="page-sub">
			Price any fixed-income instrument across 10,000 simulated rate endpoints.
			See your exposure to rate movements before they happen.
		</p>
	</div>

	<hr class="section-rule" />

	<div class="bond-layout">
		<aside class="inputs-panel">
			<div class="control-group">
				<label class="ctrl-label" for="face-val">Face Value (₹)</label>
				<input id="face-val" type="number" min="100" step="100"
					bind:value={faceValue} class="ctrl-input mono" />
			</div>

			<div class="control-group">
				<label class="ctrl-label" for="coupon">Annual Coupon Rate (%)</label>
				<input id="coupon" type="number" min="0" max="30" step="0.25"
					bind:value={couponRate} class="ctrl-input mono" />
			</div>

			<div class="control-group">
				<label class="ctrl-label" for="maturity">Maturity (years)</label>
				<input id="maturity" type="number" min="0.5" max="30" step="0.5"
					bind:value={maturityYears} class="ctrl-input mono" />
			</div>

			<div class="control-group">
				<label class="ctrl-label" for="b-rate">Current Repo Rate (%)</label>
				<input id="b-rate" type="number" min="0" max="25" step="0.25"
					bind:value={currentRate} class="ctrl-input mono" />
			</div>

			<div class="control-group">
				<div class="ctrl-label">Model</div>
				<div class="model-toggle">
					<button class="toggle-btn" class:active={model === 'cir'}
						onclick={() => (model = 'cir')}>CIR</button>
					<button class="toggle-btn" class:active={model === 'vasicek'}
						onclick={() => (model = 'vasicek')}>Vasicek</button>
				</div>
			</div>

			<button class="run-btn" onclick={calculate} disabled={loading}>
				{loading ? 'Pricing…' : 'Price Bond'}
			</button>

			{#if result}
				<div class="metrics-card">
					<div class="metric">
						<span class="m-label">Modified Duration</span>
						<span class="m-val mono">{result.modified_duration.toFixed(4)}</span>
					</div>
					<div class="metric">
						<span class="m-label">Convexity</span>
						<span class="m-val mono">{result.convexity.toFixed(4)}</span>
					</div>
					<div class="metric">
						<span class="m-label">Current Price</span>
						<span class="m-val mono">₹{result.current_price.toFixed(2)}</span>
					</div>
				</div>
			{/if}
		</aside>

		<div class="results-panel">
			{#if error}
				<div class="error-msg">{error}</div>
			{:else if loading}
				<div class="loading-state">
					<div class="loading-bar"></div>
					<span class="mono" style="font-size:0.8125rem;color:var(--text-muted)">Pricing across paths…</span>
				</div>
			{:else if result && pd}
				<div class="results-header">
					<h2>Bond price distribution</h2>
					<p class="results-sub">Across 10,000 terminal rate paths at month 12</p>
				</div>

				<div class="price-strip">
					{#each [['5th pct', pd.p5, 'down'], ['25th pct', pd.p25, ''], ['Median', pd.p50, ''], ['75th pct', pd.p75, ''], ['95th pct', pd.p95, 'up']] as [label, val, cls]}
						<div class="price-item">
							<span class="price-label">{label}</span>
							<span class="price-val mono" class:up={cls === 'up'} class:down={cls === 'down'}>
								₹{(val as number).toFixed(2)}
							</span>
						</div>
					{/each}
				</div>

				<hr class="section-rule" style="margin: 2rem 0;" />

				<div class="scatter-section">
					<h3 class="scatter-title">Price vs terminal rate</h3>
					<p class="scatter-sub">Each dot is one simulated path endpoint. The inverse relationship illustrates duration risk.</p>
					<div bind:this={scatterContainer} style="height: 320px; width: 100%;" class="chart-container"></div>
				</div>
			{:else}
				<div class="empty-state">Enter bond details to see price sensitivity.</div>
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

	.page-header { padding: 3rem 0 2rem; }
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
		max-width: 540px;
		line-height: 1.6;
	}

	.bond-layout {
		display: grid;
		grid-template-columns: 280px 1fr;
		gap: 3rem;
		margin-top: 2.5rem;
	}

	.inputs-panel {
		display: flex;
		flex-direction: column;
		gap: 1.25rem;
	}

	.control-group { display: flex; flex-direction: column; gap: 0.375rem; }

	.ctrl-label {
		font-size: 0.6875rem;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--text-faint);
		font-family: var(--font-mono);
	}

	.ctrl-input {
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

	.ctrl-input:focus { border-color: var(--accent); }

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
		background-color: var(--color-ink, #1A2332);
		color: var(--color-paper, #F8F5F0);
		border: none;
		padding: 0.75rem;
		font-size: 0.875rem;
		font-weight: 500;
		cursor: pointer;
		border-radius: 2px;
		transition: opacity 0.15s;
		margin-top: 0.5rem;
	}

	.run-btn:hover:not(:disabled) { opacity: 0.85; }
	.run-btn:disabled { opacity: 0.5; cursor: not-allowed; }

	.metrics-card {
		border: 1px solid var(--border);
		padding: 1rem;
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.metric {
		display: flex;
		justify-content: space-between;
		font-size: 0.8125rem;
	}

	.m-label { color: var(--text-muted); }
	.m-val { color: var(--text-primary); }

	.results-panel { min-height: 400px; }

	.results-header { margin-bottom: 1.5rem; }
	.results-header h2 {
		font-family: var(--font-display);
		font-size: 1.5rem;
		margin-bottom: 0.375rem;
	}
	.results-sub { font-size: 0.8125rem; color: var(--text-muted); }

	.price-strip {
		display: flex;
		border: 1px solid var(--border);
	}

	.price-item {
		flex: 1;
		padding: 0.875rem 1rem;
		border-right: 1px solid var(--border);
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.price-item:last-child { border-right: none; }

	.price-label {
		font-size: 0.625rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: var(--text-faint);
		font-family: var(--font-mono);
	}

	.price-val { font-size: 1rem; color: var(--text-primary); }
	.price-val.up { color: var(--color-up); }
	.price-val.down { color: var(--color-down); }

	.scatter-title {
		font-family: var(--font-display);
		font-size: 1rem;
		margin-bottom: 0.25rem;
	}
	.scatter-sub { font-size: 0.8125rem; color: var(--text-muted); margin-bottom: 1rem; }

	.loading-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 320px;
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

	@keyframes slide { to { left: 100%; } }

	.error-msg { color: var(--color-down); font-size: 0.875rem; padding: 2rem; border: 1px solid var(--color-down); }
	.empty-state { color: var(--text-faint); font-size: 0.875rem; padding: 4rem 0; text-align: center; }

	@media (max-width: 900px) { .bond-layout { grid-template-columns: 1fr; } }
</style>
