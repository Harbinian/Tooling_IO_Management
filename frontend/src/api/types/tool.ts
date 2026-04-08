import type { ApiHttpResponse, ApiResponse, PaginatedResponse } from './response'

export interface ToolSearchParams {
  keyword?: string
  status?: string
  location_id?: number
  page_no?: number
  page_size?: number
}

export interface ToolRecord extends Record<string, unknown> {
  tool_id?: number | string
  tool_code?: string | null
  serial_no?: string | null
  tool_name?: string
  drawing_no?: string
  spec_model?: string
  current_location_text?: string
  location?: string
  location_info?: string
  application_history?: string
  status_text?: string
  io_status?: string
  available_status?: string
  valid_status?: string
  disabled?: boolean
  disabled_reason?: string | null
}

export interface NormalizedToolRecord {
  toolId: string | number
  serialNo: string
  toolName: string
  drawingNo: string
  specModel: string
  currentVersion: string
  applyQty: number
  approvedQty: number
  split_quantity: number | null
  itemStatus: string
  availableStatus: string
  validStatus: string
  ioStatus: string
  statusText: string
  currentLocationText: string
  applicationHistory: string
  ownerName: string
  workPackage: string
  mainMaterial: string
  manufacturer: string
  inspectionExpiryDate: string
  keeperConfirmLocationText: string
  checkResult: string
  checkRemark: string
  confirmPerson: string
  confirmTime: string
  rejectReason: string
}

export interface ToolSearchResponse extends PaginatedResponse<ToolRecord> {}

export interface NormalizedToolSearchResponse extends ApiResponse<NormalizedToolRecord[]> {
  total?: number
  page_no?: number
  page_size?: number
}

export interface ToolBatchStatusPayload {
  serial_nos: string[]
  new_status: string
  remark?: string
  operator?: {
    user_id?: string
    display_name?: string
  }
  operator_id?: string
  operator_name?: string
  operator_role?: string
}

export interface ToolStatusChangeRecord {
  tool_code?: string
  old_status?: string
  new_status?: string
}

export interface ToolBatchStatusResult extends ApiResponse<ToolStatusChangeRecord[]> {
  updated_count?: number
  records?: ToolStatusChangeRecord[]
  missing_tool_codes?: string[]
}

export type ToolBatchStatusHttpResponse = ApiHttpResponse<ToolBatchStatusResult, ToolBatchStatusPayload>

export interface ToolStatusHistoryEntry extends Record<string, unknown> {
  old_status?: string
  new_status?: string
  remark?: string
  operator_id?: string
  operator_name?: string
  change_time?: string
  client_ip?: string
}

export interface ToolStatusHistoryParams {
  page_no?: number
  page_size?: number
}

export interface ToolStatusHistoryResponse extends ApiResponse<ToolStatusHistoryEntry[]> {
  total?: number
  page_no?: number
  page_size?: number
}

export type ToolStatusHistoryHttpResponse = ApiHttpResponse<ToolStatusHistoryResponse>
