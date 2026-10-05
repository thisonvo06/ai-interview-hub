<template>
  <div class="analytics-page">
    <div class="page-header"><div><h2>招聘数据中心</h2><p>统计平台历史申请；官网投递笔记由求职者独立维护。</p></div>
      <el-radio-group v-model="period" @change="fetchAnalytics"><el-radio-button value="7d">最近 7 天</el-radio-button><el-radio-button value="30d">最近 30 天</el-radio-button><el-radio-button value="90d">最近 90 天</el-radio-button></el-radio-group>
    </div>
    <StateContainer :loading="loading" :error="error" @retry="fetchAnalytics">
      <div class="metrics"><div v-for="metric in metrics" :key="metric.label"><span>{{ metric.label }}</span><strong>{{ metric.value }}</strong></div></div>
      <div class="chart-grid"><section v-for="chart in chartItems" :key="chart.key"><h3>{{ chart.title }}</h3><div :ref="el => setChartRef(chart.key, el)" class="chart" /></section></div>
    </StateContainer>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import StateContainer from '@/components/StateContainer.vue'
import { enterpriseApi } from '@/api'
const period = ref('30d'), loading = ref(false), error = ref(false), data = ref<any>(null)
const chartRefs: Record<string, HTMLElement> = {}, charts: echarts.ECharts[] = []
const chartItems = [{ key: 'trend', title: '历史平台申请趋势' }, { key: 'funnel', title: '阶段推进记录' }, { key: 'jobs', title: '各岗位历史申请量' }, { key: 'education', title: '候选人登记学历' }]
const setChartRef = (key: string, el: any) => { if (el instanceof HTMLElement) chartRefs[key] = el }
const rate = (value: number | null | undefined) => value == null ? '—' : `${value}%`
const metrics = computed(() => [
  { label: '历史申请数', value: data.value?.kpis?.total_applications ?? 0 },
  { label: '面试推进率', value: rate(data.value?.kpis?.interview_rate) },
  { label: '平均录用周期', value: data.value?.kpis?.avg_days_to_hire == null ? '—' : `${data.value.kpis.avg_days_to_hire} 天` },
  { label: '已录用', value: data.value?.kpis?.hired_count ?? 0 },
])
const renderCharts = () => {
  charts.splice(0).forEach(c => c.dispose())
  const options: Record<string, any> = {
    trend: { tooltip: { trigger: 'axis' }, xAxis: { type: 'category', data: data.value.trend.map((r: any) => r.date) }, yAxis: { type: 'value', minInterval: 1 }, series: [{ type: 'line', data: data.value.trend.map((r: any) => r.applications), smooth: true }] },
    funnel: { tooltip: {}, xAxis: { type: 'category', data: data.value.funnel.map((r: any) => r.stage) }, yAxis: { type: 'value', minInterval: 1 }, series: [{ type: 'bar', data: data.value.funnel.map((r: any) => r.count), barMaxWidth: 40 }] },
    jobs: { tooltip: {}, grid: { containLabel: true }, xAxis: { type: 'value', minInterval: 1 }, yAxis: { type: 'category', data: data.value.job_performance.map((r: any) => r.title) }, series: [{ type: 'bar', data: data.value.job_performance.map((r: any) => r.applications), barMaxWidth: 28 }] },
    education: { tooltip: {}, series: [{ type: 'pie', radius: ['45%', '70%'], data: data.value.education_distribution }] },
  }
  for (const item of chartItems) if (chartRefs[item.key]) { const chart = echarts.init(chartRefs[item.key]); chart.setOption({ color: ['#268879', '#538bbf', '#99c9bd'], ...options[item.key] }); charts.push(chart) }
}
const fetchAnalytics = async () => {
  loading.value = true; error.value = false
  try { data.value = await enterpriseApi.getAnalytics({ range: period.value }) } catch { error.value = true }
  finally { loading.value = false }
  await nextTick(); if (data.value && !error.value) renderCharts()
}
const resize = () => charts.forEach(c => c.resize())
onMounted(() => { fetchAnalytics(); window.addEventListener('resize', resize) })
onUnmounted(() => { charts.forEach(c => c.dispose()); window.removeEventListener('resize', resize) })
</script>
<style scoped>
.page-header { display: flex; align-items: center; justify-content: space-between; gap: 20px; margin-bottom: 24px; flex-wrap: wrap; }.page-header h2 { margin: 0 0 10px; color: #21443e; }.page-header p { font-size: 13px; color: #708179; }
.metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }.metrics > div { background: white; border: 1px solid #e2eae6; border-radius: 14px; padding: 22px; }.metrics span { display: block; font-size: 13px; color: #74857d; }.metrics strong { display: block; margin-top: 14px; font-size: 28px; color: #256255; }
.chart-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-top: 24px; }.chart-grid section { min-width: 0; background: white; border: 1px solid #e2eae6; padding: 24px; border-radius: 14px; }.chart-grid h3 { margin: 0; font-size: 16px; }.chart { height: 320px; }
@media(max-width: 760px) { .metrics { grid-template-columns: repeat(2, 1fr); }.chart-grid { grid-template-columns: 1fr; } }
</style>
