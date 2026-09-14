<template>
  <div class="job-form-page">
    <div class="page-header">
      <div>
        <el-button type="default" size="small" @click="$router.push('/enterprise/jobs')" style="margin-bottom: 8px;">
          <el-icon><ArrowLeft /></el-icon> 返回职位列表
        </el-button>
        <h2 class="page-title">{{ isEdit ? '编辑招聘职位' : '发布新招聘职位' }}</h2>
        <p class="page-subtitle">配置标准岗位画像、技能要求与胜任力权重（权重总和需为100%）</p>
      </div>
      <div class="header-actions">
        <el-button type="success" plain @click="showJDParser = true">
          <el-icon style="margin-right: 4px;"><MagicStick /></el-icon> AI 智能解析 JD
        </el-button>
        <el-button :loading="submitting" @click="handleSave('DRAFT')">保存为草稿</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSave('PENDING_REVIEW')">提交发布审核</el-button>
      </div>
    </div>

    <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
      <el-row :gutter="24">
        <!-- 左侧：基础信息与JD内容 -->
        <el-col :xs="24" :lg="16">
          <div class="form-card">
            <h3 class="card-title">基本信息</h3>
            <el-row :gutter="16">
              <el-col :span="14">
                <el-form-item label="职位名称" prop="title">
                  <el-input v-model="form.title" placeholder="如：资深后端架构师 (Go/Python)" />
                </el-form-item>
              </el-col>
              <el-col :span="10">
                <el-form-item label="所属部门" prop="department_id">
                  <el-select v-model="form.department_id" placeholder="选择部门" style="width: 100%;">
                    <el-option label="技术研发部" :value="1" />
                    <el-option label="人工智能算法中心" :value="2" />
                    <el-option label="产品体验设计部" :value="3" />
                    <el-option label="市场与商务运营部" :value="4" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="16">
              <el-col :span="8">
                <el-form-item label="工作城市" prop="city">
                  <el-input v-model="form.city" placeholder="如：深圳" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="最低月薪 (K)" prop="salary_min">
                  <el-input-number v-model="form.salary_min" :min="1" :max="300" style="width: 100%;" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="最高月薪 (K)" prop="salary_max">
                  <el-input-number v-model="form.salary_max" :min="1" :max="500" style="width: 100%;" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="16">
              <el-col :span="8">
                <el-form-item label="经验要求 (年)" prop="experience_min">
                  <el-select v-model="form.experience_min" style="width: 100%;">
                    <el-option label="应届生 / 经验不限" :value="0" />
                    <el-option label="1-3年" :value="1" />
                    <el-option label="3-5年" :value="3" />
                    <el-option label="5-10年" :value="5" />
                    <el-option label="10年以上" :value="10" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="最低学历要求" prop="education">
                  <el-select v-model="form.education" style="width: 100%;">
                    <el-option label="大专及以上" value="专科" />
                    <el-option label="本科及以上" value="本科" />
                    <el-option label="硕士及以上" value="硕士" />
                    <el-option label="博士" value="博士" />
                    <el-option label="不限学历" value="不限" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="招聘人数" prop="headcount">
                  <el-input-number v-model="form.headcount" :min="1" :max="999" style="width: 100%;" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="岗位职责描述" prop="description">
              <el-input
                v-model="form.description"
                type="textarea"
                :rows="6"
                placeholder="详细说明日常业务负责范围、关键技术挑战与交付目标..."
              />
            </el-form-item>

            <el-form-item label="任职资格要求" prop="requirements">
              <el-input
                v-model="form.requirements"
                type="textarea"
                :rows="6"
                placeholder="说明对候选人的技术栈、架构能力、工程规范与软素质期望..."
              />
            </el-form-item>
          </div>
        </el-col>

        <!-- 右侧：胜任力权重 & 必备技能标签 -->
        <el-col :xs="24" :lg="8">
          <!-- 胜任力权重配置 (100%校验) -->
          <div class="form-card">
            <div class="card-header">
              <h3 class="card-title">五维胜任力考核权重</h3>
              <div :class="['weight-total', totalWeight === 100 ? 'valid' : 'invalid']">
                总计: {{ totalWeight }}%
              </div>
            </div>
            <p class="card-tip">AI 评测与初筛评分将根据此权重分配分值，五项相加必须精确等于 100%。</p>

            <div class="weight-item">
              <div class="weight-label">
                <span>专业技能 (Hard Skills)</span>
                <span class="weight-val">{{ form.weights.skills }}%</span>
              </div>
              <el-slider v-model="form.weights.skills" :step="5" :max="100" />
            </div>

            <div class="weight-item">
              <div class="weight-label">
                <span>项目与实战经验 (Experience)</span>
                <span class="weight-val">{{ form.weights.experience }}%</span>
              </div>
              <el-slider v-model="form.weights.experience" :step="5" :max="100" />
            </div>

            <div class="weight-item">
              <div class="weight-label">
                <span>逻辑与架构分析 (Analytical)</span>
                <span class="weight-val">{{ form.weights.logic }}%</span>
              </div>
              <el-slider v-model="form.weights.logic" :step="5" :max="100" />
            </div>

            <div class="weight-item">
              <div class="weight-label">
                <span>沟通协作与表达 (Communication)</span>
                <span class="weight-val">{{ form.weights.communication }}%</span>
              </div>
              <el-slider v-model="form.weights.communication" :step="5" :max="100" />
            </div>

            <div class="weight-item">
              <div class="weight-label">
                <span>快速学习与适应力 (Adaptability)</span>
                <span class="weight-val">{{ form.weights.learning }}%</span>
              </div>
              <el-slider v-model="form.weights.learning" :step="5" :max="100" />
            </div>

            <el-alert
              v-if="totalWeight !== 100"
              title="当前权重总和不等于100%，请调整各维度滑块"
              type="error"
              :closable="false"
              show-icon
              style="margin-top: 16px;"
            />
          </div>

          <!-- 必备核心技能 -->
          <div class="form-card" style="margin-top: 20px;">
            <h3 class="card-title">核心技能标签</h3>
            <p class="card-tip">用于精准匹配简历中的技能项，可回车添加。</p>
            <div class="tags-container">
              <el-tag
                v-for="(tag, index) in form.skills"
                :key="index"
                closable
                @close="removeSkill(index)"
                style="margin-right: 8px; margin-bottom: 8px;"
              >
                {{ tag }}
              </el-tag>
              <el-input
                v-if="inputSkillVisible"
                ref="skillInputRef"
                v-model="inputSkillValue"
                size="small"
                style="width: 100px; margin-bottom: 8px;"
                @keyup.enter="handleSkillInputConfirm"
                @blur="handleSkillInputConfirm"
              />
              <el-button v-else size="small" @click="showSkillInput" style="margin-bottom: 8px;">
                + 添加技能
              </el-button>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-form>

    <!-- AI JD 解析弹窗 -->
    <el-dialog v-model="showJDParser" title="AI 智能解析招聘需求 (JD)" width="680px" destroy-on-close>
      <p style="color: #64748B; font-size: 13px; margin-top: 0;">
        直接粘贴从各大招聘平台或文档中复制的原始职位需求文本，AI 将自动提取职位名、职责要求、薪资范围、技能标签并推荐科学胜任力权重。
      </p>
      <el-input
        v-model="rawJDText"
        type="textarea"
        :rows="10"
        placeholder="粘贴完整的 JD 文本，例如：&#10;职位：高级Python研发工程师&#10;岗位职责：&#10;1. 负责高并发微服务后端架构设计与实现...&#10;任职资格：&#10;1. 统招本科以上，3年以上开发经验..."
      />
      <template #footer>
        <el-button @click="showJDParser = false">取消</el-button>
        <el-button type="primary" :loading="parsingJD" @click="handleRunJDParse">
          <el-icon style="margin-right: 4px;"><MagicStick /></el-icon> 开始智能提取
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, nextTick, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, MagicStick } from '@element-plus/icons-vue'
import { enterpriseApi } from '@/api'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)

const formRef = ref()
const submitting = ref(false)

const form = reactive({
  title: '',
  department_id: 1,
  city: '深圳',
  salary_min: 20,
  salary_max: 35,
  experience_min: 3,
  experience_max: 6,
  education: '本科',
  headcount: 2,
  description: '',
  requirements: '',
  skills: ['Python', 'FastAPI', 'MySQL', 'Docker'],
  weights: {
    skills: 30,
    experience: 25,
    logic: 20,
    communication: 15,
    learning: 10
  }
})

const rules = {
  title: [{ required: true, message: '请输入职位名称', trigger: 'blur' }],
  city: [{ required: true, message: '请输入工作地点', trigger: 'blur' }],
  description: [{ required: true, message: '请填写岗位职责描述', trigger: 'blur' }],
  requirements: [{ required: true, message: '请填写任职资格要求', trigger: 'blur' }]
}

const totalWeight = computed(() => {
  const w = form.weights
  return (w.skills || 0) + (w.experience || 0) + (w.logic || 0) + (w.communication || 0) + (w.learning || 0)
})

// 技能标签管理
const inputSkillVisible = ref(false)
const inputSkillValue = ref('')
const skillInputRef = ref()

const showSkillInput = () => {
  inputSkillVisible.value = true
  nextTick(() => {
    skillInputRef.value?.focus()
  })
}

const handleSkillInputConfirm = () => {
  if (inputSkillValue.value.trim()) {
    if (!form.skills.includes(inputSkillValue.value.trim())) {
      form.skills.push(inputSkillValue.value.trim())
    }
  }
  inputSkillVisible.value = false
  inputSkillValue.value = ''
}

const removeSkill = (index: number) => {
  form.skills.splice(index, 1)
}

// AI JD 解析
const showJDParser = ref(false)
const rawJDText = ref('')
const parsingJD = ref(false)

const handleRunJDParse = async () => {
  if (!rawJDText.value.trim()) {
    ElMessage.warning('请先粘贴 JD 文本')
    return
  }
  parsingJD.value = true
  try {
    const res: any = await enterpriseApi.parseJD(rawJDText.value)
    if (res) {
      if (res.title) form.title = res.title
      if (res.city) form.city = res.city
      if (res.salary_min) form.salary_min = res.salary_min
      if (res.salary_max) form.salary_max = res.salary_max
      if (res.experience_min !== undefined) form.experience_min = res.experience_min
      if (res.education) form.education = res.education
      if (res.description) form.description = res.description
      if (res.requirements) form.requirements = res.requirements
      if (res.skills && Array.isArray(res.skills)) form.skills = res.skills
      if (res.weights) {
        form.weights.skills = res.weights.skills || 30
        form.weights.experience = res.weights.experience || 25
        form.weights.logic = res.weights.logic || 20
        form.weights.communication = res.weights.communication || 15
        form.weights.learning = res.weights.learning || 10
      }
      ElMessage.success('JD 解析完成，已自动填充各字段与胜任力权重')
      showJDParser.value = false
    }
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || 'JD 解析失败')
  } finally {
    parsingJD.value = false
  }
}

// 保存/提交
const handleSave = async (statusTarget: 'DRAFT' | 'PENDING_REVIEW') => {
  if (totalWeight.value !== 100) {
    ElMessage.error('五维胜任力权重总和必须等于 100%')
    return
  }

  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    submitting.value = true
    try {
      const payload: any = {
        title: form.title,
        department_id: form.department_id,
        city: form.city,
        salary_min: form.salary_min,
        salary_max: form.salary_max,
        experience_min: form.experience_min,
        experience_max: form.experience_max,
        education: form.education,
        headcount: form.headcount,
        description: form.description,
        requirements: form.requirements,
        skills: form.skills.map(s => ({ skill_name: s, weight: 1, is_required: true })),
        competencies: [
          { dimension: '专业技能', weight: form.weights.skills },
          { dimension: '项目经验', weight: form.weights.experience },
          { dimension: '逻辑分析', weight: form.weights.logic },
          { dimension: '沟通协作', weight: form.weights.communication },
          { dimension: '学习敏锐', weight: form.weights.learning }
        ]
      }

      if (isEdit.value) {
        await enterpriseApi.updateJob(Number(route.params.id), payload)
        if (statusTarget === 'PENDING_REVIEW') {
          await enterpriseApi.submitJob(Number(route.params.id))
        }
        ElMessage.success('职位已更新')
      } else {
        const created: any = await enterpriseApi.createJob(payload)
        if (statusTarget === 'PENDING_REVIEW' && created && created.id) {
          await enterpriseApi.submitJob(created.id)
        }
        ElMessage.success(statusTarget === 'PENDING_REVIEW' ? '职位已提交平台审核' : '职位已保存为草稿')
      }
      router.push('/enterprise/jobs')
    } catch (err: any) {
      ElMessage.error(err.response?.data?.detail || '保存职位失败')
    } finally {
      submitting.value = false
    }
  })
}

onMounted(async () => {
  if (isEdit.value) {
    try {
      const res: any = await enterpriseApi.getJob(Number(route.params.id))
      if (res) {
        form.title = res.title || ''
        form.department_id = res.department_id || 1
        form.city = res.city || ''
        form.salary_min = res.salary_min || 15
        form.salary_max = res.salary_max || 30
        form.experience_min = res.experience_min || 0
        form.education = res.education || '本科'
        form.headcount = res.headcount || 1
        form.description = res.description || ''
        form.requirements = res.requirements || ''
        if (res.skills && res.skills.length) {
          form.skills = res.skills.map((s: any) => s.skill_name || s)
        }
      }
    } catch (err: any) {
      ElMessage.error('加载职位详情失败')
    }
  }
})
</script>

<style scoped>
.job-form-page {
  max-width: 1300px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #0F2347;
  margin: 0 0 6px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748B;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.form-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #F1F5F9;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1E293B;
  margin: 0 0 8px 0;
}

.card-tip {
  font-size: 12px;
  color: #64748B;
  margin: 0 0 16px 0;
  line-height: 1.5;
}

.weight-total {
  font-size: 14px;
  font-weight: 700;
  padding: 2px 10px;
  border-radius: 12px;
}

.weight-total.valid {
  background: #DCFCE7;
  color: #16A34A;
}

.weight-total.invalid {
  background: #FEE2E2;
  color: #DC2626;
}

.weight-item {
  margin-bottom: 16px;
}

.weight-label {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #334155;
  margin-bottom: 4px;
}

.weight-val {
  font-weight: 600;
  color: #2563EB;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}
</style>
