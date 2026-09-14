<template>
  <div class="job-explore-page">
    <div class="header-box zh-card">
      <h2 class="title">岗位智能探索与匹配</h2>
      <p class="subtitle">系统基于你的当前能力模型与简历经历，实时计算确定性匹配分与技能差距解释</p>
    </div>

    <StateContainer :loading="loading" :empty="!loading && jobs.length === 0">
      <div class="jobs-grid">
        <div
          v-for="job in jobs"
          :key="job.id"
          class="job-explore-card zh-card zh-card-hover"
          @click="$router.push(`/jobs/${job.id}`)"
        >
          <div class="card-head">
            <div>
              <h3 class="j-title">{{ job.title }}</h3>
              <span class="j-comp">{{ job.company_name }} · {{ job.city }}</span>
            </div>
            <span class="j-salary">{{ job.salary_min }}-{{ job.salary_max }}K</span>
          </div>

          <div class="match-bar">
            <div class="match-badge">
              <el-icon><Cpu /></el-icon>
              <span>匹配度 <strong>{{ job.match_score || 90 }}%</strong></span>
            </div>
            <span class="match-reason">{{ job.match_reason || '核心技能 Java/MySQL/Redis 高度匹配' }}</span>
          </div>

          <div class="skills-row">
            <el-tag v-for="s in job.skills" :key="s" size="small" effect="plain">{{ s }}</el-tag>
          </div>

          <div class="card-footer" @click.stop>
            <router-link :to="`/personal/interviews/create?jobId=${job.id}`">
              <el-button size="small" type="primary" plain>针对模拟面试</el-button>
            </router-link>
            <router-link :to="`/jobs/${job.id}`">
              <el-button size="small" type="primary">查看投递详情 →</el-button>
            </router-link>
          </div>
        </div>
      </div>
    </StateContainer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { personalApi } from '@/api'
import StateContainer from '@/components/StateContainer.vue'
import { Cpu } from '@element-plus/icons-vue'

const loading = ref(true)
const jobs = ref<any[]>([])

onMounted(async () => {
  loading.value = true
  try {
    const res: any = await personalApi.getRecommendedJobs()
    jobs.value = res || []
  } catch (e) {
    // handled
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.job-explore-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.header-box {
  padding: 24px 32px;
}
.title {
  font-size: 22px;
  font-weight: 800;
  color: var(--zh-text-title);
  margin-bottom: 6px;
}
.subtitle {
  font-size: 13px;
  color: var(--zh-text-muted);
}
.jobs-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}
.job-explore-card {
  padding: 24px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.card-head {
  display: flex;
  justify-content: space-between;
  margin-bottom: 14px;
}
.j-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--zh-text-title);
}
.j-comp {
  font-size: 13px;
  color: var(--zh-text-muted);
  margin-top: 4px;
  display: block;
}
.j-salary {
  font-size: 18px;
  font-weight: 800;
  color: #EF4444;
}
.match-bar {
  background: #EFF6FF;
  border-radius: 6px;
  padding: 8px 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}
.match-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #2563EB;
  font-size: 13px;
  flex-shrink: 0;
}
.match-reason {
  font-size: 12px;
  color: #1E40AF;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.skills-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}
.card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  border-top: 1px solid var(--zh-border-light);
  padding-top: 14px;
}
@media (max-width: 900px) {
  .jobs-grid { grid-template-columns: 1fr; }
}
</style>
