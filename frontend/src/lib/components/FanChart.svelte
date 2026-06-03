<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import type { PathsSummary } from '$lib/api/types';

	interface Props {
		data: PathsSummary;
		timeAxis: number[];
		model?: string;
		height?: number;
	}

	let { data, timeAxis, model = 'cir', height = 400 }: Props = $props();

	let container: HTMLDivElement;
	let chart: ReturnType<typeof import('echarts')['init']> | null = null;

	async function initChart() {
		const echarts = await import('echarts');
		if (!container) return;

		chart = echarts.init(container, undefined, { renderer: 'svg' });
		renderChart(echarts);

		const ro = new ResizeObserver(() => chart?.resize());
		ro.observe(container);
	}

	function renderChart(echarts: typeof import('echarts')) {
		if (!chart) return;

		const accent = getComputedStyle(document.documentElement)
			.getPropertyValue('--color-accent').trim() || '#C17D3C';
		const textColor = getComputedStyle(document.documentElement)
			.getPropertyValue('--text-muted').trim() || '#4A5568';
		const gridColor = getComputedStyle(document.documentElement)
			.getPropertyValue('--border').trim() || '#D8D2C8';

		const x = timeAxis;

		const option = {
			animation: true,
			animationDuration: 600,
			animationEasing: 'cubicOut' as const,
			grid: { top: 20, right: 20, bottom: 48, left: 52, containLabel: false },
			tooltip: {
				trigger: 'axis',
				backgroundColor: 'var(--surface)',
				borderColor: 'var(--border)',
				borderWidth: 1,
				padding: [10, 14],
				textStyle: {
					fontFamily: 'JetBrains Mono, monospace',
					fontSize: 12,
					color: 'var(--text-primary)'
				},
				formatter(params: { name: string; seriesName: string; value: number[] }[]) {
					const month = parseFloat(params[0]?.name ?? '0').toFixed(1);
					const vals = params.filter(
						(p) => p.seriesName !== 'band_p95_base' &&
							p.seriesName !== 'band_p75_base' &&
							p.seriesName !== 'band_p50_base'
					);
					let html = `<div style="margin-bottom:6px;font-family:var(--font-sans);font-size:11px;color:var(--text-muted)">Month ${month}</div>`;
					const labels: Record<string, string> = {
						p95_fill: '95th pct',
						p75_fill: '75th pct',
						median: 'Median',
						p25_fill: '25th pct',
						p5_fill: '5th pct',
						mean: 'Mean'
					};
					for (const p of vals) {
						const v = Array.isArray(p.value) ? p.value[1] : p.value;
						if (typeof v === 'number' && labels[p.seriesName]) {
							html += `<div style="display:flex;justify-content:space-between;gap:16px"><span>${labels[p.seriesName]}</span><span style="font-weight:500">${v.toFixed(2)}%</span></div>`;
						}
					}
					return html;
				}
			},
			xAxis: {
				type: 'category' as const,
				data: x.map(String),
				boundaryGap: false,
				axisLine: { lineStyle: { color: gridColor } },
				axisTick: { show: false },
				axisLabel: {
					fontFamily: 'JetBrains Mono, monospace',
					fontSize: 11,
					color: textColor,
					formatter: (v: string) => `${parseFloat(v).toFixed(0)}m`
				},
				splitLine: { show: false }
			},
			yAxis: {
				type: 'value' as const,
				axisLine: { show: false },
				axisTick: { show: false },
				axisLabel: {
					fontFamily: 'JetBrains Mono, monospace',
					fontSize: 11,
					color: textColor,
					formatter: (v: number) => `${v.toFixed(1)}%`
				},
				splitLine: { lineStyle: { color: gridColor, type: 'dashed' as const, width: 1, opacity: 0.5 } }
			},
			series: [
				// p5–p95 band (outer)
				{
					name: 'band_p95_base',
					type: 'line',
					data: data.p5.map((v, i) => [x[i], v]),
					lineStyle: { opacity: 0 },
					areaStyle: { opacity: 0 },
					symbol: 'none',
					stack: 'outer_base'
				},
				{
					name: 'p95_fill',
					type: 'line',
					data: data.p95.map((v, i) => [x[i], v - data.p5[i]]),
					lineStyle: { opacity: 0 },
					areaStyle: {
						color: accent,
						opacity: 0.10
					},
					symbol: 'none',
					stack: 'outer_base'
				},
				// p25–p75 band (inner)
				{
					name: 'band_p75_base',
					type: 'line',
					data: data.p25.map((v, i) => [x[i], v]),
					lineStyle: { opacity: 0 },
					areaStyle: { opacity: 0 },
					symbol: 'none',
					stack: 'inner_base'
				},
				{
					name: 'p75_fill',
					type: 'line',
					data: data.p75.map((v, i) => [x[i], v - data.p25[i]]),
					lineStyle: { opacity: 0 },
					areaStyle: {
						color: accent,
						opacity: 0.22
					},
					symbol: 'none',
					stack: 'inner_base'
				},
				// Median path
				{
					name: 'median',
					type: 'line',
					data: data.p50.map((v, i) => [x[i], v]),
					lineStyle: { color: accent, width: 2 },
					symbol: 'none',
					z: 5
				},
				// Mean path (dashed)
				{
					name: 'mean',
					type: 'line',
					data: data.mean.map((v, i) => [x[i], v]),
					lineStyle: { color: textColor, width: 1, type: 'dashed' as const },
					symbol: 'none',
					z: 4
				}
			]
		};

		chart.setOption(option);
	}

	$effect(() => {
		// Re-render whenever data or timeAxis changes
		void data;
		void timeAxis;
		if (chart) {
			renderChart(null as unknown as typeof import('echarts'));
		}
	});

	onMount(async () => {
		await initChart();
	});

	onDestroy(() => {
		chart?.dispose();
	});
</script>

<div bind:this={container} style:height="{height}px" class="chart-container w-full"></div>
