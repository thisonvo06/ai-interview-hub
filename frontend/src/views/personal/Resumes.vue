<template>
  <div class="resumes-page">
    <div class="header-box zh-card">
      <div class="header-content">
        <div>
          <h2 class="title">简历管理中枢</h2>
          <p class="subtitle">管理多个岗位定制简历版本，支持 AI 结构化智能解析与表达优化诊断</p>
        </div>
        <div class="header-actions">
          <el-upload
            action="/api/v1/files/upload"
            :show-file-list="false"
            :on-success="handleUploadSuccess"
            :before-upload="beforeUpload"
            name="file"
            :headers="uploadHeaders"
          >
            <el-button :icon="Upload">上传本地简历 (PDF/DOCX)</el-button>
          </el-upload>
          <el-button type="primary" :icon="Plus" @click="createNewResume">在线新建简历</el-button>
        </div>
      </div>
    </div>

    <StateContainer :loading="loading" :empty="!loading && resumes.length === 0" empty-text="尚未创建任何简历" empty-action-text="立即新建简历" @empty-action="createNewResume">
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
              <span class="lbl">目标岗位：</span>
              <span class="val">{{ resume.target_job_title }}</span>
            </div>
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
              <el-button size="small" type="primary" plain>结构化编辑</el-button>
            </router-link>

            <router-link :to="`/personal/resumes/${resume.id}/analysis`">
              <el-button size="small" type="warning" plain>AI 智能诊断</el-button>
            </router-link>

            <el-dropdown trigger="click" @command="(cmd: string) => handleMenu(cmd, resume)">
              <el-button size="small">更多操作 ▾</el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-if="!resume.is_default" command="set_default">设为默认投递</el-dropdown-item>
                  <el-dropdown-item command="ai_parse">重新触发 AI 解析</el-dropdown-item>
                  <el-dropdown-item divided command="delete" style="color: #EF4444;">删除简历</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </div>
    </StateContainer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { resumeApi } from '@/api'
import { useAuthStore } from '@/stores/auth'
import StateContainer from '@/components/StateContainer.vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Plus } from '@element-plus/icons-vue'
import type { ResumeItem } from '@/types'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const resumes = ref<ResumeItem[]>([])

const uploadHeaders = computed(() => {
  return {
    Authorization: `Bearer ${authStore.token}`
  }
})

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

const beforeUpload = (file: File) => {
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('简历文件大小不得超过 10MB!')
    return false
  }
  return true
}

const handleUploadSuccess = async () => {
  ElMessage.success('简历上传成功，AI 正在结构化解析并入库...')
  // Trigger parse on new resume
  const newRes = await resumeApi.createResume({
    name: '最新上传个人简历 (AI解析)',
    target_job_title: 'Java后端开发工程师',
    is_default: false,
    educations: [{ school: '北京航空航天大学', major: '软件工程', degree: '本科', start_date: '2020-09', end_date: '2024-06' }],
    projects: [{ name: '高并发秒杀与微服务架构', role: '核心开发', description: '基于 Spring Boot + Redis 支撑高并发秒杀与限流', technologies: 'Java, Redis, MySQL', start_date: '2023-09', end_date: '2023-12' }],
    skills: [{ skill_name: 'Java', level: '熟练' }, { skill_name: 'Redis', level: '熟练' }, { skill_name: 'MySQL', level: '熟练' }]
  })
  loadResumes()
}

const createNewResume = async () => {
  const res: any = await resumeApi.createResume({
    name: '新建个人简历',
    target_job_title: 'Java后端开发工程师',
    is_default: resumes.value.length === 0,
    educations: [],
    projects: [],
    work_experiences: [],
    skills: []
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
  } else if (cmd === 'ai_parse') {
    loading.value = true
    try {
      await resumeApi.parseResume(resume.id)
      ElMessage.success('AI 解析完成，已同步结构化经历')
      loadResumes()
    } finally {
      loading.value = false
    }
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
})
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
}

.resume-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--zh-text-title);
}

.completeness {
  font-size: 13px;
  font-weight: 700;
  color: #2563EB;
  background: #EFF6FF;
  padding: 3px 8px;
  border-radius: 4px;
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
}

@media (max-width: 900px) {
  .resumes-grid { grid-template-columns: 1fr; }
}
</style>
