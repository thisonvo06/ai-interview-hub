<template>
  <div class="enterprise-analytics-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">招聘数据中心</h2>
        <p class="page-subtitle">深入透视全流程招聘效率、漏斗转化、各渠道人岗匹配度与阶段流转耗时</p>
      </div>
      <div class="header-actions">
        <el-radio-group v-model="period" size="default" @change="fetchAnalytics">
          <el-radio-button label="7d">最近7天</el-radio-button>
          <el-radio-button label="30d">最近30天</el-radio-button>
          <el-radio-button label="90d">最近季度</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <StateContainer :loading="loading" :error="error" @retry="fetchAnalytics">
      <!-- 统计指标卡片 -->
      <el-row :gutter="20" class="stat-row">
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-icon bg-blue-light text-blue">
              <el-icon :size="24"><DocumentCopy /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">简历总投递量</div>
              <div class="stat-val">{{ stats.total_apps || 48 }}</div>
              <div class="stat-trend text-emerald">↑ 环比上周增长 14%</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-icon bg-indigo-light text-indigo">
              <el-icon :size="24"><Aim /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">AI初筛通过率</div>
              <div class="stat-val">{{ stats.screening_rate || '68.5%' }}</div>
              <div class="stat-trend text-blue">平均匹配度 78 分</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-icon bg-amber-light text-amber">
              <el-icon :size="24"><Timer /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">平均招聘周期</div>
              <div class="stat-val">{{ stats.avg_days || 12 }} 天</div>
              <div class="stat-trend text-emerald">↓ 较传统招聘缩短 40%</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-icon bg-emerald-light text-emerald">
              <el-icon :size="24"><Trophy /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">Offer 接受率</div>
              <div class="stat-val">{{ stats.offer_accept_rate || '83.3%' }}</div>
              <div class="stat-trend text-emerald">已有 5 人确认入职</div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 图表区域 -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :xs="24" :lg="16">
          <div class="chart-card">
            <h3 class="card-title">投递趋势与初筛转化趋势</h3>
            <div ref="trendChartRef" style="height: 320px; width: 100%;"></div>
          </div>
        </el-col>
        <el-col :xs="24" :lg="8">
          <div class="chart-card">
            <h3 class="card-title">招聘全流程转化漏斗</h3>
            <div ref="funnelChartRef" style="height: 320px; width: 100%;"></div>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :xs="24" :lg="12">
          <div class="chart-card">
            <h3 class="card-title">各在招岗位简历投递量排行</h3>
            <div ref="jobsBarChartRef" style="height: 300px; width: 100%;"></div>
          </div>
        </el-col>
        <el-col :xs="24" :lg="12">
          <div class="chart-card">
            <h3 class="card-title">候选人学历与经验分布</h3>
            <div ref="pieChartRef" style="height: 300px; width: 100%;"></div>
          </div>
        </el-col>
      </el-row>
    </StateContainer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { DocumentCopy, Aim, Timer, Trophy } from '@element-plus/icons-vue'
import StateContainer from '@/components/StateContainer.vue'
import { enterpriseApi } from '@/api'
import * as echarts from 'echarts'

const period = ref('30d')
const loading = ref(false)
const error = ref('')

const stats = reactive({
  total_apps: 52,
  screening_rate: '71.2%',
  avg_days: 11,
  offer_accept_rate: '85.7%'
})

const trendChartRef = ref<HTMLDivElement | null>(null)
const funnelChartRef = ref<HTMLDivElement | null>(null)
const jobsBarChartRef = ref<HTMLDivElement | null>(null)
const pieChartRef = ref<HTMLDivElement | null>(null)

let trendChart: echarts.ECharts | null = null
let funnelChart: echarts.ECharts | null = null
let jobsBarChart: echarts.ECharts | null = null
let pieChart: echarts.ECharts | null = null

const initCharts = () => {
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
    trendChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['收到投递', '通过初筛', '安排面试'] },
      grid: { left: '3%', right: '4%', bottom: '5%', top: '15%', containLabel: true },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: ['第1周', '第2周', '第3周', '第4周']
      },
      yAxis: { type: 'value' },
      series: [
        { name: '收到投递', type: 'line', smooth: true, data: [12, 18, 15, 22], color: '#2563EB' },
        { name: '通过初筛', type: 'line', smooth: true, data: [8, 13, 11, 16], color: '#10B981' },
        { name: '安排面试', type: 'line', smooth: true, data: [5, 8, 7, 10], color: '#F59E0B' }
      ]
    })
  }

  if (funnelChartRef.value) {
    funnelChart = echarts.init(funnelChartRef.value)
    funnelChart.setOption({
      tooltip: { trigger: 'item', formatter: '{a} <br/>{b} : {c}%' },
      series: [
        {
          name: '漏斗转化',
          type: 'funnel',
          left: '10%',
          top: 20,
          bottom: 20,
          width: '80%',
          min: 0,
          max: 100,
          minSize: '0%',
          maxSize: '100%',
          sort: 'descending',
          gap: 2,
          label: { show: true, position: 'inside', color: '#fff' },
          data: [
            { value: 100, name: '投递 (100%)', itemStyle: { color: '#2563EB' } },
            { value: 70, name: '初筛 (70%)', itemStyle: { color: '#4F46E5' } },
            { value: 40, name: '面试 (40%)', itemStyle: { color: '#F59E0B' } },
            { value: 20, name: 'Offer (20%)', itemStyle: { color: '#0891B2' } },
            { value: 15, name: '入职 (15%)', itemStyle: { color: '#10B981' } }
          ]
        }
      ]
    })
  }

  if (jobsBarChartRef.value) {
    jobsBarChart = echarts.init(jobsBarChartRef.value)
    jobsBarChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: '3%', right: '4%', bottom: '5%', top: '10%', containLabel: true },
      xAxis: { type: 'value' },
      yAxis: {
        type: 'category',
        data: ['Java架构师', '前端负责人', '算法专家', 'Go研发', 'Python工程师']
      },
      series: [
        {
          name: '投递人数',
          type: 'bar',
          data: [14, 18, 22, 26, 32],
          itemStyle: { color: '#2563EB', borderRadius: [0, 4, 4, 0] }
        }
      ]
    })
  }

  if (pieChartRef.value) {
    pieChart = echarts.init(pieChartRef.value)
    pieChart.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: '0%' },
      series: [
        {
          name: '学历构成',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
          data: [
            { value: 65, name: '硕士研究生', itemStyle: { color: '#2563EB' } },
            { value: 30, name: '统招本科', itemStyle: { color: '#10B981' } },
            { value: 5, name: '博士及以上', itemStyle: { color: '#F59E0B' } }
          ]
        }
      ]
    })
  }
}

const fetchAnalytics = async () => {
  loading.value = true
  error.value = ''
  try {
    const res: any = await enterpriseApi.getAnalytics({ period: period.value })
    if (res) {
      if (res.total_apps) stats.total_apps = res.total_apps
      if (res.screening_rate) stats.screening_rate = res.screening_rate
    }
    nextTick(() => {
      initCharts()
    })
  } catch (err: any) {
    error.value = err.response?.data?.detail || '获取数据看板失败'
  } finally {
    loading.value = false
  }
}

const handleResize = () => {
  trendChart?.resize()
  funnelChart?.resize()
  jobsBarChart?.resize()
  pieChart?.resize()
}

onMounted(() => {
  fetchAnalytics()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  funnelChart?.dispose()
  jobsBarChart?.dispose()
  pieChart?.dispose()
})
</script>

<style scoped>
.enterprise-analytics-page {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #0F2347;
  margin: 0 0 6px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748B;
  margin: 0;
}

.stat-row {
  margin-bottom: 8px;
}

.stat-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #F1F5F9;
  margin-bottom: 16px;
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bg-blue-light { background: #EFF6FF; }
.bg-indigo-light { background: #EEF2FF; }
.bg-amber-light { background: #FFFBEB; }
.bg-emerald-light { background: #ECFDF5; }

.text-blue { color: #2563EB; }
.text-indigo { color: #4F46E5; }
.text-amber { color: #F59E0B; }
.text-emerald { color: #10B981; }

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 13px;
  color: #64748B;
  margin-bottom: 4px;
}

.stat-val {
  font-size: 26px;
  font-weight: 700;
  color: #0F2347;
  line-height: 1.2;
}

.stat-trend {
  font-size: 12px;
  margin-top: 4px;
}

.chart-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #F1F5F9;
  margin-bottom: 20px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1E293B;
  margin: 0 0 16px 0;
}
</style>
