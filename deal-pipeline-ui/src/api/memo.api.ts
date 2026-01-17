import { api } from "./axios";
import type { ICMemo, ICMemoCreateRequest, ICMemoVersionResponse } from "../types";

export const memoAPI = {
  create: async (memoData: ICMemoCreateRequest): Promise<ICMemo> => {
    const response = await api.post("/memos", memoData);
    return response.data;
  },

  getByDeal: async (dealId: number): Promise<ICMemo> => {
    const response = await api.get(`/deals/${dealId}/memo`);
    return response.data;
  },

  update: async (dealId: number, memoData: ICMemoCreateRequest): Promise<ICMemo> => {
    const response = await api.put(`/deals/${dealId}/memo`, memoData);
    return response.data;
  },

  getVersions: async (dealId: number): Promise<ICMemoVersionResponse[]> => {
    const response = await api.get(`/deals/${dealId}/memo/versions`);
    return response.data;
  },

  getVersion: async (dealId: number, version: number): Promise<ICMemoVersionResponse> => {
    const response = await api.get(`/deals/${dealId}/memo/versions/${version}`);
    return response.data;
  },
};
