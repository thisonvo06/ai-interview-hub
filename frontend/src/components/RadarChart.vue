<template>
  <div ref="chartRef" class="chart-container" :style="{ height: height, width: width }"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts'

const props = withDefaults(defineProps<{
  indicators: { name: string; max: number }[]
  values: number[]
  compareValues?: number[]
  title?: string
  height?: string
  width?: string
}>(), {
  compareValues: () => [],
  title: '',
  height: '320px',
  width: '100%'
})

const chartRef = ref<HTMLDivElement | null>(null)
let myChart: echarts.ECharts | null = null

const initChart = () => {
  if (!chartRef.value) return
  if (myChart) {
    myChart.dispose()
  }
  myChart = echarts.init(chartRef.value)

  const seriesData: any[] = [
    {
      value: props.values,
      name: '本次得分 / 当前掌握',
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(37, 99, 235, 0.4)' },
          { offset: 1, color: 'rgba(37, 99, 235, 0.05)' }
        ])
      },
      itemStyle: {
        color: '#2563EB'
      },
      lineStyle: {
        width: 2.5
      }
    }
  ]

  if (props.compareValues && props.compareValues.length > 0) {
    seriesData.push({
      value: props.compareValues,
      name: '岗位基准要求',
      areaStyle: {
        color: 'transparent'
      },
      itemStyle: {
        color: '#F59E0B'
      },
      lineStyle: {
        width: 2,
        type: 'dashed'
      }
    })
  }

  const option = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      bottom: 0,
      textStyle: {
        color: '#64748B',
        fontSize: 12
      }
    },
    radar: {
      indicator: props.indicators,
      shape: 'polygon',
      splitNumber: 4,
      axisName: {
        color: '#334155',
        fontSize: 12,
        fontWeight: 500
      },
      splitLine: {
        lineStyle: {
          color: '#E2E8F0'
        }
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ['#FFFFFF', '#F8FAFC']
        }
      },
      axisLine: {
        lineStyle: {
          color: '#E2E8F0'
        }
      }
    },
    series: [
      {
        type: 'radar',
        data: seriesData
      }
    ]
  }

  myChart.setOption(option)
}

const handleResize = () => {
  myChart?.resize()
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  myChart?.dispose()
})

watch(() => [props.indicators, props.values, props.compareValues], () => {
  initChart()
}, { deep: true })
</script>

<style scoped>
.chart-container {
  width: 100%;
}
</style>
