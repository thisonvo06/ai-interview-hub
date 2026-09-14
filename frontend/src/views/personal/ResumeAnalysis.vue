<template>
  <div class="resume-analysis-page">
    <StateContainer :loading="loading" :error="error" @retry="loadAnalysis">
      <div v-if="analysis" class="analysis-container">
        <!-- Top Score Bar -->
        <div class="header-card zh-card">
          <div class="head-left">
            <h2 class="title">AI 简历深度质量分析报告</h2>
            <p class="subtitle">针对【{{ resumeName }}】与目标岗位【Java后端开发工程师】的深度比对诊断</p>
          </div>
          <div class="head-score">
            <div class="score-circle">
              <span class="num">{{ analysis.completeness_score }}</span>
              <span class="unit">分</span>
            </div>
            <span class="score-lbl">综合质量评级</span>
          </div>
        </div>

        <!-- 3-Tier Issues List: 严重 / 中等 / 建议 -->
        <div class="issues-grid">
          <div class="issue-col zh-card border-red">
            <div class="col-header">
              <el-tag type="danger">严重需补充 (1项)</el-tag>
            </div>
            <div class="issue-item">
              <h4>缺少高并发量化性能指标</h4>
              <p>项目经历中提到“优化秒杀与缓存”，但未给出具体压测数据（如 QPS 从 800 提升至 5000+，P99 延迟降至 20ms）。建议使用真实压测数据补充 STAR 描述。</p>
            </div>
          </div>

          <div class="issue-col zh-card border-yellow">
            <div class="col-header">
              <el-tag type="warning">中等待优化 (2项)</el-tag>
            </div>
            <div class="issue-item">
              <h4>技能熟练度需精细区分</h4>
              <p>避免所有技能均标记为“熟练”。针对核心竞争力（如 Redis/MySQL）突出底层原理掌握，其余辅助工具标记为“熟悉”。</p>
            </div>
            <div class="issue-item">
              <h4>项目技术选型未体现取舍考量</h4>
              <p>建议补充“为何选用 Redisson 而非简单 setnx”、“双写一致性中延迟双删与 Canal 监听的对比权衡”。</p>
            </div>
          </div>

          <div class="issue-col zh-card border-blue">
            <div class="col-header">
              <el-tag type="primary">体验级建议 (2项)</el-tag>
            </div>
            <div class="issue-item">
              <h4>STAR 原则表述微调</h4>
              <p>在自我评价中突出对解决线上疑难故障的热情，展现工程韧性。</p>
            </div>
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
      </div>
    </StateContainer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { resumeApi } from '@/api'
import StateContainer from '@/components/StateContainer.vue'

const route = useRoute()
const loading = ref(true)
const error = ref(false)
const analysis = ref<any>(null)
const resumeName = ref('核心简历')

const loadAnalysis = async () => {
  loading.value = true
  error.value = false
  try {
    const id = Number(route.params.id)
    const rRes: any = await resumeApi.getResume(id)
    resumeName.value = rRes.name
    const res: any = await resumeApi.optimizeResume(id)
    analysis.value = res
  } catch (e) {
    error.value = true
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadAnalysis()
})
</script>

<style scoped>
.resume-analysis-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
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
  grid-template-columns: repeat(3, 1fr);
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

@media (max-width: 900px) {
  .issues-grid { grid-template-columns: 1fr; }
  .bottom-sections { grid-template-columns: 1fr; }
}
</style>
