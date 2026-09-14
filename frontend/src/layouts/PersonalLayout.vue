<template>
  <div class="workspace-layout">
    <Navbar />
    <div class="workspace-body">
      <!-- Left Sidebar (230px per spec) -->
      <aside class="workspace-sidebar">
        <div class="sidebar-user-card">
          <el-avatar :size="48" class="user-avatar">{{ userInitial }}</el-avatar>
          <div class="user-info">
            <h4 class="user-name">{{ authStore.user?.name || '同学' }}</h4>
            <span class="user-target">{{ authStore.user?.target_job_title || 'Java后端开发' }}</span>
          </div>
        </div>

        <el-menu
          :default-active="activeRoute"
          class="sidebar-menu"
          router
        >
          <el-menu-item index="/personal/dashboard">
            <el-icon><Odometer /></el-icon>
            <span>个人工作台</span>
          </el-menu-item>
          <el-menu-item index="/personal/jobs">
            <el-icon><Suitcase /></el-icon>
            <span>岗位探索</span>
          </el-menu-item>
          <el-menu-item index="/personal/applications">
            <el-icon><Document /></el-icon>
            <span>我的求职</span>
          </el-menu-item>
          <el-menu-item index="/personal/resumes">
            <el-icon><Files /></el-icon>
            <span>简历中心</span>
          </el-menu-item>
          <el-menu-item index="/personal/assessment">
            <el-icon><PieChart /></el-icon>
            <span>能力诊断</span>
          </el-menu-item>
          <el-menu-item index="/personal/interviews">
            <el-icon><VideoCamera /></el-icon>
            <span>模拟面试</span>
          </el-menu-item>
          <el-menu-item index="/personal/growth">
            <el-icon><TrendCharts /></el-icon>
            <span>成长中心</span>
          </el-menu-item>
          <el-menu-item index="/personal/learning">
            <el-icon><Reading /></el-icon>
            <span>学习路线</span>
          </el-menu-item>
          <el-menu-item index="/personal/notifications">
            <el-icon><Bell /></el-icon>
            <span>消息中心</span>
          </el-menu-item>
          <el-menu-item index="/personal/profile">
            <el-icon><User /></el-icon>
            <span>个人档案</span>
          </el-menu-item>
          <el-menu-item index="/personal/settings">
            <el-icon><Setting /></el-icon>
            <span>账号与隐私</span>
          </el-menu-item>
        </el-menu>

        <!-- Quick Start Interview button in sidebar -->
        <div class="sidebar-action">
          <router-link to="/personal/interviews/create">
            <el-button type="primary" class="quick-interview-btn">
              <el-icon><VideoPlay /></el-icon> 开始模拟面试
            </el-button>
          </router-link>
        </div>
      </aside>

      <!-- Main Workspace Content -->
      <main class="workspace-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Navbar from '@/components/Navbar.vue'
import {
  Odometer, Suitcase, Document, Files, PieChart,
  VideoCamera, TrendCharts, Reading, Bell, User, Setting, VideoPlay
} from '@element-plus/icons-vue'

const route = useRoute()
const authStore = useAuthStore()

const activeRoute = computed(() => {
  const p = route.path
  if (p.startsWith('/personal/interviews/') && p.endsWith('/report')) return '/personal/interviews'
  if (p.startsWith('/personal/resumes/')) return '/personal/resumes'
  return p
})

const userInitial = computed(() => {
  return authStore.user?.name ? authStore.user.name.charAt(0).toUpperCase() : 'U'
})
</script>

<style scoped>
.workspace-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.workspace-body {
  flex: 1;
  display: flex;
  background-color: var(--zh-bg);
}

.workspace-sidebar {
  width: 230px;
  min-width: 230px;
  background: #FFFFFF;
  border-right: 1px solid var(--zh-border);
  display: flex;
  flex-direction: column;
}

.sidebar-user-card {
  padding: 20px 16px;
  border-bottom: 1px solid var(--zh-border-light);
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%);
  color: #FFFFFF;
  font-weight: 700;
  font-size: 18px;
}

.user-info {
  overflow: hidden;
}

.user-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--zh-text-title);
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.user-target {
  font-size: 12px;
  color: var(--zh-text-muted);
  display: block;
  margin-top: 2px;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.sidebar-menu {
  border-right: none;
  flex: 1;
  padding: 12px 0;
}

.sidebar-menu :deep(.el-menu-item) {
  height: 44px;
  line-height: 44px;
  margin: 2px 10px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--zh-text-body);
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background-color: var(--zh-primary-light);
  color: var(--zh-primary);
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: var(--zh-primary-light);
  color: var(--zh-primary);
  font-weight: 600;
}

.sidebar-action {
  padding: 16px;
  border-top: 1px solid var(--zh-border-light);
}

.quick-interview-btn {
  width: 100%;
  height: 40px;
  font-weight: 600;
}

.workspace-content {
  flex: 1;
  min-width: 0;
  padding: 24px 28px 48px;
  overflow-y: auto;
}
</style>
