<template>
  <div class="resume-edit-page">
    <StateContainer :loading="loading" :error="error" @retry="loadResume">
      <div v-if="resume" class="edit-container">
        <!-- Top Toolbar -->
        <div class="top-toolbar zh-card">
          <div class="toolbar-left">
            <router-link to="/personal/resumes">
              <el-button link>← 返回简历列表</el-button>
            </router-link>
            <el-input v-model="resume.name" placeholder="简历名称" style="width: 220px;" />
            <el-input v-model="resume.target_job_title" placeholder="目标岗位名称" style="width: 220px;" />
          </div>

          <div class="toolbar-right">
            <router-link :to="`/personal/resumes/${resume.id}/analysis`">
              <el-button type="warning" plain>查看 AI 分析报告</el-button>
            </router-link>
            <el-button type="primary" :loading="saving" @click="handleSave">保存修改</el-button>
          </div>
        </div>

        <!-- 1. Education Section -->
        <div class="section-card zh-card">
          <div class="section-head">
            <h3 class="sec-title">教育背景</h3>
            <el-button size="small" type="primary" plain @click="addEdu">+ 添加教育经历</el-button>
          </div>
          <div class="items-list">
            <div v-for="(edu, idx) in resume.educations" :key="idx" class="form-item-box">
              <div class="item-grid-4">
                <el-input v-model="edu.school" placeholder="学校名称" />
                <el-input v-model="edu.major" placeholder="专业名称" />
                <el-select v-model="edu.degree" placeholder="学历层次">
                  <el-option label="本科" value="本科" />
                  <el-option label="硕士" value="硕士" />
                  <el-option label="博士" value="博士" />
                  <el-option label="大专" value="大专" />
                </el-select>
                <div class="date-range">
                  <el-input v-model="edu.start_date" placeholder="入学年月 (如2020-09)" />
                  <span>-</span>
                  <el-input v-model="edu.end_date" placeholder="毕业年月 (如2024-06)" />
                </div>
              </div>
              <el-button link type="danger" @click="resume.educations.splice(idx, 1)">删除</el-button>
            </div>
          </div>
        </div>

        <!-- 2. Projects Section -->
        <div class="section-card zh-card">
          <div class="section-head">
            <h3 class="sec-title">项目经历 (核心考察)</h3>
            <el-button size="small" type="primary" plain @click="addProj">+ 添加项目经历</el-button>
          </div>
          <div class="items-list">
            <div v-for="(proj, idx) in resume.projects" :key="idx" class="form-item-box">
              <div class="item-grid-3">
                <el-input v-model="proj.name" placeholder="项目名称" />
                <el-input v-model="proj.role" placeholder="担任角色 (如：核心开发/项目负责人)" />
                <el-input v-model="proj.technologies" placeholder="主要技术栈 (如：Java, Redis, Spring Boot)" />
              </div>
              <el-input
                v-model="proj.description"
                type="textarea"
                :rows="3"
                placeholder="详细说明项目背景、你的职责与攻克的具体技术难点 (建议包含高并发、分布式、容灾、压测等量化指标)..."
                style="margin-top: 10px;"
              />
              <div class="item-foot">
                <div class="date-inputs">
                  <el-input v-model="proj.start_date" placeholder="起始时间" style="width: 140px;" />
                  <span>至</span>
                  <el-input v-model="proj.end_date" placeholder="结束时间" style="width: 140px;" />
                </div>
                <el-button link type="danger" @click="resume.projects.splice(idx, 1)">删除此项</el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 3. Work Experience Section -->
        <div class="section-card zh-card">
          <div class="section-head">
            <h3 class="sec-title">工作 / 实习经历</h3>
            <el-button size="small" type="primary" plain @click="addWork">+ 添加工作经历</el-button>
          </div>
          <div class="items-list">
            <div v-for="(work, idx) in resume.work_experiences" :key="idx" class="form-item-box">
              <div class="item-grid-2">
                <el-input v-model="work.company" placeholder="公司名称" />
                <el-input v-model="work.title" placeholder="岗位职位" />
              </div>
              <el-input
                v-model="work.description"
                type="textarea"
                :rows="2"
                placeholder="主要工作内容与核心产出..."
                style="margin-top: 10px;"
              />
              <div class="item-foot">
                <div class="date-inputs">
                  <el-input v-model="work.start_date" placeholder="入职年月" style="width: 140px;" />
                  <span>至</span>
                  <el-input v-model="work.end_date" placeholder="离职年月" style="width: 140px;" />
                </div>
                <el-button link type="danger" @click="resume.work_experiences.splice(idx, 1)">删除此项</el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 4. Skills Section -->
        <div class="section-card zh-card">
          <div class="section-head">
            <h3 class="sec-title">技能掌握与证据</h3>
            <el-button size="small" type="primary" plain @click="addSkill">+ 添加技能项</el-button>
          </div>
          <div class="skills-grid">
            <div v-for="(sk, idx) in resume.skills" :key="idx" class="skill-item-box">
              <div class="skill-inputs">
                <el-input v-model="sk.skill_name" placeholder="技能 (如 Redis)" style="width: 140px;" />
                <el-select v-model="sk.level" placeholder="掌握程度" style="width: 120px;">
                  <el-option label="精通" value="精通" />
                  <el-option label="熟练" value="熟练" />
                  <el-option label="熟悉" value="熟悉" />
                  <el-option label="了解" value="了解" />
                </el-select>
                <el-input v-model="sk.evidence" placeholder="佐证经历或深入掌握的要点" />
                <el-button link type="danger" @click="resume.skills.splice(idx, 1)">删除</el-button>
              </div>
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
import { resumeApi } from '@/api'
import StateContainer from '@/components/StateContainer.vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const loading = ref(true)
const error = ref(false)
const saving = ref(false)
const resume = ref<any>(null)

const loadResume = async () => {
  loading.value = true
  error.value = false
  try {
    const id = Number(route.params.id)
    const res: any = await resumeApi.getResume(id)
    resume.value = res
  } catch (e) {
    error.value = true
  } finally {
    loading.value = false
  }
}

const addEdu = () => {
  resume.value.educations.push({ school: '', major: '', degree: '本科', start_date: '', end_date: '' })
}

const addProj = () => {
  resume.value.projects.push({ name: '', role: '核心开发', description: '', technologies: '', start_date: '', end_date: '' })
}

const addWork = () => {
  resume.value.work_experiences.push({ company: '', title: '', description: '', start_date: '', end_date: '' })
}

const addSkill = () => {
  resume.value.skills.push({ skill_name: '', level: '熟练', evidence: '' })
}

const handleSave = async () => {
  saving.value = true
  try {
    await resumeApi.updateResume(resume.value.id, resume.value)
    ElMessage.success('简历保存成功！已更新完整度与结构化数据')
    loadResume()
  } catch (e) {
    // handled
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadResume()
})
</script>

<style scoped>
.resume-edit-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.top-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
}

.toolbar-left, .toolbar-right {
  display: flex;
  align-items: center;
  gap: 14px;
}

.section-card {
  padding: 24px;
  margin-bottom: 20px;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--zh-border-light);
  padding-bottom: 12px;
}

.sec-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--zh-text-title);
}

.items-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-item-box {
  background: #F8FAFC;
  border: 1px solid var(--zh-border);
  border-radius: 8px;
  padding: 16px;
}

.item-grid-4 {
  display: grid;
  grid-template-columns: 1.5fr 1.5fr 1fr 2fr;
  gap: 12px;
  margin-bottom: 10px;
}

.item-grid-3 {
  display: grid;
  grid-template-columns: 2fr 1.5fr 2fr;
  gap: 12px;
}

.item-grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.date-range, .date-inputs {
  display: flex;
  align-items: center;
  gap: 8px;
}

.item-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px dashed var(--zh-border);
}

.skills-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skill-inputs {
  display: flex;
  align-items: center;
  gap: 12px;
}
</style>
