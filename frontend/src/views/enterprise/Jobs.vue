<template>
  <div class="enterprise-jobs-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">职位管理</h2>
        <p class="page-subtitle">发布新职位、配置岗位多维胜任力权重及管理全生命周期状态</p>
      </div>
      <el-button type="primary" @click="$router.push('/enterprise/jobs/create')">
        <el-icon style="margin-right: 4px;"><Plus /></el-icon> 发布新岗位
      </el-button>
    </div>

    <!-- 筛选工具栏 -->
    <div class="filter-card">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="8" :md="6">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索岗位名称/技能要求"
            clearable
            @keyup.enter="fetchJobs"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :xs="24" :sm="8" :md="5">
          <el-select v-model="statusFilter" placeholder="岗位状态" clearable @change="fetchJobs">
            <el-option label="全部状态" value="" />
            <el-option label="招聘中 (PUBLISHED)" value="PUBLISHED" />
            <el-option label="待平台审核 (PENDING_REVIEW)" value="PENDING_REVIEW" />
            <el-option label="草稿 (DRAFT)" value="DRAFT" />
            <el-option label="已暂停 (PAUSED)" value="PAUSED" />
            <el-option label="已关闭 (CLOSED)" value="CLOSED" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="8" :md="6">
          <el-button type="primary" @click="fetchJobs">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 职位列表 -->
    <StateContainer :loading="loading" :error="error" :empty="jobs.length === 0" @retry="fetchJobs">
      <div class="table-card">
        <el-table :data="jobs" style="width: 100%;">
          <el-table-column prop="title" label="职位名称" min-width="180">
            <template #default="{ row }">
              <div class="job-cell-title" @click="$router.push(`/jobs/${row.id}`)">{{ row.title }}</div>
              <div class="job-cell-sub">
                <span>{{ row.department_name || '技术研发部' }}</span>
                <span class="dot">•</span>
                <span>{{ row.experience_min ? `${row.experience_min}-${row.experience_max}年` : '经验不限' }}</span>
                <span class="dot">•</span>
                <span>{{ row.education || '本科及以上' }}</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="city" label="工作地点" width="110" />

          <el-table-column prop="salary" label="薪资范围" width="130">
            <template #default="{ row }">
              <span class="salary-text">{{ row.salary_min }}-{{ row.salary_max }}K</span>
            </template>
          </el-table-column>

          <el-table-column prop="headcount" label="招聘人数" width="100">
            <template #default="{ row }">{{ row.headcount }} 人</template>
          </el-table-column>

          <el-table-column prop="applications_count" label="收到投递" width="110">
            <template #default="{ row }">
              <el-button
                type="primary"
                link
                size="small"
                @click="$router.push(`/enterprise/candidates?job_id=${row.id}`)"
              >
                {{ row.applications_count || 0 }} 份简历
              </el-button>
            </template>
          </el-table-column>

          <el-table-column prop="status" label="当前状态" width="130">
            <template #default="{ row }">
              <el-tag :type="getStatusTag(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="created_at" label="创建时间" width="130">
            <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
          </el-table-column>

          <el-table-column label="操作" width="220" fixed="right" align="right">
            <template #default="{ row }">
              <el-button
                type="primary"
                link
                size="small"
                @click="$router.push(`/enterprise/jobs/${row.id}/edit`)"
              >
                编辑
              </el-button>

              <!-- 草稿操作：提交审核 -->
              <el-button
                v-if="row.status === 'DRAFT'"
                type="success"
                link
                size="small"
                @click="handleSubmitJob(row.id)"
              >
                提交审核
              </el-button>

              <!-- 开放中操作：暂停招聘 -->
              <el-button
                v-if="row.status === 'PUBLISHED'"
                type="warning"
                link
                size="small"
                @click="handlePauseJob(row.id)"
              >
                暂停
              </el-button>

              <!-- 暂停中操作：恢复招聘 -->
              <el-button
                v-if="row.status === 'PAUSED'"
                type="success"
                link
                size="small"
                @click="handleResumeJob(row.id)"
              >
                恢复
              </el-button>

              <!-- 开放/暂停中操作：关闭招聘 -->
              <el-button
                v-if="['PUBLISHED', 'PAUSED'].includes(row.status)"
                type="info"
                link
                size="small"
                @click="handleCloseJob(row.id)"
              >
                关闭
              </el-button>

              <!-- 复制职位 -->
              <el-button
                type="default"
                link
                size="small"
                @click="handleCopyJob(row.id)"
              >
                复制
              </el-button>

              <!-- 删除草稿 -->
              <el-button
                v-if="row.status === 'DRAFT'"
                type="danger"
                link
                size="small"
                @click="handleDeleteJob(row.id)"
              >
                删除
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
import { Plus, Search } from '@element-plus/icons-vue'
import StateContainer from '@/components/StateContainer.vue'
import { enterpriseApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const error = ref('')
const jobs = ref<any[]>([])
const searchKeyword = ref('')
const statusFilter = ref('')

const fetchJobs = async () => {
  loading.value = true
  error.value = ''
  try {
    const params: any = {}
    if (searchKeyword.value) params.q = searchKeyword.value
    if (statusFilter.value) params.status = statusFilter.value
    const res: any = await enterpriseApi.listJobs(params)
    jobs.value = res || []
  } catch (err: any) {
    error.value = err.response?.data?.detail || '获取职位列表失败'
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  searchKeyword.value = ''
  statusFilter.value = ''
  fetchJobs()
}

const handleSubmitJob = async (id: number) => {
  try {
    await enterpriseApi.submitJob(id)
    ElMessage.success('已提交平台审核')
    fetchJobs()
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '提交审核失败')
  }
}

const handlePauseJob = (id: number) => {
  ElMessageBox.confirm('确定暂停该职位的公开招聘吗？候选人将暂时无法在广场搜索并投递该岗位。', '暂停提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await enterpriseApi.pauseJob(id)
      ElMessage.success('岗位已暂停招聘')
      fetchJobs()
    } catch (err: any) {
      ElMessage.error(err.response?.data?.detail || '暂停失败')
    }
  })
}

const handleResumeJob = async (id: number) => {
  try {
    await enterpriseApi.resumeJob(id)
    ElMessage.success('岗位已恢复正常招聘')
    fetchJobs()
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '恢复失败')
  }
}

const handleCloseJob = (id: number) => {
  ElMessageBox.confirm('确定关闭该职位的招聘吗？关闭后不可直接恢复投递。', '关闭提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await enterpriseApi.closeJob(id)
      ElMessage.success('岗位已关闭')
      fetchJobs()
    } catch (err: any) {
      ElMessage.error(err.response?.data?.detail || '关闭失败')
    }
  })
}

const handleCopyJob = async (id: number) => {
  try {
    await enterpriseApi.copyJob(id)
    ElMessage.success('职位副本已创建为草稿')
    fetchJobs()
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '复制职位失败')
  }
}

const handleDeleteJob = (id: number) => {
  ElMessageBox.confirm('确定删除该草稿岗位吗？删除后不可恢复。', '删除确认', {
    type: 'error'
  }).then(async () => {
    try {
      await enterpriseApi.deleteJob(id)
      ElMessage.success('草稿职位已删除')
      fetchJobs()
    } catch (err: any) {
      ElMessage.error(err.response?.data?.detail || '删除失败')
    }
  })
}

const getStatusTag = (s: string) => {
  switch (s) {
    case 'PUBLISHED': return 'success'
    case 'PENDING_REVIEW': return 'warning'
    case 'PAUSED': return 'info'
    case 'CLOSED': return 'danger'
    default: return ''
  }
}

const getStatusLabel = (s: string) => {
  switch (s) {
    case 'PUBLISHED': return '招聘中'
    case 'PENDING_REVIEW': return '审核中'
    case 'DRAFT': return '草稿'
    case 'PAUSED': return '已暂停'
    case 'CLOSED': return '已关闭'
    default: return s || '未知'
  }
}

const formatDate = (val: string) => {
  if (!val) return '-'
  return new Date(val).toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchJobs()
})
</script>

<style scoped>
.enterprise-jobs-page {
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

.job-cell-title {
  font-size: 14px;
  font-weight: 600;
  color: #1E293B;
  cursor: pointer;
  margin-bottom: 4px;
}

.job-cell-title:hover {
  color: #2563EB;
}

.job-cell-sub {
  font-size: 12px;
  color: #64748B;
  display: flex;
  align-items: center;
  gap: 6px;
}

.dot {
  color: #CBD5E1;
}

.salary-text {
  font-weight: 600;
  color: #D97706;
}
</style>
