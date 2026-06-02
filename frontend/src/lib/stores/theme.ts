import { writable } from 'svelte/store';
import { browser } from '$app/environment';

function createTheme() {
	const initial = browser
		? (localStorage.getItem('theme') ?? 'light')
		: 'light';

	const { subscribe, set, update } = writable<'light' | 'dark'>(initial as 'light' | 'dark');

	return {
		subscribe,
		toggle() {
			update((v) => {
				const next = v === 'light' ? 'dark' : 'light';
				if (browser) {
					localStorage.setItem('theme', next);
					document.documentElement.classList.toggle('dark', next === 'dark');
				}
				return next;
			});
		},
		init() {
			if (browser) {
				const saved = localStorage.getItem('theme') ?? 'light';
				set(saved as 'light' | 'dark');
				document.documentElement.classList.toggle('dark', saved === 'dark');
			}
		}
	};
}

export const theme = createTheme();
