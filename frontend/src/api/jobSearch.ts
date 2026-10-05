import client from './client'
import type { Opportunity, OpportunityCollection, OpportunityInput, OpportunityPatch, OpportunityAnalysis, OpportunityPrep } from '@/types/jobSearch'
const root = '/personal/job-search'
export const jobSearchApi = {
  list: () => client.get<any, OpportunityCollection>(root),
  create: (data: OpportunityInput) => client.post<any, { item: Opportunity; duplicate: boolean }>(root, data),
  savePlatformJob: (id: number) => client.post<any, { item: Opportunity; duplicate: boolean }>(`${root}/from-job/${id}`),
  get: (id: number) => client.get<any, Opportunity>(`${root}/${id}`),
  update: (id: number, data: OpportunityPatch) => client.patch<any, Opportunity>(`${root}/${id}`, data),
  analyze: (id: number, resume_id?: number) => client.post<any, { item: Opportunity; analysis: OpportunityAnalysis }>(`${root}/${id}/analyze`, { resume_id }),
  prepare: (id: number, resume_id?: number) => client.post<any, { item: Opportunity; prep: OpportunityPrep }>(`${root}/${id}/prepare`, { resume_id }),
  followUp: (id: number, version: number) => client.post<any, Opportunity>(`${root}/${id}/follow-up`, { version }),
  remove: (id: number) => client.delete(`${root}/${id}`),
}
