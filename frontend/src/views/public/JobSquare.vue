<template>
  <div class="job-square-page">
    <div class="zh-page-container">
      <!-- Top Title Area -->
      <div class="square-title-row">
        <h1 class="page-main-title">岗位广场</h1>
        <span class="page-subtitle">汇聚一线名企在招技术与管理职位，智能胜任力匹配</span>
      </div>

      <!-- Prominent Search Bar (Appendix A.2) -->
      <div class="search-section zh-card">
        <div class="search-input-wrapper">
          <el-input
            v-model="filters.keyword"
            placeholder="搜索职位、企业或技术关键词 (如: Java, 秒杀, Redis, 大模型)..."
            size="large"
            clearable
            prefix-icon="Search"
            @keyup.enter="handleSearch"
            class="big-search-input"
          >
            <template #append>
              <el-button type="primary" class="search-action-btn" @click="handleSearch">
                搜索职位
              </el-button>
            </template>
          </el-input>
        </div>

        <!-- Filter Pills Matrix -->
        <div class="filter-pills-row">
          <div class="pill-group">
            <span class="group-label">城市：</span>
            <div class="pill-items">
              <span
                v-for="c in cityOptions"
                :key="c"
                :class="['filter-pill', { active: filters.city === c }]"
                @click="setFilter('city', c)"
              >
                {{ c }}
              </span>
            </div>
          </div>

          <div class="pill-group">
            <span class="group-label">学历：</span>
            <div class="pill-items">
              <span
                v-for="edu in educationOptions"
                :key="edu"
                :class="['filter-pill', { active: filters.education === edu }]"
                @click="setFilter('education', edu)"
              >
                {{ edu }}
              </span>
            </div>
          </div>

          <div class="pill-group">
            <span class="group-label">经验：</span>
            <div class="pill-items">
              <span
                v-for="exp in experienceOptions"
                :key="exp"
                :class="['filter-pill', { active: filters.experience === exp }]"
                @click="setFilter('experience', exp)"
              >
                {{ exp }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Body: 2 Columns (Left Categories, Right Horizontal Job List) -->
      <div class="market-main-grid">
        <!-- Left Column: Category Navigation -->
        <aside class="category-sidebar zh-card">
          <h3 class="category-sidebar-title">
            <el-icon><Menu /></el-icon>
            岗位类别分类
          </h3>
          <ul class="category-list">
            <li
              v-for="cat in categoryOptions"
              :key="cat"
              :class="['category-item', { active: filters.category === cat }]"
              @click="setFilter('category', cat)"
            >
              <span class="cat-name">{{ cat }}</span>
              <el-icon class="cat-arrow"><ArrowRight /></el-icon>
            </li>
          </ul>

          <div class="sidebar-tip-box">
            <div class="tip-badge">AI 智能匹配</div>
            <p class="tip-text">完善在线简历，即可由 AI 算法秒级计算所有岗位的胜任力匹配度与技能差距。</p>
            <router-link to="/personal/resumes">
              <el-button link type="primary" size="small">去完善简历 →</el-button>
            </router-link>
          </div>
        </aside>

        <!-- Right Column: Horizontal Job List Items -->
        <main class="jobs-column">
          <!-- Sort & Count Bar -->
          <div class="jobs-toolbar zh-card">
            <div class="sort-tabs">
              <span
                :class="['sort-tab', { active: filters.sort === 'latest' }]"
                @click="setSort('latest')"
              >
                最新发布
              </span>
              <span
                :class="['sort-tab', { active: filters.sort === 'salary' }]"
                @click="setSort('salary')"
              >
                薪资最高
              </span>
              <span
                v-if="authStore.isPersonal"
                :class="['sort-tab', { active: filters.sort === 'match' }]"
                @click="setSort('match')"
              >
                能力匹配最高
              </span>
            </div>

            <div class="toolbar-right">
              <span class="total-badge">共找到 <strong>{{ total }}</strong> 个真实在招岗位</span>
              <el-button v-if="hasActiveFilter" link type="primary" size="small" @click="resetFilters">
                清空筛选
              </el-button>
            </div>
          </div>

          <!-- 4-State Container -->
          <StateContainer
            :loading="loading"
            :empty="!loading && jobs.length === 0"
            empty-text="未找到匹配的岗位，您可以尝试调整筛选条件或搜索其他关键词"
            empty-action-text="查看全部在招职位"
            @empty-action="resetFilters"
          >
            <div class="horizontal-job-list">
              <div
                v-for="job in jobs"
                :key="job.id"
                class="job-row-item zh-card zh-card-hover"
                @click="$router.push(`/jobs/${job.id}`)"
              >
                <div class="job-row-left">
                  <!-- Company Logo & Basic Meta -->
                  <div class="company-logo-wrap">
                    <img v-if="job.company_logo" :src="job.company_logo" class="comp-logo-img" alt="logo" />
                    <div v-else class="comp-logo-fallback">
                      {{ (job.company_name || '智')[0] }}
                    </div>
                  </div>

                  <div class="job-text-meta">
                    <div class="job-primary-line">
                      <h2 class="job-item-title">{{ job.title }}</h2>
                      <span class="job-item-salary">{{ job.salary_min }}-{{ job.salary_max }}K</span>
                    </div>

                    <div class="job-company-line">
                      <span class="comp-name">{{ job.company_name }}</span>
                      <el-tag size="small" type="success" effect="light" class="auth-tag">名企官方认证</el-tag>
                    </div>

                    <div class="job-requirements-line">
                      <span>{{ job.city }}</span>
                      <span class="line-dot">·</span>
                      <span>{{ job.education }}</span>
                      <span class="line-dot">·</span>
                      <span>{{ job.experience }}</span>
                      <span class="line-dot">·</span>
                      <span>{{ job.type }}</span>
                    </div>

                    <!-- Skills Tags -->
                    <div class="job-skills-row">
                      <el-tag
                        v-for="(s, idx) in (job.skills || []).slice(0, 5)"
                        :key="idx"
                        size="small"
                        effect="plain"
                        class="skill-badge"
                      >
                        {{ s.skill_name }}
                      </el-tag>
                    </div>
                  </div>
                </div>

                <!-- Right Action & Date -->
                <div class="job-row-right">
                  <div class="post-date-row">
                    <span class="post-date">发布于 {{ formatTime(job.created_at) }}</span>
                  </div>

                  <div class="actions-row" @click.stop>
                    <el-button
                      :icon="job.is_favorited ? 'StarFilled' : 'Star'"
                      :type="job.is_favorited ? 'warning' : 'default'"
                      circle
                      size="default"
                      title="收藏职位"
                      @click="toggleFav(job)"
                    />
                    <router-link :to="`/jobs/${job.id}`">
                      <el-button type="primary" size="default" class="view-detail-btn">
                        查看详情
                      </el-button>
                    </router-link>
                  </div>
                </div>
              </div>
            </div>

            <!-- Pagination -->
            <div v-if="total > pageSize" class="pagination-wrapper">
              <el-pagination
                v-model:current-page="page"
                :page-size="pageSize"
                :total="total"
                layout="prev, pager, next, jumper"
                @current-change="handlePageChange"
              />
            </div>
          </StateContainer>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { jobApi } from '@/api'
import type { JobItem } from '@/types'
import StateContainer from '@/components/StateContainer.vue'
import { ElMessage } from 'element-plus'
import { Menu, ArrowRight } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const jobs = ref<JobItem[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)

const cityOptions = ['全部', '深圳', '北京', '上海', '杭州', '广州', '长沙']
const categoryOptions = [
  '全部', '后端开发', '前端开发', '人工智能', '质量保障', '大数据', '系统底层', '运维架构', '信息安全', '产品规划', '全栈研发'
]
const educationOptions = ['全部', '本科及以上', '本科', '硕士及以上', '大专及以上']
const experienceOptions = ['全部', '在校生', '应届生/1-3年', '1-3年', '3-5年']

const filters = reactive({
  keyword: (route.query.keyword as string) || '',
  city: '全部',
  category: '全部',
  education: '全部',
  experience: '全部',
  sort: 'latest'
})

const hasActiveFilter = computed(() => {
  return filters.city !== '全部' || filters.category !== '全部' ||
    filters.education !== '全部' || filters.experience !== '全部' || filters.keyword !== ''
})

const setFilter = (key: 'city' | 'category' | 'education' | 'experience', val: string) => {
  filters[key] = val
  page.value = 1
  fetchJobs()
}

const setSort = (sortVal: string) => {
  filters.sort = sortVal
  page.value = 1
  fetchJobs()
}

const handleSearch = () => {
  page.value = 1
  fetchJobs()
}

const resetFilters = () => {
  filters.keyword = ''
  filters.city = '全部'
  filters.category = '全部'
  filters.education = '全部'
  filters.experience = '全部'
  filters.sort = 'latest'
  page.value = 1
  fetchJobs()
}

const handlePageChange = (newPage: number) => {
  page.value = newPage
  fetchJobs()
  window.scrollTo({ top: 120, behavior: 'smooth' })
}

const formatTime = (timeStr?: string) => {
  if (!timeStr) return '近期'
  try {
    return timeStr.split('T')[0]
  } catch {
    return '近期'
  }
}

const toggleFav = async (job: JobItem) => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning('请先登录求职者账号后再收藏职位')
    router.push('/login')
    return
  }
  try {
    if (job.is_favorited) {
      await jobApi.unfavoriteJob(job.id)
      job.is_favorited = false
      ElMessage.success('已取消收藏')
    } else {
      await jobApi.favoriteJob(job.id)
      job.is_favorited = true
      ElMessage.success('岗位收藏成功')
    }
  } catch (err: any) {
    ElMessage.error(err.message || '操作失败')
  }
}

const fetchJobs = async () => {
  loading.value = true
  try {
    const params: any = {
      page: page.value,
      page_size: pageSize.value
    }
    if (filters.keyword.trim()) params.keyword = filters.keyword.trim()
    if (filters.city !== '全部') params.city = filters.city
    if (filters.category !== '全部') params.category = filters.category
    if (filters.education !== '全部') params.education = filters.education
    if (filters.experience !== '全部') params.experience = filters.experience
    if (filters.sort) params.sort = filters.sort

    const res: any = await jobApi.listJobs(params)
    if (res && res.data) {
      jobs.value = res.data.items || []
      total.value = res.data.total || 0
    } else if (res && res.items) {
      jobs.value = res.items || []
      total.value = res.total || 0
    }
  } catch (err: any) {
    ElMessage.error(err.message || '获取职位列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchJobs()
})
</script>

<style scoped>
.job-square-page {
  min-height: calc(100vh - 64px);
  background-color: var(--zh-bg);
}

.square-title-row {
  margin-bottom: 24px;
}

.page-main-title {
  font-size: 28px;
  font-weight: 800;
  color: var(--zh-text-title);
  letter-spacing: -0.02em;
  margin-bottom: 6px;
}

.page-subtitle {
  font-size: 14px;
  color: var(--zh-text-muted);
}

/* Search Box & Filters Matrix */
.search-section {
  padding: 24px 28px;
  margin-bottom: 28px;
}

.search-input-wrapper {
  margin-bottom: 20px;
}

.search-action-btn {
  height: 44px;
  padding: 0 28px !important;
  font-size: 15px !important;
  font-weight: 600 !important;
}

.filter-pills-row {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-top: 8px;
  border-top: 1px solid var(--zh-border-light);
}

.pill-group {
  display: flex;
  align-items: center;
}

.group-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--zh-text-muted);
  width: 56px;
  flex-shrink: 0;
}

.pill-items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-pill {
  font-size: 13px;
  color: var(--zh-text-body);
  padding: 4px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.filter-pill:hover {
  color: var(--zh-primary);
  background: var(--zh-primary-light);
}

.filter-pill.active {
  background: var(--zh-primary);
  color: #FFFFFF;
  font-weight: 600;
}

/* 2-Column Main Market Grid */
.market-main-grid {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 24px;
  align-items: start;
}

/* Left Category Sidebar */
.category-sidebar {
  padding: 20px 16px;
  position: sticky;
  top: 88px;
}

.category-sidebar-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--zh-text-title);
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--zh-border-light);
}

.category-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.category-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 14px;
  color: var(--zh-text-body);
  cursor: pointer;
  transition: all 0.15s ease;
}

.category-item:hover {
  background-color: var(--zh-primary-light);
  color: var(--zh-primary);
}

.category-item.active {
  background-color: var(--zh-primary-light);
  color: var(--zh-primary);
  font-weight: 600;
}

.cat-arrow {
  font-size: 12px;
  color: var(--zh-text-light);
}

.sidebar-tip-box {
  margin-top: 24px;
  padding: 14px;
  background: var(--zh-sub-bg);
  border-radius: 8px;
  border: 1px dashed var(--zh-border);
}

.tip-badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  color: var(--zh-primary);
  background: #FFFFFF;
  padding: 2px 6px;
  border-radius: 4px;
  margin-bottom: 6px;
  border: 1px solid #BFDBFE;
}

.tip-text {
  font-size: 12px;
  color: var(--zh-text-muted);
  line-height: 1.5;
  margin-bottom: 8px;
}

/* Right Jobs Column */
.jobs-toolbar {
  padding: 14px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.sort-tabs {
  display: flex;
  gap: 18px;
}

.sort-tab {
  font-size: 14px;
  color: var(--zh-text-muted);
  cursor: pointer;
  padding-bottom: 2px;
  transition: color 0.15s;
}

.sort-tab:hover, .sort-tab.active {
  color: var(--zh-primary);
  font-weight: 600;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.total-badge {
  font-size: 13px;
  color: var(--zh-text-muted);
}
.total-badge strong {
  color: var(--zh-text-title);
}

/* Horizontal Job List */
.horizontal-job-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.job-row-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  cursor: pointer;
}

.job-row-left {
  display: flex;
  align-items: flex-start;
  gap: 18px;
  flex: 1;
}

.company-logo-wrap {
  width: 52px;
  height: 52px;
  border-radius: 10px;
  background: var(--zh-sub-bg);
  border: 1px solid var(--zh-border);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
}

.comp-logo-img {
  width: 36px;
  height: 36px;
  object-fit: contain;
}

.comp-logo-fallback {
  font-size: 20px;
  font-weight: 700;
  color: var(--zh-primary);
}

.job-text-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.job-primary-line {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.job-item-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--zh-text-title);
  margin: 0;
}

.job-item-salary {
  font-size: 17px;
  font-weight: 800;
  color: #F97316;
}

.job-company-line {
  display: flex;
  align-items: center;
  gap: 8px;
}

.comp-name {
  font-size: 13px;
  color: var(--zh-text-body);
}

.auth-tag {
  font-size: 11px;
}

.job-requirements-line {
  font-size: 12.5px;
  color: var(--zh-text-muted);
  display: flex;
  align-items: center;
  gap: 6px;
}

.line-dot {
  color: #CBD5E1;
}

.job-skills-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 4px;
}

.skill-badge {
  font-size: 11.5px;
  border-radius: 4px;
}

/* Right Action Section */
.job-row-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 14px;
  flex-shrink: 0;
  margin-left: 20px;
}

.post-date {
  font-size: 12px;
  color: var(--zh-text-light);
}

.actions-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.view-detail-btn {
  padding: 0 16px !important;
  font-size: 13.5px !important;
  font-weight: 600 !important;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

@media (max-width: 1024px) {
  .market-main-grid {
    grid-template-columns: 1fr;
  }
  .category-sidebar {
    display: none;
  }
}
</style>
