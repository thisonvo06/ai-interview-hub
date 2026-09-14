<template>
  <div class="auth-page">
    <div class="register-card">
      <div class="form-header">
        <h2 class="title">企业招聘协作账号注册</h2>
        <p class="subtitle">注册将创建企业档案并绑定企业负责人 (OWNER) 账号</p>
      </div>

      <el-form :model="form" class="auth-form" @submit.prevent="handleRegister">
        <el-form-item label="企业全称" required>
          <el-input
            v-model="form.company_name"
            placeholder="请输入营业执照上的企业全称"
            size="large"
          />
        </el-form-item>

        <el-form-item label="联系人姓名" required>
          <el-input
            v-model="form.contact_name"
            placeholder="请输入招聘负责人/HR 姓名"
            size="large"
          />
        </el-form-item>

        <el-form-item label="联系人手机" required>
          <el-input
            v-model="form.phone"
            placeholder="请输入手机号"
            size="large"
          />
        </el-form-item>

        <el-form-item label="企业工作邮箱" required>
          <el-input
            v-model="form.email"
            placeholder="请输入工作邮箱 (如 hr@company.com)"
            size="large"
          />
        </el-form-item>

        <el-form-item label="设置初始密码" required>
          <el-input
            v-model="form.password"
            type="password"
            placeholder="设置登录密码 (至少6位)"
            show-password
            size="large"
          />
        </el-form-item>

        <div class="info-tip">
          注：新注册企业默认状态为 <code>UNVERIFIED</code>（未实名），登入工作台后需提交企业营业执照资质核验方可正式公开发布在招职位。
        </div>

        <el-button
          type="primary"
          class="submit-btn"
          size="large"
          :loading="loading"
          @click="handleRegister"
        >
          立即注册企业
        </el-button>
      </el-form>

      <div class="form-footer">
        已有企业账号？<router-link to="/login" class="link-primary">返回登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '@/api'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const form = reactive({
  company_name: '',
  contact_name: '',
  phone: '',
  email: '',
  password: '',
  industry: '互联网/人工智能',
  city: '北京'
})

const handleRegister = async () => {
  if (!form.company_name || !form.contact_name || !form.email || !form.password) {
    ElMessage.warning('请将必填信息填写完整')
    return
  }

  loading.value = true
  try {
    const res: any = await authApi.registerEnterprise(form)
    authStore.setAuth(res.access_token, {
      id: res.user_id,
      email: form.email,
      account_type: 'ENTERPRISE',
      roles: ['ENTERPRISE_OWNER'],
      name: form.contact_name,
      company_id: res.company_id,
      company_name: form.company_name
    })
    ElMessage.success('企业创建成功！进入企业工作台')
    router.push('/enterprise/dashboard')
  } catch (e) {
    // Interceptor handled
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: calc(100vh - 64px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
}

.register-card {
  width: 100%;
  max-width: 520px;
  background: #FFFFFF;
  border-radius: var(--zh-radius-xl);
  padding: 40px 36px;
  box-shadow: var(--zh-shadow);
  border: 1px solid var(--zh-border-light);
}

.form-header {
  margin-bottom: 24px;
}

.title {
  font-size: 22px;
  font-weight: 700;
  color: var(--zh-text-title);
  margin-bottom: 6px;
}

.subtitle {
  font-size: 13px;
  color: var(--zh-text-muted);
}

.info-tip {
  font-size: 12px;
  color: var(--zh-text-muted);
  background: #F8FAFC;
  padding: 10px 12px;
  border-radius: 6px;
  line-height: 1.5;
  margin-bottom: 16px;
}

.info-tip code {
  color: #D97706;
  font-weight: 600;
}

.submit-btn {
  width: 100%;
  height: 44px;
  font-weight: 600;
}

.form-footer {
  text-align: center;
  margin-top: 24px;
  font-size: 13px;
  color: var(--zh-text-muted);
}

.link-primary {
  color: var(--zh-primary);
  font-weight: 600;
}
</style>
