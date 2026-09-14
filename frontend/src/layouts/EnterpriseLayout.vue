<template>
  <div class="enterprise-layout">
    <Navbar />
    <div class="enterprise-body">
      <!-- Left Sidebar (230px) -->
      <aside class="enterprise-sidebar">
        <div class="company-badge-card">
          <div class="company-avatar">
            <el-icon :size="24" color="#2563EB"><OfficeBuilding /></el-icon>
          </div>
          <div class="company-info">
            <h4 class="company-name">{{ authStore.user?.company_name || '企业招聘协同中心' }}</h4>
            <el-tag size="small" type="success">认证企业</el-tag>
          </div>
        </div>

        <el-menu
          :default-active="activeRoute"
          class="sidebar-menu"
          router
        >
          <el-menu-item index="/enterprise/dashboard">
            <el-icon><Odometer /></el-icon>
            <span>企业工作台</span>
          </el-menu-item>
          <el-menu-item index="/enterprise/jobs">
            <el-icon><Suitcase /></el-icon>
            <span>岗位管理</span>
          </el-menu-item>
          <el-menu-item index="/enterprise/jobs/create">
            <el-icon><Plus /></el-icon>
            <span>发布岗位 (AI-JD)</span>
          </el-menu-item>
          <el-menu-item index="/enterprise/candidates">
            <el-icon><UserFilled /></el-icon>
            <span>候选人管理</span>
          </el-menu-item>
          <el-menu-item index="/enterprise/pipeline">
            <el-icon><Finished /></el-icon>
            <span>招聘流程看板</span>
          </el-menu-item>
          <el-menu-item index="/enterprise/interviews">
            <el-icon><VideoCamera /></el-icon>
            <span>面试与评价</span>
          </el-menu-item>
          <el-menu-item index="/enterprise/talent-pool">
            <el-icon><Collection /></el-icon>
            <span>企业人才库</span>
          </el-menu-item>
          <el-menu-item index="/enterprise/analytics">
            <el-icon><DataAnalysis /></el-icon>
            <span>招聘数据中心</span>
          </el-menu-item>
          <el-menu-item index="/enterprise/members">
            <el-icon><Avatar /></el-icon>
            <span>企业成员与权限</span>
          </el-menu-item>
          <el-menu-item index="/enterprise/settings">
            <el-icon><Setting /></el-icon>
            <span>企业资料与设置</span>
          </el-menu-item>
        </el-menu>
      </aside>

      <!-- Main Workspace Content -->
      <main class="enterprise-content">
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
  OfficeBuilding, Odometer, Suitcase, Plus, UserFilled,
  Finished, VideoCamera, Collection, DataAnalysis, Avatar, Setting
} from '@element-plus/icons-vue'

const route = useRoute()
const authStore = useAuthStore()

const activeRoute = computed(() => {
  const p = route.path
  if (p.startsWith('/enterprise/jobs/') && p.endsWith('/edit')) return '/enterprise/jobs'
  if (p.startsWith('/enterprise/candidates/')) return '/enterprise/candidates'
  return p
})
</script>

<style scoped>
.enterprise-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.enterprise-body {
  flex: 1;
  display: flex;
  background-color: var(--zh-bg);
}

.enterprise-sidebar {
  width: 230px;
  min-width: 230px;
  background: #FFFFFF;
  border-right: 1px solid var(--zh-border);
  display: flex;
  flex-direction: column;
}

.company-badge-card {
  padding: 18px 16px;
  border-bottom: 1px solid var(--zh-border-light);
  display: flex;
  align-items: center;
  gap: 12px;
}

.company-avatar {
  width: 42px;
  height: 42px;
  border-radius: 8px;
  background: #EFF6FF;
  display: flex;
  align-items: center;
  justify-content: center;
}

.company-info {
  overflow: hidden;
}

.company-name {
  font-size: 14px;
  font-weight: 700;
  color: var(--zh-text-title);
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
  margin-bottom: 4px;
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

.enterprise-content {
  flex: 1;
  min-width: 0;
  padding: 24px 28px 48px;
  overflow-y: auto;
}
</style>
