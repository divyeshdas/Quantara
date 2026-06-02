<script lang="ts">
	import type { CalibratedParams, SimulationResponse } from '$lib/api/types';

	interface Props {
		result: SimulationResponse;
	}

	let { result }: Props = $props();

	const params = $derived(result.calibrated_params);

	function fmt(v: number, dp = 4) {
		return v.toFixed(dp);
	}
</script>

<div class="params-panel">
	<h3 class="panel-title">Calibrated Parameters</h3>
	<hr class="section-rule" />

	<div class="param-grid">
		<div class="param-item">
			<span class="param-label mono">κ</span>
			<span class="param-value mono">{fmt(params.kappa)}</span>
			<span class="param-desc">Mean reversion speed — how quickly rates return to long-run average</span>
		</div>
		<div class="param-item">
			<span class="param-label mono">θ</span>
			<span class="param-value mono">{fmt(params.theta, 2)}%</span>
			<span class="param-desc">Long-run mean — where rates are drawn towards over time</span>
		</div>
		<div class="param-item">
			<span class="param-label mono">σ</span>
			<span class="param-value mono">{fmt(params.sigma, 4)}</span>
			<span class="param-desc">Volatility — magnitude of random rate movements</span>
		</div>
	</div>

	<hr class="section-rule mt-4" />

	<div class="meta-grid">
		<div class="meta-row">
			<span class="meta-label">Model</span>
			<span class="meta-val mono">{result.model.toUpperCase()}</span>
		</div>
		<div class="meta-row">
			<span class="meta-label">Computed in</span>
			<span class="meta-val mono">{result.computation_time_ms.toFixed(0)} ms</span>
		</div>
		<div class="meta-row">
			<span class="meta-label">Cache</span>
			<span class="meta-val mono" class:hit={result.cache_hit}>
				{result.cache_hit ? 'HIT' : 'MISS'}
			</span>
		</div>

		{#if result.model === 'cir'}
			<div class="meta-row">
				<span class="meta-label">Feller condition</span>
				<span class="meta-val mono" class:ok={result.feller_condition_met} class:warn={!result.feller_condition_met}>
					{result.feller_condition_met ? 'MET' : 'VIOLATED'}
				</span>
			</div>
		{/if}

		{#if result.negative_rate_probability !== undefined}
			<div class="meta-row">
				<span class="meta-label">P(rate &lt; 0)</span>
				<span class="meta-val mono">{(result.negative_rate_probability * 100).toFixed(2)}%</span>
			</div>
		{/if}

		{#if result.used_fallback_params}
			<div class="meta-row warn-row">
				<span class="meta-label">Note</span>
				<span class="meta-val">Using default parameters — calibration did not converge</span>
			</div>
		{/if}
	</div>
</div>

<style>
	.params-panel {
		padding: 1.25rem 0;
	}

	.panel-title {
		font-family: var(--font-display);
		font-size: 1rem;
		margin-bottom: 0.75rem;
	}

	.param-grid {
		display: flex;
		flex-direction: column;
		gap: 0.875rem;
		margin: 0.875rem 0;
	}

	.param-item {
		display: grid;
		grid-template-columns: 1.5rem 4rem 1fr;
		align-items: start;
		gap: 0.75rem;
	}

	.param-label {
		font-size: 1.125rem;
		color: var(--accent);
		font-weight: 400;
	}

	.param-value {
		font-size: 0.875rem;
		color: var(--text-primary);
		padding-top: 2px;
	}

	.param-desc {
		font-size: 0.75rem;
		color: var(--text-muted);
		line-height: 1.4;
	}

	.meta-grid {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		margin-top: 0.75rem;
	}

	.meta-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		font-size: 0.75rem;
	}

	.meta-label {
		color: var(--text-muted);
	}

	.meta-val {
		color: var(--text-primary);
	}

	.meta-val.hit {
		color: var(--color-up);
	}

	.meta-val.ok {
		color: var(--color-up);
	}

	.meta-val.warn {
		color: var(--color-down);
	}

	.warn-row .meta-val {
		color: var(--color-down);
		font-size: 0.7rem;
		text-align: right;
		max-width: 160px;
	}

	.mt-4 {
		margin-top: 1rem;
	}
</style>
