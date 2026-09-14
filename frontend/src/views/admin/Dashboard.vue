<template>
  <div class="admin-dashboard-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">平台总览看板</h2>
        <p class="page-subtitle">监控全平台求职者、认证企业、在招职位与 AI 面试实时运行态势</p>
      </div>
      <div class="header-status">
        <span class="status-dot"></span>
        <span style="font-size: 13px; color: #16A34A; font-weight: 500;">系统与 AI 引擎运行正常</span>
      </div>
    </div>

    <StateContainer :loading="loading" :error="error" @retry="fetchDashboard">
      <!-- 核心大盘指标 -->
      <el-row :gutter="20" class="stat-row">
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-icon bg-blue-light text-blue">
              <el-icon :size="24"><UserFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">个人求职者用户</div>
              <div class="stat-val">{{ data.metrics?.personal_users || 0 }}</div>
              <div class="stat-trend text-blue">实名活跃用户</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-icon bg-emerald-light text-emerald">
              <el-icon :size="24"><OfficeBuilding /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">认证企业总数</div>
              <div class="stat-val">{{ data.metrics?.verified_companies || 0 }}</div>
              <div class="stat-trend text-emerald">已核验统一信用代码</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-icon bg-amber-light text-amber">
              <el-icon :size="24"><Briefcase /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">全平台在招岗位</div>
              <div class="stat-val">{{ data.metrics?.active_jobs || 0 }}</div>
              <div class="stat-trend text-amber">广场开放投递</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card">
            <div class="stat-icon bg-purple-light text-purple">
              <el-icon :size="24"><ChatDotSquare /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">今日 AI 面试场次</div>
              <div class="stat-val">{{ data.metrics?.today_interviews || 0 }}</div>
              <div class="stat-trend text-purple">结构化实时评测</div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 待处理审核看板 -->
      <div class="todo-card" style="margin-top: 20px;">
        <h3 class="card-title">待办审核与治理任务</h3>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="8">
            <div class="todo-item" @click="$router.push('/admin/verifications')">
              <div class="todo-count text-amber">{{ data.pending_todos?.verifications || 0 }}</div>
              <div class="todo-text">
                <div class="todo-title">待审核企业资质</div>
                <div class="todo-desc">企业实名认证及营业执照合规核查</div>
              </div>
              <el-icon><ArrowRight /></el-icon>
            </div>
          </el-col>
          <el-col :xs="24" :sm="8">
            <div class="todo-item" @click="$router.push('/admin/jobs-review')">
              <div class="todo-count text-blue">{{ data.pending_todos?.jobs_review || 0 }}</div>
              <div class="todo-text">
                <div class="todo-title">待审核发布职位</div>
                <div class="todo-desc">企业新提交岗位的合法性与薪资核验</div>
              </div>
              <el-icon><ArrowRight /></el-icon>
            </div>
          </el-col>
          <el-col :xs="24" :sm="8">
            <div class="todo-item" @click="$router.push('/admin/complaints')">
              <div class="todo-count text-red">{{ data.pending_todos?.complaints || 0 }}</div>
              <div class="todo-text">
                <div class="todo-title">待处置举报投诉</div>
                <div class="todo-desc">虚假招聘、薪资不符或违规言论申诉</div>
              </div>
              <el-icon><ArrowRight /></el-icon>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 业务趋势折线图 -->
      <div class="chart-card" style="margin-top: 20px;">
        <div class="card-header">
          <h3 class="card-title">全平台周度业务增长趋势（面试与投递）</h3>
        </div>
        <div ref="chartRef" style="height: 320px; width: 100%;"></div>
      </div>
    </StateContainer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { UserFilled, OfficeBuilding, Briefcase, ChatDotSquare, ArrowRight } from '@element-plus/icons-vue'
import StateContainer from '@/components/StateContainer.vue'
import { adminApi } from '@/api'
import * as echarts from 'echarts'

const loading = ref(false)
const error = ref('')
const data = ref<any>({
  metrics: {},
  pending_todos: {},
  trends: []
})

const chartRef = ref<HTMLDivElement | null>(null)
let myChart: echarts.ECharts | null = null

const initChart = () => {
  if (!chartRef.value) return
  if (myChart) myChart.dispose()
  myChart = echarts.init(chartRef.value)

  const trends = data.value.trends || []
  const dates = trends.map((t: any) => t.date)
  const interviews = trends.map((t: any) => t.interviews)
  const apps = trends.map((t: any) => t.applications)

  myChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['AI 面试场次', '投递申请量'] },
    grid: { left: '3%', right: '4%', bottom: '5%', top: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates
    },
    yAxis: { type: 'value' },
    series: [
      {
        name: 'AI 面试场次',
        type: 'line',
        smooth: true,
        data: interviews,
        color: '#2563EB',
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(37, 99, 235, 0.25)' },
            { offset: 1, color: 'rgba(37, 99, 235, 0.01)' }
          ])
        }
      },
      {
        name: '投递申请量',
        type: 'line',
        smooth: true,
        data: apps,
        color: '#10B981',
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(16, 185, 129, 0.25)' },
            { offset: 1, color: 'rgba(16, 185, 129, 0.01)' }
          ])
        }
      }
    ]
  })
}

const fetchDashboard = async () => {
  loading.value = true
  error.value = ''
  try {
    const res: any = await adminApi.getDashboard()
    data.value = res || {}
    nextTick(() => {
      initChart()
    })
  } catch (err: any) {
    error.value = err.response?.data?.detail || '获取管理后台总览数据失败'
  } finally {
    loading.value = false
  }
}

const handleResize = () => {
  myChart?.resize()
}

onMounted(() => {
  fetchDashboard()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  myChart?.dispose()
})
</script>

<style scoped>
.admin-dashboard-page {
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

.header-status {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #DCFCE7;
  padding: 6px 14px;
  border-radius: 20px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #16A34A;
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
.bg-emerald-light { background: #ECFDF5; }
.bg-amber-light { background: #FFFBEB; }
.bg-purple-light { background: #FAF5FF; }

.text-blue { color: #2563EB; }
.text-emerald { color: #10B981; }
.text-amber { color: #F59E0B; }
.text-purple { color: #8B5CF6; }
.text-red { color: #EF4444; }

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

.todo-card, .chart-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #F1F5F9;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1E293B;
  margin: 0 0 16px 0;
}

.todo-item {
  display: flex;
  align-items: center;
  padding: 16px;
  background: #F8FAFC;
  border-radius: 8px;
  border: 1px solid #E2E8F0;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 12px;
}

.todo-item:hover {
  background: #EFF6FF;
  border-color: #BFDBFE;
}

.todo-count {
  font-size: 32px;
  font-weight: 800;
  min-width: 50px;
  text-align: center;
}

.todo-text {
  flex: 1;
  padding: 0 12px;
}

.todo-title {
  font-size: 14px;
  font-weight: 600;
  color: #1E293B;
}

.todo-desc {
  font-size: 12px;
  color: #64748B;
  margin-top: 2px;
}
</style>
