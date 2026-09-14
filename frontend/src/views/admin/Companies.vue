<template>
  <div class="admin-companies-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">企业入驻治理</h2>
        <p class="page-subtitle">监控全平台入驻雇主、认证状态与招聘岗位合规状态</p>
      </div>
    </div>

    <!-- 企业列表表格 -->
    <StateContainer :loading="loading" :error="error" :empty="companies.length === 0" @retry="fetchCompanies">
      <div class="table-card">
        <el-table :data="companies" style="width: 100%;">
          <el-table-column prop="id" label="ID" width="70" />

          <el-table-column prop="name" label="企业名称" min-width="180">
            <template #default="{ row }">
              <span style="font-weight: 600; color: #1E293B;">{{ row.name }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="industry" label="所属行业" width="160" />
          <el-table-column prop="city" label="所在城市" width="120" />
          <el-table-column prop="size" label="企业规模" width="130" />

          <el-table-column prop="jobs_count" label="发布职位" width="110">
            <template #default="{ row }">
              <el-tag size="small">{{ row.jobs_count || 0 }} 个</el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="status" label="认证状态" width="120">
            <template #default="{ row }">
              <el-tag :type="getStatusTag(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="created_at" label="入驻时间" width="130" />

          <el-table-column label="操作" width="150" fixed="right" align="right">
            <template #default="{ row }">
              <el-button
                :type="row.status === 'SUSPENDED' ? 'success' : 'danger'"
                link
                size="small"
                @click="handleToggleStatus(row)"
              >
                {{ row.status === 'SUSPENDED' ? '解除封禁' : '封禁企业' }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </StateContainer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import StateContainer from '@/components/StateContainer.vue'
import { adminApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const error = ref('')
const companies = ref<any[]>([])

const fetchCompanies = async () => {
  loading.value = true
  error.value = ''
  try {
    const res: any = await adminApi.listCompanies()
    companies.value = res || []
  } catch (err: any) {
    error.value = err.response?.data?.detail || '获取企业列表失败'
  } finally {
    loading.value = false
  }
}

const handleToggleStatus = (row: any) => {
  const isSuspend = row.status !== 'SUSPENDED'
  const actionText = isSuspend ? '封禁' : '解除封禁'

  ElMessageBox.confirm(`确定要${actionText}企业【${row.name}】吗？${isSuspend ? '封禁后该企业发布的职位将全部下架且成员无法发邀约。' : ''}`, '状态变更确认', {
    type: isSuspend ? 'warning' : 'info'
  }).then(async () => {
    try {
      const res: any = await adminApi.toggleCompanyStatus(row.id)
      ElMessage.success(res?.message || `${actionText}成功`)
      row.status = row.status === 'SUSPENDED' ? 'VERIFIED' : 'SUSPENDED'
    } catch (err: any) {
      ElMessage.error(err.response?.data?.detail || '操作失败')
    }
  })
}

const getStatusTag = (s: string) => {
  switch (s) {
    case 'VERIFIED': return 'success'
    case 'SUSPENDED': return 'danger'
    default: return 'warning'
  }
}

const getStatusLabel = (s: string) => {
  switch (s) {
    case 'VERIFIED': return '已官方认证'
    case 'SUSPENDED': return '已被封禁'
    default: return '待审核/未认证'
  }
}

onMounted(() => {
  fetchCompanies()
})
</script>

<style scoped>
.admin-companies-page {
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
