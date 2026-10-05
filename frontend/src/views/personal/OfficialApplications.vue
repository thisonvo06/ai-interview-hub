<template>
  <div class="official-applications">
    <section class="tracking-hero">
      <div>
        <span class="eyebrow">CAREER JOURNEY / 求职进度</span>
        <h1>每一次投递，都有迹可循</h1>
        <p>前往企业官网完成投递，在这里整理进度与下一步行动。</p>
      </div>
      <router-link to="/jobs" class="explore-link">发现适合的岗位 ↗</router-link>
    </section>
    <div class="metric-grid">
      <div><span>已记录的官网入口</span><strong>{{ records.length }}</strong></div>
      <div><span>确认已投递</span><strong>{{ submittedCount }}</strong></div>
      <div><span>面试进行中</span><strong>{{ records.filter(r => r.status === 'INTERVIEWING').length }}</strong></div>
      <div><span>收到 Offer</span><strong>{{ records.filter(r => r.status === 'OFFER').length }}</strong></div>
    </div>
    <el-tabs v-model="channel">
      <el-tab-pane label="官网投递笔记" name="official" />
      <el-tab-pane label="历史平台申请" name="legacy" />
    </el-tabs>
    <LegacyApplications v-if="channel === 'legacy'" />
    <template v-else>
      <div class="filter-row">
        <el-radio-group v-model="filter">
          <el-radio-button value="ALL">全部</el-radio-button>
          <el-radio-button v-for="(label, status) in statusLabels" :key="status" :value="status">{{ label }}</el-radio-button>
        </el-radio-group>
      </div>
      <StateContainer :loading="loading" :error="error" :empty="!loading && !visibleRecords.length" empty-text="还没有官网投递笔记，探索岗位并打开招聘官网即可开始记录" @retry="load">
        <div class="record-list">
          <article v-for="record in visibleRecords" :key="record.id" class="record-card">
            <div class="record-heading">
              <div class="company-mark">{{ record.company_name.slice(0, 1) }}</div>
              <div class="record-title">
                <router-link :to="`/jobs/${record.job_id}`"><h3>{{ record.job_title }}</h3></router-link>
                <span>{{ record.company_name }} · 官网渠道</span>
              </div>
              <el-tag :type="record.status === 'OFFER' ? 'success' : record.status === 'LINK_OPENED' ? 'info' : 'primary'">{{ statusLabels[record.status] }}</el-tag>
            </div>
            <p class="record-note">{{ record.note || (record.status === 'LINK_OPENED' ? '已打开招聘官网。完成官网提交后，请在这里确认已投递。' : '进度由你手动记录，可以添加面试时间和下一步安排。') }}</p>
            <div class="record-footer">
              <span>{{ formatDate(record.updated_at) }} 更新 · 用户手动记录</span>
              <div class="record-actions">
                <a :href="record.official_apply_url" target="_blank" rel="noopener noreferrer">再次打开官网 ↗</a>
                <el-button :loading="planningId === record.id" :disabled="planningId !== null" @click="plan(record)">制定求职计划</el-button>
                <el-button @click="showHistory(record)">时间线</el-button>
                <el-button type="primary" plain @click="edit(record)">{{ record.status === 'LINK_OPENED' ? '确认投递 / 更新进度' : '更新进度' }}</el-button>
              </div>
            </div>
          </article>
        </div>
      </StateContainer>
      <p class="tracking-caption">官网访问不会发送简历。状态为个人笔记，请根据企业官网或 HR 的实际反馈更新。</p>
    </template>
    <el-dialog v-model="editing" title="更新官网投递进度" width="min(520px, 92vw)">
      <el-form label-position="top">
        <el-form-item label="我确认当前进度">
          <el-select v-model="form.status" style="width: 100%"><el-option v-for="(label, status) in statusLabels" :key="status" :label="label" :value="status" /></el-select>
        </el-form-item>
        <el-form-item label="备注与下一步安排"><el-input v-model="form.note" type="textarea" :rows="4" maxlength="1000" show-word-limit placeholder="例如：周五 14:00 技术面试，提前复习项目架构" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="editing = false">取消</el-button><el-button type="primary" :loading="saving" @click="save">保存记录</el-button></template>
    </el-dialog>
    <el-dialog v-model="historyVisible" title="我的投递时间线" width="min(520px, 92vw)">
      <el-timeline><el-timeline-item v-for="(entry, index) in selected?.status_history || []" :key="index" :timestamp="formatDate(entry.created_at)">
        <strong>{{ statusLabels[entry.to_status] }}</strong><p>{{ entry.note }}</p>
      </el-timeline-item></el-timeline>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { applicationApi } from '@/api'
import { jobSearchApi } from '@/api/jobSearch'
import type { ExternalApplicationItem } from '@/types'
import StateContainer from '@/components/StateContainer.vue'
import LegacyApplications from './LegacyApplications.vue'

const records = ref<ExternalApplicationItem[]>([])
const router = useRouter()
const planningId = ref<number | null>(null)
const loading = ref(true), error = ref(false), saving = ref(false)
const channel = ref('official'), filter = ref('ALL'), editing = ref(false), historyVisible = ref(false)
const selected = ref<ExternalApplicationItem | null>(null)
const form = reactive({ status: 'USER_SUBMITTED', note: '' })
const statusLabels: Record<string, string> = { LINK_OPENED: '已打开官网', USER_SUBMITTED: '官网已投递', INTERVIEWING: '面试中', OFFER: '收到 Offer', REJECTED: '未通过', CLOSED: '已结束跟进' }
const visibleRecords = computed(() => records.value.filter(r => filter.value === 'ALL' || r.status === filter.value))
const submittedCount = computed(() => records.value.filter(r => ['USER_SUBMITTED', 'INTERVIEWING', 'OFFER', 'REJECTED'].includes(r.status)).length)
const formatDate = (date: string) => new Date(date.endsWith('Z') ? date : `${date}Z`).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
const load = async () => {
  loading.value = true; error.value = false
  try { records.value = await applicationApi.listExternal() } catch { error.value = true } finally { loading.value = false }
}
const edit = (record: ExternalApplicationItem) => {
  selected.value = record
  form.status = record.status === 'LINK_OPENED' ? 'USER_SUBMITTED' : record.status
  form.note = record.note || ''; editing.value = true
}
const showHistory = (record: ExternalApplicationItem) => { selected.value = record; historyVisible.value = true }
const plan = async (record: ExternalApplicationItem) => {
  if (planningId.value !== null) return
  planningId.value = record.id
  try {
    const result = await jobSearchApi.savePlatformJob(record.job_id)
    await router.push({ path: '/personal/job-search', query: { opportunity_id: result.item.id } })
  } catch { /* API 客户端已显示错误，保留笔记供重试。 */ }
  finally { planningId.value = null }
}
const save = async () => {
  if (!selected.value) return
  saving.value = true
  try { await applicationApi.updateExternal(selected.value.id, form); editing.value = false; ElMessage.success('个人投递进度已更新'); await load() }
  finally { saving.value = false }
}
onMounted(load)
</script>

<style scoped>
.official-applications { max-width: 1160px; margin: 0 auto; }
.tracking-hero { display: flex; justify-content: space-between; align-items: center; gap: 24px; padding: 36px; border: 1px solid #d6e8e4; border-radius: 20px; background: linear-gradient(115deg, #f0f8f6, #f6f9fd); }
.eyebrow { font-size: 11px; font-weight: 700; letter-spacing: 2px; color: #408277; }
.tracking-hero h1 { font-size: 28px; font-weight: 700; letter-spacing: -.6px; color: #193b39; margin: 14px 0; }
.tracking-hero p { color: #647873; font-size: 14px; line-height: 1.8; margin: 0; }
.explore-link { flex-shrink: 0; border-radius: 10px; padding: 13px 18px; color: #fff; background: #18796e; text-decoration: none; }
.metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 22px 0; }
.metric-grid > div { border: 1px solid #e2e9e8; border-radius: 14px; padding: 20px; background: white; }
.metric-grid span { display: block; font-size: 12px; color: #788580; }
.metric-grid strong { display: block; font-size: 30px; margin-top: 10px; color: #244d47; font-weight: 650; }
.filter-row { margin: 10px 0 24px; overflow-x: auto; }
.record-list { display: grid; gap: 16px; }
.record-card { padding: 24px; border: 1px solid #e1e9e6; background: white; border-radius: 16px; }
.record-heading { display: flex; align-items: center; gap: 14px; }
.company-mark { width: 46px; height: 46px; background: #edf5f3; border-radius: 12px; display: grid; place-items: center; font-size: 20px; font-weight: 700; color: #3e786d; flex-shrink: 0; }
.record-title { flex: 1; min-width: 0; }
.record-title a { color: #24443e; text-decoration: none; }
.record-title h3 { font-size: 17px; margin: 0 0 7px; line-height: 1.5; }
.record-title span, .record-footer > span { font-size: 12px; color: #84908b; }
.record-note { background: #f6f9f8; color: #596c65; padding: 14px 16px; border-radius: 9px; margin: 20px 0; font-size: 13px; line-height: 1.8; white-space: pre-wrap; overflow-wrap: anywhere; }
.record-footer, .record-actions { display: flex; align-items: center; justify-content: space-between; gap: 14px; flex-wrap: wrap; }
.record-actions a { color: #18796e; font-size: 13px; text-decoration: none; }
.tracking-caption { color: #7d8d87; font-size: 12px; margin: 24px 0; line-height: 1.8; }
@media (max-width: 760px) { .tracking-hero { flex-direction: column; align-items: flex-start; padding: 24px; } .tracking-hero h1 { font-size: 24px; } .metric-grid { grid-template-columns: repeat(2, 1fr); gap: 10px; } .record-card { padding: 18px; } .record-heading { flex-wrap: wrap; } .record-actions { gap: 10px; } }
</style>
