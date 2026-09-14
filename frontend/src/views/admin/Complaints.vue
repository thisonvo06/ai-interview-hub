<template>
  <div class="admin-complaints-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">用户举报与维权申诉处置</h2>
        <p class="page-subtitle">受理并处置求职者与雇主关于虚假岗位、骚扰欺诈或违规言论的申诉投诉</p>
      </div>
    </div>

    <!-- 投诉数据表格 -->
    <StateContainer :loading="loading" :error="error" :empty="complaints.length === 0" @retry="fetchComplaints">
      <div class="table-card">
        <el-table :data="complaints" style="width: 100%;">
          <el-table-column prop="id" label="ID" width="70" />

          <el-table-column prop="reporter_name" label="举报人" width="130">
            <template #default="{ row }">
              <span style="font-weight: 500;">{{ row.reporter_name || '实名用户' }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="target_type" label="被举报主体" width="140">
            <template #default="{ row }">
              <el-tag size="small">{{ getTargetLabel(row.target_type) }} #{{ row.target_id }}</el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="reason" label="举报事由" width="160">
            <template #default="{ row }">
              <span style="font-weight: 600; color: #DC2626;">{{ row.reason }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="detail" label="详细描述与凭证" min-width="220" />

          <el-table-column prop="status" label="状态" width="110">
            <template #default="{ row }">
              <el-tag :type="row.status === 'RESOLVED' ? 'success' : 'warning'">
                {{ row.status === 'RESOLVED' ? '已处置' : '待处理' }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="created_at" label="举报时间" width="150" />

          <el-table-column label="处置" width="130" fixed="right" align="right">
            <template #default="{ row }">
              <el-button
                v-if="row.status !== 'RESOLVED'"
                type="primary"
                link
                size="small"
                @click="openResolveModal(row)"
              >
                处理投诉
              </el-button>
              <span v-else style="color: #94A3B8; font-size: 13px;">已结案</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </StateContainer>

    <!-- 处置弹窗 -->
    <el-dialog v-model="showModal" title="投诉举报核查与处置" width="480px">
      <el-form label-position="top">
        <el-form-item label="举报事由">
          <div style="font-weight: 600; color: #DC2626;">{{ currentItem?.reason }}</div>
        </el-form-item>
        <el-form-item label="处置方案与回复内容" required>
          <el-input
            v-model="resolution"
            type="textarea"
            :rows="4"
            placeholder="填写平台处置措施（如：下架岗位并给予警告、冻结账号等）及向举报人的反馈答复..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showModal = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleConfirmResolve">确认结案处置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import StateContainer from '@/components/StateContainer.vue'
import { adminApi } from '@/api'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const error = ref('')
const complaints = ref<any[]>([])

const showModal = ref(false)
const currentItem = ref<any>(null)
const resolution = ref('')
const submitting = ref(false)

const fetchComplaints = async () => {
  loading.value = true
  error.value = ''
  try {
    const res: any = await adminApi.listComplaints()
    complaints.value = res || []
  } catch (err: any) {
    error.value = err.response?.data?.detail || '获取举报列表失败'
  } finally {
    loading.value = false
  }
}

const openResolveModal = (row: any) => {
  currentItem.value = row
  resolution.value = ''
  showModal.value = true
}

const handleConfirmResolve = async () => {
  if (!resolution.value.trim()) {
    ElMessage.warning('请填写处置方案')
    return
  }
  submitting.value = true
  try {
    await adminApi.resolveComplaint(currentItem.value.id, resolution.value.trim())
    ElMessage.success('投诉已处置完毕并结案')
    showModal.value = false
    fetchComplaints()
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '处置失败')
  } finally {
    submitting.value = false
  }
}

const getTargetLabel = (t: string) => {
  switch (t) {
    case 'JOB': return '招聘岗位'
    case 'COMPANY': return '入驻企业'
    case 'USER': return '用户个人'
    default: return t || '主体'
  }
}

onMounted(() => {
  fetchComplaints()
})
</script>

<style scoped>
.admin-complaints-page {
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
