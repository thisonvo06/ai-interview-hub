<template>
  <div class="resume-analysis-page">
    <!-- 返回简历中心 -->
    <div class="toolbar-row">
      <router-link to="/personal/resumes">
        <el-button link>← 返回简历中心</el-button>
      </router-link>
    </div>

    <!-- AI 分析耗时提示 -->
    <div v-if="loading" class="ai-loading-notice">
      <div class="ai-loading-bar">
        <span class="ai-spinner"></span>
        <span>AI 正在深度分析你的简历,已用时 <strong>{{ aiElapsed }}</strong> 秒...</span>
      </div>
      <p v-if="aiElapsed >= 10" class="ai-loading-sub">
        首次分析需要 10-20 秒，AI 正在逐项诊断中，请耐心等待。
      </p>
      <p v-if="aiElapsed >= 20" class="ai-loading-warn">
        仍在分析中，如持续超时可稍后重试或联系管理员检查 AI 服务。
      </p>
    </div>

    <StateContainer :loading="loading" :error="error" @retry="loadAnalysis">
      <div v-if="analysis" class="analysis-container">
        <el-alert v-if="analysis.provenance?.source !== 'REAL'" title="当前建议来自模拟数据或回退，仅用于演示诊断流程。" type="warning" :closable="false" />
        <!-- Top Score Bar -->
        <div class="header-card zh-card">
          <div class="head-left">
            <h2 class="title">AI 简历深度质量分析报告</h2>
            <p class="subtitle">针对【{{ resumeName }}】与目标岗位【{{ targetJob }}】的深度比对诊断</p>
          </div>
          <div class="head-score">
            <div class="score-circle">
              <span class="num">{{ analysis.completeness_score }}</span>
              <span class="unit">分</span>
            </div>
            <span class="score-lbl">内容完善度</span>
          </div>
        </div>

        <!-- Dynamic Issues: 优化建议 / 逐项修改建议 -->
        <div class="issues-grid">
          <div class="issue-col zh-card border-yellow">
            <div class="col-header">
              <el-tag type="warning">需重点优化 ({{ (analysis.improvements || []).length }}项)</el-tag>
            </div>
            <div v-for="(item, idx) in analysis.improvements" :key="idx" class="issue-item">
              <p>{{ item }}</p>
            </div>
            <el-empty
              v-if="!(analysis.improvements || []).length"
              description="暂无优化项"
              :image-size="60"
            />
          </div>

          <div class="issue-col zh-card border-blue">
            <div class="col-header">
              <el-tag type="primary">逐项修改建议 ({{ (analysis.suggested_modifications || []).length }}项)</el-tag>
            </div>
            <div v-for="(m, idx) in analysis.suggested_modifications" :key="idx" class="issue-item">
              <h4>{{ m.section }}</h4>
              <p>{{ m.suggestion }}</p>
            </div>
            <el-empty
              v-if="!(analysis.suggested_modifications || []).length"
              description="暂无逐项建议"
              :image-size="60"
            />
          </div>
        </div>

        <!-- Strengths & Suggestions -->
        <div class="bottom-sections">
          <div class="zh-card">
            <h3 class="sec-title text-green">✓ 简历核心优势亮点</h3>
            <ul class="styled-list green-list">
              <li v-for="(s, idx) in analysis.strengths" :key="idx">{{ s }}</li>
            </ul>
          </div>

          <div class="zh-card">
            <h3 class="sec-title text-blue">💡 推荐高频技术关键词增强</h3>
            <div class="keywords-chips">
              <el-tag
                v-for="kw in analysis.keyword_enrichment"
                :key="kw"
                class="kw-tag"
                effect="plain"
              >
                + {{ kw }}
              </el-tag>
            </div>
            <p class="kw-tip">建议将以上关键词自然嵌入到项目职责与技能介绍中，以提高企业招聘 HR 检索权重。</p>
          </div>
        </div>

        <!-- 一键应用优化 -->
        <div class="apply-bar zh-card">
          <div class="apply-text">
            <strong>一键应用 AI 优化</strong>
            <span>在不虚构经历的前提下，自动改写项目 / 工作 / 技能表述并回写简历，同时刷新完整度。</span>
          </div>
          <el-button type="success" size="large" :loading="applying" @click="handleApply">
            应用优化建议
          </el-button>
        </div>
      </div>
    </StateContainer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { resumeApi } from '@/api'
import StateContainer from '@/components/StateContainer.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const loading = ref(true)
const error = ref(false)
const applying = ref(false)
const analysis = ref<any>(null)
const resumeName = ref('核心简历')
const targetJob = ref('目标岗位')

/* ---- AI 分析耗时追踪 ---- */
const aiElapsed = ref(0)
let aiElapsedTimer: any = null

const startAIElapsed = () => {
  aiElapsed.value = 0
  if (aiElapsedTimer) clearInterval(aiElapsedTimer)
  aiElapsedTimer = setInterval(() => { aiElapsed.value++ }, 1000)
}
const stopAIElapsed = () => {
  if (aiElapsedTimer) { clearInterval(aiElapsedTimer); aiElapsedTimer = null }
}

const loadAnalysis = async () => {
  loading.value = true
  error.value = false
  aiElapsed.value = 0
  startAIElapsed()
  try {
    const id = Number(route.params.id)
    const rRes: any = await resumeApi.getResume(id)
    resumeName.value = rRes.name
    targetJob.value = rRes.target_job_title || '目标岗位'
    const res: any = await resumeApi.optimizeResume(id)
    analysis.value = res
  } catch (e) {
    error.value = true
  } finally {
    stopAIElapsed()
    loading.value = false
  }
}

const handleApply = async () => {
  applying.value = true
  try {
    const id = Number(route.params.id)
    const res: any = await resumeApi.applyOptimization(id)
    const changes: string[] = res?.changes || []
    if (!changes.length) {
      ElMessage.warning('AI 未返回可应用的改写内容，请确认已配置 LLM 服务后重试')
      return
    }
    ElMessageBox.alert(
      `<div style="line-height:1.8;font-size:13px;">${changes.map(c => `· ${c}`).join('<br/>')}</div>`,
      'AI 优化已应用',
      { dangerouslyUseHTMLString: true, confirmButtonText: '知道了' }
    )
    await loadAnalysis()
  } catch (e) {
    ElMessage.error('优化应用失败，请稍后重试')
  } finally {
    applying.value = false
  }
}

onMounted(() => {
  loadAnalysis()
})
onUnmounted(() => {
  stopAIElapsed()
})
</script>

<style scoped>
.resume-analysis-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.toolbar-row {
  display: flex;
  align-items: center;
}

.header-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 32px;
}

.title {
  font-size: 22px;
  font-weight: 800;
  color: var(--zh-text-title);
  margin-bottom: 6px;
}

.subtitle {
  font-size: 13px;
  color: var(--zh-text-muted);
}

.head-score {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.score-circle {
  display: flex;
  align-items: baseline;
}

.score-circle .num {
  font-size: 40px;
  font-weight: 900;
  color: #2563EB;
}

.score-circle .unit {
  font-size: 16px;
  font-weight: 700;
  color: #2563EB;
}

.score-lbl {
  font-size: 11px;
  color: var(--zh-text-muted);
}

.issues-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.issue-col {
  padding: 24px;
}

.border-red { border-top: 4px solid #EF4444; }
.border-yellow { border-top: 4px solid #F59E0B; }
.border-blue { border-top: 4px solid #3B82F6; }

.col-header {
  margin-bottom: 16px;
}

.issue-item {
  margin-bottom: 16px;
}

.issue-item h4 {
  font-size: 14px;
  font-weight: 700;
  color: var(--zh-text-title);
  margin-bottom: 6px;
}

.issue-item p {
  font-size: 12px;
  color: var(--zh-text-muted);
  line-height: 1.6;
}

.bottom-sections {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.bottom-sections .zh-card {
  padding: 24px;
}

.sec-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 14px;
}

.text-green { color: #10B981; }
.text-blue { color: #2563EB; }

.styled-list {
  padding-left: 20px;
  font-size: 13px;
  line-height: 1.8;
  color: var(--zh-text-body);
}

.keywords-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.kw-tag {
  font-size: 13px;
  padding: 6px 12px;
}

.kw-tip {
  font-size: 12px;
  color: var(--zh-text-muted);
  line-height: 1.5;
}

.apply-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  padding: 24px 32px;
}

.apply-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.apply-text strong {
  font-size: 15px;
  color: var(--zh-text-title);
}

.apply-text span {
  font-size: 12px;
  color: var(--zh-text-muted);
}

@media (max-width: 900px) {
  .issues-grid { grid-template-columns: 1fr; }
  .bottom-sections { grid-template-columns: 1fr; }
  .apply-bar { flex-direction: column; align-items: flex-start; }
}

/* AI 加载等待提示 */
.ai-loading-notice {
  max-width: 680px;
  margin: 0 auto 12px;
  padding: 14px 18px;
  background: #EFF6FF;
  border: 1px solid #BFDBFE;
  border-radius: 8px;
  text-align: center;
}
.ai-loading-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  color: #1E40AF;
}
.ai-loading-bar strong {
  color: #2563EB;
  font-size: 16px;
}
.ai-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #BFDBFE;
  border-top: 2px solid #2563EB;
  border-radius: 50%;
  animation: ai-spin 0.8s linear infinite;
  display: inline-block;
}
@keyframes ai-spin {
  to { transform: rotate(360deg); }
}
.ai-loading-sub {
  font-size: 12px;
  color: #3B82F6;
  margin: 8px 0 0;
}
.ai-loading-warn {
  font-size: 12px;
  color: #92400E;
  margin: 8px 0 0;
  background: #FEF3C7;
  padding: 6px 10px;
  border-radius: 4px;
}
</style>
