/**
 * Shared type definitions for the Deal Pipeline application
 */

// ===== Authentication =====
export interface User {
  id: number;
  email: string;
  username?: string;
  full_name?: string;
  role: "admin" | "analyst" | "partner" | "user";
  is_active: boolean;
  email_verified: boolean;
  last_login?: string;
  created_at: string;
  updated_at: string;
}

export interface AuthToken {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
}

// ===== Deal Pipeline =====
export type DealStage = "Sourced" | "Screen" | "Diligence" | "IC" | "Invested" | "Passed";
export type DealStatus = "active" | "inactive" | "archived";

export interface Deal {
  id: number;
  name: string;
  company_url?: string;
  owner: string;
  stage: DealStage;
  round?: string;
  check_size?: number;
  status: DealStatus;
  created_at: string;
  updated_at: string;
}

export interface DealCreateRequest {
  name: string;
  company_url?: string;
  owner: string;
  stage?: DealStage;
  round?: string;
  check_size?: number;
  status?: DealStatus;
}

export interface DealUpdateRequest {
  name?: string;
  company_url?: string;
  owner?: string;
  round?: string;
  check_size?: number;
  status?: DealStatus;
}

export interface DealMoveRequest {
  stage: DealStage;
}

// ===== Activity Log =====
export interface Activity {
  id: number;
  deal_id: number;
  user_id: number;
  activity_type: string;
  description: string;
  old_value?: string;
  new_value?: string;
  created_at: string;
  updated_at: string;
}

// ===== IC Memo =====
export interface ICMemo {
  id: number;
  deal_id: number;
  created_by: number;
  last_updated_by: number;
  current_version: number;
  summary?: string;
  market?: string;
  product?: string;
  traction?: string;
  risks?: string;
  open_questions?: string;
  created_at: string;
  updated_at: string;
}

export interface ICMemoVersion {
  id: number;
  memo_id: number;
  deal_id: number;
  version_number: number;
  created_by: number;
  summary?: string;
  market?: string;
  product?: string;
  traction?: string;
  risks?: string;
  open_questions?: string;
  change_summary?: string;
  created_at: string;
}

// ===== API Response Types =====
export interface PaginationParams {
  skip?: number;
  limit?: number;
}

export interface PipelineSummary {
  Sourced: number;
  Screen: number;
  Diligence: number;
  IC: number;
  Invested: number;
  Passed: number;
}

export interface ErrorResponse {
  code: string;
  message: string;
  details?: string;
}
