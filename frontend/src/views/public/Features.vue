<template>
  <div class="features-page zh-page-container">
    <div class="page-header">
      <h1 class="page-title">系统核心功能与技术特色</h1>
      <p class="page-subtitle">全面覆盖“个人职业认知与训练—岗位探索投递—企业筛选面试—成长复盘”全流程双向闭环</p>
    </div>

    <div class="features-list">
      <div class="feature-item zh-card">
        <div class="item-text">
          <span class="tag blue">01 / 面试引擎</span>
          <h3>全真 AI 模拟面试仓 (U08-U11)</h3>
          <p>支持综合模拟、技术专项、项目深挖、行为面试与压力训练 5 种模式。集成 ASR 实时语音转写、动态出题与追问逻辑（FOLLOW_UP、DEEP、BASIC、CHANGE_TOPIC）。面试结束基于专业 Rubric（准确度、相关性、完整性、逻辑结构、实践深度、表达能力）输出五维能力雷达报告与可执行复盘建议。</p>
        </div>
      </div>

      <div class="feature-item zh-card">
        <div class="item-text">
          <span class="tag green">02 / 简历中枢</span>
          <h3>简历智能结构化解析与 AI 优化 (U04-U06)</h3>
          <p>支持 PDF/DOCX 简历文件秒级文本提取与 JSON Schema 严格校验。自动结构化提炼教育背景、工作经历、项目亮点与技能掌握度。AI 优化严守合规底线，仅润色真实表达与诊断缺失，绝不伪造经历或虚增项目数据。</p>
        </div>
      </div>

      <div class="feature-item zh-card">
        <div class="item-text">
          <span class="tag orange">03 / 能力与成长</span>
          <h3>能力诊断模型与长期技能轨迹 (U07, U12, U13)</h3>
          <p>个人能力画像与岗位胜任力模型可解释对比。能力差距按“差距 × 权重”动态排序，自动生成个性化学习路线与训练任务。成长中心真实沉淀每次面试的历史技能变迁（如 Redis 43 → 52 → 61 → 76），见证每一个台阶的进步。</p>
        </div>
      </div>

      <div class="feature-item zh-card">
        <div class="item-text">
          <span class="tag purple">04 / 企业协作</span>
          <h3>敏捷招聘协作与人岗双向匹配 (E01-E15)</h3>
          <p>企业一键 AI JD 解析、自动生成能力权重。HR 批量初筛候选人、发出企业 AI 面试邀请。面试官与用人经理开展结构化打分与录用建议。在敏捷看板上无缝推进招聘流程，全流程操作留痕与消息自动通知。</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.features-page {
  padding: 48px 20px 80px;
}
.page-header {
  text-align: center;
  margin-bottom: 48px;
}
.page-title {
  font-size: 32px;
  font-weight: 800;
  color: var(--zh-text-title);
  margin-bottom: 12px;
}
.page-subtitle {
  font-size: 15px;
  color: var(--zh-text-muted);
}
.features-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 900px;
  margin: 0 auto;
}
.feature-item {
  padding: 32px;
}
.tag {
  display: inline-block;
  font-size: 12px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 4px;
  margin-bottom: 12px;
}
.blue { background: #EFF6FF; color: #2563EB; }
.green { background: #ECFDF5; color: #059669; }
.orange { background: #FFFBEB; color: #D97706; }
.purple { background: #F5F3FF; color: #7C3AED; }
h3 {
  font-size: 20px;
  font-weight: 700;
  color: var(--zh-text-title);
  margin-bottom: 12px;
}
p {
  font-size: 14px;
  color: var(--zh-text-body);
  line-height: 1.75;
}
</style>
