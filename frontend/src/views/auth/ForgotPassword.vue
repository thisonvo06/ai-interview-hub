<template>
  <div class="auth-page">
    <div class="card">
      <h2>找回密码</h2>
      <p class="desc">请输入您注册时使用的邮箱，我们将向您发送重置密码验证链接</p>
      <el-form label-position="top">
        <el-form-item label="电子邮箱">
          <el-input v-model="email" placeholder="请输入注册邮箱" size="large" />
        </el-form-item>
        <el-button type="primary" size="large" style="width: 100%;" @click="handleReset">发送重置链接</el-button>
      </el-form>
      <div class="footer">
        <router-link to="/login" class="link-primary">← 返回登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const email = ref('')
const handleReset = () => {
  if (!email.value) {
    ElMessage.warning('请输入注册邮箱')
    return
  }
  ElMessage.success('重置邮件已发送（演示环境模拟发送成功，可直接使用密码 123456 登录）')
}
</script>

<style scoped>
.auth-page {
  min-height: calc(100vh - 64px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: var(--zh-bg);
}
.card {
  width: 100%;
  max-width: 440px;
  background: #FFFFFF;
  border-radius: var(--zh-radius-xl);
  padding: 40px 36px;
  box-shadow: var(--zh-shadow);
  border: 1px solid var(--zh-border-light);
}
h2 {
  font-size: 22px;
  font-weight: 700;
  color: var(--zh-text-title);
  margin-bottom: 8px;
}
.desc {
  font-size: 13px;
  color: var(--zh-text-muted);
  margin-bottom: 24px;
}
.footer {
  text-align: center;
  margin-top: 24px;
}
.link-primary {
  color: var(--zh-primary);
  font-weight: 600;
}
</style>
