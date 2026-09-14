<template>
  <div ref="chartRef" class="chart-container" :style="{ height: height, width: width }"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts'

const props = withDefaults(defineProps<{
  xAxisData: string[]
  seriesData: number[]
  title?: string
  height?: string
  width?: string
}>(), {
  title: '',
  height: '240px',
  width: '100%'
})

const chartRef = ref<HTMLDivElement | null>(null)
let myChart: echarts.ECharts | null = null

const initChart = () => {
  if (!chartRef.value) return
  if (myChart) myChart.dispose()
  myChart = echarts.init(chartRef.value)

  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#FFFFFF',
      borderColor: '#E2E8F0',
      textStyle: { color: '#0F2347' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '5%',
      top: '12%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: props.xAxisData,
      axisLine: { lineStyle: { color: '#CBD5E1' } },
      axisLabel: { color: '#64748B', fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      min: 50,
      max: 100,
      splitLine: { lineStyle: { color: '#F1F5F9', type: 'dashed' } },
      axisLabel: { color: '#64748B', fontSize: 11 }
    },
    series: [
      {
        name: '面试得分',
        type: 'line',
        smooth: true,
        data: props.seriesData,
        itemStyle: { color: '#2563EB' },
        lineStyle: { width: 3 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(37, 99, 235, 0.3)' },
            { offset: 1, color: 'rgba(37, 99, 235, 0.0)' }
          ])
        }
      }
    ]
  }

  myChart.setOption(option)
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', () => myChart?.resize())
})

onBeforeUnmount(() => {
  myChart?.dispose()
})

watch(() => [props.xAxisData, props.seriesData], () => {
  initChart()
}, { deep: true })
</script>

<style scoped>
.chart-container {
  width: 100%;
}
</style>
