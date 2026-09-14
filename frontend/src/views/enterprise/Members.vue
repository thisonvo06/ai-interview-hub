<template>
  <div class="enterprise-members-page">
    <div class="page-header">
      <div>
        <h2 class="page-title">企业团队与角色权限</h2>
        <p class="page-subtitle">管理招聘团队成员架构，细粒度分配 HR、业务面试官与管理员职责权限</p>
      </div>
      <el-button type="primary" @click="showInviteDialog = true">
        <el-icon style="margin-right: 4px;"><Plus /></el-icon> 邀请团队新成员
      </el-button>
    </div>

    <!-- 成员列表表格 -->
    <StateContainer :loading="loading" :error="error" :empty="members.length === 0" @retry="fetchMembers">
      <div class="table-card">
        <el-table :data="members" style="width: 100%;">
          <el-table-column prop="name" label="姓名" min-width="140">
            <template #default="{ row }">
              <div class="member-name">{{ row.user?.profile?.name || row.user?.name || `成员 #${row.id}` }}</div>
              <div class="member-email">{{ row.user?.email }}</div>
            </template>
          </el-table-column>

          <el-table-column prop="department" label="所属部门" width="160">
            <template #default="{ row }">
              <span>{{ row.department?.name || '技术招聘组' }}</span>
            </template>
          </el-table-column>

          <el-table-column prop="role" label="协作角色" width="160">
            <template #default="{ row }">
              <el-tag :type="getRoleTag(row.role)">{{ getRoleLabel(row.role) }}</el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="created_at" label="加入时间" width="140">
            <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
          </el-table-column>

          <el-table-column label="操作" width="180" fixed="right" align="right">
            <template #default="{ row }">
              <el-button
                v-if="row.role !== 'OWNER'"
                type="primary"
                link
                size="small"
                @click="openChangeRole(row)"
              >
                变更角色
              </el-button>
              <el-button
                v-if="row.role !== 'OWNER'"
                type="danger"
                link
                size="small"
                @click="handleRemoveMember(row.id)"
              >
                移除
              </el-button>
              <span v-else style="color: #94A3B8; font-size: 13px;">超级所有者</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </StateContainer>

    <!-- 邀请成员弹窗 -->
    <el-dialog v-model="showInviteDialog" title="邀请团队新成员加入" width="500px">
      <el-form :model="inviteForm" :rules="inviteRules" ref="inviteFormRef" label-position="top">
        <el-form-item label="成员注册邮箱" prop="email">
          <el-input v-model="inviteForm.email" placeholder="输入成员登录邮箱，系统将自动绑定" />
        </el-form-item>
        <el-form-item label="所属部门" prop="department_id">
          <el-select v-model="inviteForm.department_id" style="width: 100%;">
            <el-option label="技术研发部" :value="1" />
            <el-option label="算法与大数据中心" :value="2" />
            <el-option label="人力资源协同部" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="分配权限角色" prop="role">
          <el-select v-model="inviteForm.role" style="width: 100%;">
            <el-option label="HR 招聘负责人 (发布职位、管理候选人、发邀约)" value="HR" />
            <el-option label="业务面试官 (查看候选人简历、评测打分)" value="INTERVIEWER" />
            <el-option label="企业管理员 (全权限)" value="OWNER" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showInviteDialog = false">取消</el-button>
        <el-button type="primary" :loading="inviting" @click="handleConfirmInvite">发送加入通知</el-button>
      </template>
    </el-dialog>

    <!-- 修改角色弹窗 -->
    <el-dialog v-model="showRoleDialog" title="调整成员权限角色" width="400px">
      <el-form label-position="top">
        <el-form-item label="当前成员">
          <div style="font-weight: 600;">{{ currentMember?.user?.name }} ({{ currentMember?.user?.email }})</div>
        </el-form-item>
        <el-form-item label="目标角色">
          <el-select v-model="targetRole" style="width: 100%;">
            <el-option label="HR 招聘负责人" value="HR" />
            <el-option label="业务面试官" value="INTERVIEWER" />
            <el-option label="企业联合创建人" value="OWNER" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRoleDialog = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmChangeRole">确认调整</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import StateContainer from '@/components/StateContainer.vue'
import { enterpriseApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const error = ref('')
const members = ref<any[]>([])

const fetchMembers = async () => {
  loading.value = true
  error.value = ''
  try {
    const res: any = await enterpriseApi.listMembers()
    members.value = res || []
  } catch (err: any) {
    error.value = err.response?.data?.detail || '获取成员列表失败'
  } finally {
    loading.value = false
  }
}

// 邀请新成员
const showInviteDialog = ref(false)
const inviting = ref(false)
const inviteFormRef = ref()
const inviteForm = reactive({
  email: '',
  department_id: 1,
  role: 'HR'
})

const inviteRules = {
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }]
}

const handleConfirmInvite = async () => {
  if (!inviteFormRef.value) return
  await inviteFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    inviting.value = true
    try {
      await enterpriseApi.inviteMember(inviteForm)
      ElMessage.success('成员邀请已发送并加入企业')
      showInviteDialog.value = false
      fetchMembers()
    } catch (err: any) {
      ElMessage.error(err.response?.data?.detail || '邀请失败')
    } finally {
      inviting.value = false
    }
  })
}

// 调整角色
const showRoleDialog = ref(false)
const currentMember = ref<any>(null)
const targetRole = ref('HR')

const openChangeRole = (member: any) => {
  currentMember.value = member
  targetRole.value = member.role
  showRoleDialog.value = true
}

const handleConfirmChangeRole = async () => {
  if (!currentMember.value) return
  try {
    await enterpriseApi.updateMember(currentMember.value.id, { role: targetRole.value })
    ElMessage.success('角色权限已更新')
    showRoleDialog.value = false
    fetchMembers()
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '更新角色失败')
  }
}

// 移除成员
const handleRemoveMember = (id: number) => {
  ElMessageBox.confirm('确定将该成员移出企业吗？移出后其将无法访问企业任何数据。', '移除确认', {
    type: 'error'
  }).then(async () => {
    try {
      await enterpriseApi.removeMember(id)
      ElMessage.success('成员已移除')
      fetchMembers()
    } catch (err: any) {
      ElMessage.error(err.response?.data?.detail || '移除失败')
    }
  })
}

const getRoleTag = (role: string) => {
  switch (role) {
    case 'OWNER': return 'danger'
    case 'HR': return 'primary'
    case 'INTERVIEWER': return 'warning'
    default: return 'info'
  }
}

const getRoleLabel = (role: string) => {
  switch (role) {
    case 'OWNER': return '企业所有者'
    case 'HR': return 'HR 招聘负责人'
    case 'INTERVIEWER': return '业务面试官'
    default: return role || '协同成员'
  }
}

const formatDate = (val: string) => {
  if (!val) return '-'
  return new Date(val).toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchMembers()
})
</script>

<style scoped>
.enterprise-members-page {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.table-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #F1F5F9;
}

.member-name {
  font-size: 14px;
  font-weight: 600;
  color: #1E293B;
}

.member-email {
  font-size: 12px;
  color: #64748B;
  margin-top: 2px;
}
</style>
