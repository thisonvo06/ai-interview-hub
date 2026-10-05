<template>
  <div class="search-journal">
    <header class="journal-hero">
      <div>
        <p class="eyebrow">THE OPPORTUNITY NOTEBOOK / 求职手记</p>
        <h1>把好机会，<br />一步步变成下一站。</h1>
        <p class="hero-copy">收藏岗位要求，找到准备方向，再把每一次进展记下来。</p>
      </div>
      <div class="hero-aside">
        <span class="volume">PLAN · PREPARE · PROGRESS</span>
        <button class="primary-button" @click="createVisible = true">＋ 收集一个岗位</button>
        <router-link to="/personal/applications">查看官网投递笔记 ↗</router-link>
        <p>岗位计划与官网笔记分开记录。<br />投递与跟进需要你在企业渠道完成。</p>
      </div>
    </header>

    <div v-if="loadError" class="feedback-panel" role="alert">求职计划加载失败。<button @click="load">重新加载 →</button></div>
    <div v-if="loading && !collection" class="loading-note" role="status">正在翻开你的求职手记…</div>
    <template v-if="collection">
      <section class="journal-metrics" aria-label="求职计划统计">
        <div v-for="metric in metrics" :key="metric.label"><span>{{ metric.label }}</span><strong>{{ metric.value }}</strong><small>{{ metric.caption }}</small></div>
      </section>
      <div class="journal-grid">
        <section class="opportunity-directory" aria-labelledby="directory-title">
          <div class="section-heading"><div><p class="eyebrow">01 / YOUR SHORTLIST</p><h2 id="directory-title">机会目录</h2></div><span>{{ filteredItems.length }} 个岗位</span></div>
          <div class="directory-filters">
            <el-input v-model="search" placeholder="搜索岗位、企业或技能" clearable aria-label="搜索求职计划" />
            <el-select v-model="statusFilter" aria-label="按求职状态筛选"><el-option label="全部阶段" value="ALL" /><el-option v-for="(label, status) in statusLabels" :key="status" :label="label" :value="status" /></el-select>
          </div>
          <div v-if="!filteredItems.length" class="empty-note"><span class="empty-mark">↗</span><h3>{{ collection.items.length ? '这里暂时没有符合条件的岗位' : '从一个值得准备的机会开始' }}</h3><p>粘贴职位描述，或从岗位详情页加入计划。</p><button @click="collection.items.length ? resetFilters() : (createVisible = true)">{{ collection.items.length ? '清除筛选' : '收集岗位' }} →</button></div>
          <button v-for="(item, index) in filteredItems" :key="item.id" class="directory-row" @click="openItem(item)">
            <span class="row-number">{{ String(index + 1).padStart(2, '0') }}</span>
            <span class="row-main"><span class="row-company">{{ item.company_name }}<template v-if="item.location"> · {{ item.location }}</template></span><strong>{{ item.title }}</strong><span class="row-skills">{{ item.required_skills.length ? item.required_skills.join(' / ') : '待补充岗位技能' }}</span></span>
            <span class="row-meta"><span class="status-label">{{ statusLabels[item.status] }}</span><span v-if="item.analysis?.skill_coverage != null">技能覆盖 {{ item.analysis.skill_coverage }}%</span><span v-if="item.deadline_state === 'EXPIRED'" class="warning-text">已过截止日</span><span v-else-if="item.deadline_state === 'CLOSING_SOON'" class="warning-text">即将截止 {{ formatDate(item.deadline) }}</span><span v-else-if="item.follow_up_due" class="warning-text">待跟进</span><span v-else>{{ formatDate(item.updated_at) }} 更新</span></span>
            <span class="row-arrow" aria-hidden="true">↗</span>
          </button>
        </section>

        <aside class="journal-sidebar">
          <section class="margin-card"><p class="eyebrow">02 / KEEP THE RHYTHM</p><h2>接下来，做什么</h2><div class="reminder-counts"><span><strong>{{ collection.summary.closing_soon }}</strong> 即将截止</span><span><strong>{{ collection.summary.due_follow_ups }}</strong> 待跟进</span></div><p v-if="!attentionItems.length" class="muted">暂时没有到期事项。给心仪岗位记下截止日与下一次跟进日。</p><button v-for="item in attentionItems" :key="item.id" class="margin-entry" @click="openItem(item)"><strong>{{ item.title }}</strong><span>{{ item.company_name }}</span><small>{{ item.follow_up_due ? '跟进日已到' : '截止 ' + formatDate(item.deadline) }} →</small></button></section>
          <section class="margin-card"><p class="eyebrow">03 / LEARN WITH PURPOSE</p><h2>值得补上的技能</h2><p class="muted">来自已分析岗位的技能缺口频次，帮助你安排练习。</p><p v-if="!collection.gaps.length" class="muted">分析岗位与简历后，在这里查看共同缺口。</p><div v-for="gap in collection.gaps" :key="gap.skill" class="gap-row"><div><strong>{{ gap.skill }}</strong><span>{{ gap.count }} 个岗位</span></div><p>{{ gap.suggested_action }}</p></div><router-link to="/personal/learning" class="text-link">进入学习路线 →</router-link></section>
          <div class="journal-footnote">计划里的状态由你手动确认。技能分析采用规则比对，不能代替企业筛选结果。</div>
        </aside>
      </div>
    </template>

    <el-dialog v-model="createVisible" title="收集一个岗位" width="min(720px, calc(100vw - 24px))" class="journal-dialog" :close-on-click-modal="false">
      <p class="dialog-intro">把官网或其他渠道的职位要求粘贴进来，开始制定准备计划。</p>
      <el-form label-position="top" @submit.prevent="createOpportunity">
        <div class="form-pair"><el-form-item label="岗位名称 *"><el-input v-model="newItem.title" maxlength="150" /></el-form-item><el-form-item label="企业名称 *"><el-input v-model="newItem.company_name" maxlength="150" /></el-form-item></div>
        <div class="form-pair"><el-form-item label="工作地点"><el-input v-model="newItem.location" maxlength="120" /></el-form-item><el-form-item label="薪资说明"><el-input v-model="newItem.salary_note" maxlength="150" placeholder="按原岗位描述填写，可留空" /></el-form-item></div>
        <el-form-item label="来源链接"><el-input v-model="newItem.source_url" placeholder="https://…（可选）" maxlength="2000" /><small class="field-help">只保存链接，不会抓取网站，也不会替你发送简历。请使用公开的 HTTPS 地址。</small></el-form-item>
        <el-form-item label="职位描述 JD *"><el-input v-model="newItem.jd_text" type="textarea" :rows="7" maxlength="20000" show-word-limit placeholder="粘贴职责、任职要求、加分项等原文" /></el-form-item>
        <el-form-item label="岗位要求技能"><el-input v-model="skillInput" placeholder="例如：Python，SQL，数据分析（逗号分隔）" maxlength="2000" /><div v-if="parsedSkills.length" class="skill-tags"><el-tag v-for="skill in parsedSkills" :key="skill" effect="plain">{{ skill }}</el-tag></div><small class="field-help">请按职位要求人工补充技能；缺少要求时，技能覆盖率会显示为未知。</small></el-form-item>
        <div class="form-pair"><el-form-item label="要求经验年数"><el-input-number v-model="newItem.experience_years" :min="0" :max="60" :precision="0" placeholder="未说明可留空" controls-position="right" /></el-form-item><el-form-item label="申请截止日"><el-date-picker v-model="newItem.deadline" type="date" value-format="YYYY-MM-DD" placeholder="未说明可留空" /></el-form-item></div>
      </el-form>
      <template #footer><el-button @click="createVisible = false">取消</el-button><el-button type="primary" :loading="creating" @click="createOpportunity">加入计划</el-button></template>
    </el-dialog>

    <el-drawer v-model="detailVisible" size="min(940px, 100vw)" class="opportunity-drawer" :with-header="false" :close-on-click-modal="false" :before-close="beforeCloseDetail">
      <div v-if="selected" class="detail-journal">
        <div class="detail-topline"><span class="eyebrow">OPPORTUNITY / {{ String(selected.id).padStart(3, '0') }}</span><button aria-label="关闭岗位详情" :disabled="!!working" @click="requestCloseDetail">关闭 ×</button></div>
        <p class="detail-company">{{ selected.company_name }}<template v-if="selected.location"> · {{ selected.location }}</template></p><h2 class="detail-title">{{ selected.title }}</h2>
        <div class="detail-meta"><span>{{ statusLabels[selected.status] }}</span><span v-if="selected.salary_note">{{ selected.salary_note }}</span><span>截止 {{ formatDate(selected.deadline) }}</span><a v-if="safeSource(selected.source_url)" :href="safeSource(selected.source_url)" target="_blank" rel="noopener noreferrer">打开来源 ↗</a></div>
        <p class="detail-disclaimer">来源信息请以企业发布为准。此计划不会替你投递、发送邮件或修改原简历。</p>
        <el-tabs v-model="detailTab" class="journal-tabs">
          <el-tab-pane label="岗位与匹配" name="analysis">
            <section class="detail-section"><h3>岗位原文</h3><p class="jd-text">{{ selected.jd_text }}</p><div class="skill-tags"><el-tag v-for="skill in selected.required_skills" :key="skill" effect="plain">{{ skill }}</el-tag></div></section>
            <section class="detail-section"><div class="section-heading"><h3>带着证据，决定怎么准备</h3><span class="rule-label">规则分析</span></div><p class="muted">按简历中记录的技能与岗位要求比对，未知条件会保留为未知。</p><div class="resume-action"><el-select v-model="resumeId" clearable placeholder="默认 / 最近一份简历" aria-label="选择自己的简历" :loading="resumesLoading"><el-option v-for="resume in resumes" :key="resume.id" :label="resume.name" :value="resume.id" /></el-select><el-button type="primary" :loading="working === 'analyze'" :disabled="!!working" @click="analyze">分析这个岗位</el-button></div><p v-if="resumeError" class="warning-text">简历列表加载失败。<button class="text-button" @click="loadResumes">重新加载</button></p><p v-else-if="!resumesLoading && !resumes.length" class="muted">还没有简历。可以先查看未知条件，或<router-link to="/personal/resumes">完善简历 →</router-link></p>
              <div v-if="selected.analysis" class="analysis-panel"><div class="analysis-summary"><strong>{{ selected.analysis.skill_coverage == null ? '待补充' : selected.analysis.skill_coverage + '%' }}</strong><div><span>技能覆盖率 · {{ selected.analysis.resume_title || '未选择可用简历' }}</span><p>{{ selected.analysis.explanation }}</p><small>{{ recommendations[selected.analysis.recommendation] }} · {{ formatDate(selected.analysis.analyzed_at) }} 分析</small></div></div><div class="analysis-skills"><div><h4>已匹配</h4><p>{{ selected.analysis.matched_skills.join(' / ') || '暂无可核实交集' }}</p></div><div><h4>待补充</h4><p>{{ selected.analysis.skill_coverage == null ? '素材不足，暂时无法确定技能缺口' : selected.analysis.missing_skills.join(' / ') || '暂无已识别缺口' }}</p></div></div><div v-for="check in selected.analysis.checks" :key="check.name" class="check-row"><span :class="['verdict', 'verdict-' + check.verdict.toLowerCase()]">{{ verdictLabels[check.verdict] }}</span><div><strong>{{ check.name }}</strong><p>{{ check.detail }}</p></div></div><h4 v-if="selected.analysis.evidence.length" class="evidence-heading">简历中的依据</h4><blockquote v-for="(evidence, index) in selected.analysis.evidence" :key="index"><strong>{{ evidence.skill }}</strong><p>{{ evidence.text }}</p><small>{{ evidence.source === 'RESUME_SKILL' ? '简历技能栏' : evidence.source === 'RESUME_PROJECT' ? '简历项目经历' : evidence.source }}</small></blockquote></div>
              <p v-else class="muted">尚未分析。选择简历后，先看交集与缺口，再决定准备顺序。</p>
            </section>
          </el-tab-pane>
          <el-tab-pane label="准备材料" name="prep">
            <section class="detail-section"><div class="section-heading"><h3>准备好下一次表达</h3><span class="rule-label">规则草稿 · 需本人核实</span></div><p class="muted">材料基于岗位要求和简历已有内容组织，待补充信息需你填写。生成不会修改原简历。</p><div class="resume-action"><el-select v-model="resumeId" clearable placeholder="默认 / 最近一份简历" aria-label="准备材料所用简历"><el-option v-for="resume in resumes" :key="resume.id" :label="resume.name" :value="resume.id" /></el-select><el-button type="primary" :loading="working === 'prepare'" :disabled="!!working" @click="prepare">{{ selected.prep ? '重新生成准备包' : '生成准备包' }}</el-button></div></section>
            <template v-if="selected.prep">
              <p class="draft-note">申请信与跟进草稿可在下方编辑。修改仅在当前页面保留，请复制或下载保存；再次生成会覆盖当前草稿。</p>
              <section class="detail-section"><div class="section-heading"><h3>申请信草稿</h3><button class="text-button" @click="copy(coverDraft)">复制 ↗</button></div><el-input v-model="coverDraft" type="textarea" :rows="10" aria-label="编辑申请信草稿" /></section>
              <section class="detail-section"><div class="section-heading"><h3>跟进草稿</h3><button class="text-button" @click="copy(followDraft)">复制 ↗</button></div><el-input v-model="followDraft" type="textarea" :rows="7" aria-label="编辑跟进草稿" /></section>
              <section class="detail-section"><h3>面试问题清单</h3><ol class="preparation-list"><li v-for="(question, index) in selected.prep.interview_questions" :key="index">{{ question }}</li></ol></section>
              <section class="detail-section"><h3>把项目讲成一个故事</h3><p class="muted">STAR 提纲只使用已有材料，缺少内容会标记待补充，避免虚构经历。</p><article v-for="(example, index) in selected.prep.star_examples" :key="index" class="star-example"><h4>{{ example.project_name || '待补充项目名称' }}</h4><dl><template v-for="field in starFields" :key="field.key"><dt>{{ field.label }}</dt><dd>{{ example[field.key] || '待补充：请填写你真实参与的内容' }}</dd></template></dl></article><p v-if="!selected.prep.star_examples.length" class="muted">暂无可用项目。请补充真实项目背景、职责、行动与结果。</p></section>
              <section class="detail-section"><h3>简历表达提示</h3><ul class="preparation-list"><li v-for="(highlight, index) in selected.prep.resume_highlights" :key="index">{{ highlight }}</li></ul><p v-if="!selected.prep.resume_highlights.length" class="muted">补充简历内容后可生成表达提示。</p><h3>提交前，核对一遍</h3><ul class="preparation-list"><li v-for="(task, index) in selected.prep.checklist" :key="index">{{ task }}</li></ul><el-button @click="downloadPrep">下载当前准备包（Markdown）</el-button></section>
            </template><p v-else class="empty-note compact">还没有准备包。生成后可以编辑申请信、查看 STAR 提纲与面试问题。</p>
          </el-tab-pane>
          <el-tab-pane label="进度与复盘" name="progress">
            <section class="detail-section"><h3>记录你已经完成的事</h3><p class="muted">已投递、面试与结果均为你的手动记录；以企业渠道反馈为准。</p><el-form label-position="top"><el-form-item label="当前阶段"><el-select v-model="progress.status"><el-option v-for="(label, status) in statusLabels" :key="status" :label="label" :value="status" /></el-select></el-form-item><div class="form-pair"><el-form-item label="申请截止日"><el-date-picker v-model="progress.deadline" type="date" value-format="YYYY-MM-DD" clearable /></el-form-item><el-form-item label="下次跟进日期"><el-date-picker v-model="progress.next_follow_up" type="date" value-format="YYYY-MM-DD" clearable /></el-form-item></div><el-form-item label="计划备注"><el-input v-model="progress.note" type="textarea" :rows="4" maxlength="2000" placeholder="准备重点、招聘联系人、待完成事项…" /></el-form-item><el-form-item label="反馈与复盘"><el-input v-model="progress.feedback" type="textarea" :rows="4" maxlength="2000" placeholder="记录你收到的真实反馈，以及下一次想改善的地方" /></el-form-item></el-form><el-button type="primary" :loading="working === 'update'" :disabled="!!working" @click="saveProgress">保存进度</el-button></section>
            <section class="detail-section"><h3>跟进记录</h3><p class="muted">已记录 {{ selected.follow_up_count }} / 2 次跟进。只有已自行投递或面试中的岗位可记录跟进。你在企业渠道自行跟进后，确认一次；此按钮不会发送消息。</p><el-button :disabled="!!working || selected.follow_up_count >= 2 || !canFollowUp" :loading="working === 'follow'" @click="confirmFollowUp">我已自行跟进，记录一次</el-button></section>
            <section class="detail-section"><h3>这段机会的进展</h3><ol class="history-list"><li v-for="(event, index) in selected.history" :key="index"><time>{{ formatDate(event.created_at, true) }}</time><strong>{{ event.to_status ? statusLabels[event.to_status] : '更新记录' }}</strong><p v-if="event.note">{{ event.note }}</p></li></ol></section><button class="remove-button" :disabled="!!working" @click="removeOpportunity">删除这个求职计划</button>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { jobSearchApi } from '@/api/jobSearch'
import { resumeApi } from '@/api'
import type { ResumeItem } from '@/types'
import type { Opportunity, OpportunityCollection, OpportunityInput, OpportunityStatus } from '@/types/jobSearch'

const route = useRoute(), router = useRouter()
const collection = ref<OpportunityCollection | null>(null), loading = ref(false), loadError = ref(false)
const search = ref(''), statusFilter = ref('ALL'), createVisible = ref(false), creating = ref(false)
const selected = ref<Opportunity | null>(null), detailVisible = ref(false), detailTab = ref('analysis'), working = ref('')
const resumes = ref<ResumeItem[]>([]), resumesLoading = ref(false), resumeError = ref(false), resumeId = ref<number>()
const coverDraft = ref(''), followDraft = ref(''), skillInput = ref('')
const newItem = ref({ title: '', company_name: '', location: '', salary_note: '', source_url: '', jd_text: '', experience_years: undefined as number | undefined, deadline: '' })
const progress = ref({ status: 'SAVED' as OpportunityStatus, note: '', feedback: '', deadline: null as string | null, next_follow_up: null as string | null })
const statusLabels: Record<OpportunityStatus, string> = { SAVED: '已收集', PREPARING: '准备中', USER_SUBMITTED: '已自行投递', INTERVIEWING: '面试中', OFFER: '收到 Offer', REJECTED: '暂未通过', CLOSED: '已结束' }
const recommendations = { PRIORITIZE: '优先准备', PREPARE: '建议补充准备', REVIEW: '核对条件后再决定', EXPIRED: '已过截止日，请核实是否仍开放' }
const verdictLabels = { PASS: '符合', FAIL: '缺口', UNKNOWN: '未知', FLAG: '待核实' }
const starFields = [{ key: 'situation', label: 'S · 背景' }, { key: 'task', label: 'T · 任务' }, { key: 'action', label: 'A · 行动' }, { key: 'result', label: 'R · 结果' }] as const
const metrics = computed(() => [ { label: '进行中的机会', value: collection.value?.summary.active ?? 0, caption: '持续准备' }, { label: '已自行投递', value: collection.value?.summary.submitted ?? 0, caption: '本人确认' }, { label: '面试中的机会', value: collection.value?.summary.interviewing ?? 0, caption: '准备下一轮' }, { label: '收到的 Offer', value: collection.value?.summary.offers ?? 0, caption: '本人记录' } ])
const parsedSkills = computed(() => [...new Set(skillInput.value.split(/[,，、;；\n]/).map(s => s.trim()).filter(Boolean))])
const filteredItems = computed(() => (collection.value?.items ?? []).filter(item => (statusFilter.value === 'ALL' || item.status === statusFilter.value) && (!search.value.trim() || [item.title, item.company_name, ...item.required_skills].join(' ').toLocaleLowerCase().includes(search.value.trim().toLocaleLowerCase()))))
const attentionItems = computed(() => (collection.value?.items ?? []).filter(item => !['OFFER', 'REJECTED', 'CLOSED'].includes(item.status) && (item.follow_up_due || item.deadline_state === 'CLOSING_SOON')).slice(0, 5))
const canFollowUp = computed(() => selected.value?.status === 'USER_SUBMITTED' || selected.value?.status === 'INTERVIEWING')
const hasDraftEdits = computed(() => !!selected.value?.prep && (coverDraft.value !== selected.value.prep.cover_letter || followDraft.value !== selected.value.prep.follow_up_draft))
const hasProgressEdits = computed(() => !!selected.value && (progress.value.status !== selected.value.status || progress.value.note !== (selected.value.note || '') || progress.value.feedback !== (selected.value.feedback || '') || progress.value.deadline !== (selected.value.deadline || null) || progress.value.next_follow_up !== (selected.value.next_follow_up || null)))
function formatDate(value: string | null | undefined, withTime = false) {
  if (!value) return '未设置'
  const date = new Date(/^\d{4}-\d{2}-\d{2}$/.test(value) ? value + 'T00:00:00' : value)
  return Number.isNaN(date.getTime()) ? '日期待核实' : date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit', ...(withTime ? { hour: '2-digit', minute: '2-digit' } : {}) })
}
function safeSource(value: string | null) {
  if (!value) return undefined
  try { const url = new URL(value); return url.protocol === 'https:' && !url.username && !url.password ? url.href : undefined } catch { return undefined }
}
function resetFilters() { search.value = ''; statusFilter.value = 'ALL' }
async function load() {
  loading.value = true; loadError.value = false
  try { collection.value = await jobSearchApi.list() } catch { loadError.value = true } finally { loading.value = false }
}
async function loadResumes() {
  resumesLoading.value = true; resumeError.value = false
  try { resumes.value = await resumeApi.listResumes() } catch { resumeError.value = true } finally { resumesLoading.value = false }
}
function syncProgress(item: Opportunity) { progress.value = { status: item.status, note: item.note || '', feedback: item.feedback || '', deadline: item.deadline || null, next_follow_up: item.next_follow_up || null } }
function replaceSelected(item: Opportunity) { selected.value = item; syncProgress(item); if (collection.value) collection.value.items = collection.value.items.map(existing => existing.id === item.id ? item : existing) }
function openItem(item: Opportunity) {
  replaceSelected(item); resumeId.value = item.analysis?.resume_id ?? item.prep?.resume_id ?? undefined
  coverDraft.value = item.prep?.cover_letter || ''; followDraft.value = item.prep?.follow_up_draft || ''; detailTab.value = 'analysis'; detailVisible.value = true
  if (!resumes.value.length && !resumesLoading.value) void loadResumes()
}
async function beforeCloseDetail(done: () => void) {
  if (working.value) { ElMessage.info('正在保存，请稍候再关闭'); return }
  if (hasDraftEdits.value || hasProgressEdits.value) {
    try { await ElMessageBox.confirm('当前还有本页编辑的草稿或未保存的进度。草稿请先复制或下载；未保存内容会在重新打开记录时恢复为服务器版本。', '关闭前保留你的修改', { confirmButtonText: '关闭并放弃本页修改', cancelButtonText: '返回继续编辑', type: 'warning' }) } catch { return }
  }
  done()
}
function requestCloseDetail() { void beforeCloseDetail(() => { detailVisible.value = false }) }
async function openFromQuery() {
  const id = Number(route.query.opportunity_id)
  if (!Number.isInteger(id) || id <= 0 || selected.value?.id === id && detailVisible.value) return
  const local = collection.value?.items.find(item => item.id === id)
  try { openItem(local || await jobSearchApi.get(id)) } catch { /* client displays the error */ }
}
async function createOpportunity() {
  if (creating.value) return
  if (!newItem.value.title.trim() || !newItem.value.company_name.trim() || !newItem.value.jd_text.trim()) { ElMessage.warning('请填写岗位名称、企业名称和职位描述'); return }
  if (parsedSkills.value.length > 30 || parsedSkills.value.some(skill => skill.length > 80)) { ElMessage.warning('最多填写 30 项技能，每项不超过 80 个字符'); return }
  if (newItem.value.source_url.trim() && !safeSource(newItem.value.source_url.trim())) { ElMessage.warning('来源链接请使用公开的 HTTPS 地址'); return }
  const data: OpportunityInput = { ...newItem.value, title: newItem.value.title.trim(), company_name: newItem.value.company_name.trim(), jd_text: newItem.value.jd_text.trim(), required_skills: parsedSkills.value, deadline: newItem.value.deadline || undefined, source_url: newItem.value.source_url.trim() || undefined }
  creating.value = true
  try { const result = await jobSearchApi.create(data); createVisible.value = false; ElMessage.success(result.duplicate ? '这个岗位已经在计划中，为你打开原记录' : '已加入求职计划'); newItem.value = { title: '', company_name: '', location: '', salary_note: '', source_url: '', jd_text: '', experience_years: undefined, deadline: '' }; skillInput.value = ''; await load(); openItem(result.item) } catch { /* input remains for correction */ } finally { creating.value = false }
}
async function handleConflict(error: any) {
  if (error?.response?.status === 409 && selected.value) { ElMessage.warning('记录已在其他位置更新，正在读取最新版本。请核对后重新操作。'); try { replaceSelected(await jobSearchApi.get(selected.value.id)); await load() } catch { /* keep current data if reload failed */ } }
}
async function analyze() {
  if (!selected.value || working.value) return
  working.value = 'analyze'
  try { const result = await jobSearchApi.analyze(selected.value.id, resumeId.value); replaceSelected(result.item); await load() } catch (error) { await handleConflict(error) } finally { working.value = '' }
}
async function prepare() {
  if (!selected.value || working.value) return
  if (selected.value.prep && (coverDraft.value !== selected.value.prep.cover_letter || followDraft.value !== selected.value.prep.follow_up_draft)) { try { await ElMessageBox.confirm('重新生成会覆盖你在本页编辑的申请信和跟进草稿。请先复制或下载需要保留的内容。', '重新生成准备包', { confirmButtonText: '确认重新生成', cancelButtonText: '保留当前草稿', type: 'warning' }) } catch { return } }
  working.value = 'prepare'
  try { const result = await jobSearchApi.prepare(selected.value.id, resumeId.value); replaceSelected(result.item); coverDraft.value = result.prep.cover_letter; followDraft.value = result.prep.follow_up_draft; await load() } catch (error) { await handleConflict(error) } finally { working.value = '' }
}
async function saveProgress() {
  if (!selected.value || working.value) return
  working.value = 'update'
  const nextFollowUp = progress.value.next_follow_up || null
  const changes = { version: selected.value.version, status: progress.value.status, note: progress.value.note, feedback: progress.value.feedback, deadline: progress.value.deadline || null, ...(nextFollowUp !== (selected.value.next_follow_up || null) ? { next_follow_up: nextFollowUp } : {}) }
  try { replaceSelected(await jobSearchApi.update(selected.value.id, changes)); ElMessage.success('进度已保存'); await load() } catch (error) { await handleConflict(error) } finally { working.value = '' }
}
async function confirmFollowUp() {
  if (!selected.value || working.value || selected.value.follow_up_count >= 2 || !canFollowUp.value) return
  try { await ElMessageBox.confirm('请仅在你已通过企业官网、招聘联系人或邮件自行完成跟进后确认。这里会增加一次跟进记录，不会替你发送任何消息。', '确认已在企业渠道自行跟进', { confirmButtonText: '我已自行跟进，记录一次', cancelButtonText: '还没有跟进', type: 'warning' }) } catch { return }
  working.value = 'follow'
  try { replaceSelected(await jobSearchApi.followUp(selected.value.id, selected.value.version)); ElMessage.success('已记录本人确认的跟进'); await load() } catch (error) { await handleConflict(error) } finally { working.value = '' }
}
async function removeOpportunity() {
  if (!selected.value || working.value) return
  try { await ElMessageBox.confirm('删除后，此岗位的计划、分析、准备包和进度将被移除。官网投递笔记会继续独立保留。', '删除求职计划', { confirmButtonText: '删除计划', cancelButtonText: '保留', type: 'warning' }) } catch { return }
  working.value = 'remove'
  try { await jobSearchApi.remove(selected.value.id); detailVisible.value = false; selected.value = null; if (route.query.opportunity_id) await router.replace({ query: { ...route.query, opportunity_id: undefined } }); await load(); ElMessage.success('已删除求职计划') } catch { /* client displays the error */ } finally { working.value = '' }
}
async function copy(text: string) {
  try { await navigator.clipboard.writeText(text); ElMessage.success('草稿已复制，请核实后自行使用') } catch { ElMessage.warning('浏览器无法自动复制，请选中草稿文字手动复制') }
}
function downloadPrep() {
  const item = selected.value, prep = item?.prep
  if (!item || !prep) return
  const content = [`# ${item.title} · ${item.company_name}`, '规则准备草稿，需本人核实与补充；不会自动投递或修改原简历。', `生成时间：${formatDate(prep.generated_at, true)}`, '## 申请信草稿', coverDraft.value, '## 跟进草稿', followDraft.value, '## 面试问题', ...prep.interview_questions.map((q, i) => `${i + 1}. ${q}`), '## STAR 项目提纲', ...prep.star_examples.flatMap(example => [`### ${example.project_name || '待补充项目名称'}`, ...starFields.map(field => `- ${field.label}：${example[field.key] || '待补充真实内容'}`)]), '## 简历表达提示', ...prep.resume_highlights.map(text => `- ${text}`), '## 提交前核对', ...prep.checklist.map(text => `- [ ] ${text}`)].join('\n\n')
  const url = URL.createObjectURL(new Blob([content], { type: 'text/markdown;charset=utf-8' })), link = document.createElement('a')
  link.href = url; link.download = `${item.company_name}-${item.title}-准备包.md`.replace(/[<>:"/\\|?*\u0000-\u001f]/g, '_'); document.body.appendChild(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000)
}
watch(() => route.query.opportunity_id, () => { if (collection.value) void openFromQuery() })
onMounted(async () => { await load(); await openFromQuery() })
</script>

<style scoped>
.search-journal { color: #25362f; max-width: 1440px; margin: 0 auto; min-width: 0; }
.journal-hero { display: flex; justify-content: space-between; align-items: flex-end; gap: 36px; padding: 14px 0 34px; border-bottom: 1px solid #d8ded4; }
.eyebrow { color: #748378; font-size: 10px; letter-spacing: 1.7px; font-weight: 600; line-height: 1.7; margin: 0 0 12px; }
.journal-hero h1 { font-family: 'Songti SC', 'SimSun', serif; font-size: clamp(32px, 3.2vw, 50px); line-height: 1.35; font-weight: 500; letter-spacing: -1px; margin: 12px 0 20px; }
.hero-copy { color: #768075; line-height: 1.8; font-size: 13px; margin: 0; }
.hero-aside { max-width: 290px; display: flex; flex-direction: column; gap: 15px; padding-bottom: 3px; }
.volume { font-size: 10px; color: #7a887a; letter-spacing: 1.4px; }
.hero-aside a, .text-link { color: #246657; font-size: 13px; text-decoration: none; }
.hero-aside p { font-size: 11px; line-height: 1.8; color: #7a847b; margin: 0; }
button { font: inherit; cursor: pointer; }
.primary-button { background: #246657; color: #fff; border: 1px solid #246657; padding: 13px 26px; font-size: 13px; border-radius: 3px; }
.primary-button:hover { background: #1e574a; }
.journal-metrics { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); padding: 24px 0 26px; border-bottom: 1px solid #d8ded4; }
.journal-metrics > div { padding: 0 22px; border-right: 1px solid #d8ded4; display: flex; flex-direction: column; gap: 7px; }
.journal-metrics > div:first-child { padding-left: 0; }.journal-metrics > div:last-child { border: 0; }
.journal-metrics span { font-size: 12px; color: #657366; }.journal-metrics strong { font-family: Georgia, 'Times New Roman', serif; font-size: 34px; font-weight: 400; }.journal-metrics small { color: #8b958a; font-size: 10px; }
.journal-grid { display: grid; grid-template-columns: minmax(0, 1fr) 270px; gap: 34px; padding-top: 34px; }
.opportunity-directory, .journal-sidebar { min-width: 0; }
.section-heading { display: flex; align-items: center; justify-content: space-between; gap: 14px; margin-bottom: 20px; flex-wrap: wrap; }.section-heading h2, .margin-card h2 { font-family: 'Songti SC', 'SimSun', serif; font-size: 23px; font-weight: 500; margin: 0; }.section-heading > span { font-size: 11px; color: #8a958a; }.section-heading .eyebrow { margin-bottom: 4px; }
.directory-filters { display: grid; grid-template-columns: minmax(0, 1fr) 145px; gap: 12px; padding-bottom: 17px; border-bottom: 1px solid #d8ded4; }.directory-filters :deep(.el-input__wrapper), .directory-filters :deep(.el-select__wrapper) { background: transparent; }
.directory-row { width: 100%; border: 0; border-bottom: 1px solid #e0e4dc; background: transparent; text-align: left; display: grid; grid-template-columns: 28px minmax(0, 1fr) 115px 12px; gap: 14px; padding: 25px 2px; color: inherit; transition: background .16s; }.directory-row:hover { background: #f0f3eb; }.row-number { font-family: Georgia, serif; color: #9ba797; font-size: 14px; padding-top: 5px; }.row-main { min-width: 0; display: flex; flex-direction: column; gap: 8px; }.row-company { color: #778373; font-size: 11px; }.row-main strong { font-family: 'Songti SC', 'SimSun', serif; font-size: 21px; font-weight: 500; line-height: 1.4; overflow-wrap: anywhere; }.row-skills { font-size: 10px; color: #84907f; line-height: 1.7; overflow-wrap: anywhere; }.row-meta { font-size: 10px; color: #899281; display: flex; flex-direction: column; gap: 8px; text-align: right; line-height: 1.5; padding-top: 4px; }.status-label { color: #246657; }.row-arrow { color: #567b65; padding-top: 8px; }.warning-text { color: #a57642; font-size: 12px; line-height: 1.6; }
.margin-card { padding: 23px 22px; background: #f0f3eb; border-top: 2px solid #94aa91; margin-bottom: 23px; }.margin-card h2 { font-size: 21px; margin-bottom: 15px; }.muted { color: #7c877b; font-size: 12px; line-height: 1.85; }.reminder-counts { display: flex; justify-content: space-between; gap: 10px; font-size: 11px; color: #788773; margin-bottom: 18px; }.reminder-counts strong { font-family: Georgia, serif; color: #395e44; font-weight: 400; font-size: 24px; margin-right: 4px; }.margin-entry { display: flex; flex-direction: column; text-align: left; background: none; border: 0; border-top: 1px solid #d8e0d1; width: 100%; gap: 5px; padding: 14px 0; color: #40593e; overflow-wrap: anywhere; }.margin-entry strong { font-size: 12px; font-weight: 500; }.margin-entry span, .margin-entry small { font-size: 10px; color: #83917a; }.gap-row { padding: 13px 0; border-top: 1px solid #d8e0d1; }.gap-row > div { display: flex; justify-content: space-between; gap: 10px; font-size: 12px; }.gap-row span { color: #85917b; font-size: 10px; }.gap-row p { font-size: 11px; color: #7d8a77; line-height: 1.7; margin-bottom: 0; }.text-link { display: inline-block; margin-top: 16px; }.journal-footnote { font-size: 10px; color: #8b9584; line-height: 1.9; padding: 0 5px; }
.empty-note { text-align: center; padding: 60px 20px; color: #7c887a; }.empty-mark { display: inline-block; font-size: 40px; color: #739271; }.empty-note h3 { font-family: 'Songti SC', 'SimSun', serif; font-size: 23px; font-weight: 500; color: #4f6850; line-height: 1.6; }.empty-note p { font-size: 12px; line-height: 1.8; }.empty-note button, .feedback-panel button, .text-button { border: 0; background: none; color: #246657; font-size: 12px; padding: 5px 0; }.empty-note.compact { font-size: 12px; line-height: 1.8; padding: 40px 20px; }.feedback-panel { background: #fcf4e9; padding: 18px; margin: 20px 0; font-size: 13px; color: #8e633a; }.feedback-panel button { margin-left: 12px; }.loading-note { padding: 65px 10px; color: #7b8777; text-align: center; font-size: 13px; }
.dialog-intro { font-size: 13px; line-height: 1.8; color: #7d8878; margin-top: 0; }.form-pair { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }.field-help { display: block; font-size: 10px; line-height: 1.8; color: #899382; margin-top: 8px; }.skill-tags { display: flex; flex-wrap: wrap; gap: 7px; margin-top: 10px; width: 100%; }.form-pair :deep(.el-date-editor), .form-pair :deep(.el-input-number) { width: 100%; min-width: 0; }
.detail-journal { min-width: 0; color: #354b3a; padding: 0 14px; overflow-wrap: anywhere; }.detail-topline { display: flex; justify-content: space-between; align-items: center; gap: 16px; margin-bottom: 30px; }.detail-topline .eyebrow { margin: 0; }.detail-topline button { border: 0; background: none; font-size: 12px; color: #71826d; padding: 6px; }.detail-company { font-size: 12px; color: #86917e; margin: 0 0 12px; }.detail-title { font-family: 'Songti SC', 'SimSun', serif; font-size: 35px; font-weight: 500; line-height: 1.5; margin: 0 0 18px; }.detail-meta { display: flex; flex-wrap: wrap; gap: 10px 24px; font-size: 11px; line-height: 1.8; color: #7d8b75; }.detail-meta a { color: #246657; text-decoration: none; }.detail-disclaimer { color: #98a08f; font-size: 10px; line-height: 1.8; padding-bottom: 20px; border-bottom: 1px solid #dde3d6; margin: 12px 0 18px; }.detail-section { padding: 10px 0 24px; border-bottom: 1px solid #e1e6db; margin-bottom: 22px; }.detail-section h3 { font-family: 'Songti SC', 'SimSun', serif; font-size: 23px; font-weight: 500; line-height: 1.5; margin: 0 0 18px; }.detail-section .section-heading { margin-bottom: 8px; }.detail-section .section-heading h3 { margin: 0; }.rule-label { font-size: 10px !important; color: #839576 !important; padding: 4px 8px; border: 1px solid #d6dfcc; border-radius: 2px; }.jd-text { white-space: pre-wrap; font-size: 13px; line-height: 2; color: #6e7f66; }.resume-action { display: flex; flex-wrap: wrap; gap: 12px; margin: 20px 0; }.resume-action .el-select { width: 270px; max-width: 100%; }.analysis-panel { margin-top: 26px; }.analysis-summary { display: flex; gap: 25px; background: #f0f3ea; padding: 23px; align-items: center; }.analysis-summary > strong { font-family: Georgia, 'Songti SC', serif; font-size: 38px; color: #476f42; font-weight: 400; white-space: nowrap; }.analysis-summary span { font-size: 11px; color: #759368; }.analysis-summary p { font-size: 12px; line-height: 1.8; color: #6f8664; margin: 8px 0; }.analysis-summary small { font-size: 10px; color: #889b7c; }.analysis-skills { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 30px; padding: 20px 0; }.analysis-skills h4 { font-size: 12px; font-weight: 500; }.analysis-skills p { font-size: 12px; color: #89957e; line-height: 1.7; }.check-row { display: flex; gap: 14px; border-top: 1px solid #e1e6dc; padding: 16px 0; }.check-row strong { font-size: 12px; font-weight: 500; }.check-row p { font-size: 11px; color: #8a957e; line-height: 1.8; margin: 6px 0 0; }.verdict { font-size: 10px; border: 1px solid #dce3d5; padding: 3px 6px; height: fit-content; white-space: nowrap; color: #8e9981; }.verdict-pass { color: #518044; }.verdict-fail, .verdict-flag { color: #ad8555; }.evidence-heading { font-size: 12px; font-weight: 500; margin-top: 22px; }blockquote { border-left: 2px solid #b9c8ac; padding-left: 15px; margin: 20px 0; font-size: 11px; line-height: 1.9; color: #7f9273; }blockquote strong { font-weight: 500; }blockquote p { margin: 6px 0; }blockquote small { color: #9aaa8b; }
.draft-note { padding: 14px 18px; background: #f4f0e6; font-size: 11px; line-height: 1.9; color: #9e8963; }.preparation-list { padding-left: 20px; color: #7a8b6f; font-size: 12px; line-height: 2; }.preparation-list li { padding: 4px 0; }.star-example { padding: 20px; border: 1px solid #e0e6d8; margin: 18px 0; }.star-example h4 { font-size: 14px; font-weight: 500; margin: 0 0 15px; }.star-example dl { display: grid; grid-template-columns: 75px minmax(0, 1fr); gap: 12px; margin: 0; font-size: 12px; line-height: 1.8; }.star-example dt { color: #849873; }.star-example dd { margin: 0; color: #7f8e74; }.history-list { list-style: none; padding: 0 0 0 15px; border-left: 1px solid #cbd8bc; }.history-list li { position: relative; padding: 0 0 25px 8px; font-size: 12px; }.history-list li::before { content: ''; position: absolute; width: 5px; height: 5px; left: -18px; top: 6px; border-radius: 50%; background: #83a165; }.history-list time { display: block; color: #97a38b; font-size: 10px; margin-bottom: 6px; }.history-list strong { font-weight: 500; }.history-list p { color: #8c9b7e; font-size: 11px; line-height: 1.8; }.remove-button { background: none; border: 0; color: #a38974; font-size: 12px; padding: 8px 0 24px; }.journal-tabs :deep(.el-tabs__item) { font-size: 12px; }.detail-journal :deep(.el-form-item__label) { font-size: 12px; color: #708664; }.detail-journal :deep(.el-textarea__inner) { font-size: 12px; line-height: 1.9; }.detail-journal :deep(.el-select) { max-width: 100%; }
button:focus-visible, a:focus-visible { outline: 2px solid #407557; outline-offset: 4px; }
@media (max-width: 1150px) { .journal-grid { grid-template-columns: minmax(0, 1fr) 240px; gap: 22px; }.directory-row { grid-template-columns: 22px minmax(0, 1fr) 100px 10px; gap: 9px; }.row-main strong { font-size: 19px; }.margin-card { padding: 20px 17px; } }
@media (max-width: 900px) { .journal-grid { grid-template-columns: minmax(0, 1fr); }.journal-sidebar { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 20px; }.journal-footnote { grid-column: 1 / -1; }.journal-hero { gap: 24px; }.hero-aside { max-width: 230px; }.journal-metrics > div { padding: 0 14px; } }
@media (max-width: 600px) { .journal-hero { display: block; padding-top: 4px; }.journal-hero h1 { font-size: 34px; margin: 10px 0 16px; }.hero-copy { font-size: 12px; }.hero-aside { margin-top: 25px; max-width: none; display: grid; grid-template-columns: minmax(0, 1fr); gap: 13px; }.hero-aside .volume { display: none; }.hero-aside p { font-size: 10px; }.hero-aside p br { display: none; }.primary-button { width: 100%; }.journal-metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); row-gap: 22px; }.journal-metrics > div { padding: 0 14px; }.journal-metrics > div:nth-child(odd) { padding-left: 0; }.journal-metrics > div:nth-child(even) { border: 0; }.journal-metrics strong { font-size: 30px; }.journal-grid { padding-top: 27px; }.directory-filters { grid-template-columns: minmax(0, 1fr) 125px; gap: 8px; }.directory-row { grid-template-columns: 20px minmax(0, 1fr) 10px; padding: 21px 0; }.row-main strong { font-size: 21px; }.row-meta { grid-column: 2; grid-row: 2; flex-direction: row; flex-wrap: wrap; text-align: left; gap: 12px; padding: 0; }.row-arrow { grid-column: 3; grid-row: 1; }.journal-sidebar { grid-template-columns: minmax(0, 1fr); gap: 0; margin-top: 10px; }.empty-note { padding: 45px 10px; }.empty-note h3 { font-size: 21px; }.form-pair { grid-template-columns: minmax(0, 1fr); gap: 0; }.detail-journal { padding: 0; }.detail-title { font-size: 28px; }.detail-meta { gap: 9px 17px; }.detail-section h3 { font-size: 21px; }.analysis-summary { display: block; padding: 18px; }.analysis-summary > strong { display: block; margin-bottom: 12px; }.analysis-skills { gap: 18px; }.star-example { padding: 17px 13px; }.star-example dl { grid-template-columns: minmax(0, 1fr); gap: 4px; }.star-example dd { margin-bottom: 12px; }.resume-action .el-select { width: 100%; }.resume-action > button { width: 100%; } }
@media (prefers-reduced-motion: reduce) { .directory-row { transition: none; } }
</style>
