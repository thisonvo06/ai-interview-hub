<template>
  <div class="admin-jobs-review-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">职位合规审核与治理</h2>
        <p class="page-subtitle">审核企业提交发布的职位薪资范围、JD描述合规性与下架处置违规岗位</p>
      </div>
    </div>

    <!-- 职位审核表格 -->
    <StateContainer :loading="loading" :error="error" :empty="jobs.length === 0" @retry="fetchJobs">
      <div class="table-card">
        <el-table :data="jobs" style="width: 100%;">
          <el-table-column prop="title" label="职位名称" min-width="180">
            <template #default="{ row }">
              <div style="font-weight: 600; color: #1E293B;">{{ row.title }}</div>
              <div style="font-size: 12px; color: #64748B;">{{ row.department_name || '技术部' }}</div>
            </template>
          </el-table-column>

          <el-table-column prop="company_name" label="发布企业" min-width="160" />
          <el-table-column prop="city" label="工作地点" width="110" />

          <el-table-column prop="salary" label="薪资范围" width="130">
            <template #default="{ row }">
              <span style="font-weight: 600; color: #D97706;">{{ row.salary_min }}-{{ row.salary_max }}K</span>
            </template>
          </el-table-column>

          <el-table-column prop="status" label="状态" width="130">
            <template #default="{ row }">
              <el-tag :type="getStatusTag(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="created_at" label="提交时间" width="140" />

          <el-table-column label="审核操作" width="220" fixed="right" align="right">
            <template #default="{ row }">
              <template v-if="row.status === 'PENDING_REVIEW'">
                <el-button type="success" link size="small" @click="handleApprove(row)">
                  通过发布
                </el-button>
                <el-button type="warning" link size="small" @click="openReasonDialog(row, 'REJECT')">
                  驳回修改
                </el-button>
              </template>
              <template v-else-if="row.status === 'PUBLISHED'">
                <el-button type="danger" link size="small" @click="openReasonDialog(row, 'TAKEDOWN')">
                  强制下架
                </el-button>
              </template>
              <span v-else style="color: #94A3B8; font-size: 13px;">无可用操作</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </StateContainer>

    <!-- 原因弹窗 -->
    <el-dialog v-model="showReasonModal" :title="modalTitle" width="480px">
      <el-form label-position="top">
        <el-form-item label="职位">
          <div style="font-weight: 600;">{{ currentJob?.title }} ({{ currentJob?.company_name }})</div>
        </el-form-item>
        <el-form-item :label="reasonLabel" required>
          <el-input
            v-model="actionReason"
            type="textarea"
            :rows="4"
            placeholder="填写操作理由与依据..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showReasonModal = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleConfirmAction">确认执行</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import StateContainer from '@/components/StateContainer.vue'
import { adminApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const error = ref('')
const jobs = ref<any[]>([])

const showReasonModal = ref(false)
const currentJob = ref<any>(null)
const actionType = ref<'REJECT' | 'TAKEDOWN'>('REJECT')
const actionReason = ref('')
const submitting = ref(false)
const modalTitle = ref('')
const reasonLabel = ref('')

const fetchJobs = async () => {
  loading.value = true
  error.value = ''
  try {
    const res: any = await adminApi.listJobsReview()
    jobs.value = res || []
  } catch (err: any) {
    error.value = err.response?.data?.detail || '获取职位审核列表失败'
  } finally {
    loading.value = false
  }
}

const handleApprove = (row: any) => {
  ElMessageBox.confirm(`确认批准岗位【${row.title}】发布至广场供全平台求职者投递吗？`, '通过确认', {
    type: 'success'
  }).then(async () => {
    try {
      await adminApi.approveJob(row.id)
      ElMessage.success('职位已通过审核并公开')
      fetchJobs()
    } catch (err: any) {
      ElMessage.error(err.response?.data?.detail || '审核失败')
    }
  })
}

const openReasonDialog = (row: any, type: 'REJECT' | 'TAKEDOWN') => {
  currentJob.value = row
  actionType.value = type
  actionReason.value = ''
  if (type === 'REJECT') {
    modalTitle.value = '驳回职位发布申请'
    reasonLabel.value = '驳回整改原因'
  } else {
    modalTitle.value = '违规岗位强制下架'
    reasonLabel.value = '强制下架处置依据'
  }
  showReasonModal.value = true
}

const handleConfirmAction = async () => {
  if (!actionReason.value.trim()) {
    ElMessage.warning('请填写原因')
    return
  }
  submitting.value = true
  try {
    if (actionType.value === 'REJECT') {
      await adminApi.rejectJob(currentJob.value.id, actionReason.value.trim())
      ElMessage.success('已驳回岗位申请')
    } else {
      await adminApi.takedownJob(currentJob.value.id, actionReason.value.trim())
      ElMessage.success('违规岗位已强制下架')
    }
    showReasonModal.value = false
    fetchJobs()
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

const getStatusTag = (s: string) => {
  switch (s) {
    case 'PUBLISHED': return 'success'
    case 'PENDING_REVIEW': return 'warning'
    case 'CLOSED': return 'info'
    default: return ''
  }
}

const getStatusLabel = (s: string) => {
  switch (s) {
    case 'PUBLISHED': return '招聘中'
    case 'PENDING_REVIEW': return '待平台审核'
    case 'CLOSED': return '已下架/关闭'
    default: return s || '未知'
  }
}

onMounted(() => {
  fetchJobs()
})
</script>

<style scoped>
.admin-jobs-review-page {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
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

.table-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #F1F5F9;
}
</style>
