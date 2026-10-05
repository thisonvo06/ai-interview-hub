export type OpportunityStatus = 'SAVED' | 'PREPARING' | 'USER_SUBMITTED' | 'INTERVIEWING' | 'OFFER' | 'REJECTED' | 'CLOSED'
export interface OpportunityAnalysis {
  source: 'RULE'; resume_id: number | null; resume_title: string | null; skill_coverage: number | null
  matched_skills: string[]; missing_skills: string[]; evidence: { skill: string; source: string; text: string }[]
  checks: { name: string; verdict: 'PASS' | 'FAIL' | 'UNKNOWN' | 'FLAG'; detail: string }[]
  recommendation: 'PRIORITIZE' | 'PREPARE' | 'REVIEW' | 'EXPIRED'; explanation: string; analyzed_at: string
}
export interface OpportunityPrep {
  source: 'RULE'; resume_id: number | null; generated_at: string; cover_letter: string; follow_up_draft: string
  interview_questions: string[]; star_examples: { project_name: string; situation: string; task: string; action: string; result: string }[]
  resume_highlights: string[]; checklist: string[]
}
export interface Opportunity {
  id: number; version: number; title: string; company_name: string; location: string | null; salary_note: string | null
  source_url: string | null; jd_text: string; required_skills: string[]; experience_years: number | null
  deadline: string | null; status: OpportunityStatus; note: string | null; feedback: string | null
  next_follow_up: string | null; follow_up_count: number; created_at: string; updated_at: string
  history: { to_status?: OpportunityStatus; note?: string; created_at: string }[]
  analysis?: OpportunityAnalysis | null; prep?: OpportunityPrep | null
  deadline_state: 'NONE' | 'CLOSING_SOON' | 'EXPIRED' | 'OPEN'; follow_up_due: boolean
}
export interface OpportunityInput {
  title: string; company_name: string; location?: string; salary_note?: string; source_url?: string; jd_text: string
  required_skills: string[]; experience_years?: number; deadline?: string
}
export interface OpportunityPatch {
  version: number; status?: OpportunityStatus; note?: string; feedback?: string; next_follow_up?: string | null; deadline?: string | null
}
export interface OpportunityCollection {
  items: Opportunity[]
  summary: { total: number; active: number; submitted: number; interviewing: number; offers: number; due_follow_ups: number; closing_soon: number }
  gaps: { skill: string; count: number; opportunity_ids: number[]; suggested_action: string }[]
}
