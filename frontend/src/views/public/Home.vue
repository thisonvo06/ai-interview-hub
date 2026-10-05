<template>
  <div class="home-page editorial-home">
    <div class="journal-masthead"><span>THE CAREER JOURNAL</span><span>面试 · 求职 · 长期成长</span><span>从准备，到下一程</span></div>
    <section class="journal-hero">
      <div class="hero-copy">
        <p class="eyebrow"><span class="accent-dot"></span> 为你的职业旅程，留一页空白</p>
        <h1>好机会，<br />留给<span class="serif-accent">认真准备的你。</span></h1>
        <p class="hero-intro">把一次面试，写成下一次进步的起点。<br />发现岗位、练习表达、记录反馈，让成长有迹可循。</p>
        <div class="hero-actions">
          <router-link to="/personal/interviews/create" class="journal-button">开始一场模拟面试 <span>↗</span></router-link>
          <router-link to="/jobs" class="text-link">发现新的机会 <span>→</span></router-link>
        </div>
        <div class="hero-footnote"><span>01 / PREPARE</span><p>每一点准备，都会成为你下一步的底气。</p></div>
      </div>
      <div class="journal-cover" aria-label="职业成长流程示意">
        <div class="cover-top"><span>你的成长手记</span><span>VOL. 01</span></div>
        <div class="cover-orbit" aria-hidden="true"><div class="orbit o-one"></div><div class="orbit o-two"></div><div class="orbit o-three"></div><span class="orbit-center">向前</span><span class="orbit-note">A LITTLE BETTER,<br />EVERY DAY.</span><i class="orbit-dot"></i></div>
        <h2>让准备，<br />成为一种从容。</h2>
        <div class="cover-bottom"><span>发现 → 练习 → 复盘 → 成长</span><span>↗</span></div>
      </div>
    </section>
    <div class="journal-stats" aria-label="平台数据">
      <div v-for="item in statItems" :key="item.label"><strong>{{ stats[item.key] ?? '—' }}</strong><span>{{ item.label }}</span></div>
      <p>基于平台已登记数据<br /><span>招聘信息以企业官网为准</span></p>
    </div>
    <section class="journal-section">
      <div class="section-heading"><div><span class="eyebrow">01 — A SPACE TO GROW</span><h2>把成长，放进日常。</h2></div><router-link to="/features" class="text-link">了解全部功能 ↗</router-link></div>
      <div class="journal-features">
        <router-link v-for="feature in features" :key="feature.no" :to="feature.to" class="feature-entry">
          <div class="feature-index"><span>{{ feature.no }}</span><span>↗</span></div>
          <h3>{{ feature.title }}</h3><p>{{ feature.desc }}</p><span class="entry-category">{{ feature.category }}</span>
        </router-link>
      </div>
    </section>
    <section class="journal-section opportunities">
      <div class="section-heading"><div><span class="eyebrow">02 — THE NEXT CHAPTER</span><h2>看看，下一程的可能。</h2></div><router-link to="/jobs" class="text-link">浏览岗位广场 ↗</router-link></div>
      <div v-if="hotJobs.length" class="opportunity-list">
        <router-link v-for="(job, index) in hotJobs" :key="job.id" :to="`/jobs/${job.id}`" class="opportunity-row">
          <span class="opportunity-number">{{ String(index + 1).padStart(2, '0') }}</span>
          <div class="opportunity-title"><p>{{ job.company_name }} <span>· {{ job.city }}</span></p><h3>{{ job.title }}</h3></div>
          <div class="opportunity-tags"><span v-for="skill in (job.skills || []).slice(0, 3)" :key="skill">{{ skill }}</span></div>
          <span class="opportunity-salary">{{ job.salary_min }}–{{ job.salary_max }}<small>K / 月</small></span><span class="row-arrow">↗</span>
        </router-link>
      </div>
      <el-empty v-else :description="loadError ? '岗位信息暂时未能加载，请稍后重试' : '岗位陆续更新中'" />
      <p class="section-note">发现适合的岗位后，前往企业招聘官网完成投递。在这里记录进度，为每一步做好准备。</p>
    </section>
    <section class="journal-invitation"><span class="eyebrow">YOUR STORY CONTINUES</span><h2>下一次，<span>更接近你想成为的自己。</span></h2><router-link to="/personal/dashboard" class="journal-button">打开我的成长空间 ↗</router-link></section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { publicApi } from '@/api'
const stats = ref<Record<string, number>>({})
const hotJobs = ref<any[]>([])
const loadError = ref(false)
const statItems = [
  { key: 'verified_companies', label: '已认证企业' }, { key: 'published_jobs', label: '已发布岗位' },
  { key: 'active_talents', label: '注册求职者' }, { key: 'simulated_interviews', label: '已完成模拟面试' }
]
const features = [
  { no: '01', title: '练习一场面试', desc: '围绕目标岗位练习问答，从每一次反馈里，找到下一次表达的方向。', category: 'INTERVIEW / 面试练习', to: '/personal/interviews/create' },
  { no: '02', title: '打磨你的简历', desc: '整理经历与技能，让真实做过的事，在简历上被清楚地看见。', category: 'RESUME / 经历整理', to: '/personal/resumes' },
  { no: '03', title: '写下成长路线', desc: '把复盘中的薄弱点，转化为可以逐项完成的学习与练习任务。', category: 'GROWTH / 持续进步', to: '/personal/learning' }
]
onMounted(async () => {
  try { const res: any = await publicApi.getHome(); stats.value = res.stats || {}; hotJobs.value = (res.hot_jobs || []).slice(0, 4) }
  catch { loadError.value = true }
})
</script>

<style scoped>
.editorial-home { max-width: 1240px; margin: 0 auto; padding: 0 36px; }
.journal-masthead { display:flex; justify-content:space-between; padding:22px 0; border-bottom:1px solid var(--zh-border); font-size:11px; letter-spacing:.14em; color:var(--zh-text-muted); }
.journal-hero { display:grid; grid-template-columns:1.35fr .9fr; gap:72px; align-items:center; padding:72px 0 64px; }
.eyebrow { font-size:11px; letter-spacing:.13em; color:var(--zh-primary); font-weight:600; }
.hero-copy .eyebrow { display:flex; align-items:center; gap:10px; letter-spacing:.09em; }
.accent-dot { width:6px; height:6px; border-radius:50%; background:var(--zh-primary); }
.hero-copy h1 { font-family:var(--zh-font-editorial); font-size:clamp(36px,4.4vw,62px); line-height:1.45; letter-spacing:-.04em; font-weight:500; margin:22px 0 24px; }
.serif-accent { color:var(--zh-primary); }
.hero-intro { font-size:15px; line-height:2; color:var(--zh-text-muted); }
.hero-actions { display:flex; align-items:center; gap:28px; margin:32px 0 42px; flex-wrap:wrap; }
.journal-button { display:inline-flex; align-items:center; justify-content:space-between; gap:24px; padding:14px 22px; background:var(--zh-primary); color:white; border:1px solid var(--zh-primary); border-radius:4px; font-weight:500; transition:background .2s,transform .2s; }
.journal-button:hover { background:var(--zh-primary-hover); transform:translateY(-2px); }
.text-link { font-size:13px; color:var(--zh-text-title); padding:8px 0; border-bottom:1px solid var(--zh-border); white-space:nowrap; transition:color .2s,border-color .2s; }
.text-link:hover { color:var(--zh-primary); border-color:var(--zh-primary); }
.hero-footnote { display:flex; align-items:center; gap:20px; font-size:11px; color:var(--zh-text-muted); }
.hero-footnote>span { font-family:Georgia,serif; letter-spacing:.08em; padding-right:20px; border-right:1px solid var(--zh-border); }
.journal-cover { background:#e8eee8; min-height:452px; padding:28px 32px; position:relative; border:1px solid #d4dfd7; box-shadow:8px 8px 0 #eeeee7; overflow:hidden; }
.cover-top { display:flex; justify-content:space-between; font-size:11px; color:#466058; letter-spacing:.14em; }
.cover-orbit { position:absolute; width:240px; height:230px; top:65px; right:18px; }
.orbit { position:absolute; width:166px; height:166px; border:1px solid #88a699; border-radius:50%; }
.o-one { top:0; left:8px; }.o-two { top:40px; left:60px; }.o-three { top:70px; left:0; }
.orbit-center { position:absolute; top:95px; left:70px; font-family:var(--zh-font-editorial); font-size:24px; color:#436457; }
.orbit-note { position:absolute; right:0; bottom:0; font-size:8px; letter-spacing:.15em; color:#547669; }
.orbit-dot { position:absolute; top:32px; right:37px; width:9px; height:9px; background:#245d50; border-radius:50%; }
.journal-cover h2 { position:absolute; left:32px; bottom:88px; font-family:var(--zh-font-editorial); font-size:34px; font-weight:400; line-height:1.55; color:#284f42; }
.cover-bottom { display:flex; justify-content:space-between; position:absolute; bottom:28px; left:32px; right:32px; padding-top:16px; border-top:1px solid #b8c9bc; font-size:11px; color:#466058; }
.cover-bottom>span:last-child { font-size:20px; line-height:1; }
.journal-stats { display:grid; grid-template-columns:repeat(4,1fr) 1.5fr; padding:30px 0; border-top:1px solid var(--zh-border); border-bottom:1px solid var(--zh-border); gap:24px; }
.journal-stats>div { display:flex; flex-direction:column; gap:6px; }.journal-stats strong { font-family:Georgia,serif; font-weight:400; font-size:32px; color:var(--zh-text-title); }
.journal-stats span { font-size:11px; color:var(--zh-text-muted); }.journal-stats p { font-size:11px; line-height:1.9; text-align:right; align-self:center; color:var(--zh-text-muted); }
.journal-section { padding:64px 0 16px; }.section-heading { display:flex; align-items:end; justify-content:space-between; gap:24px; margin-bottom:28px; }.section-heading h2 { font-family:var(--zh-font-editorial); font-weight:500; font-size:32px; margin-top:10px; }
.journal-features { display:grid; grid-template-columns:repeat(3,1fr); gap:0; border-top:1px solid var(--zh-border); border-bottom:1px solid var(--zh-border); }
.feature-entry { padding:26px; border-right:1px solid var(--zh-border); transition:background .2s; }.feature-entry:first-child { padding-left:0; }.feature-entry:last-child { border:0; }.feature-entry:hover { background:#eef2eb; }.feature-index { display:flex; justify-content:space-between; color:var(--zh-primary); font-size:12px; margin-bottom:30px; font-family:Georgia,serif; }
.feature-entry h3 { font-family:var(--zh-font-editorial); font-size:24px; font-weight:500; margin-bottom:12px; }.feature-entry p { color:var(--zh-text-muted); font-size:13px; line-height:1.9; max-width:290px; }.entry-category { display:block; font-size:9px; letter-spacing:.11em; color:var(--zh-text-muted); margin-top:30px; }
.opportunity-list { border-top:1px solid var(--zh-border); }.opportunity-row { display:grid; grid-template-columns:36px 1.6fr 1fr 130px 24px; gap:24px; align-items:center; padding:26px 0; border-bottom:1px solid var(--zh-border); transition:background .2s; }.opportunity-row:hover { background:#edf2eb; }.opportunity-number { font-family:Georgia,serif; color:#9aaba1; font-size:13px; }.opportunity-title p { font-size:11px; color:var(--zh-primary); margin-bottom:7px; }.opportunity-title p span { color:var(--zh-text-muted); }.opportunity-title h3 { font-family:var(--zh-font-editorial); font-size:21px; font-weight:500; }.opportunity-tags { display:flex; flex-wrap:wrap; gap:8px; }.opportunity-tags>span { font-size:10px; border:1px solid var(--zh-border); padding:3px 8px; color:var(--zh-text-muted); border-radius:3px; }.opportunity-salary { font-family:Georgia,serif; font-size:22px; color:var(--zh-text-title); }.opportunity-salary small { display:block; font-family:var(--zh-font); font-size:10px; color:var(--zh-text-muted); margin-top:4px; }.row-arrow { color:var(--zh-primary); font-size:22px; }.section-note { font-size:11px; color:var(--zh-text-muted); margin-top:18px; line-height:1.8; }
.journal-invitation { margin:64px 0; padding:48px 0; border-top:1px solid var(--zh-border); text-align:center; }.journal-invitation h2 { font-family:var(--zh-font-editorial); font-size:30px; font-weight:400; margin:18px 0 26px; line-height:1.7; }.journal-invitation h2 span { color:var(--zh-primary); }
@media(max-width:1000px) { .journal-hero { gap:36px; }.opportunity-tags { display:none; }.opportunity-row { grid-template-columns:28px 1fr 110px 20px; }.journal-cover { min-height:420px; } }
@media(max-width:700px) { .editorial-home { padding:0 20px; }.journal-masthead { font-size:9px; }.journal-masthead>span:last-child { display:none; }.journal-hero { grid-template-columns:1fr; padding:40px 0; gap:32px; }.hero-copy h1 { font-size:38px; }.journal-cover { min-height:370px; }.hero-footnote { gap:12px; font-size:10px; }.journal-stats { grid-template-columns:repeat(2,1fr); gap:22px; }.journal-stats p { grid-column:1/-1; text-align:left; }.journal-features { grid-template-columns:1fr; }.feature-entry,.feature-entry:first-child { padding:24px 0; border-right:0; border-bottom:1px solid var(--zh-border); }.feature-index { margin-bottom:16px; }.entry-category { margin-top:16px; }.feature-entry p { max-width:100%; }.journal-section { padding-top:40px; }.section-heading { align-items:start; flex-direction:column; gap:12px; }.section-heading h2 { font-size:28px; }.opportunity-row { grid-template-columns:22px 1fr 80px; gap:12px; }.opportunity-title h3 { font-size:17px; }.opportunity-salary { font-size:19px; }.row-arrow { display:none; }.journal-invitation h2 { font-size:25px; }.journal-invitation h2 span { display:block; } }
@media(prefers-reduced-motion:reduce) { * { transition:none!important; } }
</style>
