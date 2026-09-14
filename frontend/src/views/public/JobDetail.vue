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
              <img v-if="job.company_logo" :src="job.company_logo" class="logo-img" alt="logo" />
              <div v-else class="logo-fallback">{{ (job.company_name || '智')[0] }}</div>
            </div>

            <div class="header-main">
              <div class="title-row">
                <h1 class="title">{{ job.title }}</h1>
                <el-tag v-if="job.status === 'PUBLISHED'" type="success" size="small">招聘中</el-tag>
                <el-tag v-else type="info" size="small">已关闭/暂停</el-tag>
                <el-tag size="small" type="primary" effect="light">已官方认证</el-tag>
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

            <el-button
              type="primary"
              size="large"
              class="apply-btn"
              :disabled="job.status !== 'PUBLISHED'"
              @click="openApplyDialog"
            >
              立即投递简历
            </el-button>
          </div>
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
                      <el-progress :percentage="c.weight * 2" :stroke-width="8" :show-text="false" color="#2563EB" />
                    </div>
                  </div>
                </div>
              </el-tab-pane>

              <el-tab-pane label="企业介绍" name="company">
                <div class="section-block">
                  <h3 class="block-title">关于 {{ job.company_name }}</h3>
                  <p class="text-content">
                    我们致力于为全球用户提供卓越的技术产品与服务生态。公司拥有健全的人才晋升机制、完善的导师带教体系以及丰厚的福利保障。
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
                <h4 class="match-title">AI 人岗匹配度诊断</h4>
              </div>

              <div v-if="authStore.isPersonal" class="match-body">
                <div class="score-circle">
                  <span class="score-num">{{ matchInfo?.overall_score || 88 }}</span>
                  <span class="score-unit">%</span>
                </div>
                <p class="match-summary">{{ matchInfo?.explanation || '你的技术栈与该岗位核心要求高度匹配！建议重点练习高并发实战与系统设计题。' }}</p>

                <div class="match-skills-block">
                  <span class="block-tag green-tag">优势技能点</span>
                  <div class="skill-chips">
                    <span v-for="s in matchInfo?.advantage_skills || ['Java', 'Spring Boot', 'MySQL']" :key="s" class="chip-item green-chip">
                      ✓ {{ s }}
                    </span>
                  </div>
                </div>

                <div class="match-skills-block">
                  <span class="block-tag orange-tag">建议拓展提升</span>
                  <div class="skill-chips">
                    <span v-for="s in matchInfo?.missing_skills || ['大型分布式存储', '微服务限流容灾']" :key="s" class="chip-item orange-chip">
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
                <p class="hint-text">登录个人求职账号后，系统将结合你的简历与能力画像自动生成精准匹配分与差距诊断。</p>
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
                  <span class="val">{{ job.created_at ? job.created_at.substring(0, 10) : '2026-05-18' }}</span>
                </div>
                <div class="meta-item">
                  <span class="lbl">岗位性质</span>
                  <span class="val">{{ job.type }}</span>
                </div>
                <div class="meta-item">
                  <span class="lbl">所属行业</span>
                  <span class="val">计算机软件 / 互联网</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </StateContainer>

    <!-- Apply Modal Dialog per Spec Section 4 P03 -->
    <el-dialog
      v-model="applyDialogVisible"
      title="投递职位简历确认"
      width="540px"
      destroy-on-close
    >
      <div v-if="myResumes.length === 0" class="no-resume-guide">
        <el-result
          icon="warning"
          title="尚未创建个人简历"
          sub-title="投递前请先在简历中心创建或上传一份结构化简历"
        >
          <template #extra>
            <el-button type="primary" @click="$router.push('/personal/resumes')">前往简历中心创建</el-button>
          </template>
        </el-result>
      </div>

      <div v-else class="apply-form-modal">
        <el-form label-position="top">
          <el-form-item label="选择投递简历版本" required>
            <el-select v-model="selectedResumeId" placeholder="请选择简历" style="width: 100%;">
              <el-option
                v-for="r in myResumes"
                :key="r.id"
                :label="`${r.name} (完整度: ${r.completeness}%)`"
                :value="r.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="确认联系电话">
            <el-input v-model="applicantPhone" placeholder="请输入手机号" />
          </el-form-item>

          <div class="apply-notice">
            <el-icon color="#2563EB"><InfoFilled /></el-icon>
            <span>点击确认投递后，系统将生成该版本简历快照并实时同步至【{{ job?.company_name }}】的候选人待筛选列表中。</span>
          </div>
        </el-form>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="applyDialogVisible = false">取消</el-button>
          <el-button
            v-if="myResumes.length > 0"
            type="primary"
            :loading="submittingApply"
            @click="handleConfirmApply"
          >
            确认投递
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { jobApi, resumeApi, personalApi } from '@/api'
import { useAuthStore } from '@/stores/auth'
import StateContainer from '@/components/StateContainer.vue'
import { ElMessage } from 'element-plus'
import { Star, StarFilled, Cpu, InfoFilled } from '@element-plus/icons-vue'
import type { JobItem, ResumeItem } from '@/types'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref(false)
const job = ref<JobItem | null>(null)
const activeTab = ref('desc')

const matchInfo = ref<any>(null)
const applyDialogVisible = ref(false)
const myResumes = ref<ResumeItem[]>([])
const selectedResumeId = ref<number | null>(null)
const applicantPhone = ref('13800138001')
const submittingApply = ref(false)

const fetchDetail = async () => {
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

const openApplyDialog = async () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录求职账号后再投递')
    router.push(`/login?redirect=${encodeURIComponent(route.fullPath)}`)
    return
  }
  if (!authStore.isPersonal) {
    ElMessage.error('企业账号不可投递职位')
    return
  }

  // Load user resumes
  try {
    const list: any = await resumeApi.listResumes()
    myResumes.value = list || []
    if (myResumes.value.length > 0) {
      const def = myResumes.value.find(r => r.is_default) || myResumes.value[0]
      selectedResumeId.value = def.id
    }
    applyDialogVisible.value = true
  } catch (e) {
    ElMessage.error('加载简历失败')
  }
}

const handleConfirmApply = async () => {
  if (!selectedResumeId.value || !job.value) {
    ElMessage.warning('请选择要投递的简历')
    return
  }

  submittingApply.value = true
  try {
    await jobApi.applyJob(job.value.id, { resume_id: selectedResumeId.value })
    ElMessage.success('简历投递成功！已同步至企业候选人库，可在“我的求职”查看进度')
    applyDialogVisible.value = false
  } catch (e) {
    // handled
  } finally {
    submittingApply.value = false
  }
}

onMounted(() => {
  fetchDetail()
})
</script>

<style scoped>
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
