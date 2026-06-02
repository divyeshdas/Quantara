export interface PathsSummary {
	p5: number[];
	p25: number[];
	p50: number[];
	p75: number[];
	p95: number[];
	mean: number[];
}

export interface TerminalDistribution {
	mean: number;
	std: number;
	p5: number;
	p25: number;
	p50: number;
	p75: number;
	p95: number;
}

export interface CalibratedParams {
	kappa: number;
	theta: number;
	sigma: number;
}

export interface SimulationResponse {
	model: string;
	paths_summary: PathsSummary;
	terminal_distribution: TerminalDistribution;
	calibrated_params: CalibratedParams;
	time_axis: number[];
	feller_condition_met?: boolean;
	feller_margin?: number;
	negative_rate_probability?: number;
	prob_increase: number;
	prob_decrease: number;
	computation_time_ms: number;
	cache_hit: boolean;
	calibration_converged: boolean;
	used_fallback_params: boolean;
}

export interface CompareResponse {
	vasicek: SimulationResponse;
	cir: SimulationResponse;
	vasicek_rmse: number;
	cir_rmse: number;
	recommended_model: string;
}

export interface SimulationRequest {
	current_rate: number;
	horizon_months: number;
	n_paths: number;
	model_params?: { kappa?: number; theta?: number; sigma?: number };
	use_calibrated: boolean;
}

export interface EMIRequest {
	loan_amount: number;
	current_rate: number;
	tenure_months: number;
	loan_type: 'home' | 'personal' | 'business';
	bank_spread: number;
	horizon_months: number;
	n_paths: number;
}

export interface EMIScenario {
	rate: number;
	emi: number;
	total_payment: number;
	total_interest: number;
	label: string;
}

export interface EMIResponse {
	scenarios: EMIScenario[];
	emi_distribution: {
		p5: number; p25: number; p50: number; p75: number; p95: number;
		mean: number; std: number;
	};
	current_emi: number;
	max_additional_monthly: number;
	max_additional_tenure: number;
}

export interface BondRequest {
	face_value: number;
	coupon_rate: number;
	maturity_years: number;
	current_rate: number;
	model: 'vasicek' | 'cir';
	horizon_months: number;
	n_paths: number;
	frequency: number;
}

export interface BondResponse {
	current_price: number;
	price_distribution: {
		p5: number; p25: number; p50: number; p75: number; p95: number;
		mean: number; std: number;
	};
	modified_duration: number;
	convexity: number;
	terminal_rates_sample: number[];
	price_sample: number[];
	ytm_at_median_rate: number;
}

export interface RatePoint {
	date: string;
	rate: number;
}

export interface HistoricalRatesResponse {
	data: RatePoint[];
	current_rate: number;
	data_source: string;
}
