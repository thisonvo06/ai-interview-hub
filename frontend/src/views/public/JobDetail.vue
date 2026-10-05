<template>
  <div class="job-detail-page">
    <StateContainer :loading="loading" :error="error" @retry="fetchDetail">
      <div v-if="job" class="zh-page-container">
        <!-- Breadcrumb -->
        <el-breadcrumb separator="/" class="detail-breadcrumb">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: '/jobs' }">岗位广场</el-breadcrumb-item>
          <el-breadcrumb-item>{{ job.title }}</el-breadcrumb-item>
        </el-breadcrumb>

        <!-- Top Header Card per Appendix A.3 & Mockup 03 -->
        <div class="job-header-card zh-card">
          <div class="header-left-wrap">
            <div class="header-comp-logo">
              <img v-if="job.company_logo && !logoFailed" :src="job.company_logo" class="logo-img" :alt="job.company_name" @error="logoFailed = true" />
              <div v-else class="logo-fallback">{{ (job.company_name || '智')[0] }}</div>
            </div>

            <div class="header-main">
              <div class="title-row">
                <h1 class="title">{{ job.title }}</h1>
                <el-tag v-if="job.status === 'PUBLISHED'" type="success" size="small">招聘中</el-tag>
                <el-tag v-else type="info" size="small">已关闭/暂停</el-tag>
                <el-tag size="small" type="primary" effect="light">官网投递</el-tag>
              </div>

              <div class="company-row">
                <router-link :to="`/companies/${job.company_id}`" class="company-link">
                  {{ job.company_name }}
                </router-link>
              </div>

              <div class="tags-row">
                <span class="salary-tag">{{ job.salary_min }}-{{ job.salary_max }}K</span>
                <span class="spec-tag">{{ job.city }}</span>
                <span class="spec-tag">{{ job.education }}</span>
                <span class="spec-tag">{{ job.experience }}</span>
                <span class="spec-tag">{{ job.type }}</span>
              </div>
            </div>
          </div>

          <div class="header-actions">
            <el-button
              :icon="job.is_favorited ? 'StarFilled' : 'Star'"
              :type="job.is_favorited ? 'warning' : 'default'"
              size="large"
              @click="toggleFav"
            >
              {{ job.is_favorited ? '已收藏' : '收藏职位' }}
            </el-button>

            <a v-if="job.official_apply_url && job.status === 'PUBLISHED'" :href="job.official_apply_url"
              target="_blank" rel="noopener noreferrer" class="official-link" @click="recordVisit">
              前往企业官网 ↗
            </a>
            <el-button v-else size="large" disabled>{{ job.status === 'PUBLISHED' ? '暂无官网链接' : '招聘已暂停' }}</el-button>
            <el-button v-if="authStore.isPersonal && job.status === 'PUBLISHED'" size="large" :loading="savingPlan" @click="addToPlan">加入求职计划</el-button>
          </div>
        </div>

        <div class="official-notice">
          <span class="channel-badge">官网投递</span>
          <p>在企业招聘官网完成简历提交。这里的岗位信息供探索与训练参考，实际职位和要求以官网为准。</p>
          <router-link v-if="authStore.isPersonal" to="/personal/applications">管理我的投递进度 →</router-link>
        </div>

        <!-- Detail Layout (Left Main Tabs, Right AI Matching & Company Info) -->
        <div class="detail-content-grid">
          <!-- Left Main Tabs -->
          <div class="left-main zh-card">
            <el-tabs v-model="activeTab" class="detail-tabs">
              <el-tab-pane label="职位详情" name="desc">
                <div class="section-block">
                  <h3 class="block-title">职位描述</h3>
                  <p class="text-content">{{ job.description }}</p>
                </div>

                <div class="section-block">
                  <h3 class="block-title">岗位职责</h3>
                  <div class="text-content multiline">{{ job.duties }}</div>
                </div>

                <div class="section-block">
                  <h3 class="block-title">任职要求</h3>
                  <div class="text-content multiline">{{ job.requirements }}</div>
                </div>

                <div v-if="job.bonus" class="section-block">
                  <h3 class="block-title">加分项</h3>
                  <div class="text-content multiline">{{ job.bonus }}</div>
                </div>
              </el-tab-pane>

              <el-tab-pane label="岗位能力胜任力模型" name="competencies">
                <div class="section-block">
                  <h3 class="block-title">能力模型权重构成 (总和100%)</h3>
                  <div class="competency-list">
                    <div v-for="(c, idx) in job.competencies" :key="idx" class="comp-row">
                      <div class="comp-info">
                        <span class="comp-name">{{ c.competency_name }}</span>
                        <span class="comp-weight">权重: {{ c.weight }}% · 基准分: {{ c.required_score }}分</span>
                      </div>
                      <el-progress :percentage="Math.min(100, Math.max(0, c.weight))" :stroke-width="8" :show-text="false" color="#2563EB" />
                    </div>
                  </div>
                </div>
              </el-tab-pane>

              <el-tab-pane label="企业介绍" name="company">
                <div class="section-block">
                  <h3 class="block-title">关于 {{ job.company_name }}</h3>
                  <p class="text-content">
                    查看企业主页了解已登记的公司介绍；招聘与待遇信息请以企业官网为准。
                  </p>
                  <router-link :to="`/companies/${job.company_id}`">
                    <el-button type="primary" plain style="margin-top: 16px;">进入企业公开主页查看在招职位 →</el-button>
                  </router-link>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>

          <!-- Right Sidebar: AI Match & Job Meta -->
          <div class="right-sidebar">
            <!-- AI Matching Card -->
            <div class="zh-card match-card">
              <div class="match-header">
                <el-icon :size="20" color="#2563EB"><Cpu /></el-icon>
                <h4 class="match-title">你的技能与这个岗位</h4>
              </div>

              <div v-if="authStore.isPersonal" class="match-body">
                <div class="score-circle">
                  <span class="score-num">{{ matchInfo?.overall_score ?? matchInfo?.match_score ?? '—' }}</span>
                  <span class="score-unit">%</span>
                </div>
                <p class="match-summary">{{ matchInfo?.explanation || '完善简历技能后可查看匹配结果' }}</p>

                <div class="match-skills-block">
                  <span class="block-tag green-tag">优势技能点</span>
                  <div class="skill-chips">
                    <span v-for="s in matchInfo?.advantage_skills || []" :key="s" class="chip-item green-chip">
                      ✓ {{ s }}
                    </span>
                  </div>
                </div>

                <div class="match-skills-block">
                  <span class="block-tag orange-tag">建议拓展提升</span>
                  <div class="skill-chips">
                    <span v-for="s in matchInfo?.missing_skills || []" :key="s" class="chip-item orange-chip">
                      ⚡ {{ s }}
                    </span>
                  </div>
                </div>

                <router-link :to="`/personal/interviews/create?jobId=${job.id}`">
                  <el-button type="primary" class="quick-train-btn">
                    针对该岗位开展模拟面试 →
                  </el-button>
                </router-link>
              </div>

              <div v-else class="guest-match-hint">
                <p class="hint-text">登录并完善简历技能后，查看与岗位要求的交集，为面试选择练习方向。</p>
                <router-link :to="`/login?redirect=${encodeURIComponent($route.fullPath)}`">
                  <el-button type="primary" plain>登录后查看匹配度</el-button>
                </router-link>
              </div>
            </div>

            <!-- Job Meta Summary -->
            <div class="zh-card meta-card">
              <h4 class="meta-title">职位关键信息</h4>
              <div class="meta-list">
                <div class="meta-item">
                  <span class="lbl">招聘人数</span>
                  <span class="val">{{ job.headcount }} 人</span>
                </div>
                <div class="meta-item">
                  <span class="lbl">发布日期</span>
                  <span class="val">{{ job.created_at ? job.created_at.substring(0, 10) : '—' }}</span>
                </div>
                <div class="meta-item">
                  <span class="lbl">岗位性质</span>
                  <span class="val">{{ job.type }}</span>
                </div>
                <div class="meta-item">
                  <span class="lbl">所属行业</span>
                  <span class="val">{{ job.category || '未登记' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </StateContainer>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { jobApi, personalApi } from '@/api'
import { jobSearchApi } from '@/api/jobSearch'
import { useAuthStore } from '@/stores/auth'
import StateContainer from '@/components/StateContainer.vue'
import { ElMessage } from 'element-plus'
import { Cpu } from '@element-plus/icons-vue'
import type { JobItem } from '@/types'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref(false)
const job = ref<JobItem | null>(null)
const logoFailed = ref(false)
const savingPlan = ref(false)
const activeTab = ref('desc')

const matchInfo = ref<any>(null)
const fetchDetail = async () => {
  logoFailed.value = false
  matchInfo.value = null
  loading.value = true
  error.value = false
  try {
    const rawId = route.params.id || route.params.jobId
    const id = Number(rawId)
    if (!rawId || isNaN(id) || id <= 0) {
      error.value = true
      return
    }
    const res: any = await jobApi.getJobDetail(id)
    job.value = res

    if (authStore.isPersonal) {
      try {
        const matchRes: any = await personalApi.getJobMatch(id)
        matchInfo.value = matchRes
      } catch (e) {
        // ignore
      }
    }
  } catch (e) {
    error.value = true
  } finally {
    loading.value = false
  }
}

watch(() => route.params.id, (newVal) => {
  if (newVal) fetchDetail()
})

const toggleFav = async () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请登录后再操作')
    router.push(`/login?redirect=${encodeURIComponent(route.fullPath)}`)
    return
  }
  if (!job.value) return

  try {
    if (job.value.is_favorited) {
      await jobApi.unfavoriteJob(job.value.id)
      job.value.is_favorited = false
      ElMessage.success('已取消收藏')
    } else {
      await jobApi.favoriteJob(job.value.id)
      job.value.is_favorited = true
      ElMessage.success('已收藏该职位')
    }
  } catch (e) {
    // handled
  }
}

const recordVisit = async () => {
  if (!job.value || !authStore.isPersonal) return
  try {
    await jobApi.recordOfficialVisit(job.value.id)
    ElMessage.info('已记录官网访问；完成官网提交后，可在“我的求职”确认已投递')
  } catch {
    ElMessage.warning('投递笔记保存失败，可返回此页重试')
  }
}

const addToPlan = async () => {
  if (!job.value || savingPlan.value) return
  savingPlan.value = true
  try {
    const result = await jobSearchApi.savePlatformJob(job.value.id)
    ElMessage.success(result.duplicate ? '这个岗位已经在求职计划中' : '已加入求职计划，可继续分析与准备')
    await router.push({ path: '/personal/job-search', query: { opportunity_id: result.item.id } })
  } catch { /* API client displays the error */ }
  finally { savingPlan.value = false }
}

onMounted(() => {
  fetchDetail()
})
</script>

<style scoped>
.official-link { display: inline-flex; align-items: center; justify-content: center; padding: 12px 22px; border-radius: 10px; background: #18796e; color: white; font-weight: 700; text-decoration: none; }
.official-link:hover { background: #11665d; }
.official-notice { display: flex; align-items: center; gap: 14px; padding: 18px 24px; margin-bottom: 24px; background: #edf7f5; border: 1px solid #c7e5dd; border-radius: 14px; color: #365e58; font-size: 13px; }
.official-notice p { flex: 1; margin: 0; line-height: 1.7; }
.channel-badge { font-weight: 700; white-space: nowrap; }
@media (max-width: 768px) { .job-header-card, .header-left-wrap, .official-notice { flex-direction: column; align-items: flex-start; } .header-actions { flex-wrap: wrap; margin-top: 20px; } .tags-row, .title-row { flex-wrap: wrap; } .job-header-card, .left-main { padding: 22px; } }

.job-detail-page {
  padding: 24px 0 64px;
}

.detail-breadcrumb {
  margin-bottom: 20px;
}

.job-header-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 32px;
  margin-bottom: 24px;
}

.header-left-wrap {
  display: flex;
  align-items: center;
  gap: 24px;
}

.header-comp-logo {
  width: 72px;
  height: 72px;
  border-radius: 12px;
  background: var(--zh-sub-bg);
  border: 1px solid var(--zh-border);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
}

.logo-img {
  width: 52px;
  height: 52px;
  object-fit: contain;
}

.logo-fallback {
  font-size: 28px;
  font-weight: 800;
  color: var(--zh-primary);
}

.header-main .title-row {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 12px;
}

.header-main .title {
  font-size: 26px;
  font-weight: 800;
  color: var(--zh-text-title);
}

.company-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.company-link {
  font-size: 15px;
  color: var(--zh-text-body);
  font-weight: 600;
}
.company-link:hover {
  color: var(--zh-primary);
}

.tags-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.salary-tag {
  font-size: 22px;
  font-weight: 800;
  color: #EF4444;
}

.spec-tag {
  font-size: 13px;
  color: #475569;
  background: #F1F5F9;
  padding: 4px 10px;
  border-radius: 6px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.apply-btn {
  height: 44px;
  padding: 0 28px;
  font-size: 15px;
  font-weight: 700;
}

.detail-content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}

.left-main {
  padding: 32px;
}

.section-block {
  margin-bottom: 32px;
}

.block-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--zh-text-title);
  margin-bottom: 14px;
  position: relative;
  padding-left: 12px;
}

.block-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 3px;
  bottom: 3px;
  width: 4px;
  background: var(--zh-primary);
  border-radius: 2px;
}

.text-content {
  font-size: 14px;
  color: var(--zh-text-body);
  line-height: 1.8;
}

.multiline {
  white-space: pre-line;
}

.competency-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comp-row .comp-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 13px;
}

.comp-name {
  font-weight: 600;
  color: var(--zh-text-title);
}

.comp-weight {
  color: var(--zh-text-muted);
}

.right-sidebar {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.match-card {
  padding: 24px;
  background: linear-gradient(180deg, #EFF6FF 0%, #FFFFFF 100%);
  border: 1px solid #BFDBFE;
}

.match-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
}

.match-title {
  font-size: 16px;
  font-weight: 700;
  color: #1E40AF;
}

.score-circle {
  display: flex;
  align-items: baseline;
  justify-content: center;
  margin-bottom: 12px;
}

.score-num {
  font-size: 44px;
  font-weight: 900;
  color: #2563EB;
}

.score-unit {
  font-size: 20px;
  font-weight: 700;
  color: #2563EB;
  margin-left: 2px;
}

.match-summary {
  font-size: 13px;
  color: var(--zh-text-body);
  line-height: 1.6;
  text-align: center;
  margin-bottom: 20px;
}

.match-skills-block {
  margin-bottom: 16px;
}

.block-tag {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
  margin-bottom: 8px;
}

.green-tag { background: #ECFDF5; color: #059669; }
.orange-tag { background: #FFFBEB; color: #D97706; }

.skill-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.chip-item {
  font-size: 12px;
  padding: 3px 8px;
  border-radius: 4px;
}

.green-chip { background: #F0FDF4; border: 1px solid #BBF7D0; color: #166534; }
.orange-chip { background: #FFFDF5; border: 1px solid #FDE68A; color: #92400E; }

.quick-train-btn {
  width: 100%;
  height: 40px;
  margin-top: 12px;
  font-weight: 600;
}

.guest-match-hint {
  text-align: center;
  padding: 16px 0;
}

.hint-text {
  font-size: 13px;
  color: var(--zh-text-muted);
  line-height: 1.6;
  margin-bottom: 16px;
}

.meta-card {
  padding: 24px;
}

.meta-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--zh-text-title);
  margin-bottom: 16px;
}

.meta-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.meta-item {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.meta-item .lbl { color: var(--zh-text-muted); }
.meta-item .val { font-weight: 500; color: var(--zh-text-title); }

.apply-notice {
  background: #EFF6FF;
  padding: 10px 14px;
  border-radius: 6px;
  font-size: 12px;
  color: #1E40AF;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  line-height: 1.5;
}

@media (max-width: 992px) {
  .detail-content-grid {
    grid-template-columns: 1fr;
  }
}
</style>
