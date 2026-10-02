<template>
  <div class="bookmarks-page">
    <div class="page-header">
      <h2 class="page-title">我的收藏夹</h2>
      <p class="page-desc">面试报告中收藏的题目，集中回顾</p>
    </div>

    <div v-if="bookmarks.length === 0" class="empty-state">
      <el-empty description="暂无收藏题目">
        <p class="empty-tip">在面试报告 → 逐题深度复盘 中点击 ⭐ 收藏题目</p>
        <router-link to="/personal/interviews">
          <el-button type="primary">去看面试记录</el-button>
        </router-link>
      </el-empty>
    </div>

    <div v-else class="bookmark-list">
      <div
        v-for="(item, idx) in bookmarks"
        :key="idx"
        class="bookmark-card"
      >
        <div class="bk-header">
          <span class="bk-seq">第 {{ item.seq }} 题</span>
          <span class="bk-skill">{{ item.skill_name }}</span>
          <span :class="['bk-score', item.score >= 80 ? 'green' : item.score >= 60 ? 'amber' : 'red']">
            {{ item.score }} 分
          </span>
          <button class="bk-remove-btn" @click="removeBookmark(idx)" title="取消收藏">
            <el-icon :size="16"><Delete /></el-icon>
          </button>
        </div>
        <p class="bk-question">{{ item.question }}</p>
        <div class="bk-footer">
          <router-link :to="'/interviews/' + item.reportId + '/report'">
            <el-button link type="primary" size="small">查看来源报告 →</el-button>
          </router-link>
          <span class="bk-time">{{ formatTime(item.savedAt) }}</span>
        </div>
      </div>
    </div>

    <div v-if="bookmarks.length > 0" class="clear-bar">
      <el-button text type="danger" size="small" @click="clearAll">
        清空全部收藏 ({{ bookmarks.length }} 题)
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Delete } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'

interface BookmarkEntry {
  reportId: number
  seq: number
  question: string
  skill_name: string
  score: number
  savedAt: string
}

const BM_KEY = 'zhimeicang_bookmarks'
const bookmarks = ref<BookmarkEntry[]>([])

const load = () => {
  try {
    bookmarks.value = JSON.parse(localStorage.getItem(BM_KEY) || '[]')
  } catch {
    bookmarks.value = []
  }
}

const removeBookmark = (idx: number) => {
  bookmarks.value.splice(idx, 1)
  bookmarks.value = [...bookmarks.value]
  localStorage.setItem(BM_KEY, JSON.stringify(bookmarks.value))
}

const clearAll = () => {
  ElMessageBox.confirm('确定清空全部收藏吗？', '确认', {
    type: 'warning',
    confirmButtonText: '确定清空'
  }).then(() => {
    bookmarks.value = []
    localStorage.removeItem(BM_KEY)
  })
}

const formatTime = (iso: string) => {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleString('zh-CN', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

onMounted(load)
</script>

<style scoped>
.bookmarks-page {
  max-width: 860px;
  margin: 0 auto;
}
.page-header {
  margin-bottom: 24px;
}
.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #0F2347;
  margin: 0 0 4px;
}
.page-desc {
  font-size: 14px;
  color: #64748B;
  margin: 0;
}
.empty-state {
  margin-top: 40px;
}
.empty-tip {
  font-size: 13px;
  color: #94A3B8;
  margin: 4px 0 16px;
}
.bookmark-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.bookmark-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 10px;
  padding: 16px 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,.04);
}
.bk-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
.bk-seq {
  font-size: 12px;
  font-weight: 600;
  color: #64748B;
  background: #F1F5F9;
  padding: 2px 8px;
  border-radius: 4px;
}
.bk-skill {
  font-size: 12px;
  color: #3B82F6;
  background: #EFF6FF;
  padding: 2px 8px;
  border-radius: 4px;
}
.bk-score {
  font-size: 13px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
}
.bk-score.green { color: #16A34A; background: #DCFCE7; }
.bk-score.amber { color: #D97706; background: #FEF3C7; }
.bk-score.red   { color: #DC2626; background: #FEE2E2; }
.bk-remove-btn {
  margin-left: auto;
  background: none;
  border: none;
  cursor: pointer;
  color: #94A3B8;
  padding: 2px;
}
.bk-remove-btn:hover { color: #EF4444; }
.bk-question {
  font-size: 14px;
  color: #1E293B;
  line-height: 1.6;
  margin: 0 0 10px;
}
.bk-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.bk-time {
  font-size: 11px;
  color: #94A3B8;
}
.clear-bar {
  margin-top: 20px;
  text-align: right;
}
</style>