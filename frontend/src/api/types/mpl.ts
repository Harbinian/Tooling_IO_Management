import type { ApiResponse, PaginatedResponse } from './response'

export interface MplComponentPayload {
  component_no: string
  component_name: string
  quantity: number
  photo_data?: string
}

export interface MplPayload {
  tool_drawing_no: string
  tool_revision: string
  items: MplComponentPayload[]
}

export interface MplComponentRecord extends Record<string, unknown> {
  component_no?: string
  component_name?: string
  quantity?: number
  photo_url?: string
  photo_data?: string
}

export interface MplRecord extends Record<string, unknown> {
  mpl_no?: string
  tool_drawing_no?: string
  tool_revision?: string
  drawing_no?: string
  revision?: string
  items?: MplComponentRecord[]
}

export interface MplListResponse extends PaginatedResponse<MplRecord> {}

export interface MplDetailResponse extends ApiResponse<MplRecord> {}

export interface MplMutationResponse extends ApiResponse<MplRecord> {
  mpl_no?: string
}
