<template>
  <div class="onboarding-page">
    <div class="onboarding-card">
      <div class="step-header">
        <el-steps :active="currentStep" finish-status="success" align-center>
          <el-step title="身份与学业" />
          <el-step title="求职目标与偏好" />
          <el-step title="完成初始化" />
        </el-steps>
      </div>

      <!-- Step 1: Education & Profile -->
      <div v-if="currentStep === 0" class="step-content">
        <h3 class="step-title">请完善你的基本学业与身份信息</h3>
        <p class="step-desc">帮助系统为你推荐更精准的校招/社招岗位及面试难度</p>

        <el-form label-position="top" class="step-form">
          <el-form-item label="当前身份" required>
            <el-radio-group v-model="form.profile_type">
              <el-radio-button label="STUDENT">在校生 / 应届毕业生</el-radio-button>
              <el-radio-button label="EXPERIENCED">社会求职者</el-radio-button>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="真实姓名 / 昵称" required>
            <el-input v-model="form.name" placeholder="请输入你的姓名" />
          </el-form-item>

          <div class="form-row">
            <el-form-item label="最高学历" required>
              <el-select v-model="form.education" placeholder="请选择">
                <el-option label="本科" value="本科" />
                <el-option label="硕士" value="硕士" />
                <el-option label="博士" value="博士" />
                <el-option label="大专" value="大专" />
              </el-select>
            </el-form-item>
            <el-form-item label="毕业年份" required>
              <el-input-number v-model="form.graduation_year" :min="2020" :max="2030" />
            </el-form-item>
          </div>

          <div class="form-row">
            <el-form-item label="毕业院校" required>
              <el-input v-model="form.school" placeholder="如：北京航空航天大学" />
            </el-form-item>
            <el-form-item label="所学专业" required>
              <el-input v-model="form.major" placeholder="如：计算机科学与技术" />
            </el-form-item>
          </div>
        </el-form>

        <div class="step-actions">
          <el-button type="primary" size="large" @click="currentStep = 1">下一步：设置求职偏好 →</el-button>
        </div>
      </div>

      <!-- Step 2: Career Preferences -->
      <div v-else-if="currentStep === 1" class="step-content">
        <h3 class="step-title">设置你的核心求职目标</h3>
        <p class="step-desc">系统将基于此岗位能力模型生成专属模拟面试题库与成长路线</p>

        <el-form label-position="top" class="step-form">
          <el-form-item label="目标职位名称" required>
            <el-input v-model="form.target_job_title" placeholder="如：Java后端开发工程师" />
          </el-form-item>

          <el-form-item label="期望工作城市" required>
            <el-input v-model="form.target_cities" placeholder="如：北京,上海,深圳 (多城市逗号隔开)" />
          </el-form-item>

          <el-form-item label="期望薪资区间 (单位：千元/月)">
            <div class="salary-range">
              <el-input-number v-model="form.salary_min" :min="5" :max="100" />
              <span>至</span>
              <el-input-number v-model="form.salary_max" :min="5" :max="100" />
              <span>K</span>
            </div>
          </el-form-item>

          <el-form-item label="当前求职状态">
            <el-select v-model="form.job_status">
              <el-option label="正在积极找工作 (离校/离职)" value="LOOKING" />
              <el-option label="在职/在读，考虑更好机会" value="OPEN_TO_OFFERS" />
              <el-option label="暂无找工作打算，仅模拟训练" value="NOT_LOOKING" />
            </el-select>
          </el-form-item>
        </el-form>

        <div class="step-actions">
          <el-button size="large" @click="currentStep = 0">← 上一步</el-button>
          <el-button type="primary" size="large" :loading="loading" @click="handleFinish">完成并进入工作台 →</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '@/api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const currentStep = ref(0)
const loading = ref(false)

const form = reactive({
  profile_type: 'STUDENT',
  name: '张同学',
  gender: '男',
  education: '本科',
  school: '北京航空航天大学',
  major: '计算机科学与技术',
  graduation_year: 2024,
  target_job_title: 'Java后端开发工程师',
  target_cities: '北京,上海,深圳',
  salary_min: 15,
  salary_max: 25,
  job_status: 'LOOKING'
})

const handleFinish = async () => {
  loading.value = true
  try {
    await authApi.updateOnboarding(form)
    ElMessage.success('引导完成！已为你定制能力模型与推荐岗位')
    router.push('/personal/dashboard')
  } catch (e) {
    // Handled
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.onboarding-page {
  min-height: calc(100vh - 64px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: var(--zh-bg);
}

.onboarding-card {
  width: 100%;
  max-width: 680px;
  background: #FFFFFF;
  border-radius: var(--zh-radius-xl);
  padding: 44px 40px;
  box-shadow: var(--zh-shadow);
  border: 1px solid var(--zh-border-light);
}

.step-header {
  margin-bottom: 36px;
}

.step-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--zh-text-title);
  margin-bottom: 6px;
}

.step-desc {
  font-size: 13px;
  color: var(--zh-text-muted);
  margin-bottom: 24px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.salary-range {
  display: flex;
  align-items: center;
  gap: 12px;
}

.step-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 32px;
}
</style>
