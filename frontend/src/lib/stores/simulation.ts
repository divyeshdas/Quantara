import { writable } from 'svelte/store';
import type { SimulationResponse } from '$lib/api/types';

interface SimulationState {
	loading: boolean;
	error: string | null;
	result: SimulationResponse | null;
	model: 'vasicek' | 'cir' | 'both';
	currentRate: number;
	horizonMonths: number;
	nPaths: number;
}

function createSimulation() {
	const { subscribe, set, update } = writable<SimulationState>({
		loading: false,
		error: null,
		result: null,
		model: 'cir',
		currentRate: 5.75,
		horizonMonths: 12,
		nPaths: 10000
	});

	return {
		subscribe,
		setLoading: (v: boolean) => update((s) => ({ ...s, loading: v })),
		setError: (e: string | null) => update((s) => ({ ...s, error: e })),
		setResult: (r: SimulationResponse | null) => update((s) => ({ ...s, result: r })),
		setModel: (m: 'vasicek' | 'cir' | 'both') => update((s) => ({ ...s, model: m })),
		setRate: (r: number) => update((s) => ({ ...s, currentRate: r })),
		setHorizon: (h: number) => update((s) => ({ ...s, horizonMonths: h })),
		setPaths: (n: number) => update((s) => ({ ...s, nPaths: n })),
		reset: () =>
			update((s) => ({ ...s, loading: false, error: null, result: null }))
	};
}

export const simulation = createSimulation();
