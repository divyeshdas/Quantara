<script lang="ts">
	import { api } from '$lib/api/client';
	import EMIComparison from '$lib/components/EMIComparison.svelte';
	import type { EMIResponse } from '$lib/api/types';

	let loanAmount = $state(5000000);
	let currentRate = $state(5.75);
	let tenureMonths = $state(240);
	let loanType = $state<'home' | 'personal' | 'business'>('home');
	let bankSpread = $state(2.75);
	let loading = $state(false);
	let error = $state<string | null>(null);
	let result = $state<EMIResponse | null>(null);

	async function calculate() {
		loading = true;
		error = null;
		try {
			result = await api.emiImpact({
				loan_amount: loanAmount,
				current_rate: currentRate,
				tenure_months: tenureMonths,
				loan_type: loanType,
				bank_spread: bankSpread,
				horizon_months: 12,
				n_paths: 10000
			});
		} catch (e) {
			error = e instanceof Error ? e.message : 'Calculation failed';
		} finally {
			loading = false;
		}
	}

	function formatINR(v: number) {
		return new Intl.NumberFormat('en-IN', {
			style: 'currency',
			currency: 'INR',
			maximumFractionDigits: 0
		}).format(v);
	}

	function formatINRCr(v: number) {
		if (v >= 10000000) return `₹${(v / 10000000).toFixed(2)} Cr`;
		if (v >= 100000) return `₹${(v / 100000).toFixed(2)} L`;
		return formatINR(v);
	}
</script>

<svelte:head>
	<title>EMI Impact — Quantara</title>
</svelte:head>

<div class="page">
	<div class="page-header">
		<div class="page-eyebrow">EMI Impact Calculator</div>
		<h1>What rate scenario<br />fits your budget?</h1>
		<p class="page-sub">
			See your monthly EMI under best, median, and worst simulated rate scenarios —
			12 months ahead, calibrated on RBI data.
		</p>
	</div>

	<hr class="section-rule" />

	<div class="emi-layout">
		<aside class="inputs-panel">
			<div class="control-group">
				<label class="ctrl-label" for="loan-amt">Loan Amount</label>
				<input
					id="loan-amt"
					type="number"
					min="100000"
					step="100000"
					bind:value={loanAmount}
					class="ctrl-input mono"
				/>
				<span class="ctrl-hint">{formatINRCr(loanAmount)}</span>
			</div>

			<div class="control-group">
				<label class="ctrl-label" for="loan-type">Loan Type</label>
				<select id="loan-type" bind:value={loanType} class="ctrl-select">
					<option value="home">Home Loan</option>
					<option value="personal">Personal Loan</option>
					<option value="business">Business Loan</option>
				</select>
			</div>

			<div class="control-group">
				<label class="ctrl-label" for="repo-rate">Current Repo Rate (%)</label>
				<input
					id="repo-rate"
					type="number"
					min="0" max="25" step="0.25"
					bind:value={currentRate}
					class="ctrl-input mono"
				/>
			</div>

			<div class="control-group">
				<label class="ctrl-label" for="spread">Bank Spread (%)</label>
				<input
					id="spread"
					type="number"
					min="0" max="10" step="0.25"
					bind:value={bankSpread}
					class="ctrl-input mono"
				/>
				<span class="ctrl-hint">Lending rate = repo + spread = {(currentRate + bankSpread).toFixed(2)}%</span>
			</div>

			<div class="control-group">
				<label class="ctrl-label" for="tenure">Loan Tenure (months)</label>
				<input
					id="tenure"
					type="range"
					min="12" max="360" step="12"
					bind:value={tenureMonths}
					class="ctrl-range"
				/>
				<span class="ctrl-range-val mono">{tenureMonths} months ({(tenureMonths / 12).toFixed(0)} years)</span>
			</div>

			<button class="run-btn" onclick={calculate} disabled={loading}>
				{loading ? 'Calculating…' : 'Calculate EMI Scenarios'}
			</button>
		</aside>

		<div class="results-panel">
			{#if error}
				<div class="error-msg">{error}</div>
			{:else if loading}
				<div class="loading-state">
					<div class="loading-bar"></div>
					<span class="mono" style="font-size:0.8125rem;color:var(--text-muted)">Running rate simulation…</span>
				</div>
			{:else if result}
				<div class="results-header">
					<h2>EMI across rate scenarios</h2>
					<p class="results-sub">Lending rate = repo rate (simulated) + {bankSpread}% bank spread</p>
				</div>

				<div class="emi-comp-wrapper">
					<EMIComparison scenarios={result.scenarios} currentEMI={result.current_emi} />
				</div>

				<hr class="section-rule" style="margin: 2rem 0;" />

				<div class="impact-section">
					<h3 class="impact-title">Worst-case additional cost</h3>
					<div class="impact-grid">
						<div class="impact-item">
							<div class="impact-label">Extra per month</div>
							<div class="impact-val mono up">
								{result.max_additional_monthly > 0 ? '+' : ''}{formatINR(result.max_additional_monthly)}
							</div>
						</div>
						<div class="impact-item">
							<div class="impact-label">Extra over full tenure</div>
							<div class="impact-val mono up">
								{result.max_additional_tenure > 0 ? '+' : ''}{formatINR(result.max_additional_tenure)}
							</div>
						</div>
					</div>
				</div>

				<hr class="section-rule" style="margin: 2rem 0;" />

				<div class="dist-note">
					<h3 class="dist-title">Full EMI distribution</h3>
					<p class="dist-sub">Across 10,000 simulated rate paths at month 12</p>
					<div class="dist-grid">
						{#each [['5th pct', result.emi_distribution.p5], ['25th pct', result.emi_distribution.p25], ['Median', result.emi_distribution.p50], ['75th pct', result.emi_distribution.p75], ['95th pct', result.emi_distribution.p95]] as [label, val]}
							<div class="dist-item">
								<span class="dist-label">{label}</span>
								<span class="dist-val mono">{formatINR(val as number)}</span>
							</div>
						{/each}
					</div>
				</div>
			{:else}
				<div class="empty-state">Enter your loan details and calculate scenarios.</div>
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
		max-width: 540px;
		line-height: 1.6;
	}

	.emi-layout {
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

	.ctrl-hint {
		font-size: 0.75rem;
		color: var(--text-muted);
		font-family: var(--font-mono);
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

	/* Results */
	.results-panel { min-height: 400px; }

	.results-header { margin-bottom: 2rem; }

	.results-header h2 {
		font-family: var(--font-display);
		font-size: 1.5rem;
		margin-bottom: 0.375rem;
	}

	.results-sub {
		font-size: 0.8125rem;
		color: var(--text-muted);
	}

	.emi-comp-wrapper { max-width: 560px; }

	.impact-section { }

	.impact-title {
		font-family: var(--font-display);
		font-size: 1rem;
		margin-bottom: 1rem;
	}

	.impact-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
		max-width: 480px;
	}

	.impact-item {
		padding: 1.25rem;
		border: 1px solid var(--border);
	}

	.impact-label {
		font-size: 0.6875rem;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--text-faint);
		font-family: var(--font-mono);
		margin-bottom: 0.5rem;
	}

	.impact-val {
		font-size: 1.5rem;
		color: var(--text-primary);
	}

	.impact-val.up { color: var(--color-down); }

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

	.dist-grid {
		display: flex;
		gap: 0;
		border: 1px solid var(--border);
		max-width: 600px;
	}

	.dist-item {
		flex: 1;
		padding: 0.875rem 1rem;
		border-right: 1px solid var(--border);
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.dist-item:last-child { border-right: none; }

	.dist-label {
		font-size: 0.625rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: var(--text-faint);
		font-family: var(--font-mono);
	}

	.dist-val { font-size: 0.875rem; color: var(--text-primary); }

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

	.error-msg {
		color: var(--color-down);
		font-size: 0.875rem;
		padding: 2rem;
		border: 1px solid var(--color-down);
	}

	.empty-state {
		color: var(--text-faint);
		font-size: 0.875rem;
		padding: 4rem 0;
		text-align: center;
	}

	@media (max-width: 900px) {
		.emi-layout { grid-template-columns: 1fr; }
		.dist-grid { flex-wrap: wrap; }
		.impact-grid { grid-template-columns: 1fr; }
	}
</style>
