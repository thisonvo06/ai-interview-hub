<template>
  <div class="enterprise-candidates-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">候选人管理</h2>
        <p class="page-subtitle">全面掌握应聘者动态，AI 匹配度初筛，多阶段流程推进与精准标签画像</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="$router.push('/enterprise/pipeline')">
          <el-icon style="margin-right: 4px;"><Histogram /></el-icon> 切换到看板视图
        </el-button>
      </div>
    </div>

    <!-- 筛选面板 -->
    <div class="filter-card">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="6" :md="5">
          <el-select v-model="filters.job_id" placeholder="应聘岗位" clearable @change="fetchCandidates">
            <el-option label="全部岗位" :value="undefined" />
            <el-option v-for="j in jobs" :key="j.id" :label="j.title" :value="j.id" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="6" :md="4">
          <el-select v-model="filters.status" placeholder="招聘阶段" clearable @change="fetchCandidates">
            <el-option label="全部阶段" value="" />
            <el-option label="新投递 (SUBMITTED)" value="SUBMITTED" />
            <el-option label="AI 初筛中 (AI_SCREENING)" value="AI_SCREENING" />
            <el-option label="AI 面试就绪 (AI_INTERVIEW_PENDING)" value="AI_INTERVIEW_PENDING" />
            <el-option label="AI 面试已完成 (AI_INTERVIEW_DONE)" value="AI_INTERVIEW_DONE" />
            <el-option label="企业面试中 (ENTERPRISE_INTERVIEW)" value="ENTERPRISE_INTERVIEW" />
            <el-option label="意向 Offer (OFFER)" value="OFFER" />
            <el-option label="已入职 (HIRED)" value="HIRED" />
            <el-option label="不合适/已淘汰 (REJECTED)" value="REJECTED" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="6" :md="4">
          <el-select v-model="filters.min_score" placeholder="AI 匹配度" clearable @change="fetchCandidates">
            <el-option label="不限匹配度" :value="undefined" />
            <el-option label="高匹配 (≥ 80分)" :value="80" />
            <el-option label="中高匹配 (≥ 70分)" :value="70" />
            <el-option label="及格以上 (≥ 60分)" :value="60" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="6" :md="6">
          <el-input
            v-model="filters.search"
            placeholder="搜索候选人姓名/专业/学校"
            clearable
            @keyup.enter="fetchCandidates"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :xs="24" :sm="6" :md="5">
          <el-button type="primary" @click="fetchCandidates">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 候选人数据表格 -->
    <StateContainer :loading="loading" :error="error" :empty="candidates.length === 0" @retry="fetchCandidates">
      <div class="table-card">
        <el-table :data="candidates" style="width: 100%;">
          <el-table-column prop="user_name" label="候选人" min-width="150">
            <template #default="{ row }">
              <div class="cand-cell-name" @click="$router.push(`/enterprise/candidates/${row.id}`)">
                {{ row.user?.profile?.name || row.user?.name || `候选人 #${row.id}` }}
              </div>
              <div class="cand-cell-sub">
                <span>{{ row.user?.profile?.education || '统招本科' }}</span>
                <span class="dot">•</span>
                <span>{{ row.user?.profile?.major || '软件工程' }}</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="job_title" label="投递岗位" min-width="160">
            <template #default="{ row }">
              <span style="font-weight: 500;">{{ row.job?.title || '-' }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="match_score" label="AI 匹配度" width="130" sortable>
            <template #default="{ row }">
              <div v-if="row.match_score !== null && row.match_score !== undefined" class="score-badge-wrap">
                <el-tag :type="getScoreTag(row.match_score)" size="small">
                  {{ row.match_score }} 分
                </el-tag>
                <el-progress
                  :percentage="row.match_score"
                  :color="getScoreColor(row.match_score)"
                  :stroke-width="4"
                  :show-text="false"
                  style="width: 50px;"
                />
              </div>
              <span v-else style="color: #94A3B8; font-size: 13px;">待初筛</span>
            </template>
          </el-table-column>

          <el-table-column prop="status" label="招聘阶段" width="140">
            <template #default="{ row }">
              <el-tag :type="getStatusTag(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="tags" label="标签" min-width="150">
            <template #default="{ row }">
              <el-tag
                v-for="(t, idx) in row.tags || []"
                :key="idx"
                size="small"
                type="info"
                style="margin-right: 4px; margin-bottom: 4px;"
              >
                {{ t.tag_name || t }}
              </el-tag>
              <el-button
                type="primary"
                link
                size="small"
                @click="openAddTagDialog(row)"
              >
                +标签
              </el-button>
            </template>
          </el-table-column>

          <el-table-column prop="created_at" label="投递时间" width="130">
            <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
          </el-table-column>

          <el-table-column label="操作" width="220" fixed="right" align="right">
            <template #default="{ row }">
              <el-button
                type="primary"
                link
                size="small"
                @click="$router.push(`/enterprise/candidates/${row.id}`)"
              >
                查看档案
              </el-button>
              <el-button
                type="success"
                link
                size="small"
                @click="openAdvanceDialog(row)"
              >
                推进阶段
              </el-button>
              <el-button
                type="warning"
                link
                size="small"
                @click="handleAddToTalentPool(row.id)"
              >
                入库
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </StateContainer>

    <!-- 推进阶段弹窗 -->
    <el-dialog v-model="showAdvanceDialog" title="推进候选人阶段" width="500px">
      <el-form label-position="top">
        <el-form-item label="当前候选人">
          <div style="font-weight: 600;">
            {{ currentCand?.user?.profile?.name || currentCand?.user?.name }} (应聘: {{ currentCand?.job?.title }})
          </div>
        </el-form-item>
        <el-form-item label="流转目标阶段">
          <el-select v-model="advanceForm.target_status" style="width: 100%;">
            <el-option label="AI 初筛 (AI_SCREENING)" value="AI_SCREENING" />
            <el-option label="发起 AI 模拟面试 (AI_INTERVIEW_PENDING)" value="AI_INTERVIEW_PENDING" />
            <el-option label="安排企业面试 (ENTERPRISE_INTERVIEW)" value="ENTERPRISE_INTERVIEW" />
            <el-option label="发放 Offer (OFFER)" value="OFFER" />
            <el-option label="确认入职 (HIRED)" value="HIRED" />
            <el-option label="淘汰/不合适 (REJECTED)" value="REJECTED" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="advanceForm.target_status === 'REJECTED'" label="淘汰原因说明">
          <el-select v-model="advanceForm.reject_reason" placeholder="选择或输入未通过原因" style="width: 100%;">
            <el-option label="专业技术与岗位要求差距较大" value="专业技术不符" />
            <el-option label="项目实战与独立解决问题经验不足" value="经验不符" />
            <el-option label="薪资期望超出预算上限" value="薪资不匹配" />
            <el-option label="沟通协作或稳定性评估未达标" value="综合素质不达标" />
            <el-option label="其他原因" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="流转备注 / 评语">
          <el-input v-model="advanceForm.comment" type="textarea" :rows="3" placeholder="填写阶段推进意见..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdvanceDialog = false">取消</el-button>
        <el-button type="primary" :loading="advancing" @click="handleConfirmAdvance">确认推进</el-button>
      </template>
    </el-dialog>

    <!-- 打标签弹窗 -->
    <el-dialog v-model="showTagDialog" title="添加候选人标签" width="400px">
      <el-form label-position="top">
        <el-form-item label="标签名称">
          <el-input v-model="newTagName" placeholder="如：985保研、大厂背景、ACM金牌" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTagDialog = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmAddTag">确认添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Histogram, Search } from '@element-plus/icons-vue'
import StateContainer from '@/components/StateContainer.vue'
import { enterpriseApi } from '@/api'
import { ElMessage } from 'element-plus'

const route = useRoute()
const loading = ref(false)
const error = ref('')
const candidates = ref<any[]>([])
const jobs = ref<any[]>([])

const filters = reactive({
  job_id: route.query.job_id ? Number(route.query.job_id) : undefined,
  status: '',
  min_score: undefined as number | undefined,
  search: ''
})

const fetchJobs = async () => {
  try {
    const res: any = await enterpriseApi.listJobs()
    jobs.value = res || []
  } catch {}
}

const fetchCandidates = async () => {
  loading.value = true
  error.value = ''
  try {
    const params: any = {}
    if (filters.job_id) params.job_id = filters.job_id
    if (filters.status) params.status = filters.status
    if (filters.min_score) params.min_score = filters.min_score
    if (filters.search) params.search = filters.search

    const res: any = await enterpriseApi.listCandidates(params)
    // res might be PaginatedData or Array
    candidates.value = res.items || res || []
  } catch (err: any) {
    error.value = err.response?.data?.detail || '获取候选人列表失败'
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.job_id = undefined
  filters.status = ''
  filters.min_score = undefined
  filters.search = ''
  fetchCandidates()
}

// 推进阶段
const showAdvanceDialog = ref(false)
const currentCand = ref<any>(null)
const advancing = ref(false)
const advanceForm = reactive({
  target_status: 'AI_SCREENING',
  reject_reason: '',
  comment: ''
})

const openAdvanceDialog = (cand: any) => {
  currentCand.value = cand
  advanceForm.target_status = 'ENTERPRISE_INTERVIEW'
  advanceForm.reject_reason = ''
  advanceForm.comment = ''
  showAdvanceDialog.value = true
}

const handleConfirmAdvance = async () => {
  if (!currentCand.value) return
  advancing.value = true
  try {
    await enterpriseApi.advanceCandidate(currentCand.value.id, {
      target_status: advanceForm.target_status,
      reject_reason: advanceForm.target_status === 'REJECTED' ? advanceForm.reject_reason : undefined,
      comment: advanceForm.comment
    })
    ElMessage.success('候选人阶段推进成功')
    showAdvanceDialog.value = false
    fetchCandidates()
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '推进失败')
  } finally {
    advancing.value = false
  }
}

// 添加标签
const showTagDialog = ref(false)
const newTagName = ref('')

const openAddTagDialog = (cand: any) => {
  currentCand.value = cand
  newTagName.value = ''
  showTagDialog.value = true
}

const handleConfirmAddTag = async () => {
  if (!newTagName.value.trim() || !currentCand.value) return
  try {
    await enterpriseApi.addTag(currentCand.value.id, newTagName.value.trim())
    ElMessage.success('标签已添加')
    showTagDialog.value = false
    fetchCandidates()
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '添加标签失败')
  }
}

// 人才库
const handleAddToTalentPool = async (id: number) => {
  try {
    await enterpriseApi.addToTalentPool(id)
    ElMessage.success('已收录到企业人才库')
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '加入人才库失败')
  }
}

const getScoreTag = (score: number) => {
  if (score >= 80) return 'success'
  if (score >= 60) return 'warning'
  return 'danger'
}

const getScoreColor = (score: number) => {
  if (score >= 80) return '#10B981'
  if (score >= 60) return '#F59E0B'
  return '#EF4444'
}

const getStatusTag = (s: string) => {
  switch (s) {
    case 'SUBMITTED': return 'info'
    case 'AI_SCREENING': return 'primary'
    case 'AI_INTERVIEW_PENDING': return 'warning'
    case 'AI_INTERVIEW_DONE': return 'warning'
    case 'ENTERPRISE_INTERVIEW': return 'warning'
    case 'OFFER': return 'success'
    case 'HIRED': return 'success'
    case 'REJECTED': return 'danger'
    default: return ''
  }
}

const getStatusLabel = (s: string) => {
  switch (s) {
    case 'SUBMITTED': return '新投递'
    case 'AI_SCREENING': return 'AI初筛'
    case 'AI_INTERVIEW_PENDING': return '待模拟面试'
    case 'AI_INTERVIEW_DONE': return 'AI面试完成'
    case 'ENTERPRISE_INTERVIEW': return '企业面试'
    case 'OFFER': return '录用意向'
    case 'HIRED': return '已入职'
    case 'REJECTED': return '未通过'
    default: return s || '未知'
  }
}

const formatDate = (val: string) => {
  if (!val) return '-'
  return new Date(val).toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchJobs()
  fetchCandidates()
})
</script>

<style scoped>
.enterprise-candidates-page {
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

.filter-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #F1F5F9;
}

.table-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #F1F5F9;
}

.cand-cell-name {
  font-size: 14px;
  font-weight: 600;
  color: #1E293B;
  cursor: pointer;
  margin-bottom: 4px;
}

.cand-cell-name:hover {
  color: #2563EB;
}

.cand-cell-sub {
  font-size: 12px;
  color: #64748B;
  display: flex;
  align-items: center;
  gap: 6px;
}

.dot {
  color: #CBD5E1;
}

.score-badge-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
