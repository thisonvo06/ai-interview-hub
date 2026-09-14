<template>
  <div class="admin-users-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">全平台用户治理</h2>
        <p class="page-subtitle">统一管理个人求职者、企业雇主与管理员账号状态及权限生命周期</p>
      </div>
    </div>

    <!-- 筛选工具栏 -->
    <div class="filter-card">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="8" :md="6">
          <el-input
            v-model="keyword"
            placeholder="搜索用户邮箱或手机号"
            clearable
            @keyup.enter="fetchUsers"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :xs="24" :sm="8" :md="6">
          <el-button type="primary" @click="fetchUsers">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 用户列表 -->
    <StateContainer :loading="loading" :error="error" :empty="users.length === 0" @retry="fetchUsers">
      <div class="table-card">
        <el-table :data="users" style="width: 100%;">
          <el-table-column prop="id" label="UID" width="80" />

          <el-table-column prop="name" label="姓名 / 邮箱" min-width="180">
            <template #default="{ row }">
              <div style="font-weight: 600; color: #1E293B;">{{ row.name || '-' }}</div>
              <div style="font-size: 12px; color: #64748B;">{{ row.email }}</div>
            </template>
          </el-table-column>

          <el-table-column prop="phone" label="手机号" width="130">
            <template #default="{ row }">{{ row.phone || '未绑定' }}</template>
          </el-table-column>

          <el-table-column prop="account_type" label="账号类型" width="130">
            <template #default="{ row }">
              <el-tag :type="getTypeTag(row.account_type)">{{ getTypeLabel(row.account_type) }}</el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="roles" label="分配角色" min-width="150">
            <template #default="{ row }">
              <el-tag
                v-for="(r, idx) in row.roles || []"
                :key="idx"
                size="small"
                type="info"
                style="margin-right: 4px; margin-bottom: 4px;"
              >
                {{ r }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="status" label="当前状态" width="110">
            <template #default="{ row }">
              <el-tag :type="row.status === 'ACTIVE' ? 'success' : 'danger'">
                {{ row.status === 'ACTIVE' ? '正常' : '已冻结' }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="created_at" label="注册时间" width="160" />

          <el-table-column label="治理操作" width="140" fixed="right" align="right">
            <template #default="{ row }">
              <el-button
                :type="row.status === 'ACTIVE' ? 'danger' : 'success'"
                link
                size="small"
                @click="handleToggleStatus(row)"
              >
                {{ row.status === 'ACTIVE' ? '冻结账号' : '解除冻结' }}
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
import { Search } from '@element-plus/icons-vue'
import StateContainer from '@/components/StateContainer.vue'
import { adminApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const error = ref('')
const users = ref<any[]>([])
const keyword = ref('')

const fetchUsers = async () => {
  loading.value = true
  error.value = ''
  try {
    const res: any = await adminApi.listUsers({ keyword: keyword.value || undefined })
    users.value = res || []
  } catch (err: any) {
    error.value = err.response?.data?.detail || '获取用户列表失败'
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  keyword.value = ''
  fetchUsers()
}

const handleToggleStatus = (row: any) => {
  const isFreeze = row.status === 'ACTIVE'
  const actionText = isFreeze ? '冻结' : '解除冻结'

  ElMessageBox.confirm(`确定要${actionText}用户【${row.email}】吗？${isFreeze ? '冻结后该用户将立即无法登录。' : ''}`, `${actionText}确认`, {
    type: isFreeze ? 'warning' : 'info'
  }).then(async () => {
    try {
      const res: any = await adminApi.toggleUserStatus(row.id)
      ElMessage.success(res?.message || `${actionText}成功`)
      row.status = row.status === 'ACTIVE' ? 'SUSPENDED' : 'ACTIVE'
    } catch (err: any) {
      ElMessage.error(err.response?.data?.detail || `${actionText}失败`)
    }
  })
}

const getTypeTag = (t: string) => {
  switch (t) {
    case 'ADMIN': return 'danger'
    case 'ENTERPRISE': return 'warning'
    default: return 'primary'
  }
}

const getTypeLabel = (t: string) => {
  switch (t) {
    case 'ADMIN': return '平台运维'
    case 'ENTERPRISE': return '企业雇主'
    case 'PERSONAL': return '求职者'
    default: return t || '普通用户'
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.admin-users-page {
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
