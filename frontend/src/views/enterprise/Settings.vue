<template>
  <div class="enterprise-settings-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">企业设置与资质认证</h2>
        <p class="page-subtitle">维护企业公共品牌主页资料、提交或查看官方营业执照实名认证与安全审计日志</p>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="settings-tabs">
      <!-- 基本资料 -->
      <el-tab-pane label="企业资料与雇主品牌" name="profile">
        <StateContainer :loading="loading" :error="error" @retry="fetchSettings">
          <div class="form-container">
            <el-form :model="form" label-position="top">
              <el-row :gutter="20">
                <el-col :span="16">
                  <el-form-item label="企业全称" required>
                    <el-input v-model="form.name" placeholder="请输入工商注册全称" />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="企业简称">
                    <el-input v-model="form.short_name" placeholder="如：华为" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :span="8">
                  <el-form-item label="所属行业">
                    <el-select v-model="form.industry" style="width: 100%;">
                      <el-option label="互联网/IT/软件" value="互联网/IT/软件" />
                      <el-option label="人工智能/大数据" value="人工智能/大数据" />
                      <el-option label="智能硬件/芯片" value="智能硬件/芯片" />
                      <el-option label="金融科技" value="金融科技" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="团队规模">
                    <el-select v-model="form.scale" style="width: 100%;">
                      <el-option label="0-20人 (初创团队)" value="0-20人" />
                      <el-option label="20-99人 (成长型企业)" value="20-99人" />
                      <el-option label="100-499人 (中型企业)" value="100-499人" />
                      <el-option label="500-9999人 (大型成熟企业)" value="500-9999人" />
                      <el-option label="10000人以上 (行业巨头)" value="10000人以上" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="总部城市">
                    <el-input v-model="form.city" placeholder="如：深圳" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item label="官方网址">
                <el-input v-model="form.website" placeholder="https://www.example.com" />
              </el-form-item>

              <el-form-item label="企业简介与愿景">
                <el-input
                  v-model="form.description"
                  type="textarea"
                  :rows="5"
                  placeholder="介绍企业发展历程、主营业务体系与技术愿景..."
                />
              </el-form-item>

              <el-form-item>
                <el-button type="primary" :loading="saving" @click="handleSaveProfile">
                  保存资料
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </StateContainer>
      </el-tab-pane>

      <!-- 资质认证 -->
      <el-tab-pane label="企业资质实名认证" name="verification">
        <div class="form-container">
          <div class="verify-status-banner">
            <div class="status-left">
              <span class="status-badge" :class="verifyStatusClass">
                {{ getVerifyStatusText(verification.status) }}
              </span>
              <span class="status-tip">{{ getVerifyStatusDesc(verification.status) }}</span>
            </div>
          </div>

          <div v-if="verification.status === 'REJECTED'" class="reject-reason-box">
            <strong>审核驳回原因：</strong>{{ verification.review_comment || '营业执照统一社会信用代码与企业名称不匹配，请核对后重新提交。' }}
          </div>

          <el-form :model="verifyForm" label-position="top" style="max-width: 600px; margin-top: 24px;">
            <el-form-item label="统一社会信用代码" required>
              <el-input v-model="verifyForm.license_no" placeholder="18位统一社会信用代码，如 91440300MA5..." />
            </el-form-item>
            <el-form-item label="法定代表人姓名" required>
              <el-input v-model="verifyForm.legal_person" placeholder="如：任正非" />
            </el-form-item>
            <el-form-item label="营业执照扫描件/图片 (模拟上传或URL)">
              <el-input v-model="verifyForm.license_image" placeholder="如：https://static.example.com/license.jpg" />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                :loading="submittingVerify"
                @click="handleSubmitVerify"
              >
                {{ verification.status === 'REJECTED' ? '重新提交审核' : '提交实名认证' }}
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 审计日志 -->
      <el-tab-pane label="团队操作日志与安全审计" name="logs">
        <div class="form-container">
          <el-table :data="logs" v-loading="logsLoading" style="width: 100%;">
            <el-table-column prop="created_at" label="操作时间" width="180">
              <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
            </el-table-column>
            <el-table-column prop="operator_name" label="操作人" width="140">
              <template #default="{ row }">{{ row.operator_name || 'HR管理员' }}</template>
            </el-table-column>
            <el-table-column prop="action" label="操作类型" width="180">
              <template #default="{ row }">
                <el-tag size="small">{{ row.action }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="detail" label="详细内容" min-width="240" />
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import StateContainer from '@/components/StateContainer.vue'
import { enterpriseApi } from '@/api'
import { ElMessage } from 'element-plus'

const activeTab = ref('profile')
const loading = ref(false)
const saving = ref(false)
const error = ref('')

const form = reactive({
  name: '华为技术有限公司',
  short_name: '华为',
  industry: '互联网/IT/软件',
  scale: '10000人以上',
  city: '深圳',
  website: 'https://www.huawei.com',
  description: '华为是全球领先的ICT基础设施和智能终端提供商。'
})

const verification = reactive({
  status: 'APPROVED',
  review_comment: ''
})

const verifyForm = reactive({
  license_no: '914403001922038216',
  legal_person: '赵明',
  license_image: 'https://images.unsplash.com/photo-license.png'
})

const submittingVerify = ref(false)

const verifyStatusClass = computed(() => {
  switch (verification.status) {
    case 'APPROVED': return 'badge-approved'
    case 'PENDING': return 'badge-pending'
    case 'REJECTED': return 'badge-rejected'
    default: return 'badge-pending'
  }
})

const getVerifyStatusText = (status: string) => {
  switch (status) {
    case 'APPROVED': return '已通过官方认证'
    case 'PENDING': return '资质正在审核中'
    case 'REJECTED': return '资质审核已驳回'
    default: return '未认证'
  }
}

const getVerifyStatusDesc = (status: string) => {
  switch (status) {
    case 'APPROVED': return '企业已完成工信部营业执照核验，享有职位优先展示与免审极速发布特权。'
    case 'PENDING': return '平台管理员将在1个工作日内完成审核，审核期间职位可正常编辑。'
    case 'REJECTED': return '资质未通过平台审核，请检查统一信用代码后重新提交。'
    default: return '提交实名认证可提升招聘转化率及平台背书。'
  }
}

const fetchSettings = async () => {
  loading.value = true
  error.value = ''
  try {
    const res: any = await enterpriseApi.getSettings()
    if (res) {
      if (res.name) form.name = res.name
      if (res.short_name) form.short_name = res.short_name
      if (res.industry) form.industry = res.industry
      if (res.scale) form.scale = res.scale
      if (res.city) form.city = res.city
      if (res.website) form.website = res.website
      if (res.description) form.description = res.description
      if (res.verification_status) {
        verification.status = res.verification_status
      }
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || '获取企业设置失败'
  } finally {
    loading.value = false
  }
}

const handleSaveProfile = async () => {
  saving.value = true
  try {
    await enterpriseApi.updateSettings(form)
    ElMessage.success('企业资料已成功保存')
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '保存资料失败')
  } finally {
    saving.value = false
  }
}

const handleSubmitVerify = async () => {
  if (!verifyForm.license_no.trim() || !verifyForm.legal_person.trim()) {
    ElMessage.warning('请填写完整的信用代码与法人姓名')
    return
  }
  submittingVerify.value = true
  try {
    await enterpriseApi.submitVerification(verifyForm)
    ElMessage.success('资质审核已提交，请等待管理员审核')
    verification.status = 'PENDING'
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '提交资质认证失败')
  } finally {
    submittingVerify.value = false
  }
}

// 审计日志
const logsLoading = ref(false)
const logs = ref<any[]>([])

const fetchLogs = async () => {
  logsLoading.value = true
  try {
    const res: any = await enterpriseApi.getLogs()
    logs.value = res || [
      { id: 1, operator_name: '企业管理员', action: 'JOB_UPDATE', detail: '更新岗位“资深后端架构师”薪资待遇与胜任力权重', created_at: new Date().toISOString() },
      { id: 2, operator_name: 'HR经理', action: 'CANDIDATE_ADVANCE', detail: '推进候选人张三至企业面试阶段', created_at: new Date(Date.now() - 3600000).toISOString() }
    ]
  } catch {
    logs.value = [
      { id: 1, operator_name: '企业管理员', action: 'JOB_UPDATE', detail: '更新岗位“资深后端架构师”薪资待遇与胜任力权重', created_at: new Date().toISOString() }
    ]
  } finally {
    logsLoading.value = false
  }
}

const formatDate = (val: string) => {
  if (!val) return '-'
  return new Date(val).toLocaleString('zh-CN', { hour12: false })
}

onMounted(() => {
  fetchSettings()
  fetchLogs()
})
</script>

<style scoped>
.enterprise-settings-page {
  max-width: 1100px;
  margin: 0 auto;
}

.page-header {
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

.settings-tabs {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 20px 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #F1F5F9;
}

.form-container {
  padding: 16px 0;
}

.verify-status-banner {
  background: #F8FAFC;
  border-radius: 8px;
  padding: 16px 20px;
  border: 1px solid #E2E8F0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  margin-right: 12px;
}

.badge-approved {
  background: #DCFCE7;
  color: #16A34A;
}

.badge-pending {
  background: #FEF3C7;
  color: #D97706;
}

.badge-rejected {
  background: #FEE2E2;
  color: #DC2626;
}

.status-tip {
  font-size: 13px;
  color: #64748B;
}

.reject-reason-box {
  background: #FEF2F2;
  border: 1px solid #F87171;
  border-radius: 6px;
  padding: 12px 16px;
  color: #B91C1C;
  font-size: 13px;
  margin-top: 16px;
}
</style>
