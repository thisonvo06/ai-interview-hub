<template>
  <div class="evaluation-page">
    <div class="page-header">
      <div>
        <el-button type="default" size="small" @click="$router.push('/enterprise/interviews')" style="margin-bottom: 8px;">
          <el-icon><ArrowLeft /></el-icon> 返回面试列表
        </el-button>
        <h2 class="page-title">面试官结构化评估与录用评价</h2>
        <p class="page-subtitle">多维度量化评估候选人表现，沉淀团队协作打分与录用建议</p>
      </div>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">
        <el-icon style="margin-right: 4px;"><Check /></el-icon> 提交评价并归档
      </el-button>
    </div>

    <el-row :gutter="24">
      <!-- 评价表单 -->
      <el-col :xs="24" :lg="16">
        <div class="eval-card">
          <h3 class="card-title">五维量化打分 (1-100分)</h3>
          <el-form label-position="top">
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="专业技术实力 (Hard Skills)">
                  <el-slider v-model="form.score_skill" :min="0" :max="100" show-input />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="项目实战与解决问题 (Experience)">
                  <el-slider v-model="form.score_exp" :min="0" :max="100" show-input />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="逻辑分析与系统架构 (Logic & System)">
                  <el-slider v-model="form.score_logic" :min="0" :max="100" show-input />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="沟通协作与清晰表达 (Communication)">
                  <el-slider v-model="form.score_comm" :min="0" :max="100" show-input />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="团队文化与自驱力契合 (Culture Fit)">
                  <el-slider v-model="form.score_culture" :min="0" :max="100" show-input />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="计算加权总评分">
                  <div class="total-score-display">{{ computedTotalScore }} 分</div>
                </el-form-item>
              </el-col>
            </el-row>

            <el-divider />

            <h3 class="card-title">录用建议与决策</h3>
            <el-form-item label="综合推荐结论" required>
              <el-radio-group v-model="form.recommendation">
                <el-radio label="STRONG_HIRE">强烈推荐录用 (Strong Hire)</el-radio>
                <el-radio label="HIRE">建议录用 (Hire)</el-radio>
                <el-radio label="NEUTRAL">存疑 / 建议加试二面 (Neutral)</el-radio>
                <el-radio label="NO_HIRE">不予录用 (No Hire)</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="核心突出优势 (Strengths)" required>
              <el-input
                v-model="form.strengths"
                type="textarea"
                :rows="3"
                placeholder="例如：底层原理理解扎实，代码工程规范意识强，面对高并发场景具备清晰的压测与排查思路..."
              />
            </el-form-item>

            <el-form-item label="关键风险与短板 (Weaknesses)">
              <el-input
                v-model="form.weaknesses"
                type="textarea"
                :rows="3"
                placeholder="例如：对微服务跨库分布式事务缺乏大规模实操，建议入职后由导师加强指导..."
              />
            </el-form-item>

            <el-form-item label="最终评语摘要 (Summary)" required>
              <el-input
                v-model="form.summary"
                type="textarea"
                :rows="4"
                placeholder="概括面试整体表现，给出定级与入职评估意见..."
              />
            </el-form-item>
          </el-form>
        </div>
      </el-col>

      <!-- 右侧面试与AI报告快览 -->
      <el-col :xs="24" :lg="8">
        <div class="eval-card">
          <h3 class="card-title">面试信息</h3>
          <div class="info-list">
            <div class="info-item">
              <span class="info-label">面试编号</span>
              <span class="info-val">#{{ interviewId }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">面试类型</span>
              <span class="info-val">企业结构化面试</span>
            </div>
            <div class="info-item">
              <span class="info-label">面试官</span>
              <span class="info-val">当前登录评审员</span>
            </div>
          </div>

          <el-divider />

          <h3 class="card-title">AI 初筛报告联动</h3>
          <p class="card-tip">AI 诊断报告已就绪，可作为评定参考依据。</p>
          <el-button
            type="primary"
            plain
            style="width: 100%;"
            @click="$router.push(`/interviews/${interviewId}/report`)"
          >
            查看 AI 评测雷达图与逐题分析
          </el-button>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Check } from '@element-plus/icons-vue'
import { enterpriseApi } from '@/api'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const interviewId = Number(route.query.interview_id || 1)
const submitting = ref(false)

const form = reactive({
  score_skill: 85,
  score_exp: 80,
  score_logic: 88,
  score_comm: 75,
  score_culture: 90,
  recommendation: 'HIRE',
  strengths: '',
  weaknesses: '',
  summary: ''
})

const computedTotalScore = computed(() => {
  return Math.round(
    form.score_skill * 0.3 +
    form.score_exp * 0.25 +
    form.score_logic * 0.2 +
    form.score_comm * 0.15 +
    form.score_culture * 0.1
  )
})

const handleSubmit = async () => {
  if (!form.summary.trim()) {
    ElMessage.warning('请填写最终评语摘要')
    return
  }
  submitting.value = true
  try {
    await enterpriseApi.submitEvaluation(interviewId, {
      score_skill: form.score_skill,
      score_exp: form.score_exp,
      score_logic: form.score_logic,
      score_comm: form.score_comm,
      score_culture: form.score_culture,
      total_score: computedTotalScore.value,
      recommendation: form.recommendation,
      strengths: form.strengths,
      weaknesses: form.weaknesses,
      summary: form.summary
    })
    ElMessage.success('面试评价已成功提交并归档')
    router.push('/enterprise/interviews')
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '提交评价失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.evaluation-page {
  max-width: 1300px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
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

.eval-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 24px;
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

.card-tip {
  font-size: 13px;
  color: #64748B;
  margin: 0 0 16px 0;
}

.total-score-display {
  font-size: 28px;
  font-weight: 800;
  color: #2563EB;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.info-label {
  color: #64748B;
}

.info-val {
  font-weight: 600;
  color: #1E293B;
}
</style>
