<template>
  <header class="zh-navbar">
    <div class="zh-nav-container">
      <!-- Logo -->
      <router-link to="/" class="zh-logo">
        <div class="logo-icon">
          <el-icon :size="22" color="#FFFFFF"><Monitor /></el-icon>
        </div>
        <div class="logo-text">
          <span class="logo-main">智面仓<span class="brand-divider"> / </span>职引</span>
          <span class="logo-sub">THE CAREER JOURNAL</span>
        </div>
      </router-link>

      <!-- Nav Links -->
      <button class="mobile-nav-toggle" @click="mobileNavOpen = !mobileNavOpen" :aria-expanded="mobileNavOpen" aria-controls="primary-nav">{{ mobileNavOpen ? "收起" : "导航" }}</button>
      <nav id="primary-nav" :class="['zh-nav-links', { 'mobile-open': mobileNavOpen }]" aria-label="主要导航" @click="mobileNavOpen = false">
        <router-link to="/" class="nav-item" exact-active-class="active">首页</router-link>
        <router-link to="/jobs" class="nav-item" active-class="active">岗位广场</router-link>
        <router-link to="/features" class="nav-item" active-class="active">功能介绍</router-link>
        <router-link to="/about" class="nav-item" active-class="active">关于我们</router-link>
        <router-link to="/help" class="nav-item" active-class="active">帮助中心</router-link>
      </nav>

      <!-- Right Action Area -->
      <div class="zh-nav-actions">
        <!-- Search bar -->
        <div class="nav-search">
          <el-input
            v-model="searchKey"
            placeholder="搜索职位、企业或技能..."
            prefix-icon="Search"
            clearable
            @keyup.enter="handleSearch"
          />
        </div>

        <!-- Unauthenticated -->
        <div v-if="!authStore.isAuthenticated" class="auth-buttons">
          <router-link to="/login">
            <el-button text>登录</el-button>
          </router-link>
          <router-link to="/register">
            <el-button type="primary">免费注册</el-button>
          </router-link>
        </div>

        <!-- Authenticated -->
        <div v-else class="user-session">
          <!-- Notification Bell -->
          <router-link v-if="authStore.isPersonal" to="/personal/notifications" class="noti-bell">
            <el-badge v-if="hasUnread" is-dot class="badge-item">
              <el-icon :size="20"><Bell /></el-icon>
            </el-badge>
            <el-icon v-else :size="20"><Bell /></el-icon>
          </router-link>

          <!-- User Dropdown -->
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-avatar-trigger">
              <el-avatar :size="34" class="avatar-circle">
                {{ userInitial }}
              </el-avatar>
              <span class="user-name">{{ authStore.user?.name || '用户' }}</span>
              <el-tag size="small" :type="tagType" class="role-tag">
                {{ roleLabel }}
              </el-tag>
              <el-icon :size="14"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item v-if="authStore.isPersonal" command="/personal/dashboard">
                  <el-icon><Odometer /></el-icon>个人工作台
                </el-dropdown-item>
                <el-dropdown-item v-if="authStore.isPersonal" command="/personal/jobs">
                  <el-icon><Suitcase /></el-icon>岗位探索
                </el-dropdown-item>
                <el-dropdown-item v-if="authStore.isPersonal" command="/personal/applications">
                  <el-icon><Document /></el-icon>我的求职
                </el-dropdown-item>
                <el-dropdown-item v-if="authStore.isPersonal" command="/personal/resumes">
                  <el-icon><Files /></el-icon>简历中心
                </el-dropdown-item>
                <el-dropdown-item v-if="authStore.isPersonal" command="/personal/interviews">
                  <el-icon><VideoCamera /></el-icon>模拟面试
                </el-dropdown-item>
                <el-dropdown-item v-if="authStore.isPersonal" command="/personal/growth">
                  <el-icon><TrendCharts /></el-icon>成长中心
                </el-dropdown-item>
                <el-dropdown-item v-if="authStore.isPersonal" command="/personal/profile">
                  <el-icon><User /></el-icon>个人档案
                </el-dropdown-item>

                <!-- Enterprise items -->
                <el-dropdown-item v-if="authStore.isEnterprise" command="/enterprise/dashboard">
                  <el-icon><OfficeBuilding /></el-icon>企业工作台
                </el-dropdown-item>
                <el-dropdown-item v-if="authStore.isEnterprise" command="/enterprise/jobs">
                  <el-icon><Briefcase /></el-icon>岗位管理
                </el-dropdown-item>
                <el-dropdown-item v-if="authStore.isEnterprise" command="/enterprise/candidates">
                  <el-icon><UserFilled /></el-icon>候选人管理
                </el-dropdown-item>
                <el-dropdown-item v-if="authStore.isEnterprise" command="/enterprise/pipeline">
                  <el-icon><Finished /></el-icon>招聘流程看板
                </el-dropdown-item>
                <el-dropdown-item v-if="authStore.isEnterprise" command="/enterprise/settings">
                  <el-icon><Setting /></el-icon>企业设置与认证
                </el-dropdown-item>

                <!-- Admin items -->
                <el-dropdown-item v-if="authStore.isAdmin" command="/admin/dashboard">
                  <el-icon><Cpu /></el-icon>平台管理后台
                </el-dropdown-item>

                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { personalApi, authApi } from '@/api'
import {
  Monitor, Search, Bell, ArrowDown, Odometer, Suitcase, Document,
  Files, VideoCamera, TrendCharts, User, OfficeBuilding, Briefcase,
  UserFilled, Finished, Setting, Cpu, SwitchButton
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const mobileNavOpen = ref(false)
const searchKey = ref('')
const hasUnread = ref(false)

// 仅当存在未读消息时才显示红点，避免常态红点误导
const loadUnreadStatus = async () => {
  if (!authStore.isPersonal) return
  try {
    const res: any = await personalApi.getNotifications()
    hasUnread.value = Array.isArray(res) && res.some((n: any) => !n.read)
  } catch (e) {
    hasUnread.value = false
  }
}

// 连接通知 WebSocket，收到新通知时实时刷新红点
let notiWs: WebSocket | null = null
let disposed = false
const connectNotificationWS = async () => {
  const userId = authStore.user?.id
  if (!authStore.isPersonal || !userId || notiWs) return
  try {
    const data: any = await authApi.getRealtimeTicket('notifications', userId)
    if (disposed || authStore.user?.id !== userId || !authStore.isPersonal) return
    const proto = location.protocol === 'https:' ? 'wss' : 'ws'
    notiWs = new WebSocket(`${proto}://${location.host}/ws/notifications/${userId}?ticket=${encodeURIComponent(data.ticket)}`)
    notiWs.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data)
        if (data.type === 'new_notification' || data.type === 'connected') {
          loadUnreadStatus()
        }
      } catch (e) { /* ignore */ }
    }
    notiWs.onerror = () => { notiWs?.close(); notiWs = null }
    notiWs.onclose = () => { notiWs = null }
  } catch (e) { /* ignore */ }
}

onMounted(() => {
  loadUnreadStatus()
  connectNotificationWS()
})

watch(() => authStore.user?.id, () => { notiWs?.close(); notiWs = null; loadUnreadStatus(); connectNotificationWS() })

onUnmounted(() => {
  disposed = true
  notiWs?.close()
  notiWs = null
})

const userInitial = computed(() => {
  return authStore.user?.name ? authStore.user.name.charAt(0).toUpperCase() : 'U'
})

const roleLabel = computed(() => {
  if (authStore.isAdmin) return '平台管理'
  if (authStore.isEnterprise) return '企业工作台'
  return '求职者'
})

const tagType = computed<'primary' | 'success' | 'warning' | 'info' | 'danger'>(() => {
  if (authStore.isAdmin) return 'danger'
  if (authStore.isEnterprise) return 'warning'
  return 'primary'
})

const handleSearch = () => {
  if (searchKey.value.trim()) {
    router.push(`/jobs?keyword=${encodeURIComponent(searchKey.value.trim())}`)
  } else {
    router.push('/jobs')
  }
}

const handleCommand = (cmd: string) => {
  if (cmd === 'logout') {
    authStore.logout()
  } else {
    router.push(cmd)
  }
}
</script>

<style scoped>
.zh-navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  height: 76px;
  background: rgba(248, 248, 243, 0.96);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--zh-border);
}

.zh-nav-container {
  max-width: 1360px;
  height: 100%;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.zh-logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: #246657;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: none;
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.logo-main {
  font-size: 18px;
  font-weight: 800;
  color: #0F2347;
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.logo-sub {
  font-size: 11px;
  font-weight: 600;
  color: #2563EB;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.zh-nav-links {
  display: flex;
  align-items: center;
  gap: 28px;
  margin-left: 36px;
}

.nav-item {
  font-size: 15px;
  font-weight: 500;
  color: var(--zh-text-body);
  transition: color 0.15s ease;
  position: relative;
  padding: 8px 0;
}

.nav-item:hover, .nav-item.active {
  color: var(--zh-primary);
}

.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: -18px;
  left: 0;
  right: 0;
  height: 2px;
  background-color: var(--zh-primary);
  border-radius: 2px;
}

.zh-nav-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.nav-search {
  width: 190px;
}

.auth-buttons {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-session {
  display: flex;
  align-items: center;
  gap: 18px;
}

.noti-bell {
  color: var(--zh-text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
}
.noti-bell:hover {
  color: var(--zh-primary);
}

.user-avatar-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 20px;
  transition: background 0.15s ease;
}

.user-avatar-trigger:hover {
  background: var(--zh-primary-light);
}

.avatar-circle {
  background: var(--zh-primary);
  color: #FFFFFF;
  font-weight: 600;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--zh-text-title);
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.role-tag {
  border-radius: 4px;
}
.brand-divider { font-weight:400; color:#a8b6aa; margin:0 3px; }
.mobile-nav-toggle { display:none; background:none; border:0; color:var(--zh-primary); cursor:pointer; font:inherit; padding:8px; }
.zh-nav-links { gap:24px; margin-left:20px; }
.logo-main { font-family:var(--zh-font-editorial); font-size:21px; font-weight:600; letter-spacing:.04em; }
.logo-sub { font-size:8px; letter-spacing:.14em; }
.nav-item { font-size:13px; }.nav-item.active::after { bottom:-22px; }
@media(max-width:1200px) { .nav-search { display:none; }.zh-nav-links { margin-left:0; gap:20px; } }
@media(max-width:860px) { .zh-nav-links { gap:14px; }.zh-nav-links .nav-item:nth-last-child(-n+2) { display:none; }.role-tag { display:none; }.zh-nav-container { padding:0 20px; }.logo-icon { width:30px; height:30px; }.zh-logo { gap:8px; } }
@media(max-width:620px) { .zh-navbar { height:68px; }.mobile-nav-toggle { display:block; margin-left:auto; margin-right:10px; }.zh-nav-links { display:none; }.zh-nav-links.mobile-open { display:flex; position:absolute; top:68px; left:0; right:0; padding:18px 20px; gap:22px; background:var(--zh-bg); border-bottom:1px solid var(--zh-border); flex-wrap:wrap; }.zh-nav-links.mobile-open .nav-item { display:block; }.nav-item.active::after { bottom:0; }.user-avatar-trigger .user-name,.user-avatar-trigger>.el-icon { display:none; }.user-session { gap:12px; }.logo-main { font-size:18px; }.auth-buttons { gap:2px; }.auth-buttons .el-button { padding:8px 10px; }.zh-nav-actions { gap:4px; } }
</style>
