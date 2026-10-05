<template>
  <div class="resumes-page">
    <div class="header-box zh-card">
      <div class="header-content">
        <div>
          <h2 class="title">简历管理中枢</h2>
          <p class="subtitle">在线简历与简历原文档分开管理，支持 AI 结构化智能解析与表达优化诊断</p>
        </div>
        <div class="header-actions">
          <template v-if="activeTab === 'online'">
            <el-button :icon="Upload" @click="docFileInput?.click()">上传原文档 (PDF/DOCX)</el-button>
            <el-button type="primary" :icon="Plus" @click="createNewResume">在线新建简历</el-button>
          </template>
          <template v-else>
            <el-button type="primary" :icon="Upload" @click="docFileInput?.click()">上传原文档 (PDF/DOCX)</el-button>
          </template>
        </div>
      </div>
    </div>

    <!-- 隐藏的文档上传入口（两个 Tab 共用） -->
    <input
      ref="docFileInput"
      type="file"
      accept=".pdf,.docx,.doc"
      style="display: none"
      @change="handleDocFileChange"
    />

    <el-tabs v-model="activeTab" class="resume-tabs">
      <!-- ============ 在线简历 ============ -->
      <el-tab-pane label="在线简历" name="online">
        <StateContainer :loading="loading" :empty="!loading && resumes.length === 0" empty-text="尚未创建任何在线简历" empty-action-text="立即新建简历" @empty-action="createNewResume">
          <div class="resumes-grid">
            <div
              v-for="resume in resumes"
              :key="resume.id"
              class="resume-card zh-card zh-card-hover"
            >
              <div class="card-head">
                <div class="title-with-badge">
                  <h3 class="resume-title">{{ resume.name }}</h3>
                  <el-tag v-if="resume.is_default" size="small" type="success" effect="dark">默认投递简历</el-tag>
                </div>
                <span class="completeness">完整度 {{ resume.completeness }}%</span>
              </div>

              <div class="card-body">
                <div class="meta-row">
                  <span class="lbl">更新时间：</span>
                  <span class="val">{{ resume.created_at ? resume.created_at.substring(0, 10) : '' }}</span>
                </div>

                <!-- Content preview -->
                <div class="resume-stats-chips">
                  <span class="chip">{{ resume.educations?.length || 0 }} 段教育</span>
                  <span class="chip">{{ resume.projects?.length || 0 }} 个项目经历</span>
                  <span class="chip">{{ resume.skills?.length || 0 }} 项技术掌握</span>
                </div>
              </div>

              <div class="card-actions">
                <router-link :to="`/personal/resumes/${resume.id}/edit`">
                  <el-button size="small" class="action-btn" :icon="EditPen">结构化编辑</el-button>
                </router-link>

                <router-link :to="`/personal/resumes/${resume.id}/analysis`">
                  <el-button size="small" class="action-btn" :icon="MagicStick">AI诊断优化</el-button>
                </router-link>

                <el-dropdown trigger="click" @command="(cmd: string) => handleMenu(cmd, resume)">
                  <el-button size="small" class="action-btn" :icon="MoreFilled">更多操作</el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item v-if="!resume.is_default" command="set_default">设为默认投递</el-dropdown-item>
                      <el-dropdown-item divided command="delete" style="color: #EF4444;">删除简历</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </div>
        </StateContainer>
      </el-tab-pane>

      <!-- ============ 原文档 ============ -->
      <el-tab-pane label="原文档" name="documents">
        <StateContainer :loading="docLoading" :empty="!docLoading && documents.length === 0" empty-text="尚未上传任何简历原文档" empty-action-text="上传原文档" @empty-action="docFileInput?.click()">
          <div class="doc-split">
            <!-- 左侧：文档列表 -->
            <div class="doc-list">
              <div
                v-for="doc in documents"
                :key="doc.id"
                class="doc-item zh-card"
                :class="{ 'doc-item-active': selectedDocId === doc.id }"
                @click="selectDoc(doc)"
              >
                <div class="doc-item-head">
                  <span class="doc-icon"><el-icon :size="18"><Document /></el-icon></span>
                  <div class="doc-item-meta">
                    <h4 class="doc-title" :title="doc.file_name">{{ doc.file_name }}</h4>
                    <span class="doc-date">{{ doc.created_at ? doc.created_at.substring(0, 10) : '' }}</span>
                  </div>
                </div>
                <div class="doc-item-actions" @click.stop>
                  <el-button
                    size="small"
                    class="action-btn"
                    :icon="MagicStick"
                    :loading="parsingDocId === doc.id"
                    @click="handleDocParse(doc)"
                  >
                    解析为在线简历
                  </el-button>
                  <el-button size="small" class="action-btn-danger" :icon="Delete" @click="handleDocDelete(doc)">删除</el-button>
                </div>
              </div>
            </div>

            <!-- 右侧：内嵌预览区 -->
            <div class="doc-preview zh-card">
              <div class="doc-preview-head">
                <span class="doc-preview-title">{{ selectedDoc ? selectedDoc.file_name : '文档预览' }}</span>
                <el-button v-if="docPreviewUrl" link type="primary" @click="openDocInNewTab">在新窗口打开 ↗</el-button>
              </div>
              <div class="doc-preview-body">
                <iframe
                  v-if="docPreviewUrl && isPdfSelected"
                  :src="docPreviewUrl"
                  class="doc-preview-frame"
                  title="简历文档预览"
                />
                <el-empty
                  v-else-if="selectedDoc && !isPdfSelected"
                  description="DOC/DOCX 暂不支持浏览器内嵌预览，请解析为在线简历或在新窗口尝试打开"
                />
                <el-empty v-else description="选择左侧文档进行预览" />
              </div>
            </div>
          </div>
        </StateContainer>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { resumeApi, resumeDocumentApi, privateFileApi } from '@/api'
import StateContainer from '@/components/StateContainer.vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Plus, EditPen, MagicStick, Document, MoreFilled, Delete } from '@element-plus/icons-vue'
import type { ResumeItem, ResumeDocumentItem } from '@/types'

const router = useRouter()

const activeTab = ref<'online' | 'documents'>('online')

const loading = ref(true)
const resumes = ref<ResumeItem[]>([])

const docLoading = ref(false)
const documents = ref<ResumeDocumentItem[]>([])
const parsingDocId = ref<number | null>(null)
const docFileInput = ref<HTMLInputElement | null>(null)

// 右侧内嵌预览
const selectedDocId = ref<number | null>(null)
const docPreviewUrl = ref('')
const selectedDoc = computed(() => documents.value.find(d => d.id === selectedDocId.value) || null)
const isPdfSelected = computed(() => (selectedDoc.value?.file_name || '').toLowerCase().endsWith('.pdf'))

const revokeDocPreview = () => {
  if (docPreviewUrl.value) { URL.revokeObjectURL(docPreviewUrl.value); docPreviewUrl.value = '' }
}

const loadResumes = async () => {
  loading.value = true
  try {
    const res: any = await resumeApi.listResumes()
    resumes.value = res || []
  } catch (e) {
    // handled
  } finally {
    loading.value = false
  }
}

const loadDocuments = async () => {
  docLoading.value = true
  try {
    const res: any = await resumeDocumentApi.list()
    documents.value = res || []
    // 保持选中项有效：默认选中第一个
    if (documents.value.length === 0) {
      selectedDocId.value = null
      revokeDocPreview()
    } else if (!documents.value.some(d => d.id === selectedDocId.value)) {
      await selectDoc(documents.value[0])
    }
  } catch (e) {
    // handled
  } finally {
    docLoading.value = false
  }
}

const selectDoc = async (doc: ResumeDocumentItem) => {
  if (selectedDocId.value === doc.id && docPreviewUrl.value) return
  selectedDocId.value = doc.id
  revokeDocPreview()
  if (!isPdfSelected.value) return
  try {
    docPreviewUrl.value = await privateFileApi.preview(doc.file_url)
  } catch (e) {
    // handled
  }
}

const openDocInNewTab = () => {
  if (docPreviewUrl.value) window.open(docPreviewUrl.value, '_blank')
}

// ---------- 原文档 Tab ----------

const handleDocFileChange = async (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  input.value = ''

  if (file.size / 1024 / 1024 >= 10) {
    ElMessage.error('简历文件大小不得超过 10MB!')
    return
  }

  const formData = new FormData()
  formData.append('file', file)
  docLoading.value = true
  try {
    const uploadRes: any = await resumeApi.uploadFile(formData)
    const data = uploadRes?.data || uploadRes || {}
    const fileUrl: string = data.file_url || ''
    const fileName: string = data.file_name || file.name
    if (!fileUrl) {
      ElMessage.error('上传失败：未获取到文件地址')
      return
    }
    await resumeDocumentApi.create({ file_url: fileUrl, file_name: fileName })
    ElMessage.success('原文档已保存')
    await loadDocuments()
  } catch (e) {
    // 拦截器已提示具体错误
  } finally {
    docLoading.value = false
  }
}

const handleDocParse = async (doc: ResumeDocumentItem) => {
  parsingDocId.value = doc.id
  try {
    const res: any = await resumeDocumentApi.parse(doc.id)
    ElMessage.success(`已由【${doc.file_name}】生成在线简历「${res?.name}」`)
    activeTab.value = 'online'
    await loadResumes()
  } catch (e) {
    // handled（后端 503 提示会由拦截器展示）
  } finally {
    parsingDocId.value = null
  }
}

const handleDocDelete = async (doc: ResumeDocumentItem) => {
  try {
    await ElMessageBox.confirm(`确定要删除文档【${doc.file_name}】吗？已生成的在线简历不受影响。`, '确认删除', { type: 'warning' })
  } catch {
    return
  }
  try {
    await resumeDocumentApi.remove(doc.id)
    ElMessage.success('文档已删除')
    await loadDocuments()
  } catch (e) {
    // handled
  }
}

// ---------- 在线简历 Tab ----------

const createNewResume = async () => {
  // 不预填任何内容数据，由用户在编辑页自行填写
  const res: any = await resumeApi.createResume({
    is_default: resumes.value.length === 0
  })
  router.push(`/personal/resumes/${res.id}/edit`)
}

const handleMenu = async (cmd: string, resume: ResumeItem) => {
  if (cmd === 'set_default') {
    await resumeApi.updateResume(resume.id, {
      ...resume,
      is_default: true
    })
    ElMessage.success('已设为默认简历')
    loadResumes()
  } else if (cmd === 'delete') {
    ElMessageBox.confirm('确定要删除此简历吗？若已有投递引用，将软删除保留历史快照。', '确认删除', {
      type: 'warning'
    }).then(async () => {
      await resumeApi.deleteResume(resume.id)
      ElMessage.success('简历已删除/归档')
      loadResumes()
    })
  }
}

onMounted(() => {
  loadResumes()
  loadDocuments()
})
onUnmounted(() => { revokeDocPreview() })
</script>

<style scoped>
.resumes-page {
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

.header-actions {
  display: flex;
  gap: 12px;
}

.resume-tabs :deep(.el-tabs__item.is-active) {
  font-weight: 700;
}

.resumes-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.resume-card {
  padding: 24px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.title-with-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.resume-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--zh-text-title);
}

.doc-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: var(--zh-primary-light);
  color: var(--zh-primary);
  flex-shrink: 0;
}

.doc-title {
  font-size: 15px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.completeness {
  font-size: 13px;
  font-weight: 700;
  color: #2563EB;
  background: #EFF6FF;
  padding: 3px 8px;
  border-radius: 4px;
  flex-shrink: 0;
}

.card-body {
  margin-bottom: 20px;
}

.meta-row {
  display: flex;
  font-size: 13px;
  margin-bottom: 6px;
}

.meta-row .lbl { color: var(--zh-text-muted); width: 75px; }
.meta-row .val { color: var(--zh-text-body); font-weight: 500; }

.resume-stats-chips {
  display: flex;
  gap: 8px;
  margin-top: 14px;
}

.chip {
  font-size: 11px;
  background: #F1F5F9;
  color: #475569;
  padding: 3px 8px;
  border-radius: 4px;
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  border-top: 1px solid var(--zh-border-light);
  padding-top: 16px;
  flex-wrap: wrap;
}

/* 卡片操作按钮：统一使用页面深绿主题色，保证文字清晰可读 */
.card-actions .action-btn {
  background: var(--zh-primary-light) !important;
  border-color: #CFE0D8 !important;
  color: var(--zh-primary) !important;
  font-weight: 600 !important;
}
.card-actions .action-btn:hover,
.card-actions .action-btn:focus {
  background: var(--zh-primary) !important;
  border-color: var(--zh-primary) !important;
  color: #FFFFFF !important;
}

.card-actions .action-btn-danger {
  background: #FEF2F2 !important;
  border-color: #FECACA !important;
  color: #B91C1C !important;
  font-weight: 600 !important;
}
.card-actions .action-btn-danger:hover,
.card-actions .action-btn-danger:focus {
  background: #DC2626 !important;
  border-color: #DC2626 !important;
  color: #FFFFFF !important;
}

/* ===== 原文档 Tab：左右分栏 ===== */
.doc-split {
  display: grid;
  grid-template-columns: 340px 1fr;
  gap: 20px;
  align-items: stretch;
  min-height: 60vh;
}

.doc-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 70vh;
  overflow-y: auto;
  padding-right: 4px;
}

.doc-item {
  padding: 16px;
  cursor: pointer;
  border: 1px solid var(--zh-border-light);
  transition: all 0.12s ease;
}
.doc-item:hover {
  border-color: var(--zh-primary);
}
.doc-item-active {
  border-color: var(--zh-primary);
  box-shadow: 0 0 0 2px var(--zh-primary-focus);
  background: var(--zh-primary-lighter);
}

.doc-item-head {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.doc-item-meta {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.doc-item-meta .doc-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--zh-text-title);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.doc-date {
  font-size: 12px;
  color: var(--zh-text-muted);
}

.doc-item-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.doc-preview {
  display: flex;
  flex-direction: column;
  padding: 16px 20px;
  min-height: 60vh;
  border: 1px solid var(--zh-border-light);
}

.doc-preview-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--zh-border-light);
  margin-bottom: 12px;
}

.doc-preview-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--zh-text-title);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.doc-preview-body {
  flex: 1;
  min-height: 0;
  display: flex;
}
.doc-preview-frame {
  width: 100%;
  height: 100%;
  min-height: 55vh;
  border: 1px solid var(--zh-border-light);
  border-radius: 8px;
  background: #fff;
}

@media (max-width: 900px) {
  .resumes-grid { grid-template-columns: 1fr; }
  .doc-split { grid-template-columns: 1fr; }
  .doc-list { max-height: none; }
}
</style>
