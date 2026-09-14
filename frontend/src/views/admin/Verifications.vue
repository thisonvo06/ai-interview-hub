<template>
  <div class="admin-verifications-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">企业资质与实名认证审核</h2>
        <p class="page-subtitle">人工复核企业提交的营业执照代码、法人信息及合规材料</p>
      </div>
    </div>

    <!-- 资质列表表格 -->
    <StateContainer :loading="loading" :error="error" :empty="verifications.length === 0" @retry="fetchVerifications">
      <div class="table-card">
        <el-table :data="verifications" style="width: 100%;">
          <el-table-column prop="company_name" label="企业名称" min-width="180">
            <template #default="{ row }">
              <div style="font-weight: 600; color: #1E293B;">{{ row.company_name }}</div>
              <div style="font-size: 12px; color: #64748B;">企业ID: #{{ row.company_id }}</div>
            </template>
          </el-table-column>

          <el-table-column prop="license_number" label="统一社会信用代码" width="200">
            <template #default="{ row }">
              <code style="background: #F1F5F9; padding: 2px 6px; border-radius: 4px;">{{ row.license_number }}</code>
            </template>
          </el-table-column>

          <el-table-column prop="legal_person" label="法定代表人" width="120" />
          <el-table-column prop="contact_phone" label="联系电话" width="130" />

          <el-table-column prop="status" label="审核状态" width="120">
            <template #default="{ row }">
              <el-tag :type="getStatusTag(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="opinion" label="审核意见/驳回原因" min-width="200">
            <template #default="{ row }">
              <span v-if="row.opinion" style="font-size: 13px; color: #475569;">{{ row.opinion }}</span>
              <span v-else style="color: #94A3B8; font-size: 12px;">暂无评语</span>
            </template>
          </el-table-column>

          <el-table-column prop="created_at" label="提交时间" width="150" />

          <el-table-column label="审核操作" width="180" fixed="right" align="right">
            <template #default="{ row }">
              <template v-if="row.status === 'PENDING'">
                <el-button
                  type="success"
                  link
                  size="small"
                  @click="handleApprove(row)"
                >
                  通过
                </el-button>
                <el-button
                  type="danger"
                  link
                  size="small"
                  @click="openRejectDialog(row)"
                >
                  驳回
                </el-button>
              </template>
              <span v-else style="color: #94A3B8; font-size: 13px;">已处理</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </StateContainer>

    <!-- 驳回原因输入弹窗 -->
    <el-dialog v-model="showRejectModal" title="驳回企业资质认证" width="480px">
      <el-form label-position="top">
        <el-form-item label="企业名称">
          <div style="font-weight: 600;">{{ currentRecord?.company_name }}</div>
        </el-form-item>
        <el-form-item label="驳回原因与修改指引" required>
          <el-input
            v-model="rejectReason"
            type="textarea"
            :rows="4"
            placeholder="说明材料不合规具体原因，如营业执照与主体名称不符、照片模糊等..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRejectModal = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleConfirmReject">确认驳回</el-button>
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
const verifications = ref<any[]>([])

const showRejectModal = ref(false)
const currentRecord = ref<any>(null)
const rejectReason = ref('')
const submitting = ref(false)

const fetchVerifications = async () => {
  loading.value = true
  error.value = ''
  try {
    const res: any = await adminApi.listVerifications()
    verifications.value = res || []
  } catch (err: any) {
    error.value = err.response?.data?.detail || '获取资质审核列表失败'
  } finally {
    loading.value = false
  }
}

const handleApprove = (row: any) => {
  ElMessageBox.confirm(`确认通过【${row.company_name}】的企业实名资质审核吗？通过后企业将获得官方认证标识并可正常招募候选人。`, '审核通过确认', {
    type: 'success'
  }).then(async () => {
    try {
      await adminApi.approveVerification(row.id, '资质审核通过，准予公开发布招聘岗位')
      ElMessage.success('审核已通过')
      fetchVerifications()
    } catch (err: any) {
      ElMessage.error(err.response?.data?.detail || '操作失败')
    }
  })
}

const openRejectDialog = (row: any) => {
  currentRecord.value = row
  rejectReason.value = ''
  showRejectModal.value = true
}

const handleConfirmReject = async () => {
  if (!rejectReason.value.trim()) {
    ElMessage.warning('请输入驳回原因')
    return
  }
  submitting.value = true
  try {
    await adminApi.rejectVerification(currentRecord.value.id, rejectReason.value.trim())
    ElMessage.success('已驳回资质申请')
    showRejectModal.value = false
    fetchVerifications()
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

const getStatusTag = (s: string) => {
  switch (s) {
    case 'APPROVED': return 'success'
    case 'REJECTED': return 'danger'
    default: return 'warning'
  }
}

const getStatusLabel = (s: string) => {
  switch (s) {
    case 'APPROVED': return '审核通过'
    case 'REJECTED': return '已驳回'
    default: return '待审核'
  }
}

onMounted(() => {
  fetchVerifications()
})
</script>

<style scoped>
.admin-verifications-page {
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
