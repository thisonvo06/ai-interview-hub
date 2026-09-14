<template>
  <div class="company-public-page">
    <StateContainer :loading="loading" :error="error" @retry="loadCompany">
      <div v-if="company" class="zh-page-container">
        <!-- Company Header Card -->
        <div class="company-header zh-card">
          <div class="header-left">
            <div class="company-logo-placeholder">
              <el-icon :size="36" color="#2563EB"><OfficeBuilding /></el-icon>
            </div>
            <div class="company-title-info">
              <div class="title-row">
                <h1 class="company-name">{{ company.name }}</h1>
                <el-tag v-if="company.status === 'VERIFIED'" type="success">认证企业</el-tag>
              </div>
              <div class="meta-row">
                <span>{{ company.industry }}</span>
                <span class="dot">·</span>
                <span>{{ company.size }}</span>
                <span class="dot">·</span>
                <span>{{ company.city }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="company-main-grid">
          <!-- Left: Jobs List -->
          <div class="jobs-column">
            <div class="column-header">
              <h3 class="col-title">在招职位 ({{ company.jobs?.length || 0 }})</h3>
            </div>

            <div v-if="company.jobs && company.jobs.length > 0" class="company-jobs-list">
              <div
                v-for="job in company.jobs"
                :key="job.id"
                class="job-card zh-card zh-card-hover"
                @click="$router.push(`/jobs/${job.id}`)"
              >
                <div class="card-top">
                  <h4 class="job-title">{{ job.title }}</h4>
                  <span class="salary">{{ job.salary_min }}-{{ job.salary_max }}K</span>
                </div>
                <div class="card-meta">
                  <span>{{ job.city }}</span>
                  <span class="dot">·</span>
                  <span>{{ job.education }}</span>
                  <span class="dot">·</span>
                  <span>{{ job.experience }}</span>
                  <span class="dot">·</span>
                  <span>{{ job.type }}</span>
                </div>
                <div class="card-skills">
                  <el-tag v-for="s in job.skills" :key="s" size="small" effect="plain">{{ s }}</el-tag>
                </div>
              </div>
            </div>
            <el-empty v-else description="该企业目前暂无公开发布的在招职位" />
          </div>

          <!-- Right: Company Profile & Location -->
          <div class="profile-column">
            <div class="zh-card profile-card">
              <h4 class="card-heading">企业基本简介</h4>
              <p class="intro-text">{{ company.intro || '该企业资料正在完善中。' }}</p>

              <div class="divider"></div>

              <h4 class="card-heading">办公地址</h4>
              <p class="address-text">{{ company.address || `${company.city}市高新技术科技园区` }}</p>
            </div>
          </div>
        </div>
      </div>
    </StateContainer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { publicApi } from '@/api'
import StateContainer from '@/components/StateContainer.vue'
import { OfficeBuilding } from '@element-plus/icons-vue'

const route = useRoute()
const loading = ref(true)
const error = ref(false)
const company = ref<any>(null)

const loadCompany = async () => {
  loading.value = true
  error.value = false
  try {
    const id = Number(route.params.companyId)
    const res: any = await publicApi.getCompanyPublic(id)
    company.value = res
  } catch (e) {
    error.value = true
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCompany()
})
</script>

<style scoped>
.company-public-page {
  padding: 24px 0 64px;
}

.company-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 32px;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.company-logo-placeholder {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  background: #EFF6FF;
  display: flex;
  align-items: center;
  justify-content: center;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.company-name {
  font-size: 24px;
  font-weight: 800;
  color: var(--zh-text-title);
}

.meta-row {
  font-size: 14px;
  color: var(--zh-text-muted);
  display: flex;
  align-items: center;
  gap: 8px;
}

.dot { color: #CBD5E1; }

.company-main-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}

.col-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--zh-text-title);
  margin-bottom: 16px;
}

.company-jobs-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.job-card {
  padding: 20px;
  cursor: pointer;
}

.card-top {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.job-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--zh-text-title);
}

.salary {
  font-size: 16px;
  font-weight: 800;
  color: #EF4444;
}

.card-meta {
  font-size: 12px;
  color: var(--zh-text-muted);
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 12px;
}

.card-skills {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.profile-card {
  padding: 24px;
}

.card-heading {
  font-size: 15px;
  font-weight: 700;
  color: var(--zh-text-title);
  margin-bottom: 12px;
}

.intro-text, .address-text {
  font-size: 13px;
  color: var(--zh-text-body);
  line-height: 1.7;
}

.divider {
  height: 1px;
  background: var(--zh-border-light);
  margin: 20px 0;
}

@media (max-width: 860px) {
  .company-main-grid {
    grid-template-columns: 1fr;
  }
}
</style>
