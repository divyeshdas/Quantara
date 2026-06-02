<script lang="ts">
	import { page } from '$app/stores';
	import { theme } from '$lib/stores/theme';

	const links = [
		{ href: '/simulator', label: 'Simulator' },
		{ href: '/emi', label: 'EMI' },
		{ href: '/bond', label: 'Bond' },
		{ href: '/compare', label: 'Compare' }
	];

	function active(href: string) {
		return $page.url.pathname.startsWith(href);
	}
</script>

<nav>
	<div class="nav-wrap">
		<a href="/" class="logo" aria-label="Quantara home">
			<span class="logo-mark">Q</span>
			<span class="logo-text">uantara</span>
		</a>

		<div class="links">
			{#each links as { href, label }}
				<a {href} class="link" class:active={active(href)}>{label}</a>
			{/each}
		</div>

		<div class="right">
			<a href="/simulator" class="cta">Run simulation →</a>
			<button
				class="theme-toggle"
				onclick={() => theme.toggle()}
				aria-label="Toggle theme"
				title={$theme === 'light' ? 'Switch to dark' : 'Switch to light'}
			>
				{#if $theme === 'light'}
					<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
						<path d="M12 3a9 9 0 1 0 9 9c0-.46-.04-.92-.1-1.36a5.389 5.389 0 0 1-4.4 2.26 5.403 5.403 0 0 1-3.14-9.8c-.44-.06-.9-.1-1.36-.1z"/>
					</svg>
				{:else}
					<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<circle cx="12" cy="12" r="4"/>
						<path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>
					</svg>
				{/if}
			</button>
		</div>
	</div>
</nav>

<style>
	nav {
		position: sticky;
		top: 0;
		z-index: 100;
		background: var(--paper);
		border-bottom: 1px solid var(--rule);
		backdrop-filter: blur(8px);
		background: color-mix(in srgb, var(--paper) 92%, transparent);
	}

	.nav-wrap {
		max-width: 1320px;
		margin: 0 auto;
		padding: 0 2rem;
		height: 52px;
		display: flex;
		align-items: center;
		gap: 2.5rem;
	}

	.logo {
		text-decoration: none;
		display: flex;
		align-items: baseline;
		gap: 0;
		flex-shrink: 0;
	}

	.logo-mark {
		font-family: var(--font-display);
		font-size: 1.375rem;
		color: var(--accent);
		font-style: italic;
		line-height: 1;
	}

	.logo-text {
		font-family: var(--font-display);
		font-size: 1.375rem;
		color: var(--ink);
		line-height: 1;
	}

	.links {
		display: flex;
		gap: 0.25rem;
		flex: 1;
	}

	.link {
		font-family: var(--font-sans);
		font-size: 0.8125rem;
		font-weight: 400;
		color: var(--ink-soft);
		text-decoration: none;
		padding: 0.375rem 0.75rem;
		border-radius: var(--radius-sm);
		transition: color 0.15s, background 0.15s;
		letter-spacing: 0.01em;
	}

	.link:hover { color: var(--ink); background: var(--tag-bg); }

	.link.active {
		color: var(--ink);
		font-weight: 500;
	}

	.right {
		display: flex;
		align-items: center;
		gap: 1rem;
		margin-left: auto;
	}

	.cta {
		font-family: var(--font-sans);
		font-size: 0.8125rem;
		font-weight: 500;
		color: var(--accent);
		text-decoration: none;
		transition: color 0.15s;
		white-space: nowrap;
	}

	.cta:hover { color: var(--accent-hover); }

	.theme-toggle {
		background: none;
		border: 1px solid var(--rule);
		border-radius: var(--radius-sm);
		width: 30px;
		height: 30px;
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		color: var(--ink-soft);
		transition: color 0.15s, border-color 0.15s;
	}

	.theme-toggle:hover { color: var(--ink); border-color: var(--ink-soft); }

	@media (max-width: 768px) {
		.links { display: none; }
		.cta { display: none; }
		.nav-wrap { gap: 1rem; }
	}
</style>
