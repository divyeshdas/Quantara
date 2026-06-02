<script lang="ts">
	import type { EMIScenario } from '$lib/api/types';

	interface Props {
		scenarios: EMIScenario[];
		currentEMI: number;
	}

	let { scenarios, currentEMI }: Props = $props();

	const maxEMI = $derived(Math.max(...scenarios.map((s) => s.emi)));

	function barWidth(emi: number) {
		return ((emi / maxEMI) * 100).toFixed(1) + '%';
	}

	function formatINR(v: number) {
		return new Intl.NumberFormat('en-IN', {
			style: 'currency',
			currency: 'INR',
			maximumFractionDigits: 0
		}).format(v);
	}

	const colors = ['#2D7A4F', '#C17D3C', '#C0392B'];
</script>

<div class="emi-comp">
	{#each scenarios as scenario, i}
		<div class="scenario">
			<div class="scenario-header">
				<span class="scenario-label">{scenario.label}</span>
				<span class="scenario-rate mono">{scenario.rate.toFixed(2)}%</span>
			</div>
			<div class="bar-track">
				<div
					class="bar-fill"
					style:width={barWidth(scenario.emi)}
					style:background-color={colors[i]}
				></div>
			</div>
			<div class="scenario-nums">
				<span class="emi-val mono">{formatINR(scenario.emi)}/mo</span>
				{#if i > 0}
					<span class="emi-diff mono" style:color={colors[i]}>
						+{formatINR(scenario.emi - scenarios[0].emi)}/mo
					</span>
				{/if}
			</div>
		</div>
	{/each}

	<div class="current-line">
		<span class="meta-label">Current EMI (at today's rate)</span>
		<span class="mono">{formatINR(currentEMI)}</span>
	</div>
</div>

<style>
	.emi-comp {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.scenario-header {
		display: flex;
		justify-content: space-between;
		margin-bottom: 0.375rem;
	}

	.scenario-label {
		font-size: 0.8125rem;
		color: var(--text-muted);
		text-transform: uppercase;
		letter-spacing: 0.04em;
	}

	.scenario-rate {
		font-size: 0.8125rem;
		color: var(--text-primary);
	}

	.bar-track {
		height: 8px;
		background-color: var(--border);
		border-radius: 1px;
		overflow: hidden;
	}

	.bar-fill {
		height: 100%;
		border-radius: 1px;
		transition: width 0.6s ease;
	}

	.scenario-nums {
		display: flex;
		justify-content: space-between;
		margin-top: 0.375rem;
	}

	.emi-val {
		font-size: 1.125rem;
		color: var(--text-primary);
	}

	.emi-diff {
		font-size: 0.875rem;
	}

	.current-line {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding-top: 1rem;
		border-top: 1px solid var(--border);
		font-size: 0.8125rem;
	}

	.meta-label {
		color: var(--text-muted);
	}
</style>
