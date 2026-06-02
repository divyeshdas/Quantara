<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';

	let currentRate = $state<number | null>(null);
	let rateDate = $state('');

	onMount(async () => {
		try {
			const hist = await api.historicalRates();
			currentRate = hist.current_rate;
			rateDate = hist.data[hist.data.length - 1]?.date ?? '';
		} catch {
			currentRate = 5.75;
		}
	});

	const useCases = [
		{
			id: 'home',
			tag: 'Home Loan',
			headline: 'Know your EMI in every scenario',
			body: 'Input your loan amount and tenure. See your monthly payment under the 5th, 50th, and 95th percentile rate paths — not just one forecast.',
			href: '/emi'
		},
		{
			id: 'bond',
			tag: 'Bond Investor',
			headline: 'Quantify duration risk',
			body: 'Enter any fixed-income instrument. See how its price shifts across 10,000 simulated rate endpoints. Modified duration and convexity included.',
			href: '/bond'
		},
		{
			id: 'analyst',
			tag: 'Analyst / CFO',
			headline: 'Stress-test with calibrated paths',
			body: 'Calibrated directly against RBI historical data via MLE. Export percentile scenarios for planning models and board presentations.',
			href: '/simulator'
		}
	];
</script>

<svelte:head>
	<title>Quantara — RBI Rate Path Simulator</title>
</svelte:head>

<div class="page">
	<!-- Hero -->
	<section class="hero">
		<div class="hero-inner">
			<div class="hero-left">
				<div class="eyebrow">RBI Repo Rate Simulator</div>
				<h1 class="hero-headline">
					Where will Indian<br />interest rates land?
				</h1>
				<p class="hero-sub">
					Monte Carlo simulation of 10,000 rate paths using the Vasicek and CIR stochastic
					differential equations, calibrated against RBI historical data.
				</p>
				<div class="hero-actions">
					<a href="/simulator" class="btn-primary">Run Simulation</a>
					<a href="/compare" class="btn-ghost">Compare Models</a>
				</div>
			</div>

			<div class="hero-right">
				<div class="rate-card">
					<div class="rate-label">RBI Repo Rate</div>
					<div class="rate-display">
						{currentRate !== null ? currentRate.toFixed(2) : '—'}%
					</div>
					{#if rateDate}
						<div class="rate-date">as of {rateDate}</div>
					{/if}
					<div class="rate-model-note">
						Simulating forward with CIR + Vasicek models
					</div>
				</div>
			</div>
		</div>
	</section>

	<hr class="section-rule" />

	<!-- Use cases -->
	<section class="use-cases">
		<div class="use-cases-inner">
			<div class="section-label">Three ways to use Quantara</div>
			<div class="cards-grid">
				{#each useCases as uc}
					<a href={uc.href} class="use-card">
						<div class="card-tag">{uc.tag}</div>
						<h3 class="card-headline">{uc.headline}</h3>
						<p class="card-body">{uc.body}</p>
						<span class="card-link">Open →</span>
					</a>
				{/each}
			</div>
		</div>
	</section>

	<hr class="section-rule" />

	<!-- Models section -->
	<section class="models-section">
		<div class="models-inner">
			<div class="section-label">The mathematics</div>

			<div class="models-grid">
				<div class="model-block">
					<h3 class="model-name">Vasicek (1977)</h3>
					<div class="sde mono">dr = κ(θ − r)dt + σ dW</div>
					<p class="model-desc">
						Mean-reverting Ornstein–Uhlenbeck process. Analytically tractable with closed-form
						bond pricing. Can produce negative rates — appropriate for stress tests.
					</p>
					<div class="model-props">
						<span class="prop"><span class="prop-key">κ</span> Mean reversion speed</span>
						<span class="prop"><span class="prop-key">θ</span> Long-run equilibrium</span>
						<span class="prop"><span class="prop-key">σ</span> Instantaneous volatility</span>
					</div>
				</div>

				<div class="model-divider"></div>

				<div class="model-block">
					<h3 class="model-name">Cox–Ingersoll–Ross (1985)</h3>
					<div class="sde mono">dr = κ(θ − r)dt + σ√r dW</div>
					<p class="model-desc">
						Guarantees non-negative rates when the Feller condition 2κθ &gt; σ² holds.
						Volatility scales with the rate level — empirically more accurate for emerging markets.
					</p>
					<div class="model-props">
						<span class="prop"><span class="prop-key">Feller</span> 2κθ &gt; σ² ensures r &ge; 0</span>
						<span class="prop"><span class="prop-key">Exact</span> Non-central χ² transitions</span>
						<span class="prop"><span class="prop-key">MLE</span> Calibrated on RBI DBIE data</span>
					</div>
				</div>
			</div>
		</div>
	</section>

	<hr class="section-rule" />

	<footer class="site-footer">
		<span>Quantara — Interest Rate Research Tool</span>
		<span>Calibrated on RBI repo rate data 2011–2025</span>
	</footer>
</div>

<style>
	.page {
		max-width: 1280px;
		margin: 0 auto;
	}

	/* Hero */
	.hero {
		padding: 5rem 2rem 4rem;
	}

	.hero-inner {
		display: grid;
		grid-template-columns: 1fr 340px;
		gap: 4rem;
		align-items: center;
	}

	.eyebrow {
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.12em;
		color: var(--accent);
		margin-bottom: 1.25rem;
		font-family: var(--font-mono);
	}

	.hero-headline {
		font-size: clamp(2.25rem, 4vw, 3.25rem);
		line-height: 1.1;
		margin-bottom: 1.25rem;
	}

	.hero-sub {
		font-size: 1rem;
		line-height: 1.7;
		color: var(--text-muted);
		max-width: 480px;
		margin-bottom: 2rem;
	}

	.hero-actions {
		display: flex;
		gap: 1rem;
		align-items: center;
	}

	.btn-primary {
		background-color: var(--accent);
		color: white;
		padding: 0.625rem 1.5rem;
		font-size: 0.875rem;
		font-weight: 500;
		text-decoration: none;
		border-radius: 2px;
		transition: opacity 0.15s;
	}

	.btn-primary:hover {
		opacity: 0.88;
	}

	.btn-ghost {
		color: var(--text-muted);
		font-size: 0.875rem;
		text-decoration: none;
		border-bottom: 1px solid var(--border);
		padding-bottom: 1px;
		transition: color 0.15s, border-color 0.15s;
	}

	.btn-ghost:hover {
		color: var(--text-primary);
		border-color: var(--text-primary);
	}

	/* Rate card */
	.rate-card {
		border: 1px solid var(--border);
		padding: 2rem;
		background-color: var(--surface);
	}

	.rate-label {
		font-size: 0.6875rem;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: var(--text-muted);
		margin-bottom: 0.5rem;
		font-family: var(--font-mono);
	}

	.rate-display {
		font-family: var(--font-mono);
		font-size: 3.5rem;
		color: var(--text-primary);
		line-height: 1;
		margin-bottom: 0.375rem;
	}

	.rate-date {
		font-size: 0.75rem;
		color: var(--text-faint);
		font-family: var(--font-mono);
		margin-bottom: 1rem;
	}

	.rate-model-note {
		font-size: 0.75rem;
		color: var(--text-muted);
		line-height: 1.4;
		border-top: 1px solid var(--border);
		padding-top: 0.75rem;
	}

	/* Use cases */
	.use-cases {
		padding: 4rem 2rem;
	}

	.use-cases-inner {
		max-width: 1280px;
	}

	.section-label {
		font-size: 0.6875rem;
		text-transform: uppercase;
		letter-spacing: 0.12em;
		color: var(--text-faint);
		margin-bottom: 2rem;
		font-family: var(--font-mono);
	}

	.cards-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 0;
		border: 1px solid var(--border);
	}

	.use-card {
		padding: 2rem;
		border-right: 1px solid var(--border);
		text-decoration: none;
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		transition: background-color 0.15s;
	}

	.use-card:last-child {
		border-right: none;
	}

	.use-card:hover {
		background-color: var(--accent-faint);
	}

	.card-tag {
		font-size: 0.6875rem;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: var(--accent);
		font-family: var(--font-mono);
	}

	.card-headline {
		font-family: var(--font-display);
		font-size: 1.125rem;
		color: var(--text-primary);
		line-height: 1.25;
	}

	.card-body {
		font-size: 0.875rem;
		color: var(--text-muted);
		line-height: 1.6;
		flex: 1;
	}

	.card-link {
		font-size: 0.8125rem;
		color: var(--accent);
		margin-top: 0.5rem;
	}

	/* Models */
	.models-section {
		padding: 4rem 2rem;
	}

	.models-inner {
		max-width: 1280px;
	}

	.models-grid {
		display: grid;
		grid-template-columns: 1fr 1px 1fr;
		gap: 3rem;
		margin-top: 0;
	}

	.model-divider {
		background-color: var(--border);
		width: 1px;
	}

	.model-name {
		font-family: var(--font-display);
		font-size: 1.25rem;
		margin-bottom: 0.75rem;
	}

	.sde {
		font-size: 1rem;
		color: var(--accent);
		padding: 0.75rem 1rem;
		background-color: var(--accent-faint);
		margin-bottom: 1rem;
		letter-spacing: 0.02em;
	}

	.model-desc {
		font-size: 0.875rem;
		color: var(--text-muted);
		line-height: 1.65;
		margin-bottom: 1.25rem;
	}

	.model-props {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.prop {
		font-size: 0.8125rem;
		color: var(--text-muted);
		display: flex;
		gap: 0.75rem;
	}

	.prop-key {
		font-family: var(--font-mono);
		color: var(--text-primary);
		min-width: 3rem;
	}

	/* Footer */
	.site-footer {
		padding: 1.5rem 2rem;
		display: flex;
		justify-content: space-between;
		font-size: 0.75rem;
		color: var(--text-faint);
		font-family: var(--font-mono);
	}

	/* Responsive */
	@media (max-width: 900px) {
		.hero-inner {
			grid-template-columns: 1fr;
		}

		.hero-right {
			order: -1;
		}

		.cards-grid {
			grid-template-columns: 1fr;
		}

		.use-card {
			border-right: none;
			border-bottom: 1px solid var(--border);
		}

		.use-card:last-child {
			border-bottom: none;
		}

		.models-grid {
			grid-template-columns: 1fr;
		}

		.model-divider {
			display: none;
		}
	}
</style>
