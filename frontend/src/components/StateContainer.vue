<template>
  <div class="state-container">
    <!-- Loading State: Skeleton -->
    <div v-if="loading" class="state-loading">
      <el-skeleton :rows="skeletonRows" animated />
    </div>

    <!-- Forbidden State (403) -->
    <div v-else-if="forbidden" class="state-forbidden">
      <el-result
        icon="warning"
        title="403 权限不足"
        :sub-title="forbiddenMsg || '您无权访问当前企业范围或敏感数据，请返回可访问页面。'"
      >
        <template #extra>
          <el-button type="primary" @click="handleGoHome">返回工作台</el-button>
        </template>
      </el-result>
    </div>

    <!-- Error State -->
    <div v-else-if="hasError" class="state-error">
      <el-result
        icon="error"
        title="数据加载失败"
        :sub-title="computedErrorMsg"
      >
        <template #extra>
          <el-button type="primary" @click="$emit('retry')">重新加载</el-button>
        </template>
      </el-result>
    </div>

    <!-- Empty State -->
    <div v-else-if="empty" class="state-empty">
      <el-empty :description="emptyText || '暂无相关数据记录'">
        <el-button v-if="emptyActionText" type="primary" @click="$emit('empty-action')">
          {{ emptyActionText }}
        </el-button>
      </el-empty>
    </div>

    <!-- Default Content Slot -->
    <div v-else class="state-content">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const props = withDefaults(defineProps<{
  loading?: boolean
  empty?: boolean
  error?: string | boolean | any
  forbidden?: boolean
  skeletonRows?: number
  emptyText?: string
  emptyActionText?: string
  errorMsg?: string
  forbiddenMsg?: string
}>(), {
  loading: false,
  empty: false,
  error: false,
  forbidden: false,
  skeletonRows: 6,
  emptyText: '暂无数据',
  emptyActionText: '',
  errorMsg: '',
  forbiddenMsg: ''
})

const hasError = computed(() => {
  if (props.error === true) return true
  if (typeof props.error === 'string' && props.error.trim().length > 0) return true
  return false
})

const computedErrorMsg = computed(() => {
  if (typeof props.error === 'string' && props.error) {
    return props.error
  }
  return props.errorMsg || '服务响应异常，请点击下方按钮重新尝试。'
})

defineEmits(['retry', 'empty-action'])

const router = useRouter()
const authStore = useAuthStore()

const handleGoHome = () => {
  if (authStore.isPersonal) {
    router.push('/personal/dashboard')
  } else if (authStore.isEnterprise) {
    router.push('/enterprise/dashboard')
  } else if (authStore.isAdmin) {
    router.push('/admin/dashboard')
  } else {
    router.push('/')
  }
}
</script>

<style scoped>
.state-container {
  width: 100%;
}
.state-loading {
  padding: 32px 20px;
}
.state-empty, .state-error, .state-forbidden {
  padding: 48px 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
