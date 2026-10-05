<template>
  <div class="candidate-detail-page">
    <StateContainer :loading="loading" :error="error" @retry="fetchDetail">
      <div v-if="cand" class="detail-container">
        <!-- 头部全貌卡片 -->
        <div class="header-card">
          <div class="cand-main-info">
            <div class="cand-avatar">
              {{ snapshot.candidate_name?.charAt(0) || '候' }}
            </div>
            <div>
              <div class="cand-name-row">
                <span class="cand-name">{{ snapshot.candidate_name || '姓名未记录' }}</span>
                <el-tag :type="getStatusTag(cand.status)" size="small">
                  {{ getStatusLabel(cand.status) }}
                </el-tag>
                <span class="job-tag">应聘: {{ cand.job_title }}</span>
              </div>
              <div class="cand-sub-meta">
                <span>{{ snapshot.school || '学校未记录' }}</span><span class="dot">•</span>
                <span>{{ snapshot.education || '学历未记录' }}</span><span class="dot">•</span>
                <span>{{ snapshot.major || '专业未记录' }}</span>
              </div>
            </div>
          </div>

          <div class="cand-match-box">
            <div class="match-score-num" :style="{ color: getScoreColor(cand.match_score || 0) }">
              {{ cand.match_score ?? '—' }}
            </div>
            <div class="match-score-label">简历技能覆盖率</div>
          </div>

          <div class="header-actions">
            <el-button type="primary" :disabled="!nextStatuses.length" @click="openAdvanceDialog">
              <el-icon style="margin-right: 4px;"><Promotion /></el-icon> 推进阶段
            </el-button>
            <el-button type="success" plain @click="openInviteDialog">
              <el-icon style="margin-right: 4px;"><Calendar /></el-icon> 发起面试邀请
            </el-button>
            <el-button @click="handleAddToTalentPool">
              <el-icon style="margin-right: 4px;"><CollectionTag /></el-icon> 存入人才库
            </el-button>
          </div>
        </div>

        <!-- 标签栏 -->
        <div class="tags-bar">
          <span style="font-size: 13px; color: #64748B; margin-right: 8px;">候选人标签:</span>
          <el-tag
            v-for="(t, idx) in cand.tags || []"
            :key="idx"
            size="small"
            type="info"
            style="margin-right: 6px;"
          >
            {{ t.tag_name || t }}
          </el-tag>
          <el-button type="primary" link size="small" @click="openAddTagDialog">+ 添加标签</el-button>
        </div>

        <!-- 详细内容选项卡 -->
        <el-tabs v-model="activeTab" class="detail-tabs">
          <el-tab-pane label="投递时的简历快照" name="resume">
            <p class="exp-desc">此页仅展示历史平台申请时保存的内容。官网渠道笔记不会进入企业候选人库。</p>
            <div v-for="(items, section) in snapshotSections" :key="section" class="tab-content-card">
              <h4 class="section-title">{{ section }}</h4>
              <div v-for="(item, idx) in items" :key="idx" class="exp-item" style="margin-bottom:12px">
                <div class="exp-title">{{ item.school || item.name || item.company }}</div>
                <div class="exp-sub">{{ [item.degree, item.major, item.role, item.title, item.start_date, item.end_date].filter(Boolean).join(' · ') }}</div>
                <p class="exp-desc">{{ item.description || item.technologies || '' }}</p>
              </div>
              <el-empty v-if="!items.length" description="该快照未保存此项" :image-size="50" />
            </div>
            <h4 class="section-title">已记录技能</h4>
            <el-tag v-for="(skill, idx) in snapshot.skills || []" :key="idx" style="margin:0 8px 8px 0">{{ skill.skill_name || skill.name || skill }}</el-tag>
            <el-empty v-if="!snapshot.skills?.length" description="该快照未保存技能" :image-size="50" />
          </el-tab-pane>
          <el-tab-pane label="匹配与团队评估" name="ai_eval">
            <div class="tab-content-card">
              <div class="eval-banner">
                <div class="eval-score-box"><div class="eval-num">{{ cand.match_score ?? '—' }}</div><div class="eval-txt">简历技能覆盖率</div></div>
                <div class="summary-p">按投递快照中的技能与岗位要求计算覆盖率，供人工评估参考。缺少技能记录时不生成分数。</div>
              </div>
              <h4 class="section-title" style="margin-top:24px">团队评价</h4>
              <p v-if="cand.recruiter_evaluation" class="exp-desc">{{ cand.recruiter_evaluation.summary }}</p>
              <el-empty v-else description="暂无团队评价" :image-size="60" />
            </div>
          </el-tab-pane>

          <!-- 面试记录与评估 -->
          <el-tab-pane label="面试记录与团队评分" name="interviews">
            <div class="tab-content-card">
              <div v-if="cand.interview_report" class="interview-record-item">
                <div class="exp-title">企业面试 · {{ cand.interview_report.score }} 分</div>
                <p class="exp-desc">{{ cand.interview_report.summary }}</p>
                <el-button type="primary" link @click="$router.push(`/personal/interviews/${cand.interview_report.interview_id}/report`)">查看授权报告</el-button>
              </div>
              <el-empty v-else description="暂无已生成的授权面试报告" />
            </div>
          </el-tab-pane>

          <!-- 流程流转记录 -->
          <el-tab-pane label="流转记录与操作日志" name="timeline">
            <div class="tab-content-card">
              <el-timeline>
                <el-timeline-item
                  v-for="(rec, idx) in (cand.timeline || [])"
                  :key="idx"
                  :timestamp="formatDate(rec.created_at)"
                  placement="top"
                >
                  <div style="font-weight: 600; color: #1E293B;">
                    阶段流转: {{ getStatusLabel(rec.to_status || rec.status) }}
                  </div>
                  <div style="font-size: 13px; color: #64748B; margin-top: 4px;">
                    {{ rec.note || '未记录备注' }}
                  </div>
                </el-timeline-item>
              </el-timeline>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </StateContainer>

    <!-- 推进阶段弹窗 -->
    <el-dialog v-model="showAdvanceDialog" title="推进候选人阶段" width="500px">
      <el-form label-position="top">
        <el-form-item label="流转目标阶段">
          <el-select v-model="advanceForm.to_status" style="width: 100%;">
            <el-option v-for="status in nextStatuses" :key="status" :label="getStatusLabel(status)" :value="status" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="advanceForm.to_status === 'REJECTED'" label="淘汰原因说明">
          <el-select v-model="advanceForm.reject_reason" placeholder="选择未通过原因" style="width: 100%;">
            <el-option label="专业技术与岗位要求差距较大" value="专业技术不符" />
            <el-option label="项目实战与独立解决问题经验不足" value="经验不符" />
            <el-option label="薪资期望超出预算上限" value="薪资不匹配" />
            <el-option label="综合素质与企业文化不匹配" value="文化契合度" />
          </el-select>
        </el-form-item>
        <el-form-item label="流转备注 / 评语">
          <el-input v-model="advanceForm.note" type="textarea" :rows="3" placeholder="填写阶段推进评语..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdvanceDialog = false">取消</el-button>
        <el-button type="primary" :loading="advancing" @click="handleConfirmAdvance">确认推进</el-button>
      </template>
    </el-dialog>

    <!-- 发起面试邀请弹窗 -->
    <el-dialog v-model="showInviteDialog" title="发起面试邀请" width="540px">
      <el-form :model="inviteForm" label-position="top">
        <el-form-item label="面试类型">
          <el-radio-group v-model="inviteForm.session_type">
            <el-radio label="AI_MOCK">AI 智能初筛面试 (即时自主完成)</el-radio>
            <el-radio label="ENTERPRISE_RECRUITMENT">企业真人结构化面试 (视频会议)</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="约定面试时间">
          <el-date-picker
            v-model="inviteForm.scheduled_at"
            type="datetime"
            placeholder="选择面试日期与时间"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="面试地点 / 会议链接">
          <el-input v-model="inviteForm.location" placeholder="例如：腾讯会议 ID 123-456-789 或 经纬职引-智面仓在线协同室" />
        </el-form-item>
        <el-form-item label="给候选人的附言通知">
          <el-input v-model="inviteForm.note" type="textarea" :rows="3" placeholder="附言说明..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showInviteDialog = false">取消</el-button>
        <el-button type="primary" :loading="inviting" @click="handleConfirmInvite">发送面试邀请</el-button>
      </template>
    </el-dialog>

    <!-- 打标签弹窗 -->
    <el-dialog v-model="showTagDialog" title="添加标签" width="400px">
      <el-form label-position="top">
        <el-form-item label="标签名称">
          <el-input v-model="newTagName" placeholder="如：985硕士、技术极客" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTagDialog = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmAddTag">确认添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Promotion, Calendar, CollectionTag } from '@element-plus/icons-vue'
import StateContainer from '@/components/StateContainer.vue'
import { enterpriseApi } from '@/api'
import { ElMessage } from 'element-plus'

const route = useRoute()
const loading = ref(false)
const error = ref('')
const cand = ref<any>(null)
const activeTab = ref('resume')

const snapshot = computed(() => cand.value?.resume_snapshot || {})
const snapshotSections = computed(() => ({
  '教育经历': snapshot.value.educations || snapshot.value.education_experiences || [],
  '项目经历': snapshot.value.projects || [],
  '工作经历': snapshot.value.work_experiences || []
}))

const fetchDetail = async () => {
  loading.value = true
  error.value = ''
  try {
    const res: any = await enterpriseApi.getCandidate(Number(route.params.id))
    cand.value = res || null
  } catch (err: any) {
    error.value = err.response?.data?.detail || '获取候选人档案失败'
  } finally {
    loading.value = false
  }
}

const nextStatuses = computed(() => ({
  SUBMITTED: ['VIEWED', 'AI_SCREENING', 'REJECTED'], VIEWED: ['AI_SCREENING', 'REJECTED'],
  AI_SCREENING: ['AI_INTERVIEW_PENDING', 'REJECTED'], AI_INTERVIEW_PENDING: ['AI_INTERVIEW_DONE', 'ENTERPRISE_INTERVIEW', 'REJECTED'],
  AI_INTERVIEW_DONE: ['ENTERPRISE_INTERVIEW', 'OFFER', 'REJECTED'], ENTERPRISE_INTERVIEW: ['OFFER', 'REJECTED'], OFFER: ['HIRED', 'REJECTED']
} as Record<string, string[]>)[cand.value?.status] || [])

// 推进阶段
const showAdvanceDialog = ref(false)
const advancing = ref(false)
const advanceForm = reactive({
  to_status: 'ENTERPRISE_INTERVIEW',
  reject_reason: '',
  note: ''
})

const openAdvanceDialog = () => {
  advanceForm.to_status = nextStatuses.value[0] || ''
  advanceForm.reject_reason = ''
  advanceForm.note = ''
  showAdvanceDialog.value = true
}

const handleConfirmAdvance = async () => {
  advancing.value = true
  try {
    await enterpriseApi.advanceCandidate(cand.value.id, {
      to_status: advanceForm.to_status,
      reject_reason: advanceForm.to_status === 'REJECTED' ? advanceForm.reject_reason : undefined,
      note: advanceForm.note
    })
    ElMessage.success('流转成功')
    showAdvanceDialog.value = false
    fetchDetail()
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '流转失败')
  } finally {
    advancing.value = false
  }
}

// 发起面试邀请
const showInviteDialog = ref(false)
const inviting = ref(false)
const inviteForm = reactive({
  session_type: 'ENTERPRISE_RECRUITMENT',
  scheduled_at: new Date(Date.now() + 86400000 * 2),
  location: '经纬职引-智面仓实时视频协同会议室',
  note: '请准时出席本次线上面试。'
})

const openInviteDialog = () => {
  showInviteDialog.value = true
}

const handleConfirmInvite = async () => {
  inviting.value = true
  try {
    await enterpriseApi.sendInvitation({
      application_id: cand.value.id,
      session_type: inviteForm.session_type,
      scheduled_at: inviteForm.scheduled_at.toISOString(),
      location: inviteForm.location,
      note: inviteForm.note
    })
    ElMessage.success('面试邀请已成功发送')
    showInviteDialog.value = false
    fetchDetail()
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '发送面试邀请失败')
  } finally {
    inviting.value = false
  }
}

// 人才库
const handleAddToTalentPool = async () => {
  try {
    await enterpriseApi.addToTalentPool(cand.value.id)
    ElMessage.success('已加入企业人才库')
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '操作失败')
  }
}

// 打标签
const showTagDialog = ref(false)
const newTagName = ref('')

const openAddTagDialog = () => {
  newTagName.value = ''
  showTagDialog.value = true
}

const handleConfirmAddTag = async () => {
  if (!newTagName.value.trim()) return
  try {
    await enterpriseApi.addTag(cand.value.id, newTagName.value.trim())
    ElMessage.success('标签已添加')
    showTagDialog.value = false
    fetchDetail()
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '添加标签失败')
  }
}

const getScoreColor = (score: number) => {
  if (score >= 80) return '#10B981'
  if (score >= 60) return '#F59E0B'
  return '#EF4444'
}

const getStatusTag = (s: string) => {
  switch (s) {
    case 'SUBMITTED': return 'info'
    case 'AI_SCREENING': return 'primary'
    case 'AI_INTERVIEW_PENDING': return 'warning'
    case 'AI_INTERVIEW_DONE': return 'warning'
    case 'ENTERPRISE_INTERVIEW': return 'warning'
    case 'OFFER': return 'success'
    case 'HIRED': return 'success'
    case 'REJECTED': return 'danger'
    default: return ''
  }
}

const getStatusLabel = (s: string) => {
  switch (s) {
    case 'SUBMITTED': return '新投递'
    case 'AI_SCREENING': return 'AI初筛'
    case 'AI_INTERVIEW_PENDING': return '待模拟面试'
    case 'AI_INTERVIEW_DONE': return 'AI面试完成'
    case 'ENTERPRISE_INTERVIEW': return '企业面试'
    case 'OFFER': return '录用意向'
    case 'HIRED': return '已入职'
    case 'REJECTED': return '未通过'
    default: return s || '未知'
  }
}

const formatDate = (val: string) => {
  if (!val) return '-'
  return new Date(val).toLocaleString('zh-CN', { hour12: false })
}

onMounted(() => {
  fetchDetail()
})
</script>

<style scoped>
.candidate-detail-page {
  max-width: 1300px;
  margin: 0 auto;
}

.header-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #F1F5F9;
  margin-bottom: 16px;
}

.cand-main-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.cand-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #EFF6FF;
  color: #2563EB;
  font-size: 22px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cand-name-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.cand-name {
  font-size: 20px;
  font-weight: 700;
  color: #0F2347;
}

.job-tag {
  font-size: 13px;
  color: #64748B;
  background: #F1F5F9;
  padding: 2px 8px;
  border-radius: 4px;
}

.cand-sub-meta {
  font-size: 13px;
  color: #64748B;
  display: flex;
  align-items: center;
  gap: 6px;
}

.dot {
  color: #CBD5E1;
}

.cand-match-box {
  text-align: center;
  padding: 0 24px;
  border-left: 1px solid #F1F5F9;
  border-right: 1px solid #F1F5F9;
}

.match-score-num {
  font-size: 32px;
  font-weight: 800;
  line-height: 1.1;
}

.match-score-label {
  font-size: 12px;
  color: #64748B;
  margin-top: 4px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.tags-bar {
  background: #FFFFFF;
  border-radius: 8px;
  padding: 12px 20px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  border: 1px solid #F1F5F9;
}

.detail-tabs {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 20px 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #F1F5F9;
}

.tab-content-card {
  padding: 12px 0;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1E293B;
  margin: 0 0 12px 0;
}

.exp-item {
  background: #F8FAFC;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #E2E8F0;
}

.exp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.exp-title {
  font-size: 15px;
  font-weight: 600;
  color: #1E293B;
}

.exp-time {
  font-size: 12px;
  color: #64748B;
}

.exp-sub {
  font-size: 13px;
  color: #475569;
  margin-bottom: 6px;
}

.exp-desc {
  font-size: 13px;
  color: #475569;
  margin: 0;
  line-height: 1.6;
}

.eval-banner {
  display: flex;
  gap: 20px;
  background: #F0FDF4;
  border: 1px solid #BBF7D0;
  border-radius: 8px;
  padding: 20px;
  align-items: center;
}

.eval-score-box {
  text-align: center;
  min-width: 90px;
}

.eval-num {
  font-size: 32px;
  font-weight: 800;
  color: #16A34A;
}

.eval-txt {
  font-size: 12px;
  color: #15803D;
}

.summary-title {
  font-size: 16px;
  font-weight: 700;
  color: #166534;
  margin-bottom: 4px;
}

.summary-p {
  font-size: 13px;
  color: #15803D;
  line-height: 1.6;
}

.highlights-box, .questions-box {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.hl-item {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #334155;
}

.text-emerald {
  color: #10B981;
}

.q-item {
  background: #F8FAFC;
  padding: 12px 16px;
  border-radius: 6px;
  border-left: 3px solid #2563EB;
  font-size: 13px;
  color: #334155;
}

.interview-record-item {
  background: #F8FAFC;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #E2E8F0;
  margin-bottom: 12px;
}

.iv-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.iv-type {
  font-weight: 600;
  color: #1E293B;
  margin-right: 12px;
}

.iv-time {
  font-size: 12px;
  color: #64748B;
}

.iv-report-summary {
  margin-top: 10px;
  padding: 10px;
  background: #FFFFFF;
  border-radius: 6px;
}
</style>
