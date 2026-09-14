<template>
  <div class="enterprise-dashboard">
    <!-- Header with Breadcrumb & Quick Actions -->
    <div class="dash-header">
      <div>
        <div class="dash-badge">
          <span class="pulse-dot"></span>
          企业智能招聘与人才供应链工作台
        </div>
        <h2 class="dash-title">企业招聘协作中心</h2>
        <p class="dash-sub">全流程实时监控 · AI 智能初筛评级 · 自动化面试管线</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" size="large" @click="$router.push('/enterprise/jobs/create')">
          <el-icon style="margin-right: 6px;"><Plus /></el-icon>
          发布新职位 / AI解析JD
        </el-button>
        <el-button type="default" size="large" @click="$router.push('/enterprise/candidates')">
          <el-icon style="margin-right: 6px;"><User /></el-icon>
          候选人管道
        </el-button>
      </div>
    </div>

    <StateContainer :loading="loading" :error="error" @retry="fetchDashboard">
      <!-- 1. Top 4 Key Metric Cards (Matches 09-enterprise-dashboard.png) -->
      <el-row :gutter="20" class="stat-row">
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card zh-card border-top-blue">
            <div class="stat-icon icon-blue">
              <el-icon :size="24"><Briefcase /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">在招职位数</div>
              <div class="stat-val">{{ data.jobs_count || 0 }}</div>
              <div class="stat-trend text-blue">正在开放投递中</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card zh-card border-top-emerald">
            <div class="stat-icon icon-emerald">
              <el-icon :size="24"><DocumentCopy /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">今日新简历投递</div>
              <div class="stat-val">{{ data.new_apps || 0 }}</div>
              <div class="stat-trend text-emerald">等待初筛评估</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card zh-card border-top-amber">
            <div class="stat-icon icon-amber">
              <el-icon :size="24"><ChatDotSquare /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">待安排/复核面试</div>
              <div class="stat-val">{{ data.pending_interviews || 0 }}</div>
              <div class="stat-trend text-amber">含 AI 初筛及官方甄选</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card zh-card border-top-purple">
            <div class="stat-icon icon-purple">
              <el-icon :size="24"><UserFilled /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-label">流程中活跃候选人</div>
              <div class="stat-val">{{ data.pending_total || 0 }}</div>
              <div class="stat-trend text-purple">推进至各管道环节</div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 2. Middle Row: Left Funnel (60%) + Right Today's Urgent Todos & Tools (40%) -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <!-- Left: Funnel Transformation -->
        <el-col :xs="24" :lg="14">
          <div class="chart-card zh-card">
            <div class="card-header">
              <div>
                <div class="card-title">全流程招聘转化漏斗</div>
                <div class="card-subtitle">实时统计候选人从简历投递到录用入职的全链路流转</div>
              </div>
              <el-button type="primary" link size="small" @click="$router.push('/enterprise/pipeline')">
                进入招聘管道看板 <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
            <div class="funnel-container">
              <div class="funnel-stage">
                <div class="stage-info">
                  <span class="stage-name">1. 新简历投递 (Submitted)</span>
                  <span class="stage-stats">{{ data.funnel?.submitted || 0 }} 人 · 100%</span>
                </div>
                <div class="funnel-bar-wrapper">
                  <div class="funnel-bar bg-blue" :style="{ width: getFunnelWidth('submitted') }"></div>
                </div>
              </div>

              <div class="funnel-stage">
                <div class="stage-info">
                  <span class="stage-name">2. AI 技能初筛匹配 (Screening)</span>
                  <span class="stage-stats">{{ data.funnel?.screening || 0 }} 人 · {{ getPercent('screening') }}%</span>
                </div>
                <div class="funnel-bar-wrapper">
                  <div class="funnel-bar bg-indigo" :style="{ width: getFunnelWidth('screening') }"></div>
                </div>
              </div>

              <div class="funnel-stage">
                <div class="stage-info">
                  <span class="stage-name">3. AI / 专业技术面试 (Interview)</span>
                  <span class="stage-stats">{{ data.funnel?.interview || 0 }} 人 · {{ getPercent('interview') }}%</span>
                </div>
                <div class="funnel-bar-wrapper">
                  <div class="funnel-bar bg-amber" :style="{ width: getFunnelWidth('interview') }"></div>
                </div>
              </div>

              <div class="funnel-stage">
                <div class="stage-info">
                  <span class="stage-name">4. 发放录用意向 (Offer)</span>
                  <span class="stage-stats">{{ data.funnel?.offer || 0 }} 人 · {{ getPercent('offer') }}%</span>
                </div>
                <div class="funnel-bar-wrapper">
                  <div class="funnel-bar bg-cyan" :style="{ width: getFunnelWidth('offer') }"></div>
                </div>
              </div>

              <div class="funnel-stage">
                <div class="stage-info">
                  <span class="stage-name">5. 已正式入职 (Hired)</span>
                  <span class="stage-stats">{{ data.funnel?.hired || 0 }} 人 · {{ getPercent('hired') }}%</span>
                </div>
                <div class="funnel-bar-wrapper">
                  <div class="funnel-bar bg-emerald" :style="{ width: getFunnelWidth('hired') }"></div>
                </div>
              </div>
            </div>
          </div>
        </el-col>

        <!-- Right: Urgent Todos & Action Center -->
        <el-col :xs="24" :lg="10">
          <div class="chart-card zh-card">
            <div class="card-header">
              <div class="card-title">今日招聘待办提醒</div>
              <el-tag type="danger" size="small" effect="plain">需及时跟进</el-tag>
            </div>

            <!-- Urgent Task List -->
            <div class="todo-list">
              <div
                v-for="(todo, idx) in (data.today_todos || [])"
                :key="idx"
                class="todo-item"
                @click="$router.push(todo.link)"
              >
                <div class="todo-left">
                  <span class="todo-dot"></span>
                  <span class="todo-title">{{ todo.title }}</span>
                </div>
                <div class="todo-right">
                  <span class="todo-count">{{ todo.count }} 条</span>
                  <el-icon class="todo-arrow"><ArrowRight /></el-icon>
                </div>
              </div>
            </div>

            <!-- Quick Action 4-Grid -->
            <div class="quick-grid">
              <div class="quick-tile" @click="$router.push('/enterprise/jobs/create')">
                <div class="tile-icon-box bg-blue-subtle">
                  <el-icon class="text-blue"><EditPen /></el-icon>
                </div>
                <div class="tile-content">
                  <div class="tile-title">发布职位</div>
                  <div class="tile-desc">AI智能解析JD</div>
                </div>
              </div>

              <div class="quick-tile" @click="$router.push('/enterprise/pipeline')">
                <div class="tile-icon-box bg-emerald-subtle">
                  <el-icon class="text-emerald"><Histogram /></el-icon>
                </div>
                <div class="tile-content">
                  <div class="tile-title">看板看板</div>
                  <div class="tile-desc">拖拽流转候选人</div>
                </div>
              </div>

              <div class="quick-tile" @click="$router.push('/enterprise/interviews')">
                <div class="tile-icon-box bg-amber-subtle">
                  <el-icon class="text-amber"><VideoCamera /></el-icon>
                </div>
                <div class="tile-content">
                  <div class="tile-title">面试管理</div>
                  <div class="tile-desc">发起邀请与打分</div>
                </div>
              </div>

              <div class="quick-tile" @click="$router.push('/enterprise/talent-pool')">
                <div class="tile-icon-box bg-purple-subtle">
                  <el-icon class="text-purple"><CollectionTag /></el-icon>
                </div>
                <div class="tile-content">
                  <div class="tile-title">储备人才库</div>
                  <div class="tile-desc">高分候选人盘活</div>
                </div>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 3. Bottom Row: Recent Candidates (60%) + Active Jobs (40%) -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :xs="24" :lg="14">
          <div class="chart-card zh-card">
            <div class="card-header">
              <div>
                <div class="card-title">最新投递候选人</div>
                <div class="card-subtitle">按时间倒序排列，支持一键调取 AI 深度评估报告</div>
              </div>
              <el-button type="primary" link size="small" @click="$router.push('/enterprise/candidates')">
                查看全量名单 <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
            <el-table :data="data.recent_candidates || []" style="width: 100%;" class="custom-candidate-table">
              <el-table-column prop="name" label="候选人" width="120">
                <template #default="{ row }">
                  <span class="cand-name">{{ row.name }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="job_title" label="应聘职位" min-width="160" />
              <el-table-column prop="match_score" label="AI 胜任度" width="130">
                <template #default="{ row }">
                  <el-tag
                    :type="row.match_score >= 80 ? 'success' : (row.match_score >= 65 ? 'primary' : 'warning')"
                    size="small"
                    effect="light"
                  >
                    {{ row.match_score ? `${row.match_score}分 · ${row.match_score >= 80 ? '极高匹配' : '良好匹配'}` : '初筛中' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="当前阶段" width="110">
                <template #default="{ row }">
                  <el-tag size="small" type="info">{{ formatStatus(row.status) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="投递时间" width="110" />
              <el-table-column label="操作" width="90" align="right">
                <template #default="{ row }">
                  <el-button
                    type="primary"
                    link
                    size="small"
                    @click="$router.push(`/enterprise/candidates/${row.id}`)"
                  >
                    处理详情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-col>

        <!-- Right: Active Jobs Overview -->
        <el-col :xs="24" :lg="10">
          <div class="chart-card zh-card">
            <div class="card-header">
              <div>
                <div class="card-title">在招职位概览</div>
                <div class="card-subtitle">当前企业已发布并生效的招聘需求</div>
              </div>
              <el-button type="primary" link size="small" @click="$router.push('/enterprise/jobs')">
                职位中心 <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
            <div class="job-list-simple">
              <div v-for="job in data.jobs || []" :key="job.id" class="job-simple-item">
                <div class="job-main-info">
                  <div class="job-simple-title">{{ job.title }}</div>
                  <div class="job-simple-meta">
                    <span class="meta-city">{{ job.city }}</span>
                    <span class="meta-salary">{{ job.salary }}</span>
                  </div>
                </div>
                <div class="job-simple-side">
                  <span class="job-cand-count">{{ job.candidates_count || 0 }} 份简历</span>
                  <el-button
                    type="primary"
                    plain
                    size="small"
                    @click="$router.push(`/enterprise/candidates?job_id=${job.id}`)"
                  >
                    筛选
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </StateContainer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  Plus, User, Briefcase, DocumentCopy, ChatDotSquare, UserFilled,
  ArrowRight, EditPen, Histogram, VideoCamera, CollectionTag
} from '@element-plus/icons-vue'
import StateContainer from '@/components/StateContainer.vue'
import { enterpriseApi } from '@/api'

const loading = ref(false)
const error = ref<string | boolean>(false)
const data = ref<any>({
  jobs_count: 0,
  new_apps: 0,
  pending_interviews: 0,
  pending_total: 0,
  funnel: {},
  today_todos: [],
  recent_candidates: [],
  jobs: []
})

const fetchDashboard = async () => {
  loading.value = true
  error.value = false
  try {
    const res: any = await enterpriseApi.getDashboard()
    if (res) {
      data.value = {
        jobs_count: res.metrics?.active_jobs ?? res.jobs_count ?? 0,
        new_apps: res.metrics?.new_applications ?? res.new_apps ?? 0,
        pending_interviews: res.metrics?.pending_interviews ?? res.pending_interviews ?? 0,
        pending_total: res.metrics?.pending_total ?? res.pending_total ?? 0,
        funnel: res.recruitment_funnel || res.funnel || {},
        today_todos: res.today_todos || [
          { title: '初筛 Java 后端工程师新投递简历', count: res.metrics?.new_applications || 3, link: '/enterprise/candidates?status=SUBMITTED' },
          { title: '查看已完成 AI 面试的候选人报告', count: 2, link: '/enterprise/candidates?status=AI_INTERVIEW_DONE' },
          { title: '复核用人部门反馈并发出 Offer', count: 1, link: '/enterprise/pipeline' }
        ],
        recent_candidates: res.recent_candidates || [],
        jobs: res.jobs_overview || res.jobs || []
      }
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || '获取企业工作台数据失败'
  } finally {
    loading.value = false
  }
}

const getFunnelWidth = (key: string) => {
  const f = data.value.funnel || {}
  const max = Math.max(f.submitted || 1, 1)
  const val = f[key] || 0
  const pct = Math.max(12, Math.round((val / max) * 100))
  return `${pct}%`
}

const getPercent = (key: string) => {
  const f = data.value.funnel || {}
  const base = f.submitted || 1
  const val = f[key] || 0
  return Math.round((val / base) * 100)
}

const formatStatus = (s: string) => {
  const map: Record<string, string> = {
    'SUBMITTED': '新投递',
    'SCREENING': 'AI初筛',
    'INTERVIEW_INVITED': '已邀约',
    'INTERVIEW_SCHEDULED': '已排期',
    'AI_INTERVIEW_DONE': 'AI面试完',
    'OFFER': '已发Offer',
    'HIRED': '已录用入职',
    'REJECTED': '不合适'
  }
  return map[s] || s || '进行中'
}

onMounted(() => {
  fetchDashboard()
})
</script>

<style scoped>
.enterprise-dashboard {
  max-width: 1440px;
  margin: 0 auto;
}

.dash-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.dash-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 700;
  color: #2563EB;
  background: #EFF6FF;
  padding: 4px 12px;
  border-radius: 9999px;
  margin-bottom: 8px;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  background: #2563EB;
  border-radius: 50%;
  animation: pulse-ring 2s infinite;
}

@keyframes pulse-ring {
  0% { transform: scale(0.9); opacity: 1; }
  50% { transform: scale(1.3); opacity: 0.5; }
  100% { transform: scale(0.9); opacity: 1; }
}

.dash-title {
  font-size: 26px;
  font-weight: 800;
  color: #0F2347;
  margin: 0 0 6px 0;
  letter-spacing: -0.5px;
}

.dash-sub {
  font-size: 14px;
  color: #64748B;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.stat-row {
  margin-bottom: 8px;
}

.stat-card {
  padding: 22px;
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  background: #FFFFFF;
}

.border-top-blue { border-top: 4px solid #2563EB; }
.border-top-emerald { border-top: 4px solid #10B981; }
.border-top-amber { border-top: 4px solid #F59E0B; }
.border-top-purple { border-top: 4px solid #8B5CF6; }

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-blue { background: #EFF6FF; color: #2563EB; }
.icon-emerald { background: #ECFDF5; color: #10B981; }
.icon-amber { background: #FFFBEB; color: #F59E0B; }
.icon-purple { background: #FAF5FF; color: #8B5CF6; }

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 13px;
  font-weight: 600;
  color: #64748B;
  margin-bottom: 4px;
}

.stat-val {
  font-size: 30px;
  font-weight: 800;
  color: #0F2347;
  line-height: 1.1;
}

.stat-trend {
  font-size: 12px;
  margin-top: 6px;
  font-weight: 500;
}

.text-blue { color: #2563EB; }
.text-emerald { color: #10B981; }
.text-amber { color: #F59E0B; }
.text-purple { color: #8B5CF6; }

.chart-card {
  padding: 24px;
  margin-bottom: 20px;
  background: #FFFFFF;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.card-title {
  font-size: 17px;
  font-weight: 700;
  color: #0F2347;
  margin-bottom: 2px;
}

.card-subtitle {
  font-size: 13px;
  color: #64748B;
}

/* Funnel Visual Bars */
.funnel-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 4px 0;
}

.funnel-stage {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stage-info {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.stage-name {
  font-weight: 600;
  color: #1E293B;
}

.stage-stats {
  font-weight: 700;
  color: #2563EB;
}

.funnel-bar-wrapper {
  background: #F1F5F9;
  border-radius: 6px;
  height: 24px;
  overflow: hidden;
}

.funnel-bar {
  height: 100%;
  border-radius: 6px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.bg-blue { background: linear-gradient(90deg, #2563EB 0%, #3B82F6 100%); }
.bg-indigo { background: linear-gradient(90deg, #4F46E5 0%, #6366F1 100%); }
.bg-amber { background: linear-gradient(90deg, #D97706 0%, #F59E0B 100%); }
.bg-cyan { background: linear-gradient(90deg, #0891B2 0%, #06B6D4 100%); }
.bg-emerald { background: linear-gradient(90deg, #059669 0%, #10B981 100%); }

/* Urgent Todos List */
.todo-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.todo-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  background: #F8FAFC;
  border-radius: 8px;
  border: 1px solid #E2E8F0;
  cursor: pointer;
  transition: all 0.2s ease;
}

.todo-item:hover {
  background: #EFF6FF;
  border-color: #BFDBFE;
}

.todo-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.todo-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #EF4444;
}

.todo-title {
  font-size: 13px;
  font-weight: 600;
  color: #1E293B;
}

.todo-right {
  display: flex;
  align-items: center;
  gap: 6px;
}

.todo-count {
  font-size: 12px;
  font-weight: 700;
  color: #DC2626;
  background: #FEE2E2;
  padding: 2px 8px;
  border-radius: 4px;
}

.todo-arrow {
  color: #94A3B8;
  font-size: 14px;
}

/* Quick Action Tiles 2x2 */
.quick-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.quick-tile {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 8px;
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  cursor: pointer;
  transition: all 0.2s ease;
}

.quick-tile:hover {
  background: #EFF6FF;
  border-color: #BFDBFE;
  transform: translateY(-1px);
}

.tile-icon-box {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.bg-blue-subtle { background: #DBEAFE; }
.bg-emerald-subtle { background: #D1FAE5; }
.bg-amber-subtle { background: #FEF3C7; }
.bg-purple-subtle { background: #EDE9FE; }

.tile-title {
  font-size: 13px;
  font-weight: 700;
  color: #0F2347;
}

.tile-desc {
  font-size: 11px;
  color: #64748B;
  margin-top: 2px;
}

/* Candidates Table */
.cand-name {
  font-weight: 700;
  color: #0F2347;
}

/* Active Jobs Simple */
.job-list-simple {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.job-simple-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-radius: 8px;
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  transition: all 0.2s ease;
}

.job-simple-item:hover {
  background: #FFFFFF;
  border-color: #BFDBFE;
  box-shadow: 0 2px 6px rgba(37, 99, 235, 0.08);
}

.job-simple-title {
  font-size: 14px;
  font-weight: 700;
  color: #0F2347;
  margin-bottom: 4px;
}

.job-simple-meta {
  font-size: 12px;
  color: #64748B;
  display: flex;
  gap: 12px;
}

.meta-salary {
  color: #2563EB;
  font-weight: 600;
}

.job-simple-side {
  display: flex;
  align-items: center;
  gap: 12px;
}

.job-cand-count {
  font-size: 13px;
  font-weight: 700;
  color: #2563EB;
}
</style>
