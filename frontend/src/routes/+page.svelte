<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import type { RatePoint } from '$lib/api/types';

	let currentRate = $state<number | null>(null);
	let rateDate = $state('');
	let history = $state<RatePoint[]>([]);
	let rateChange = $state<number>(0);

	onMount(async () => {
		try {
			const res = await api.historicalRates();
			currentRate = res.current_rate;
			history = res.data;
			const prev = res.data.at(-2);
			if (prev) rateChange = res.current_rate - prev.rate;
			rateDate = res.data.at(-1)?.date ?? '';
		} catch {
			currentRate = 5.75;
		}
	});

	const useCases = [
		{
			n: '01',
			tag: 'Home Loan',
			headline: 'Know your EMI across every scenario',
			body: 'See what 10,000 rate paths mean for your monthly payment — at the 5th, 50th, and 95th percentile.',
			href: '/emi',
		},
		{
			n: '02',
			tag: 'Bond Investor',
			headline: 'Quantify your duration exposure',
			body: 'Price any fixed-income instrument across all simulated rate endpoints. Modified duration and convexity computed.',
			href: '/bond',
		},
		{
			n: '03',
			tag: 'Analyst',
			headline: 'MLE-calibrated stress scenarios',
			body: 'Statistically grounded rate scenarios for planning models and reports. Export percentile bands directly.',
			href: '/simulator',
		},
	];
</script>

<svelte:head><title>Quantara — RBI Rate Path Simulator</title></svelte:head>

<div class="page">

	<!-- ── Hero ──────────────────────────────────────────────── -->
	<section class="hero">
		<div class="hero-inner">

			<div class="hero-left">
				<div class="eyebrow">
					<span class="tag tag-accent">RBI Repo Rate</span>
					{#if rateDate}<span class="faint mono" style="font-size:0.6875rem">{rateDate}</span>{/if}
				</div>

				<div class="rate-hero" class:loaded={currentRate !== null}>
					{currentRate !== null ? currentRate.toFixed(2) : '—'}<span class="rate-unit">%</span>
				</div>

				{#if currentRate !== null}
					<div class="rate-delta" class:up={rateChange >= 0} class:down={rateChange < 0}>
						<span class="mono">{rateChange >= 0 ? '+' : ''}{rateChange.toFixed(2)}%</span>
						<span style="font-size:0.75rem; margin-left:0.375rem; color:var(--ink-soft)">from previous decision</span>
					</div>
				{/if}

				<p class="hero-desc">
					Monte Carlo simulation of 10,000 RBI repo rate paths
					using the Vasicek and CIR stochastic differential equations,
					calibrated against historical data from 2011 to present.
				</p>

				<div class="hero-actions">
					<a href="/simulator" class="btn-primary">Run Simulation →</a>
					<a href="/compare" class="btn-ghost">Compare models</a>
				</div>
			</div>

			<div class="hero-right">
				<!-- Rate history timeline -->
				<div class="timeline-panel">
					<div class="data-label" style="margin-bottom:0.875rem">Rate history — 2011 to present</div>
					<div class="timeline-bars">
						{#each history.slice(-20) as point, i}
							{@const maxR = Math.max(...history.map(h => h.rate))}
							{@const pct = (point.rate / maxR) * 100}
							<div class="tbar-wrap" title="{point.date}: {point.rate}%">
								<div class="tbar" style="height:{pct}%"></div>
								<div class="tbar-val mono">{point.rate}</div>
							</div>
						{/each}
					</div>
					<div class="timeline-footer">
						<span class="faint mono">2019</span>
						<span class="faint mono">2022</span>
						<span class="faint mono">2025</span>
					</div>
				</div>
			</div>

		</div>
	</section>

	<hr />

	<!-- ── Model equations ───────────────────────────────────── -->
	<section class="equations">
		<div class="eq-inner">
			<div class="eq-block">
				<div class="data-label" style="margin-bottom:0.5rem">Vasicek (1977)</div>
				<div class="sde mono">dr = κ(θ − r)dt + σ dW</div>
				<p style="font-size:0.8125rem; margin-top:0.5rem">Constant volatility, admits negative rates</p>
			</div>
			<div class="eq-sep"></div>
			<div class="eq-block">
				<div class="data-label" style="margin-bottom:0.5rem">CIR (1985)</div>
				<div class="sde mono">dr = κ(θ − r)dt + σ√r dW</div>
				<p style="font-size:0.8125rem; margin-top:0.5rem">Volatility scales with rate, always ≥ 0</p>
			</div>
			<div class="eq-sep"></div>
			<div class="eq-block">
				<div class="data-label" style="margin-bottom:0.5rem">Calibration</div>
				<div class="sde mono">MLE on RBI DBIE 2011–2025</div>
				<p style="font-size:0.8125rem; margin-top:0.5rem">κ, θ, σ estimated via L-BFGS-B optimiser</p>
			</div>
		</div>
	</section>

	<hr />

	<!-- ── Use cases ─────────────────────────────────────────── -->
	<section class="usecases">
		<div class="uc-header">
			<h2 class="uc-title">Three ways to use it</h2>
		</div>

		<div class="uc-grid">
			{#each useCases as uc}
				<a href={uc.href} class="uc-card">
					<div class="uc-num mono">{uc.n}</div>
					<div>
						<div class="tag" style="margin-bottom:0.75rem">{uc.tag}</div>
						<h3 class="uc-headline">{uc.headline}</h3>
						<p class="uc-body">{uc.body}</p>
					</div>
					<div class="uc-arrow">→</div>
				</a>
			{/each}
		</div>
	</section>

	<hr />

	<footer class="site-footer">
		<span class="faint mono">Quantara — Research tool for Indian interest rate modelling</span>
		<a href="/simulator" class="accent mono" style="font-size:0.8125rem; text-decoration:none">Run a simulation →</a>
	</footer>

</div>

<style>
	.page { max-width: 1320px; margin: 0 auto; }

	/* Hero */
	.hero { padding: 4rem 2rem 3.5rem; }

	.hero-inner {
		display: grid;
		grid-template-columns: 1fr 380px;
		gap: 5rem;
		align-items: start;
	}

	.hero-left { display: flex; flex-direction: column; gap: 1.5rem; }

	.eyebrow { display: flex; align-items: center; gap: 1rem; }

	.rate-hero {
		font-family: var(--font-mono);
		font-size: clamp(5rem, 13vw, 9.5rem);
		font-weight: 400;
		color: var(--ink);
		line-height: 0.92;
		letter-spacing: -0.04em;
		opacity: 0;
		transform: translateY(8px);
		transition: opacity 0.5s ease, transform 0.5s ease;
	}

	.rate-hero.loaded { opacity: 1; transform: none; }

	.rate-unit {
		font-size: 0.45em;
		color: var(--accent);
		vertical-align: super;
		margin-left: 0.1em;
	}

	.rate-delta {
		display: flex;
		align-items: center;
		font-size: 0.9375rem;
		font-weight: 500;
	}

	.rate-delta.up .mono { color: var(--up); }
	.rate-delta.down .mono { color: var(--down); }

	.hero-desc {
		font-size: 0.9375rem;
		line-height: 1.75;
		color: var(--ink-soft);
		max-width: 480px;
	}

	.hero-actions {
		display: flex;
		align-items: center;
		gap: 1.5rem;
		margin-top: 0.25rem;
	}

	/* Timeline panel */
	.timeline-panel {
		background: var(--surface);
		border: 1px solid var(--rule);
		border-radius: var(--radius-md);
		padding: 1.5rem;
		height: 100%;
		min-height: 220px;
		display: flex;
		flex-direction: column;
	}

	.timeline-bars {
		display: flex;
		align-items: flex-end;
		gap: 4px;
		flex: 1;
		height: 120px;
	}

	.tbar-wrap {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: flex-end;
		height: 100%;
		gap: 3px;
		cursor: default;
	}

	.tbar {
		width: 100%;
		background: var(--accent);
		border-radius: 2px 2px 0 0;
		opacity: 0.6;
		transition: opacity 0.15s;
		min-height: 4px;
	}

	.tbar-wrap:hover .tbar { opacity: 1; }

	.tbar-val {
		font-size: 0.5rem;
		color: var(--ink-faint);
		white-space: nowrap;
		transform: rotate(-90deg);
		transform-origin: center;
		height: 20px;
		display: flex;
		align-items: center;
	}

	.timeline-footer {
		display: flex;
		justify-content: space-between;
		margin-top: 0.5rem;
		padding-top: 0.5rem;
		border-top: 1px solid var(--rule);
	}

	/* Equations */
	.equations { padding: 2.5rem 2rem; }

	.eq-inner {
		display: grid;
		grid-template-columns: 1fr 1px 1fr 1px 1fr;
		gap: 2.5rem;
		align-items: start;
	}

	.eq-sep { background: var(--rule); }

	.sde {
		font-size: 0.9375rem;
		color: var(--accent);
		letter-spacing: 0.01em;
	}

	.eq-block p { color: var(--ink-soft); }

	/* Use cases */
	.usecases { padding: 3.5rem 2rem; }

	.uc-header { margin-bottom: 2.5rem; }

	.uc-title {
		font-size: clamp(1.5rem, 3vw, 2rem);
	}

	.uc-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		border: 1px solid var(--rule);
		border-radius: var(--radius-md);
		overflow: hidden;
	}

	.uc-card {
		padding: 2rem 1.75rem;
		border-right: 1px solid var(--rule);
		text-decoration: none;
		display: flex;
		flex-direction: column;
		gap: 1rem;
		transition: background 0.2s;
		cursor: pointer;
	}

	.uc-card:last-child { border-right: none; }

	.uc-card:hover { background: var(--accent-tint); }

	.uc-num {
		font-size: 2rem;
		color: var(--rule);
		font-weight: 400;
		line-height: 1;
		transition: color 0.2s;
	}

	.uc-card:hover .uc-num { color: var(--accent); }

	.uc-headline {
		font-family: var(--font-display);
		font-size: 1.125rem;
		color: var(--ink);
		margin-bottom: 0.5rem;
		line-height: 1.3;
	}

	.uc-body {
		font-size: 0.875rem;
		color: var(--ink-soft);
		line-height: 1.65;
	}

	.uc-arrow {
		font-size: 1.25rem;
		color: var(--accent);
		margin-top: auto;
		opacity: 0;
		transform: translateX(-6px);
		transition: opacity 0.2s, transform 0.2s;
	}

	.uc-card:hover .uc-arrow { opacity: 1; transform: none; }

	/* Footer */
	.site-footer {
		padding: 1.5rem 2rem;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	/* Responsive */
	@media (max-width: 1024px) {
		.hero-inner { grid-template-columns: 1fr; }
		.hero-right { display: none; }
		.eq-inner { grid-template-columns: 1fr; }
		.eq-sep { display: none; }
	}

	@media (max-width: 768px) {
		.uc-grid { grid-template-columns: 1fr; }
		.uc-card { border-right: none; border-bottom: 1px solid var(--rule); }
		.uc-card:last-child { border-bottom: none; }
	}
</style>
