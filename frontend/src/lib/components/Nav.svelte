<script lang="ts">
	import { page } from '$app/stores';
	import { theme } from '$lib/stores/theme';

	const links = [
		{ href: '/simulator', label: 'Simulator' },
		{ href: '/emi', label: 'EMI Impact' },
		{ href: '/bond', label: 'Bond Pricing' },
		{ href: '/compare', label: 'Model Compare' }
	];

	function isActive(href: string) {
		return $page.url.pathname.startsWith(href);
	}
</script>

<nav class="nav-bar">
	<div class="nav-inner">
		<a href="/" class="wordmark">
			<span class="wordmark-q">Q</span>uantara
		</a>

		<div class="nav-links">
			{#each links as { href, label }}
				<a {href} class="nav-link" class:active={isActive(href)}>
					{label}
				</a>
			{/each}
		</div>

		<button class="theme-btn" onclick={() => theme.toggle()} aria-label="Toggle theme">
			{#if $theme === 'light'}
				<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
				</svg>
			{:else}
				<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/>
					<line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
					<line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/>
					<line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
					<line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
				</svg>
			{/if}
		</button>
	</div>
</nav>

<style>
	.nav-bar {
		position: sticky;
		top: 0;
		z-index: 50;
		background-color: var(--bg);
		border-bottom: 1px solid var(--border);
	}

	.nav-inner {
		max-width: 1280px;
		margin: 0 auto;
		padding: 0 2rem;
		height: 56px;
		display: flex;
		align-items: center;
		gap: 3rem;
	}

	.wordmark {
		font-family: var(--font-display);
		font-size: 1.25rem;
		color: var(--text-primary);
		text-decoration: none;
		flex-shrink: 0;
	}

	.wordmark-q {
		color: var(--accent);
	}

	.nav-links {
		display: flex;
		gap: 2rem;
		flex: 1;
	}

	.nav-link {
		font-size: 0.8125rem;
		font-weight: 500;
		letter-spacing: 0.04em;
		text-transform: uppercase;
		color: var(--text-muted);
		text-decoration: none;
		transition: color 0.15s;
	}

	.nav-link:hover,
	.nav-link.active {
		color: var(--text-primary);
	}

	.nav-link.active {
		border-bottom: 2px solid var(--accent);
		padding-bottom: 2px;
	}

	.theme-btn {
		background: none;
		border: 1px solid var(--border);
		border-radius: 4px;
		padding: 6px;
		cursor: pointer;
		color: var(--text-muted);
		display: flex;
		align-items: center;
		transition: color 0.15s, border-color 0.15s;
		margin-left: auto;
	}

	.theme-btn:hover {
		color: var(--text-primary);
		border-color: var(--text-muted);
	}

	@media (max-width: 768px) {
		.nav-links {
			display: none;
		}
		.nav-inner {
			padding: 0 1rem;
		}
	}
</style>
