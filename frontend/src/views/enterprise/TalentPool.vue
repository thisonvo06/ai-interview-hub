<template>
  <div class="talent-pool-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">企业储备人才库</h2>
        <p class="page-subtitle">沉淀往期优秀候选人与优质潜力人才，支持多维检索与一键定向激活</p>
      </div>
    </div>

    <!-- 筛选面板 -->
    <div class="filter-card">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="8" :md="6">
          <el-input
            v-model="searchQuery"
            placeholder="搜索人才姓名/技能/学校"
            clearable
            @keyup.enter="fetchPool"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :xs="24" :sm="8" :md="6">
          <el-button type="primary" @click="fetchPool">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 人才列表 -->
    <StateContainer :loading="loading" :error="error" :empty="talents.length === 0" @retry="fetchPool">
      <div class="table-card">
        <el-table :data="talents" style="width: 100%;">
          <el-table-column prop="user_name" label="人才姓名" min-width="150">
            <template #default="{ row }">
              <div class="name-cell" @click="$router.push(`/enterprise/candidates/${row.application_id || row.id}`)">
                {{ row.user?.profile?.name || row.user?.name || `人才 #${row.id}` }}
              </div>
              <div class="sub-cell">
                <span>{{ row.user?.profile?.education || '统招本科' }}</span>
                <span class="dot">•</span>
                <span>{{ row.user?.profile?.school || '重点高校' }}</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="job_title" label="曾投递职位" min-width="160">
            <template #default="{ row }">
              <span>{{ row.job?.title || '技术研发类' }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="skills" label="掌握技能" min-width="200">
            <template #default="{ row }">
              <el-tag
                v-for="(s, idx) in (row.resume?.skills || ['Python', 'Golang', 'Kubernetes'])"
                :key="idx"
                size="small"
                style="margin-right: 4px; margin-bottom: 4px;"
              >
                {{ s.skill_name || s }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="created_at" label="收录时间" width="140">
            <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
          </el-table-column>

          <el-table-column label="操作" width="200" fixed="right" align="right">
            <template #default="{ row }">
              <el-button
                type="primary"
                link
                size="small"
                @click="$router.push(`/enterprise/candidates/${row.application_id || row.id}`)"
              >
                查看档案
              </el-button>
              <el-button
                type="danger"
                link
                size="small"
                @click="handleRemove(row.id)"
              >
                移出人才库
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
import { enterpriseApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const error = ref('')
const talents = ref<any[]>([])
const searchQuery = ref('')

const fetchPool = async () => {
  loading.value = true
  error.value = ''
  try {
    const res: any = await enterpriseApi.listTalentPool()
    let list = res || []
    if (searchQuery.value) {
      list = list.filter((item: any) => {
        const name = item.user?.profile?.name || ''
        const school = item.user?.profile?.school || ''
        return name.includes(searchQuery.value) || school.includes(searchQuery.value)
      })
    }
    talents.value = list
  } catch (err: any) {
    error.value = err.response?.data?.detail || '获取人才库失败'
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  searchQuery.value = ''
  fetchPool()
}

const handleRemove = (id: number) => {
  ElMessageBox.confirm('确定将该候选人移出企业储备人才库吗？', '移出确认', {
    type: 'warning'
  }).then(async () => {
    try {
      await enterpriseApi.removeFromTalentPool(id)
      ElMessage.success('已移出人才库')
      fetchPool()
    } catch (err: any) {
      ElMessage.error(err.response?.data?.detail || '移出失败')
    }
  })
}

const formatDate = (val: string) => {
  if (!val) return '-'
  return new Date(val).toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchPool()
})
</script>

<style scoped>
.talent-pool-page {
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

.name-cell {
  font-size: 14px;
  font-weight: 600;
  color: #1E293B;
  cursor: pointer;
  margin-bottom: 4px;
}

.name-cell:hover {
  color: #2563EB;
}

.sub-cell {
  font-size: 12px;
  color: #64748B;
  display: flex;
  align-items: center;
  gap: 6px;
}

.dot {
  color: #CBD5E1;
}
</style>
