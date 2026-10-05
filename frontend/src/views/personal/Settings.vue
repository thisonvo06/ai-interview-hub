<template>
  <div class="settings-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">账号与安全设置</h2>
        <p class="page-subtitle">管理您的个人账号信息、隐私授权及会话安全</p>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="settings-tabs">
      <!-- 账号安全 -->
      <el-tab-pane label="账号安全" name="security">
        <div class="settings-section">
          <h3 class="section-title">安全等级</h3>
          <div class="security-level-card">
            <div class="level-info">
              <span class="level-badge high">较高</span>
              <span class="level-desc">您的账号安全保护良好，已绑定邮箱并开启密码验证。</span>
            </div>
          </div>

          <h3 class="section-title" style="margin-top: 24px;">修改登录密码</h3>
          <el-form :model="pwdForm" :rules="pwdRules" ref="pwdFormRef" label-position="top" style="max-width: 480px;">
            <el-form-item label="当前密码" prop="oldPassword">
              <el-input v-model="pwdForm.oldPassword" type="password" show-password placeholder="请输入当前使用的密码" />
            </el-form-item>
            <el-form-item label="新密码" prop="newPassword">
              <el-input v-model="pwdForm.newPassword" type="password" show-password placeholder="请输入8位以上新密码，含字母数字" />
            </el-form-item>
            <el-form-item label="确认新密码" prop="confirmPassword">
              <el-input v-model="pwdForm.confirmPassword" type="password" show-password placeholder="再次输入新密码" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="pwdLoading" @click="handleUpdatePassword">确认更新密码</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- 隐私授权 -->
      <el-tab-pane label="隐私与授权" name="privacy">
        <div class="settings-section">
          <div class="section-header">
            <div>
              <h3 class="section-title">AI服务数据授权</h3>
              <p class="section-sub">您可以根据《个人信息保护法》管理简历解析、模拟面试及能力图谱的数据处理授权。</p>
            </div>
          </div>

          <el-table :data="consents" v-loading="consentsLoading" style="width: 100%; margin-top: 16px;">
            <el-table-column prop="scope" label="授权用途" min-width="180">
              <template #default="{ row }">
                <div style="font-weight: 500;">{{ scopeLabel(row.scope) }}</div>
                <div style="font-size: 12px; color: #64748B;">授权对象：{{ targetTypeLabel(row.target_type) }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="granted_at" label="授权时间" width="180">
              <template #default="{ row }">{{ formatDate(row.granted_at) }}</template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="row.revoked ? 'info' : 'success'" size="small">
                  {{ row.revoked ? '已撤销' : '生效中' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" align="right">
              <template #default="{ row }">
                <el-button
                  v-if="!row.revoked"
                  type="danger"
                  link
                  size="small"
                  @click="handleRevokeConsent(row)"
                >
                  撤销授权
                </el-button>
                <span v-else style="color: #94A3B8; font-size: 13px;">无</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <!-- 活跃会话（仅管理员可见） -->
      <el-tab-pane v-if="isAdmin" label="活跃会话" name="sessions">
        <div class="settings-section">
          <div class="section-header">
            <div>
              <h3 class="section-title">登录设备与会话</h3>
              <p class="section-sub">查看当前已登录您账号的客户端与设备，如有异常可立即踢出。</p>
            </div>
            <el-button type="default" size="small" @click="fetchSessions">刷新列表</el-button>
          </div>

          <div v-loading="sessionsLoading" class="sessions-list">
            <div v-for="item in sessions" :key="item.id" class="session-item">
              <div class="session-icon">
                <el-icon :size="24"><Monitor /></el-icon>
              </div>
              <div class="session-info">
                <div class="session-name">
                  {{ item.device || '未知设备' }}
                  <el-tag v-if="item.is_current" type="primary" size="small" style="margin-left: 8px;">当前设备</el-tag>
                </div>
                <div class="session-meta">
                  <span>IP: {{ item.ip || '-' }}</span>
                  <span>登录地: {{ item.location || '-' }}</span>
                  <span>最近活跃: {{ item.last_active === '刚刚' ? '刚刚' : formatDate(item.last_active) }}</span>
                </div>
              </div>
              <div class="session-actions">
                <el-button
                  v-if="!item.is_current"
                  type="danger"
                  link
                  size="small"
                  @click="handleRevokeSession(item.id)"
                >
                  强制下线
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 通知偏好 -->
      <el-tab-pane label="通知设置" name="notifications">
        <div class="settings-section" style="max-width: 600px;">
          <h3 class="section-title">消息与通知偏好</h3>
          <div class="notify-item">
            <div>
              <div class="notify-title">面试邀请通知</div>
              <div class="notify-desc">当企业向您发送结构化面试或AI初筛邀请时接收通知</div>
            </div>
            <el-switch v-model="notifySettings.interview" />
          </div>
          <el-divider />
          <div class="notify-item">
            <div>
              <div class="notify-title">申请状态变更</div>
              <div class="notify-desc">应聘申请被查看、通过或录用进度发生变化时通知</div>
            </div>
            <el-switch v-model="notifySettings.application" />
          </div>
          <el-divider />
          <div class="notify-item">
            <div>
              <div class="notify-title">AI 评测报告生成</div>
              <div class="notify-desc">模拟面试完成且深度诊断报告与成长路线图就绪时提醒</div>
            </div>
            <el-switch v-model="notifySettings.report" />
          </div>
          <el-divider />
          <el-button type="primary" :loading="notifyLoading" @click="handleSaveNotify">保存通知偏好</el-button>
        </div>
      </el-tab-pane>

      <!-- AI 服务接入 -->
      <el-tab-pane label="AI 服务" name="ai">
        <div class="settings-section" style="max-width: 560px;">
          <div class="section-header">
            <div>
              <h3 class="section-title">{{ isAdmin ? '大模型服务接入 (API Key)' : '个人大模型服务接入 (API Key)' }}</h3>
              <p class="section-sub">{{ isAdmin
                ? '接入 OpenAI 兼容协议的大模型后，简历诊断、模拟面试评分、学习路线等 AI 能力将使用真实模型；留空则回退内置沙箱 (Mock)。'
                : '填写您自己的 API Key 后，您的 AI 功能将使用真实模型，且仅影响您本人的调用；未配置时使用平台默认（沙箱或管理员配置）。' }}</p>
            </div>
          </div>

          <el-alert
            v-if="!isAdmin"
            type="info"
            :closable="false"
            class="ai-alert"
            :title="aiHasPersonal ? '当前生效：您的个人 AI 配置' : '当前生效：平台默认配置（您尚未绑定个人 Key）'"
          />
          <el-alert
            v-if="!aiLoading && !aiConfigured"
            type="info"
            :closable="false"
            class="ai-alert"
            title="当前未配置 API Key，AI 功能以内置沙箱 (Mock) 运行。"
          />
          <el-alert
            v-else-if="!aiLoading"
            :type="aiForm.mode === 'MOCK' ? 'warning' : 'success'"
            :closable="false"
            class="ai-alert"
            :title="aiForm.mode === 'MOCK' ? '当前引擎模式：内置沙箱 (Mock)' : '当前引擎模式：真实大语言模型 (Real)'"
          />

          <el-form :model="aiForm" label-position="top" style="margin-top: 16px;">
            <el-form-item label="服务引擎模式">
              <el-radio-group v-model="aiForm.mode">
                <el-radio-button label="REAL">真实大模型 (Real)</el-radio-button>
                <el-radio-button label="MOCK">内置沙箱 (Mock)</el-radio-button>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="API 服务 Base URL" required>
              <el-input
                v-model="aiForm.base_url"
                placeholder="https://api.openai.com/v1"
                :disabled="aiForm.mode === 'MOCK'"
              />
              <div class="ai-tip">
                常用服务商：
                <span
                  v-for="p in aiPresets"
                  :key="p.url"
                  class="ai-preset"
                  @click="applyAiPreset(p)"
                >{{ p.name }}</span>
              </div>
            </el-form-item>

            <el-form-item label="模型标识 (Model Name)" required>
              <el-input
                v-model="aiForm.model"
                placeholder="如：gpt-4o-mini, deepseek-chat, qwen-plus"
                :disabled="aiForm.mode === 'MOCK'"
              />
            </el-form-item>

            <el-form-item label="API Key">
              <el-input
                v-model="aiForm.api_key"
                type="password"
                show-password
                :placeholder="aiKeyMasked ? `已保存 (${aiKeyMasked})，留空表示不修改` : '请输入 API Key'"
                :disabled="aiForm.mode === 'MOCK'"
              />
              <div class="ai-tip">Key 仅保存在本实例数据库中，页面只回显掩码，不会明文展示。{{ isAdmin ? '该配置为平台全局配置，影响所有用户。' : '该配置为您个人专属，仅影响您自己的 AI 调用。' }}</div>
            </el-form-item>

            <el-form-item>
              <el-button :loading="aiTesting" :disabled="aiForm.mode === 'MOCK'" @click="handleAiTest">测试连接</el-button>
              <el-button type="primary" :loading="aiSaving" @click="handleAiSave">保存配置</el-button>
              <el-button v-if="!isAdmin && aiHasPersonal" @click="handleAiReset">清除个人配置</el-button>
            </el-form-item>
          </el-form>

          <el-alert
            v-if="aiTestResult"
            :type="aiTestResult.success ? 'success' : 'error'"
            :closable="true"
            class="ai-alert"
            :title="aiTestResult.message"
            @close="aiTestResult = null"
          />

          <!-- 用量统计 -->
          <div v-if="aiStats" class="ai-stats-panel" v-loading="aiStatsLoading">
            <h4 class="ai-stats-title">
              <el-icon><DataAnalysis /></el-icon>
              {{ isAdmin ? '服务用量统计' : '我的用量统计' }}
            </h4>
            <div class="ai-stats-grid">
              <div class="ai-stat-item">
                <span class="ai-stat-val">{{ aiStats.total_calls }}</span>
                <span class="ai-stat-label">总调用次数</span>
              </div>
              <div class="ai-stat-item">
                <span class="ai-stat-val" :class="{ 'text-red': aiStats.error_calls > 0 }">{{ aiStats.success_rate }}%</span>
                <span class="ai-stat-label">成功率</span>
              </div>
              <div class="ai-stat-item">
                <span class="ai-stat-val">{{ formatTokens(aiStats.tokens_total) }}</span>
                <span class="ai-stat-label">总 Token 消耗</span>
              </div>
              <div class="ai-stat-item">
                <span class="ai-stat-val">{{ aiStats.current_model || 'mock-ai' }}</span>
                <span class="ai-stat-label">当前模型</span>
              </div>
            </div>
            <div v-if="aiStats.total_calls > 0" class="ai-stats-detail">
              <span>入站 {{ formatTokens(aiStats.tokens_in) }}  ·  出站 {{ formatTokens(aiStats.tokens_out) }}</span>
            </div>
            <el-button v-if="aiStats.total_calls > 0" link size="small" style="margin-top: 8px;" @click="fetchAIStats">
              刷新统计
            </el-button>
            <span v-else class="ai-stats-empty">暂无调用记录（当前使用 Mock 模式或尚未通过真实模型完成 AI 任务）</span>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Monitor, DataAnalysis } from '@element-plus/icons-vue'
import { personalApi, authApi, publicApi } from '@/api'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'

const authStore = useAuthStore()
const isAdmin = computed(() => authStore.isAdmin)

const activeTab = ref('security')
const pwdLoading = ref(false)
const pwdFormRef = ref()
const pwdForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const pwdRules = {
  oldPassword: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不得少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (_rule: any, value: string, callback: any) => {
        if (value !== pwdForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const handleUpdatePassword = async () => {
  if (!pwdFormRef.value) return
  await pwdFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    pwdLoading.value = true
    try {
      await authApi.changePassword({
        old_password: pwdForm.oldPassword,
        new_password: pwdForm.newPassword
      })
      ElMessage.success('密码更新成功，下次登录请使用新密码')
      pwdForm.oldPassword = ''
      pwdForm.newPassword = ''
      pwdForm.confirmPassword = ''
    } catch (err: any) {
      ElMessage.error(err.response?.data?.message || err.response?.data?.detail || '密码更新失败')
    } finally {
      pwdLoading.value = false
    }
  })
}

// 隐私授权
const consentsLoading = ref(false)
const consents = ref<any[]>([])

const SCOPE_LABELS: Record<string, string> = {
  RESUME_AND_INTERVIEW: '简历与面试数据共享',
  RESUME: '简历数据共享',
  INTERVIEW: '面试数据共享'
}
const TARGET_TYPE_LABELS: Record<string, string> = {
  COMPANY: '企业',
  RECRUITER: '招聘官'
}
const scopeLabel = (scope: string) => SCOPE_LABELS[scope] || scope || '-'
const targetTypeLabel = (t: string) => TARGET_TYPE_LABELS[t] || t || '-'

const fetchConsents = async () => {
  consentsLoading.value = true
  try {
    const res: any = await personalApi.getConsents()
    consents.value = Array.isArray(res) ? res : []
  } catch {
    consents.value = []
  } finally {
    consentsLoading.value = false
  }
}

const handleRevokeConsent = (row: any) => {
  ElMessageBox.confirm(`确定撤销对${targetTypeLabel(row.target_type)}的“${scopeLabel(row.scope)}”授权吗？撤销后相关数据将不再共享。`, '撤销确认', {
    type: 'warning',
    confirmButtonText: '确定撤销',
    cancelButtonText: '取消'
  }).then(async () => {
    try {
      await personalApi.revokeConsent(row.id)
      ElMessage.success('授权已成功撤销')
      row.revoked = true
    } catch (err: any) {
      ElMessage.error(err.response?.data?.detail || '撤销失败')
    }
  })
}

// 会话管理
const sessionsLoading = ref(false)
const sessions = ref<any[]>([])

const fetchSessions = async () => {
  sessionsLoading.value = true
  try {
    const res: any = await personalApi.getSessions()
    sessions.value = Array.isArray(res) ? res : []
  } catch {
    sessions.value = []
  } finally {
    sessionsLoading.value = false
  }
}

const handleRevokeSession = (sessionId: string) => {
  ElMessageBox.confirm('确定强制下线该设备会话吗？', '下线确认', {
    type: 'warning'
  }).then(async () => {
    try {
      await personalApi.revokeSession(sessionId)
      ElMessage.success('已强制下线该设备')
      sessions.value = sessions.value.filter(s => s.id !== sessionId)
    } catch (err: any) {
      ElMessage.error(err.response?.data?.detail || '操作失败')
    }
  })
}

// 通知偏好
const notifyLoading = ref(false)
const notifySettings = reactive({
  interview: true,
  application: true,
  report: true
})

const fetchNotifyPrefs = async () => {
  try {
    const res: any = await personalApi.getNotificationPreferences()
    if (res) {
      notifySettings.interview = !!res.interview
      notifySettings.application = !!res.application
      notifySettings.report = !!res.report
    }
  } catch (e) {
    // 使用默认值
  }
}

const handleSaveNotify = async () => {
  notifyLoading.value = true
  try {
    await personalApi.updateNotificationPreferences({ ...notifySettings })
    ElMessage.success('通知设置已保存')
  } catch (e) {
    // handled
  } finally {
    notifyLoading.value = false
  }
}

// AI 服务接入（复用登录前配置向导同一套全局配置接口）
const aiLoading = ref(false)
const aiSaving = ref(false)
const aiTesting = ref(false)
const aiConfigured = ref(false)
const aiKeyMasked = ref('')
const aiTestResult = ref<{ success: boolean; message: string } | null>(null)
const aiForm = reactive({
  mode: 'REAL',
  base_url: 'https://api.openai.com/v1',
  model: 'gpt-4o-mini',
  api_key: ''
})
const aiPresets = [
  { name: 'OpenAI', url: 'https://api.openai.com/v1', model: 'gpt-4o-mini' },
  { name: 'DeepSeek', url: 'https://api.deepseek.com/v1', model: 'deepseek-chat' },
  { name: '通义千问', url: 'https://dashscope.aliyuncs.com/compatible-mode/v1', model: 'qwen-plus' },
  { name: 'Kimi', url: 'https://api.moonshot.cn/v1', model: 'moonshot-v1-8k' },
  { name: '本地 Ollama', url: 'http://localhost:11434/v1', model: 'qwen2.5' }
]

const applyAiPreset = (p: typeof aiPresets[number]) => {
  aiForm.base_url = p.url
  aiForm.model = p.model
}

// 管理员读写全局配置，普通用户读写个人配置（个人 Key 仅影响自身调用）
const aiHasPersonal = ref(false)

const fetchAIConfig = async () => {
  aiLoading.value = true
  try {
    const res: any = isAdmin.value ? await publicApi.getAISettings() : await personalApi.getPersonalAIConfig()
    if (res) {
      aiForm.mode = res.mode === 'MOCK' ? 'MOCK' : 'REAL'
      aiForm.base_url = res.base_url || aiForm.base_url
      aiForm.model = res.model || aiForm.model
      aiKeyMasked.value = res.api_key_masked || ''
      aiConfigured.value = !!res.configured
      aiHasPersonal.value = !!res.has_personal
    }
  } catch {
    // 读取失败时保持默认，允许直接填写
  } finally {
    aiLoading.value = false
  }
}

const handleAiTest = async () => {
  if (!aiForm.base_url || !aiForm.model) {
    ElMessage.warning('请先填写 Base URL 与模型名称')
    return
  }
  if (!aiForm.api_key && !aiConfigured.value) {
    ElMessage.warning('请先填写 API Key')
    return
  }
  aiTesting.value = true
  aiTestResult.value = null
  try {
    const payload = {
      base_url: aiForm.base_url,
      api_key: aiForm.api_key,
      model: aiForm.model
    }
    const res: any = isAdmin.value
      ? await publicApi.testAISettings(payload)
      : await personalApi.testPersonalAIConfig(payload)
    aiTestResult.value = res || { success: false, message: '测试接口无返回' }
  } catch (err: any) {
    aiTestResult.value = { success: false, message: err.message || '测试请求失败' }
  } finally {
    aiTesting.value = false
  }
}

const handleAiReset = async () => {
  try {
    await personalApi.resetPersonalAIConfig()
    ElMessage.success('已清除个人 AI 配置，回退到平台默认')
    aiForm.api_key = ''
    await fetchAIConfig()
    await fetchAIStats()
  } catch {
    // 拦截器已提示
  }
}

const handleAiSave = async () => {
  if (aiForm.mode === 'REAL' && (!aiForm.base_url || !aiForm.model)) {
    ElMessage.warning('真实模型模式下必须填写 Base URL 与模型名称')
    return
  }
  aiSaving.value = true
  try {
    const payload: any = { mode: aiForm.mode, base_url: aiForm.base_url, model: aiForm.model }
    if (aiForm.api_key) payload.api_key = aiForm.api_key
    const res: any = isAdmin.value
      ? await publicApi.updateAISettings(payload)
      : await personalApi.updatePersonalAIConfig(payload)
    ElMessage.success(res?.message || '配置已保存并生效')
    await fetchAIConfig()
    aiForm.api_key = ''
  } catch (err: any) {
    // 错误已由拦截器统一提示（如 403 权限拦截）
  } finally {
    aiSaving.value = false
  }
}

// 用量统计
const aiStats = ref<any>(null)
const aiStatsLoading = ref(false)

const formatTokens = (n: number) => {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K'
  return String(n)
}

const fetchAIStats = async () => {
  aiStatsLoading.value = true
  try {
    aiStats.value = isAdmin.value ? await publicApi.getAIStats() : await personalApi.getPersonalAIUsage()
  } catch {
    // 读取失败不阻塞
  } finally {
    aiStatsLoading.value = false
  }
}

const formatDate = (val: string) => {
  if (!val) return '-'
  return new Date(val).toLocaleString('zh-CN', { hour12: false })
}

onMounted(() => {
  fetchConsents()
  if (isAdmin.value) fetchSessions()
  fetchNotifyPrefs()
  fetchAIConfig()
  fetchAIStats()
})
</script>

<style scoped>
.settings-page {
  max-width: 1080px;
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
}

.settings-section {
  padding: 12px 0;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1E293B;
  margin: 0 0 8px 0;
}

.section-sub {
  font-size: 13px;
  color: #64748B;
  margin: 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.security-level-card {
  background: #F8FAFC;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #E2E8F0;
  margin-bottom: 16px;
}

.level-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  margin-right: 12px;
}

.level-badge.high {
  background: #DCFCE7;
  color: #16A34A;
}

.level-desc {
  font-size: 13px;
  color: #475569;
}

.sessions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}

.session-item {
  display: flex;
  align-items: center;
  padding: 16px;
  background: #F8FAFC;
  border-radius: 8px;
  border: 1px solid #E2E8F0;
}

.session-icon {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  background: #EFF6FF;
  color: #2563EB;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.session-info {
  flex: 1;
}

.session-name {
  font-size: 14px;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 4px;
}

.session-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #64748B;
}

.notify-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.notify-title {
  font-size: 14px;
  font-weight: 500;
  color: #1E293B;
  margin-bottom: 4px;
}

.notify-desc {
  font-size: 12px;
  color: #64748B;
}

.ai-alert {
  margin-bottom: 16px;
}

.ai-tip {
  font-size: 12px;
  color: #94A3B8;
  margin-top: 6px;
  line-height: 1.6;
}

.ai-preset {
  color: #2563EB;
  cursor: pointer;
  margin-right: 10px;
}

.ai-preset:hover {
  text-decoration: underline;
}

/* AI 用量统计 */
.ai-stats-panel {
  margin-top: 20px;
  padding: 16px;
  background: #F8FAFC;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
}

.ai-stats-title {
  font-size: 14px;
  font-weight: 600;
  color: #1E293B;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

.ai-stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.ai-stat-item {
  text-align: center;
  padding: 10px;
  background: #FFFFFF;
  border-radius: 6px;
  border: 1px solid #E2E8F0;
}

.ai-stat-val {
  display: block;
  font-size: 20px;
  font-weight: 700;
  color: #1E293B;
}
.ai-stat-val.text-red { color: #EF4444; }

.ai-stat-label {
  font-size: 11px;
  color: #64748B;
  margin-top: 4px;
  display: block;
}

.ai-stats-detail {
  font-size: 12px;
  color: #64748B;
  margin-top: 10px;
  text-align: center;
}

.ai-stats-empty {
  font-size: 12px;
  color: #94A3B8;
}
</style>
