<script lang="ts">
	import type { SimulationResponse } from '$lib/api/types';

	interface Props { result: SimulationResponse; }
	let { result }: Props = $props();

	const p = $derived(result.calibrated_params);
</script>

<div class="params">
	<div class="params-title mono">Calibrated params</div>

	<div class="param-rows">
		<div class="param-row">
			<span class="param-sym mono">κ</span>
			<div class="param-right">
				<span class="param-val mono">{p.kappa.toFixed(4)}</span>
				<span class="param-name">mean reversion speed</span>
			</div>
		</div>
		<div class="param-row">
			<span class="param-sym mono">θ</span>
			<div class="param-right">
				<span class="param-val mono">{p.theta.toFixed(2)}%</span>
				<span class="param-name">long-run mean</span>
			</div>
		</div>
		<div class="param-row">
			<span class="param-sym mono">σ</span>
			<div class="param-right">
				<span class="param-val mono">{p.sigma.toFixed(4)}</span>
				<span class="param-name">volatility</span>
			</div>
		</div>
	</div>

	<div class="meta">
		{#if result.feller_condition_met !== undefined}
			<div class="meta-row">
				<span>Feller condition</span>
				<span class="mono" class:up={result.feller_condition_met} class:down={!result.feller_condition_met}>
					{result.feller_condition_met ? 'met' : 'violated'}
				</span>
			</div>
		{/if}
		{#if result.negative_rate_probability !== undefined}
			<div class="meta-row">
				<span>P(r &lt; 0)</span>
				<span class="mono">{(result.negative_rate_probability * 100).toFixed(2)}%</span>
			</div>
		{/if}
		{#if result.used_fallback_params}
			<div class="meta-row warn">
				<span>Using default params</span>
				<span>calibration failed</span>
			</div>
		{/if}
	</div>
</div>

<style>
	.params {
		border: 1px solid var(--rule);
		border-radius: var(--radius-sm);
		overflow: hidden;
	}

	.params-title {
		font-size: 0.625rem;
		text-transform: uppercase;
		letter-spacing: 0.12em;
		color: var(--ink-faint);
		padding: 0.625rem 0.875rem;
		background: var(--tag-bg);
		border-bottom: 1px solid var(--rule);
	}

	.param-rows { padding: 0.5rem 0; }

	.param-row {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.5rem 0.875rem;
	}

	.param-sym {
		font-size: 1rem;
		color: var(--accent);
		width: 1.25rem;
		text-align: center;
		flex-shrink: 0;
	}

	.param-right {
		display: flex;
		flex-direction: column;
		gap: 1px;
	}

	.param-val {
		font-size: 0.875rem;
		color: var(--ink);
	}

	.param-name {
		font-size: 0.625rem;
		color: var(--ink-faint);
	}

	.meta {
		border-top: 1px solid var(--rule);
		padding: 0.5rem 0;
	}

	.meta-row {
		display: flex;
		justify-content: space-between;
		padding: 0.375rem 0.875rem;
		font-size: 0.75rem;
		color: var(--ink-soft);
	}

	.meta-row.warn { color: var(--down); }

	.up { color: var(--up); }
	.down { color: var(--down); }
</style>
