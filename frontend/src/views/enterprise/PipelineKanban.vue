<template>
  <div class="pipeline-kanban-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">招聘流程管道看板</h2>
        <p class="page-subtitle">可视化看板视图，实时跟踪各职位候选人流转生命周期与推进操作</p>
      </div>
      <div class="header-actions">
        <el-select
          v-model="selectedJobId"
          placeholder="全部招聘职位"
          clearable
          style="width: 240px;"
          @change="fetchPipeline"
        >
          <el-option label="全部在招职位" :value="undefined" />
          <el-option v-for="j in jobs" :key="j.id" :label="j.title" :value="j.id" />
        </el-select>
        <el-button type="default" @click="$router.push('/enterprise/candidates')">
          <el-icon style="margin-right: 4px;"><List /></el-icon> 列表模式
        </el-button>
      </div>
    </div>

    <StateContainer :loading="loading" :error="error" @retry="fetchPipeline">
      <!-- 泳道看板容器 -->
      <div class="kanban-board">
        <!-- 泳道 1: 新投递 -->
        <div class="kanban-col">
          <div class="col-header border-blue">
            <span class="col-title">新简历投递</span>
            <span class="col-count count-blue">{{ columns.submitted.length }}</span>
          </div>
          <div class="col-cards">
            <div
              v-for="cand in columns.submitted"
              :key="cand.id"
              class="cand-card"
              @click="$router.push(`/enterprise/candidates/${cand.id}`)"
            >
              <div class="card-top">
                <span class="cand-name">{{ cand.user_name || cand.user?.profile?.name || `候选人 #${cand.id}` }}</span>
                <span v-if="cand.match_score" class="score-tag">{{ cand.match_score }}分</span>
              </div>
              <div class="card-job">{{ cand.job_title || cand.job?.title }}</div>
              <div class="card-footer">
                <span class="cand-time">{{ formatDate(cand.created_at) }}</span>
                <el-button
                  type="primary"
                  link
                  size="small"
                  @click.stop="openAdvance(cand, 'AI_SCREENING')"
                >
                  推进初筛
                </el-button>
              </div>
            </div>
            <div v-if="columns.submitted.length === 0" class="col-empty">暂无候选人</div>
          </div>
        </div>

        <!-- 泳道 2: AI初筛中 -->
        <div class="kanban-col">
          <div class="col-header border-indigo">
            <span class="col-title">AI 初筛评估</span>
            <span class="col-count count-indigo">{{ columns.screening.length }}</span>
          </div>
          <div class="col-cards">
            <div
              v-for="cand in columns.screening"
              :key="cand.id"
              class="cand-card"
              @click="$router.push(`/enterprise/candidates/${cand.id}`)"
            >
              <div class="card-top">
                <span class="cand-name">{{ cand.user_name || cand.user?.profile?.name }}</span>
                <span v-if="cand.match_score" class="score-tag">{{ cand.match_score }}分</span>
              </div>
              <div class="card-job">{{ cand.job_title || cand.job?.title }}</div>
              <div class="card-footer">
                <el-button
                  type="danger"
                  link
                  size="small"
                  @click.stop="openReject(cand)"
                >
                  淘汰
                </el-button>
                <el-button
                  type="primary"
                  link
                  size="small"
                  @click.stop="openAdvance(cand, 'ENTERPRISE_INTERVIEW')"
                >
                  安排面试
                </el-button>
              </div>
            </div>
            <div v-if="columns.screening.length === 0" class="col-empty">暂无候选人</div>
          </div>
        </div>

        <!-- 泳道 3: 面试环节 -->
        <div class="kanban-col">
          <div class="col-header border-amber">
            <span class="col-title">面试阶段</span>
            <span class="col-count count-amber">{{ columns.interview.length }}</span>
          </div>
          <div class="col-cards">
            <div
              v-for="cand in columns.interview"
              :key="cand.id"
              class="cand-card"
              @click="$router.push(`/enterprise/candidates/${cand.id}`)"
            >
              <div class="card-top">
                <span class="cand-name">{{ cand.user_name || cand.user?.profile?.name }}</span>
                <span v-if="cand.match_score" class="score-tag">{{ cand.match_score }}分</span>
              </div>
              <div class="card-job">{{ cand.job_title || cand.job?.title }}</div>
              <div class="card-footer">
                <el-button
                  type="danger"
                  link
                  size="small"
                  @click.stop="openReject(cand)"
                >
                  未通过
                </el-button>
                <el-button
                  type="success"
                  link
                  size="small"
                  @click.stop="openAdvance(cand, 'OFFER')"
                >
                  发 Offer
                </el-button>
              </div>
            </div>
            <div v-if="columns.interview.length === 0" class="col-empty">暂无候选人</div>
          </div>
        </div>

        <!-- 泳道 4: 录用意向 (Offer) -->
        <div class="kanban-col">
          <div class="col-header border-cyan">
            <span class="col-title">录用意向 (Offer)</span>
            <span class="col-count count-cyan">{{ columns.offer.length }}</span>
          </div>
          <div class="col-cards">
            <div
              v-for="cand in columns.offer"
              :key="cand.id"
              class="cand-card"
              @click="$router.push(`/enterprise/candidates/${cand.id}`)"
            >
              <div class="card-top">
                <span class="cand-name">{{ cand.user_name || cand.user?.profile?.name }}</span>
                <span class="offer-badge">待接受</span>
              </div>
              <div class="card-job">{{ cand.job_title || cand.job?.title }}</div>
              <div class="card-footer">
                <span class="cand-time">发放时间: 近期</span>
                <el-button
                  type="success"
                  link
                  size="small"
                  @click.stop="openAdvance(cand, 'HIRED')"
                >
                  确认入职
                </el-button>
              </div>
            </div>
            <div v-if="columns.offer.length === 0" class="col-empty">暂无候选人</div>
          </div>
        </div>

        <!-- 泳道 5: 已入职 -->
        <div class="kanban-col">
          <div class="col-header border-emerald">
            <span class="col-title">已入职 (Hired)</span>
            <span class="col-count count-emerald">{{ columns.hired.length }}</span>
          </div>
          <div class="col-cards">
            <div
              v-for="cand in columns.hired"
              :key="cand.id"
              class="cand-card"
              @click="$router.push(`/enterprise/candidates/${cand.id}`)"
            >
              <div class="card-top">
                <span class="cand-name">{{ cand.user_name || cand.user?.profile?.name }}</span>
                <el-tag type="success" size="small">入职成功</el-tag>
              </div>
              <div class="card-job">{{ cand.job_title || cand.job?.title }}</div>
              <div class="card-footer">
                <span class="cand-time">入职归档</span>
              </div>
            </div>
            <div v-if="columns.hired.length === 0" class="col-empty">暂无候选人</div>
          </div>
        </div>
      </div>
    </StateContainer>

    <!-- 阶段推进/淘汰弹窗 -->
    <el-dialog v-model="showAdvanceDialog" :title="dialogTitle" width="480px">
      <el-form label-position="top">
        <el-form-item label="候选人">
          <div style="font-weight: 600;">
            {{ activeCand?.user_name || activeCand?.user?.profile?.name }} (应聘: {{ activeCand?.job_title || activeCand?.job?.title }})
          </div>
        </el-form-item>
        <el-form-item label="流转目标阶段">
          <el-select v-model="advanceForm.target_status" style="width: 100%;">
            <el-option label="AI 初筛 (AI_SCREENING)" value="AI_SCREENING" />
            <el-option label="安排企业面试 (ENTERPRISE_INTERVIEW)" value="ENTERPRISE_INTERVIEW" />
            <el-option label="发放 Offer (OFFER)" value="OFFER" />
            <el-option label="确认入职 (HIRED)" value="HIRED" />
            <el-option label="淘汰/不合适 (REJECTED)" value="REJECTED" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="advanceForm.target_status === 'REJECTED'" label="淘汰原因说明">
          <el-select v-model="advanceForm.reject_reason" placeholder="选择原因" style="width: 100%;">
            <el-option label="专业技术要求不匹配" value="专业技术不符" />
            <el-option label="项目实战经验欠缺" value="经验不符" />
            <el-option label="薪资要求超出上限" value="薪资不匹配" />
            <el-option label="综合素质与团队契合度不足" value="综合素质不匹配" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作评语">
          <el-input v-model="advanceForm.comment" type="textarea" :rows="3" placeholder="填写说明..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdvanceDialog = false">取消</el-button>
        <el-button type="primary" :loading="advancing" @click="handleConfirmAdvance">确认流转</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { List } from '@element-plus/icons-vue'
import StateContainer from '@/components/StateContainer.vue'
import { enterpriseApi } from '@/api'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const error = ref('')
const jobs = ref<any[]>([])
const selectedJobId = ref<number | undefined>(undefined)

const columns = reactive({
  submitted: [] as any[],
  screening: [] as any[],
  interview: [] as any[],
  offer: [] as any[],
  hired: [] as any[]
})

const fetchJobs = async () => {
  try {
    const res: any = await enterpriseApi.listJobs()
    jobs.value = res || []
  } catch {}
}

const fetchPipeline = async () => {
  loading.value = true
  error.value = ''
  try {
    const res: any = await enterpriseApi.getPipeline(selectedJobId.value)
    if (res) {
      columns.submitted = res.submitted || res.SUBMITTED || []
      columns.screening = res.screening || res.AI_SCREENING || []
      columns.interview = res.interview || [
        ...(res.AI_INTERVIEW_PENDING || []),
        ...(res.AI_INTERVIEW_DONE || []),
        ...(res.ENTERPRISE_INTERVIEW || [])
      ]
      columns.offer = res.offer || res.OFFER || []
      columns.hired = res.hired || res.HIRED || []
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || '获取招聘看板失败'
  } finally {
    loading.value = false
  }
}

// 推进/流转
const showAdvanceDialog = ref(false)
const dialogTitle = ref('推进阶段')
const activeCand = ref<any>(null)
const advancing = ref(false)
const advanceForm = reactive({
  target_status: '',
  reject_reason: '',
  comment: ''
})

const openAdvance = (cand: any, targetStatus: string) => {
  activeCand.value = cand
  dialogTitle.value = '推进候选人阶段'
  advanceForm.target_status = targetStatus
  advanceForm.reject_reason = ''
  advanceForm.comment = ''
  showAdvanceDialog.value = true
}

const openReject = (cand: any) => {
  activeCand.value = cand
  dialogTitle.value = '淘汰候选人'
  advanceForm.target_status = 'REJECTED'
  advanceForm.reject_reason = '专业技术不符'
  advanceForm.comment = '经评估与当前岗位要求存在差距'
  showAdvanceDialog.value = true
}

const handleConfirmAdvance = async () => {
  if (!activeCand.value) return
  advancing.value = true
  try {
    await enterpriseApi.advanceCandidate(activeCand.value.id, {
      target_status: advanceForm.target_status,
      reject_reason: advanceForm.target_status === 'REJECTED' ? advanceForm.reject_reason : undefined,
      comment: advanceForm.comment
    })
    ElMessage.success('流转成功')
    showAdvanceDialog.value = false
    fetchPipeline()
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '流转失败')
  } finally {
    advancing.value = false
  }
}

const formatDate = (val: string) => {
  if (!val) return ''
  return new Date(val).toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchJobs()
  fetchPipeline()
})
</script>

<style scoped>
.pipeline-kanban-page {
  max-width: 1500px;
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

.header-actions {
  display: flex;
  gap: 12px;
}

.kanban-board {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
  align-items: flex-start;
}

@media (max-width: 1200px) {
  .kanban-board {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .kanban-board {
    grid-template-columns: 1fr;
  }
}

.kanban-col {
  background: #F8FAFC;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
  display: flex;
  flex-direction: column;
  min-height: 500px;
}

.col-header {
  padding: 14px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #FFFFFF;
  border-top-left-radius: 12px;
  border-top-right-radius: 12px;
  border-bottom: 1px solid #E2E8F0;
  border-top: 3px solid transparent;
}

.border-blue { border-top-color: #2563EB; }
.border-indigo { border-top-color: #4F46E5; }
.border-amber { border-top-color: #F59E0B; }
.border-cyan { border-top-color: #0891B2; }
.border-emerald { border-top-color: #10B981; }

.col-title {
  font-size: 14px;
  font-weight: 600;
  color: #1E293B;
}

.col-count {
  font-size: 12px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 10px;
}

.count-blue { background: #EFF6FF; color: #2563EB; }
.count-indigo { background: #EEF2FF; color: #4F46E5; }
.count-amber { background: #FFFBEB; color: #D97706; }
.count-cyan { background: #ECFEFF; color: #0891B2; }
.count-emerald { background: #ECFDF5; color: #059669; }

.col-cards {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}

.cand-card {
  background: #FFFFFF;
  border-radius: 8px;
  padding: 12px;
  border: 1px solid #E2E8F0;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.cand-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.06);
  border-color: #BFDBFE;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.cand-name {
  font-size: 14px;
  font-weight: 600;
  color: #1E293B;
}

.score-tag {
  font-size: 12px;
  font-weight: 600;
  color: #16A34A;
  background: #DCFCE7;
  padding: 1px 6px;
  border-radius: 4px;
}

.offer-badge {
  font-size: 12px;
  color: #0891B2;
  background: #ECFEFF;
  padding: 1px 6px;
  border-radius: 4px;
}

.card-job {
  font-size: 12px;
  color: #64748B;
  margin-bottom: 8px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px dashed #F1F5F9;
  padding-top: 8px;
}

.cand-time {
  font-size: 11px;
  color: #94A3B8;
}

.col-empty {
  text-align: center;
  color: #94A3B8;
  font-size: 13px;
  margin-top: 40px;
}
</style>
