import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Layouts
const PublicLayout = () => import('@/layouts/PublicLayout.vue')
const PersonalLayout = () => import('@/layouts/PersonalLayout.vue')
const EnterpriseLayout = () => import('@/layouts/EnterpriseLayout.vue')
const AdminLayout = () => import('@/layouts/AdminLayout.vue')

// Error views
const NotFound = () => import('@/views/error/NotFound.vue')
const Forbidden = () => import('@/views/error/Forbidden.vue')

// Auth views
const Login = () => import('@/views/auth/Login.vue')
const RegisterSelect = () => import('@/views/auth/RegisterSelect.vue')
const RegisterPersonal = () => import('@/views/auth/RegisterPersonal.vue')
const RegisterEnterprise = () => import('@/views/auth/RegisterEnterprise.vue')
const Onboarding = () => import('@/views/auth/Onboarding.vue')
const ForgotPassword = () => import('@/views/auth/ForgotPassword.vue')
const AdminLogin = () => import('@/views/auth/AdminLogin.vue')
const AISetup = () => import('@/views/auth/AISetup.vue')

// Public views
const Home = () => import('@/views/public/Home.vue')
const JobSquare = () => import('@/views/public/JobSquare.vue')
const JobDetail = () => import('@/views/public/JobDetail.vue')
const CompanyPublic = () => import('@/views/public/CompanyPublic.vue')
const Features = () => import('@/views/public/Features.vue')
const About = () => import('@/views/public/About.vue')
const Help = () => import('@/views/public/Help.vue')

// Personal views
const PersonalDashboard = () => import('@/views/personal/Dashboard.vue')
const JobExplore = () => import('@/views/personal/JobExplore.vue')
const JobSearchWorkspace = () => import('@/views/personal/JobSearchWorkspace.vue')
const Applications = () => import('@/views/personal/Applications.vue')
const Resumes = () => import('@/views/personal/Resumes.vue')
const ResumeEdit = () => import('@/views/personal/ResumeEdit.vue')
const ResumeAnalysis = () => import('@/views/personal/ResumeAnalysis.vue')
const Assessment = () => import('@/views/personal/Assessment.vue')
const InterviewCreate = () => import('@/views/personal/InterviewCreate.vue')
const InterviewSession = () => import('@/views/personal/InterviewSession.vue')
const InterviewsList = () => import('@/views/personal/InterviewsList.vue')
const InterviewReportView = () => import('@/views/personal/InterviewReportView.vue')
const GrowthCenter = () => import('@/views/personal/GrowthCenter.vue')
const LearningRoadmap = () => import('@/views/personal/LearningRoadmap.vue')
const Notifications = () => import('@/views/personal/Notifications.vue')
const Profile = () => import('@/views/personal/Profile.vue')
const Settings = () => import('@/views/personal/Settings.vue')
const BookmarkedQuestions = () => import('@/views/personal/BookmarkedQuestions.vue')

// Enterprise views
const EnterpriseDashboard = () => import('@/views/enterprise/Dashboard.vue')
const EnterpriseJobs = () => import('@/views/enterprise/Jobs.vue')
const JobCreate = () => import('@/views/enterprise/JobCreate.vue')
const JobEdit = () => import('@/views/enterprise/JobEdit.vue')
const Candidates = () => import('@/views/enterprise/Candidates.vue')
const CandidateDetail = () => import('@/views/enterprise/CandidateDetail.vue')
const PipelineKanban = () => import('@/views/enterprise/PipelineKanban.vue')
const EnterpriseInterviews = () => import('@/views/enterprise/Interviews.vue')
const Evaluation = () => import('@/views/enterprise/Evaluation.vue')
const TalentPool = () => import('@/views/enterprise/TalentPool.vue')
const Analytics = () => import('@/views/enterprise/Analytics.vue')
const Members = () => import('@/views/enterprise/Members.vue')
const EnterpriseSettings = () => import('@/views/enterprise/Settings.vue')

// Admin views
const AdminDashboard = () => import('@/views/admin/Dashboard.vue')
const AdminUsers = () => import('@/views/admin/Users.vue')
const AdminCompanies = () => import('@/views/admin/Companies.vue')
const AdminVerifications = () => import('@/views/admin/Verifications.vue')
const AdminJobReview = () => import('@/views/admin/JobReview.vue')
const AdminComplaints = () => import('@/views/admin/Complaints.vue')
const AdminContent = () => import('@/views/admin/Content.vue')
const AdminQuestionBank = () => import('@/views/admin/QuestionBank.vue')
const AdminAIService = () => import('@/views/admin/AIService.vue')
const AdminSecurityAudit = () => import('@/views/admin/SecurityAudit.vue')

const routes: RouteRecordRaw[] = [
  // 公共门户
  {
    path: '/',
    component: PublicLayout,
    children: [
      { path: '', name: 'Home', component: Home, meta: { title: '智面舱 - AI 智能面试协同平台' } },
      { path: 'jobs', name: 'JobSquare', component: JobSquare, meta: { title: '职位广场' } },
      { path: 'jobs/:id', name: 'JobDetail', component: JobDetail, meta: { title: '职位详情' } },
      { path: 'companies/:id', name: 'CompanyPublic', component: CompanyPublic, meta: { title: '企业主页' } },
      { path: 'features', name: 'Features', component: Features, meta: { title: '核心特性' } },
      { path: 'about', name: 'About', component: About, meta: { title: '关于智面舱' } },
      { path: 'help', name: 'Help', component: Help, meta: { title: '帮助支持' } },
    ]
  },

  // 认证流程
  { path: '/login', name: 'Login', component: Login, meta: { title: '用户登录', guestOnly: true } },
  { path: '/register', name: 'RegisterSelect', component: RegisterSelect, meta: { title: '注册选择', guestOnly: true } },
  { path: '/register/personal', name: 'RegisterPersonal', component: RegisterPersonal, meta: { title: '求职者注册', guestOnly: true } },
  { path: '/register/enterprise', name: 'RegisterEnterprise', component: RegisterEnterprise, meta: { title: '企业雇主注册', guestOnly: true } },
  { path: '/onboarding', name: 'Onboarding', component: Onboarding, meta: { title: '新用户入驻指引', requiresAuth: true } },
  { path: '/forgot-password', name: 'ForgotPassword', component: ForgotPassword, meta: { title: '找回密码' } },
  { path: '/admin/login', name: 'AdminLogin', component: AdminLogin, meta: { title: '平台治理后台登录' } },
  { path: '/ai-setup', name: 'AISetup', component: AISetup, meta: { title: 'AI 引擎初始化配置' } },

  // 独立全屏沉浸式路由 (模拟面试间与报告)
  {
    path: '/personal/interviews/:id/room',
    name: 'PersonalInterviewSession',
    component: InterviewSession,
    meta: { requiresAuth: true, accountType: 'PERSONAL', title: 'AI 实时模拟面试间' }
  },
  {
    path: '/interviews/:id/report',
    name: 'InterviewReport',
    component: InterviewReportView,
    meta: { requiresAuth: true, title: '面试答题诊断报告' }
  },

  // 个人求职者工作台
  {
    path: '/personal',
    component: PersonalLayout,
    meta: { requiresAuth: true, accountType: 'PERSONAL' },
    children: [
      { path: '', redirect: '/personal/dashboard' },
      { path: 'dashboard', name: 'PersonalDashboard', component: PersonalDashboard, meta: { title: '求职者工作台' } },
      { path: 'jobs', name: 'PersonalJobExplore', component: JobExplore, meta: { title: '智能岗位探索' } },
      { path: 'job-search', name: 'PersonalJobSearch', component: JobSearchWorkspace, meta: { title: '求职计划' } },
      { path: 'applications', name: 'PersonalApplications', component: Applications, meta: { title: '我的应聘申请' } },
      { path: 'resumes', name: 'PersonalResumes', component: Resumes, meta: { title: '我的简历中心' } },
      { path: 'resumes/create', name: 'PersonalResumeCreate', component: ResumeEdit, meta: { title: '创建在线简历' } },
      { path: 'resumes/:id/edit', name: 'PersonalResumeEdit', component: ResumeEdit, meta: { title: '编辑简历' } },
      { path: 'resumes/:id/analysis', name: 'PersonalResumeAnalysis', component: ResumeAnalysis, meta: { title: '简历 AI 诊断优化' } },
      { path: 'assessment', name: 'PersonalAssessment', component: Assessment, meta: { title: '六维胜任力诊断' } },
      { path: 'interviews', name: 'PersonalInterviewsList', component: InterviewsList, meta: { title: '我的模拟面试' } },
      { path: 'interviews/create', name: 'PersonalInterviewCreate', component: InterviewCreate, meta: { title: '创建模拟面试' } },
      { path: 'growth', name: 'PersonalGrowth', component: GrowthCenter, meta: { title: '个人成长中心' } },
      { path: 'learning', name: 'PersonalLearning', component: LearningRoadmap, meta: { title: 'AI 学习路线图' } },
      { path: 'bookmarks', name: 'PersonalBookmarks', component: BookmarkedQuestions, meta: { title: '我的收藏夹' } },
      { path: 'notifications', name: 'PersonalNotifications', component: Notifications, meta: { title: '消息通知' } },
      { path: 'profile', name: 'PersonalProfile', component: Profile, meta: { title: '求职意向与资料' } },
      { path: 'settings', name: 'PersonalSettings', component: Settings, meta: { title: '账号与安全设置' } },
    ]
  },

  // 企业招聘协作中心
  {
    path: '/enterprise',
    component: EnterpriseLayout,
    meta: { requiresAuth: true, accountType: 'ENTERPRISE' },
    children: [
      { path: '', redirect: '/enterprise/dashboard' },
      { path: 'dashboard', name: 'EnterpriseDashboard', component: EnterpriseDashboard, meta: { title: '企业招聘工作台' } },
      { path: 'jobs', name: 'EnterpriseJobs', component: EnterpriseJobs, meta: { title: '职位管理' } },
      { path: 'jobs/create', name: 'EnterpriseJobCreate', component: JobCreate, meta: { title: '发布职位 (AI-JD)' } },
      { path: 'jobs/:id/edit', name: 'EnterpriseJobEdit', component: JobEdit, meta: { title: '编辑职位' } },
      { path: 'candidates', name: 'EnterpriseCandidates', component: Candidates, meta: { title: '候选人管理' } },
      { path: 'candidates/:id', name: 'EnterpriseCandidateDetail', component: CandidateDetail, meta: { title: '候选人全貌档案' } },
      { path: 'pipeline', name: 'EnterprisePipeline', component: PipelineKanban, meta: { title: '招聘管道看板' } },
      { path: 'interviews', name: 'EnterpriseInterviews', component: EnterpriseInterviews, meta: { title: '面试管理' } },
      { path: 'evaluations', name: 'EnterpriseEvaluation', component: Evaluation, meta: { title: '面试官结构化打分' } },
      { path: 'talent-pool', name: 'EnterpriseTalentPool', component: TalentPool, meta: { title: '企业储备人才库' } },
      { path: 'analytics', name: 'EnterpriseAnalytics', component: Analytics, meta: { title: '招聘数据分析中心' } },
      { path: 'members', name: 'EnterpriseMembers', component: Members, meta: { title: '团队成员与权限' } },
      { path: 'settings', name: 'EnterpriseSettings', component: EnterpriseSettings, meta: { title: '企业资料与实名认证' } },
    ]
  },

  // 平台管理后台
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, roles: ['PLATFORM_ADMIN', 'SUPER_ADMIN'] },
    children: [
      { path: '', redirect: '/admin/dashboard' },
      { path: 'dashboard', name: 'AdminDashboard', component: AdminDashboard, meta: { title: '平台运营总览' } },
      { path: 'users', name: 'AdminUsers', component: AdminUsers, meta: { title: '全平台用户治理' } },
      { path: 'companies', name: 'AdminCompanies', component: AdminCompanies, meta: { title: '企业治理' } },
      { path: 'verifications', name: 'AdminVerifications', component: AdminVerifications, meta: { title: '企业资质审核' } },
      { path: 'jobs/review', name: 'AdminJobReview', component: AdminJobReview, meta: { title: '岗位审核与下架' } },
      { path: 'jobs-review', redirect: '/admin/jobs/review' },
      { path: 'complaints', name: 'AdminComplaints', component: AdminComplaints, meta: { title: '举报投诉处置' } },
      { path: 'content', name: 'AdminContent', component: AdminContent, meta: { title: '门户内容运营' } },
      { path: 'question-bank', name: 'AdminQuestionBank', component: AdminQuestionBank, meta: { title: '结构化题库管理' } },
      { path: 'ai', name: 'AdminAIService', component: AdminAIService, meta: { title: 'AI 引擎与脱敏日志' } },
      { path: 'security', name: 'AdminSecurityAudit', component: AdminSecurityAudit, meta: { title: '安全与操作审计' } },
    ]
  },

  // 错误路由
  { path: '/403', name: 'Forbidden', component: Forbidden, meta: { title: '403 无访问权限' } },
  { path: '/404', name: 'NotFound', component: NotFound, meta: { title: '404 页面未找到' } },
  { path: '/:pathMatch(.*)*', redirect: '/404' }
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

// Navigation Guard
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()

  // Set document title
  if (to.meta.title) {
    document.title = `${to.meta.title} - 智面舱`
  }

  // Check guestOnly routes (e.g. login/register when already logged in)
  if (to.meta.guestOnly && authStore.isAuthenticated) {
    if (authStore.isAdmin) return next('/admin/dashboard')
    if (authStore.isEnterprise) return next('/enterprise/dashboard')
    return next('/personal/dashboard')
  }

  // Check requiresAuth
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      if (to.path.startsWith('/admin')) {
        return next({ path: '/admin/login', query: { redirect: to.fullPath } })
      }
      return next({ path: '/login', query: { redirect: to.fullPath } })
    }

    // Role check for admin
    if (to.meta.roles && Array.isArray(to.meta.roles)) {
      const userRoles = authStore.user?.roles || []
      const hasRole = to.meta.roles.some((r: string) => userRoles.includes(r))
      if (!hasRole) {
        return next('/403')
      }
    }

    // Account type check
    if (to.meta.accountType) {
      if (authStore.user?.account_type !== to.meta.accountType) {
        return next('/403')
      }
    }
  }

  next()
})

export default router
