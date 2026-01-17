import { api } from "./axios";
import type {
  Deal,
  DealCreateRequest,
  DealUpdateRequest,
  DealMoveRequest,
  Activity,
  PipelineSummary,
  PaginationParams,
  ICMemo,
} from "../types";

export const dealsAPI = {
  // CRUD Operations
  create: async (dealData: DealCreateRequest): Promise<Deal> => {
    const response = await api.post("/deals", dealData);
    return response.data;
  },

  getAll: async (params?: PaginationParams): Promise<Deal[]> => {
    const response = await api.get("/deals", { params });
    return response.data;
  },

  getById: async (id: number): Promise<Deal> => {
    const response = await api.get(`/deals/${id}`);
    return response.data;
  },

  update: async (id: number, dealData: DealUpdateRequest): Promise<Deal> => {
    const response = await api.put(`/deals/${id}`, dealData);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/deals/${id}`);
  },

  // Pipeline Operations
  moveToStage: async (id: number, moveData: DealMoveRequest): Promise<{ deal: Deal; activity: Activity }> => {
    const response = await api.post(`/deals/${id}/move`, moveData);
    return response.data;
  },

  getByStage: async (stage: string, params?: PaginationParams): Promise<Deal[]> => {
    const response = await api.get(`/deals/stage/${stage}`, { params });
    return response.data;
  },

  getByOwner: async (owner: string, params?: PaginationParams): Promise<Deal[]> => {
    const response = await api.get(`/deals/owner/${owner}`, { params });
    return response.data;
  },

  // Pipeline Summary
  getPipelineSummary: async (): Promise<PipelineSummary> => {
    const response = await api.get("/deals/stats/pipeline-summary");
    return response.data;
  },

  // Activities
  getActivities: async (dealId: number, params?: PaginationParams): Promise<Activity[]> => {
    const response = await api.get(`/deals/${dealId}/activities`, { params });
    return response.data;
  },

  // IC Memo Operations
  saveICMemo: async (dealId: number, memoData: Partial<ICMemo>): Promise<ICMemo> => {
    const response = await api.post(`/deals/${dealId}/memos`, memoData);
    return response.data;
  },

  getICMemo: async (dealId: number): Promise<ICMemo> => {
    const response = await api.get(`/deals/${dealId}/memos`);
    return response.data;
  },

  getICMemoHistory: async (dealId: number) => {
    const response = await api.get(`/deals/${dealId}/memos/versions`);
    return response.data;
  },

  getICMemoVersion: async (dealId: number, versionNum: number) => {
    const response = await api.get(`/deals/${dealId}/memos/versions/${versionNum}`);
    return response.data;
  },
};
