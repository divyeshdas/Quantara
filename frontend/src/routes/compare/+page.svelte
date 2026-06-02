<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import FanChart from '$lib/components/FanChart.svelte';
	import type { CompareResponse } from '$lib/api/types';

	let currentRate = $state(5.75);
	let horizonMonths = $state(12);
	let nPaths = $state(10000);
	let loading = $state(false);
	let error = $state<string | null>(null);
	let result = $state<CompareResponse | null>(null);

	async function runComparison() {
		loading = true;
		error = null;
		try {
			result = await api.simulateCompare({
				current_rate: currentRate,
				horizon_months: horizonMonths,
				n_paths: nPaths,
				use_calibrated: true
			});
		} catch (e) {
			error = e instanceof Error ? e.message : 'Comparison failed';
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		runComparison();
	});
</script>

<svelte:head>
	<title>Model Comparison — Quantara</title>
</svelte:head>

<div class="page">
	<div class="page-header">
		<div class="page-eyebrow">Vasicek vs CIR</div>
		<h1>Two models,<br />one decision</h1>
		<p class="page-sub">
			Both models are calibrated on the same RBI data. The difference is in their
			mathematical structure — and what it means for your risk assessment.
		</p>
	</div>

	<hr class="section-rule" />

	<div class="controls-row">
		<div class="ctrl-inline">
			<label class="ctrl-label" for="c-rate">Repo Rate (%)</label>
			<input id="c-rate" type="number" min="0" max="25" step="0.25"
				bind:value={currentRate} class="ctrl-input mono" />
		</div>
		<div class="ctrl-inline">
			<label class="ctrl-label" for="c-horizon">Horizon (months)</label>
			<select id="c-horizon" bind:value={horizonMonths} class="ctrl-input mono">
				{#each [3, 6, 9, 12, 18, 24] as m}
					<option value={m}>{m}</option>
				{/each}
			</select>
		</div>
		<div class="ctrl-inline">
			<label class="ctrl-label" for="c-paths">Paths</label>
			<select id="c-paths" bind:value={nPaths} class="ctrl-input mono">
				<option value={5000}>5,000</option>
				<option value={10000}>10,000</option>
				<option value={25000}>25,000</option>
			</select>
		</div>
		<button class="run-btn" onclick={runComparison} disabled={loading}>
			{loading ? 'Running…' : 'Compare'}
		</button>
	</div>

	{#if error}
		<div class="error-msg">{error}</div>
	{:else if loading}
		<div class="loading-state">
			<div class="loading-bar"></div>
			<span class="mono" style="font-size:0.8125rem;color:var(--text-muted)">Simulating both models…</span>
		</div>
	{:else if result}
		<!-- Fan charts side by side -->
		<div class="compare-grid">
			<div class="model-col">
				<div class="model-header">
					<span class="model-tag">Vasicek</span>
					{#if result.recommended_model === 'vasicek'}
						<span class="recommended-badge">Lower RMSE</span>
					{/if}
				</div>
				<div class="sde-block mono">dr = κ(θ − r)dt + σ dW</div>
				<FanChart
					data={result.vasicek.paths_summary}
					timeAxis={result.vasicek.time_axis}
					model="vasicek"
					height={300}
				/>
			</div>
			<div class="divider-col"></div>
			<div class="model-col">
				<div class="model-header">
					<span class="model-tag">CIR</span>
					{#if result.recommended_model === 'cir'}
						<span class="recommended-badge">Lower RMSE</span>
					{/if}
				</div>
				<div class="sde-block mono">dr = κ(θ − r)dt + σ√r dW</div>
				<FanChart
					data={result.cir.paths_summary}
					timeAxis={result.cir.time_axis}
					model="cir"
					height={300}
				/>
			</div>
		</div>

		<hr class="section-rule" style="margin: 2.5rem 0;" />

		<!-- Parameter comparison table -->
		<div class="params-comparison">
			<h3 class="section-subtitle">Calibrated parameters</h3>
			<div class="params-table">
				<div class="params-row header-row">
					<span class="params-cell label-cell">Parameter</span>
					<span class="params-cell">Vasicek</span>
					<span class="params-cell">CIR</span>
					<span class="params-cell">Interpretation</span>
				</div>
				<div class="params-row">
					<span class="params-cell label-cell mono">κ</span>
					<span class="params-cell mono">{result.vasicek.calibrated_params.kappa.toFixed(4)}</span>
					<span class="params-cell mono">{result.cir.calibrated_params.kappa.toFixed(4)}</span>
					<span class="params-cell text-sm">Mean reversion speed</span>
				</div>
				<div class="params-row">
					<span class="params-cell label-cell mono">θ</span>
					<span class="params-cell mono">{result.vasicek.calibrated_params.theta.toFixed(2)}%</span>
					<span class="params-cell mono">{result.cir.calibrated_params.theta.toFixed(2)}%</span>
					<span class="params-cell text-sm">Long-run equilibrium rate</span>
				</div>
				<div class="params-row">
					<span class="params-cell label-cell mono">σ</span>
					<span class="params-cell mono">{result.vasicek.calibrated_params.sigma.toFixed(4)}</span>
					<span class="params-cell mono">{result.cir.calibrated_params.sigma.toFixed(4)}</span>
					<span class="params-cell text-sm">Instantaneous volatility</span>
				</div>
				<div class="params-row">
					<span class="params-cell label-cell mono">RMSE</span>
					<span class="params-cell mono" class:rmse-winner={result.recommended_model === 'vasicek'}>
						{result.vasicek_rmse.toFixed(6)}
					</span>
					<span class="params-cell mono" class:rmse-winner={result.recommended_model === 'cir'}>
						{result.cir_rmse.toFixed(6)}
					</span>
					<span class="params-cell text-sm">Lower = better historical fit</span>
				</div>
			</div>
		</div>

		<hr class="section-rule" style="margin: 2.5rem 0;" />

		<!-- Key differences -->
		<div class="diff-grid">
			<div class="diff-block">
				<div class="diff-tag vasicek">Vasicek only</div>
				<h4 class="diff-title">Negative rate probability</h4>
				<p class="diff-body">
					The Vasicek model can produce negative rates. This is actually useful
					for stress testing scenarios. Probability observed in this simulation:
					<strong class="mono">{((result.vasicek.negative_rate_probability ?? 0) * 100).toFixed(2)}%</strong>
				</p>
			</div>
			<div class="diff-block">
				<div class="diff-tag cir">CIR only</div>
				<h4 class="diff-title">Feller condition</h4>
				<p class="diff-body">
					CIR guarantees non-negative rates when 2κθ &gt; σ².
					Current status:
					<strong class="mono" class:ok={result.cir.feller_condition_met} class:warn={!result.cir.feller_condition_met}>
						{result.cir.feller_condition_met ? 'MET' : 'VIOLATED'}
					</strong>
					(margin: {result.cir.feller_margin?.toFixed(4)})
				</p>
			</div>
			<div class="diff-block">
				<div class="diff-tag neutral">Both models</div>
				<h4 class="diff-title">Volatility structure</h4>
				<p class="diff-body">
					Vasicek has constant volatility (σ). CIR scales volatility as σ√r,
					so it is larger when rates are high — more consistent with historical
					RBI behaviour during rate cycles.
				</p>
			</div>
		</div>
	{:else}
		<div class="empty-state">Running comparison…</div>
	{/if}
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

	.controls-row {
		display: flex;
		gap: 1.5rem;
		align-items: flex-end;
		margin: 2rem 0 2.5rem;
		flex-wrap: wrap;
	}

	.ctrl-inline {
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

	.ctrl-input {
		background-color: var(--surface);
		border: 1px solid var(--border);
		color: var(--text-primary);
		padding: 0.5rem 0.75rem;
		font-size: 0.875rem;
		font-family: var(--font-mono);
		border-radius: 2px;
		outline: none;
		width: 120px;
	}

	.ctrl-input:focus { border-color: var(--accent); }

	.run-btn {
		background-color: var(--color-ink, #1A2332);
		color: var(--color-paper, #F8F5F0);
		border: none;
		padding: 0.5rem 1.5rem;
		font-size: 0.875rem;
		font-weight: 500;
		cursor: pointer;
		border-radius: 2px;
		transition: opacity 0.15s;
		height: 38px;
	}

	.run-btn:hover:not(:disabled) { opacity: 0.85; }
	.run-btn:disabled { opacity: 0.5; cursor: not-allowed; }

	/* Compare grid */
	.compare-grid {
		display: grid;
		grid-template-columns: 1fr 1px 1fr;
		gap: 2.5rem;
	}

	.divider-col { background-color: var(--border); }

	.model-header {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		margin-bottom: 0.5rem;
	}

	.model-tag {
		font-family: var(--font-display);
		font-size: 1.25rem;
		color: var(--text-primary);
	}

	.recommended-badge {
		font-size: 0.625rem;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--color-up);
		border: 1px solid var(--color-up);
		padding: 2px 6px;
		border-radius: 2px;
		font-family: var(--font-mono);
	}

	.sde-block {
		font-size: 0.875rem;
		color: var(--accent);
		background-color: var(--accent-faint);
		padding: 0.5rem 0.75rem;
		margin-bottom: 1rem;
	}

	/* Params table */
	.section-subtitle {
		font-family: var(--font-display);
		font-size: 1rem;
		margin-bottom: 1rem;
	}

	.params-table { border: 1px solid var(--border); }

	.params-row {
		display: grid;
		grid-template-columns: 80px 140px 140px 1fr;
		border-bottom: 1px solid var(--border);
	}
	.params-row:last-child { border-bottom: none; }

	.header-row {
		background-color: var(--accent-faint);
		font-size: 0.6875rem;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--text-faint);
		font-family: var(--font-mono);
	}

	.params-cell {
		padding: 0.75rem 1rem;
		font-size: 0.875rem;
		border-right: 1px solid var(--border);
	}
	.params-cell:last-child { border-right: none; }
	.label-cell { color: var(--text-primary); }

	.text-sm { font-size: 0.8125rem; color: var(--text-muted); }

	.rmse-winner { color: var(--color-up); font-weight: 500; }

	/* Diff blocks */
	.diff-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 2rem;
	}

	.diff-block { }

	.diff-tag {
		font-size: 0.625rem;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		font-family: var(--font-mono);
		margin-bottom: 0.625rem;
		display: inline-block;
	}

	.diff-tag.vasicek { color: #5B7FA6; }
	.diff-tag.cir { color: var(--accent); }
	.diff-tag.neutral { color: var(--text-faint); }

	.diff-title {
		font-family: var(--font-display);
		font-size: 1rem;
		margin-bottom: 0.625rem;
	}

	.diff-body {
		font-size: 0.875rem;
		color: var(--text-muted);
		line-height: 1.65;
	}

	.ok { color: var(--color-up); }
	.warn { color: var(--color-down); }

	/* Loading */
	.loading-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 300px;
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

	@media (max-width: 900px) {
		.compare-grid { grid-template-columns: 1fr; }
		.divider-col { display: none; }
		.diff-grid { grid-template-columns: 1fr; }
		.params-row { grid-template-columns: 60px 1fr 1fr; }
		.params-cell:last-child { display: none; }
	}
</style>
