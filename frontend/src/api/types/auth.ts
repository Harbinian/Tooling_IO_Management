import type { ApiResponse } from './response'

export interface LoginCredentials {
  login_name: string
  password: string
}

export interface AuthenticatedUser extends Record<string, unknown> {
  user_id?: string
  display_name?: string
  login_name?: string
  roles?: string[]
  permissions?: string[]
}

export interface LoginResponse extends ApiResponse<never> {
  token?: string
  user?: AuthenticatedUser
}

export interface CurrentUserResponse extends ApiResponse<never> {
  user?: AuthenticatedUser
}

export interface ChangePasswordPayload {
  old_password: string
  new_password: string
}

export interface ChangePasswordResponse extends ApiResponse<never> {}
