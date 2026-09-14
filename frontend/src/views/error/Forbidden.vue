<template>
  <div class="error-page">
    <el-result
      icon="warning"
      title="403 权限受控拒绝"
      sub-title="您无权访问该资源（如跨企业候选人、他人私人训练记录或越权操作）。"
    >
      <template #extra>
        <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
        <el-button @click="$router.back()">后退一页</el-button>
      </template>
    </el-result>
  </div>
</template>

<style scoped>
.error-page {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
