<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import type { TerminalDistribution as TDist } from '$lib/api/types';

	interface Props {
		data: TDist;
		height?: number;
	}

	let { data, height = 180 }: Props = $props();

	let container: HTMLDivElement;
	let chart: ReturnType<typeof import('echarts')['init']> | null = null;

	async function initChart() {
		const echarts = await import('echarts');
		if (!container) return;
		chart = echarts.init(container, undefined, { renderer: 'svg' });
		drawHistogram(echarts);
	}

	function drawHistogram(_echarts: typeof import('echarts')) {
		if (!chart) return;

		const accent = getComputedStyle(document.documentElement)
			.getPropertyValue('--color-accent').trim() || '#C17D3C';
		const textColor = getComputedStyle(document.documentElement)
			.getPropertyValue('--text-muted').trim() || '#4A5568';

		// Build a Gaussian approximation over the range [p5 - 0.5, p95 + 0.5]
		const mu = data.mean;
		const sigma = data.std;
		const lo = data.p5 - 0.3;
		const hi = data.p95 + 0.3;
		const N = 60;
		const step = (hi - lo) / N;

		const xs: number[] = [];
		const ys: number[] = [];
		for (let i = 0; i <= N; i++) {
			const x = lo + i * step;
			const y = (1 / (sigma * Math.sqrt(2 * Math.PI))) * Math.exp(-0.5 * ((x - mu) / sigma) ** 2);
			xs.push(x);
			ys.push(y);
		}

		const option = {
			animation: false,
			grid: { top: 8, right: 10, bottom: 32, left: 10, containLabel: true },
			xAxis: {
				type: 'category' as const,
				data: xs.map((v) => v.toFixed(2)),
				boundaryGap: false,
				axisLine: { lineStyle: { color: 'var(--border)' } },
				axisTick: { show: false },
				axisLabel: {
					fontFamily: 'JetBrains Mono, monospace',
					fontSize: 10,
					color: textColor,
					interval: Math.floor(N / 4)
				}
			},
			yAxis: { show: false },
			tooltip: { show: false },
			series: [
				{
					type: 'line',
					data: ys,
					smooth: true,
					symbol: 'none',
					lineStyle: { color: accent, width: 2 },
					areaStyle: { color: accent, opacity: 0.15 },
					markLine: {
						silent: true,
						symbol: 'none',
						data: [
							{
								xAxis: xs.findIndex((x) => x >= data.p50).toString(),
								lineStyle: { color: accent, width: 1.5 }
							}
						],
						label: {
							formatter: `${data.p50.toFixed(2)}%`,
							fontFamily: 'JetBrains Mono, monospace',
							fontSize: 10,
							color: accent
						}
					}
				}
			]
		};

		chart.setOption(option);
	}

	onMount(async () => {
		await initChart();
	});

	onDestroy(() => {
		chart?.dispose();
	});
</script>

<div bind:this={container} style:height="{height}px" class="chart-container w-full"></div>
