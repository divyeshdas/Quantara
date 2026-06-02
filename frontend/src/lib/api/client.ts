import type {
	SimulationRequest,
	SimulationResponse,
	CompareResponse,
	EMIRequest,
	EMIResponse,
	BondRequest,
	BondResponse,
	HistoricalRatesResponse
} from './types';

const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

async function post<T>(path: string, body: unknown): Promise<T> {
	const res = await fetch(`${BASE}${path}`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(body)
	});
	if (!res.ok) {
		const err = await res.json().catch(() => ({ detail: res.statusText }));
		throw new Error(err.detail ?? `Request failed: ${res.status}`);
	}
	return res.json();
}

async function get<T>(path: string): Promise<T> {
	const res = await fetch(`${BASE}${path}`);
	if (!res.ok) {
		throw new Error(`Request failed: ${res.status}`);
	}
	return res.json();
}

export const api = {
	simulateVasicek: (req: SimulationRequest) =>
		post<SimulationResponse>('/api/v1/simulate/vasicek', req),

	simulateCIR: (req: SimulationRequest) =>
		post<SimulationResponse>('/api/v1/simulate/cir', req),

	simulateCompare: (req: SimulationRequest) =>
		post<CompareResponse>('/api/v1/simulate/compare', req),

	getCalibration: (model: 'vasicek' | 'cir') =>
		get<unknown>(`/api/v1/calibrate/${model}`),

	emiImpact: (req: EMIRequest) =>
		post<EMIResponse>('/api/v1/emi/impact', req),

	bondPrice: (req: BondRequest) =>
		post<BondResponse>('/api/v1/bond/price', req),

	historicalRates: () =>
		get<HistoricalRatesResponse>('/api/v1/rates/historical'),

	health: () => get<{ status: string }>('/api/v1/health')
};
