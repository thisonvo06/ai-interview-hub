<template>
  <div class="admin-audit-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">系统安全与操作审计日志</h2>
        <p class="page-subtitle">全面记录管理后台及企业关键敏感操作，满足等保与防越权追溯要求</p>
      </div>
      <el-button size="small" @click="fetchLogs">
        刷新审计日志
      </el-button>
    </div>

    <!-- 筛选面板 -->
    <div class="filter-card">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="8" :md="6">
          <el-input
            v-model="keyword"
            placeholder="搜索操作人/动作/目标"
            clearable
            @keyup.enter="filterLogs"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :xs="24" :sm="8" :md="6">
          <el-button type="primary" @click="filterLogs">筛选</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 日志表格 -->
    <StateContainer :loading="loading" :error="error" :empty="displayedLogs.length === 0" @retry="fetchLogs">
      <div class="table-card">
        <el-table :data="displayedLogs" style="width: 100%;">
          <el-table-column prop="created_at" label="操作时间" width="180" />

          <el-table-column prop="actor_name" label="操作人" width="140">
            <template #default="{ row }">
              <span style="font-weight: 600; color: #1E293B;">{{ row.actor_name || '平台管理员' }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="role" label="操作角色" width="130">
            <template #default="{ row }">
              <el-tag size="small">{{ row.role || 'ADMIN' }}</el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="action" label="操作类型" width="180">
            <template #default="{ row }">
              <span style="font-weight: 500; color: #2563EB;">{{ row.action }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="resource" label="操作目标" width="140">
            <template #default="{ row }">
              <el-tag type="info" size="small">{{ row.resource_type }} #{{ row.resource_id }}</el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="detail" label="详细审计内容" min-width="260" />

          <el-table-column prop="ip" label="客户端 IP" width="130">
            <template #default="{ row }">
              <code style="font-size: 12px;">{{ row.ip || '127.0.0.1' }}</code>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </StateContainer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import StateContainer from '@/components/StateContainer.vue'
import { adminApi } from '@/api'

const loading = ref(false)
const error = ref('')
const allLogs = ref<any[]>([])
const displayedLogs = ref<any[]>([])
const keyword = ref('')

const fetchLogs = async () => {
  loading.value = true
  error.value = ''
  try {
    const res: any = await adminApi.getAuditLogs()
    allLogs.value = res || []
    filterLogs()
  } catch (err: any) {
    error.value = err.response?.data?.detail || '获取审计日志失败'
  } finally {
    loading.value = false
  }
}

const filterLogs = () => {
  if (!keyword.value.trim()) {
    displayedLogs.value = allLogs.value
    return
  }
  const kw = keyword.value.trim().toLowerCase()
  displayedLogs.value = allLogs.value.filter((l: any) => {
    return (
      (l.actor_name && l.actor_name.toLowerCase().includes(kw)) ||
      (l.action && l.action.toLowerCase().includes(kw)) ||
      (l.detail && l.detail.toLowerCase().includes(kw)) ||
      (l.resource_type && l.resource_type.toLowerCase().includes(kw))
    )
  })
}

const resetFilter = () => {
  keyword.value = ''
  displayedLogs.value = allLogs.value
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
.admin-audit-page {
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
</style>
