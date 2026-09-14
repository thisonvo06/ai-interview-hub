<template>
  <div class="applications-page">
    <div class="header-box zh-card">
      <div class="header-content">
        <div>
          <h2 class="title">我的求职申请与投递追踪</h2>
          <p class="subtitle">与企业招聘端实时双向同步，追踪简历初筛、面试邀请与 Offer 进展</p>
        </div>
        <router-link to="/jobs">
          <el-button type="primary">探索更多职位 →</el-button>
        </router-link>
      </div>

      <!-- Filter Tabs per Spec U03 -->
      <div class="tabs-row">
        <el-tabs v-model="currentStatus" @tab-change="handleTabChange">
          <el-tab-pane label="全部投递" name="ALL" />
          <el-tab-pane label="已投递" name="SUBMITTED" />
          <el-tab-pane label="企业已查看" name="VIEWED" />
          <el-tab-pane label="AI初筛中" name="AI_SCREENING" />
          <el-tab-pane label="待AI面试" name="AI_INTERVIEW_PENDING" />
          <el-tab-pane label="企业面试中" name="ENTERPRISE_INTERVIEW" />
          <el-tab-pane label="已发Offer/录用" name="OFFER_HIRED" />
          <el-tab-pane label="未通过" name="REJECTED" />
          <el-tab-pane label="已撤回" name="WITHDRAWN" />
        </el-tabs>
      </div>
    </div>

    <!-- Applications List -->
    <StateContainer :loading="loading" :empty="!loading && applications.length === 0" empty-text="当前分类下暂无求职申请记录">
      <div class="apps-list">
        <div
          v-for="app in applications"
          :key="app.id"
          class="app-card zh-card"
        >
          <div class="card-main-col">
            <div class="title-row">
              <h3 class="job-title" @click="$router.push(`/jobs/${app.job_id}`)">
                {{ app.job_title }}
              </h3>
              <el-tag size="default" :type="getStatusTag(app.status)">
                {{ getStatusText(app.status) }}
              </el-tag>
            </div>

            <div class="company-row">
              <span class="company-name">{{ app.company_name }}</span>
              <span class="meta-item">投递时间：{{ app.created_at ? app.created_at.substring(0, 16) : '' }}</span>
              <span class="meta-item">最近更新：{{ app.updated_at ? app.updated_at.substring(0, 16) : '' }}</span>
            </div>

            <!-- Dynamic notice banner based on stage -->
            <div v-if="app.status === 'AI_INTERVIEW_PENDING'" class="stage-alert alert-warning">
              <el-icon><Bell /></el-icon>
              <span>【面试邀请】企业已向您发送 AI 模拟面试筛选邀请，请点击右侧按钮进入作答。</span>
            </div>
            <div v-else-if="app.status === 'OFFER' || app.status === 'HIRED'" class="stage-alert alert-success">
              <el-icon><Check /></el-icon>
              <span>【喜报】恭喜您已收到录用意向，HR 将尽快与您联系签订三方协议或入职。</span>
            </div>
            <div v-else-if="app.reject_reason" class="stage-alert alert-info">
              <span>反馈信息：{{ app.reject_reason }}</span>
            </div>
          </div>

          <div class="card-action-col">
            <!-- If AI Interview Pending -->
            <div v-if="app.status === 'AI_INTERVIEW_PENDING'" class="action-btn-group">
              <router-link :to="`/personal/interviews/create?jobId=${app.job_id}&appId=${app.id}`">
                <el-button type="primary">进入 AI 面试仓</el-button>
              </router-link>
            </div>

            <el-button link type="primary" @click="viewTimeline(app)">
              查看流程时间线
            </el-button>

            <!-- Withdraw option (disabled if HIRED) -->
            <el-button
              v-if="!['HIRED', 'REJECTED', 'WITHDRAWN'].includes(app.status)"
              link
              type="danger"
              @click="openWithdrawModal(app)"
            >
              撤回申请
            </el-button>
          </div>
        </div>
      </div>
    </StateContainer>

    <!-- Timeline Drawer -->
    <el-drawer v-model="drawerVisible" title="招聘推进完整流转记录" size="440px">
      <div v-if="selectedApp" class="timeline-box">
        <h4 class="drawer-app-title">{{ selectedApp.job_title }} · {{ selectedApp.company_name }}</h4>
        <div class="timeline-container">
          <el-timeline>
            <el-timeline-item
              v-for="(h, idx) in selectedApp.status_history"
              :key="idx"
              :timestamp="h.created_at ? h.created_at.substring(0, 16) : ''"
              :type="idx === selectedApp.status_history.length - 1 ? 'primary' : 'info'"
            >
              <h4>{{ getStatusText(h.to_status) }}</h4>
              <p class="history-note">{{ h.note || '状态变迁' }}</p>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </el-drawer>

    <!-- Withdraw Dialog -->
    <el-dialog v-model="withdrawDialogVisible" title="撤回求职申请确认" width="460px">
      <p style="font-size: 13px; color: #64748B; margin-bottom: 16px;">
        撤回后，企业将收到撤回通知并不再推进当前阶段。若后续需要仍可在岗位重新开放时再次申请。
      </p>
      <el-form label-position="top">
        <el-form-item label="撤回原因类别" required>
          <el-select v-model="withdrawReason" placeholder="请选择原因" style="width: 100%;">
            <el-option label="已接受其他心仪 Offer" value="已接受其他心仪 Offer" />
            <el-option label="薪资待遇/工作地点不合适" value="薪资待遇/工作地点不合适" />
            <el-option label="个人职业规划变动" value="个人职业规划变动" />
            <el-option label="误操作/重投其他岗位" value="误操作/重投其他岗位" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="withdrawDialogVisible = false">取消</el-button>
        <el-button type="danger" :loading="withdrawing" @click="handleConfirmWithdraw">确认撤回</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { applicationApi } from '@/api'
import StateContainer from '@/components/StateContainer.vue'
import { ElMessage } from 'element-plus'
import { Bell, Check } from '@element-plus/icons-vue'
import type { ApplicationItem } from '@/types'

const loading = ref(true)
const applications = ref<ApplicationItem[]>([])
const currentStatus = ref('ALL')

const drawerVisible = ref(false)
const selectedApp = ref<ApplicationItem | null>(null)

const withdrawDialogVisible = ref(false)
const appToWithdraw = ref<ApplicationItem | null>(null)
const withdrawReason = ref('已接受其他心仪 Offer')
const withdrawing = ref(false)

const loadApplications = async () => {
  loading.value = true
  try {
    let st: any = currentStatus.value
    if (st === 'ALL') st = undefined
    if (st === 'OFFER_HIRED') st = 'OFFER'

    const res: any = await applicationApi.listApplications(st ? { status: st } : {})
    applications.value = res || []
  } catch (e) {
    // handled
  } finally {
    loading.value = false
  }
}

const handleTabChange = () => {
  loadApplications()
}

const viewTimeline = (app: ApplicationItem) => {
  selectedApp.value = app
  drawerVisible.value = true
}

const openWithdrawModal = (app: ApplicationItem) => {
  appToWithdraw.value = app
  withdrawDialogVisible.value = true
}

const handleConfirmWithdraw = async () => {
  if (!appToWithdraw.value) return
  withdrawing.value = true
  try {
    await applicationApi.withdrawApplication(appToWithdraw.value.id, { reason: withdrawReason.value })
    ElMessage.success('投递已成功撤回')
    withdrawDialogVisible.value = false
    loadApplications()
  } catch (e) {
    // handled
  } finally {
    withdrawing.value = false
  }
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    SUBMITTED: '已投递',
    VIEWED: '企业已查看',
    AI_SCREENING: 'AI评估中',
    AI_INTERVIEW_PENDING: '待AI面试',
    AI_INTERVIEW_DONE: 'AI面试完成',
    ENTERPRISE_INTERVIEW: '企业面试中',
    OFFER: '已发Offer',
    HIRED: '已录用',
    REJECTED: '未通过',
    WITHDRAWN: '已撤回'
  }
  return map[status] || status
}

const getStatusTag = (status: string): any => {
  if (['HIRED', 'OFFER'].includes(status)) return 'success'
  if (['REJECTED', 'WITHDRAWN'].includes(status)) return 'info'
  if (['AI_INTERVIEW_PENDING', 'ENTERPRISE_INTERVIEW'].includes(status)) return 'warning'
  return 'primary'
}

onMounted(() => {
  loadApplications()
})
</script>

<style scoped>
.applications-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.header-box {
  padding: 24px 32px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
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

.apps-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.app-card {
  padding: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-main-col {
  flex: 1;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.job-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--zh-text-title);
  cursor: pointer;
}
.job-title:hover {
  color: var(--zh-primary);
}

.company-row {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 13px;
  color: var(--zh-text-muted);
}

.company-name {
  color: var(--zh-text-body);
  font-weight: 600;
}

.stage-alert {
  margin-top: 14px;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.alert-warning {
  background: #FFFBEB;
  color: #D97706;
  border: 1px solid #FDE68A;
}

.alert-success {
  background: #ECFDF5;
  color: #059669;
  border: 1px solid #A7F3D0;
}

.alert-info {
  background: #F1F5F9;
  color: #475569;
}

.card-action-col {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
  margin-left: 24px;
}

.action-btn-group {
  margin-bottom: 4px;
}

.drawer-app-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 24px;
}

.history-note {
  font-size: 12px;
  color: var(--zh-text-muted);
  margin-top: 4px;
}
</style>
