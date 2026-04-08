import type { AxiosRequestConfig, AxiosResponse } from 'axios'

export interface ApiErrorBody {
  code: string
  message: string
  details?: Record<string, unknown> | null
}

export interface ApiResponse<T = unknown> {
  success: boolean
  data?: T
  error?: string | ApiErrorBody
  error_detail?: ApiErrorBody
  message?: string
  [key: string]: unknown
}

export interface PaginatedResponse<T = unknown> extends ApiResponse<T[]> {
  total?: number
  page_no?: number
  page_size?: number
}

export interface ApiRequestConfig<D = unknown> extends AxiosRequestConfig<D> {
  suppressErrorMessage?: boolean
}

export type ApiHttpResponse<T = unknown, D = unknown> = AxiosResponse<T, D>
