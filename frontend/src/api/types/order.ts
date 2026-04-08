import type { ApiResponse, PaginatedResponse } from './response'

export type OrderType = 'inbound' | 'outbound'

export type OrderStatus =
  | 'draft'
  | 'submitted'
  | 'keeper_confirmed'
  | 'partially_confirmed'
  | 'transport_notified'
  | 'transporting'
  | 'transport_in_progress'
  | 'transport_completed'
  | 'final_confirmation_pending'
  | 'completed'
  | 'rejected'
  | 'cancelled'

export type ItemStatus = 'pending_check' | 'approved' | 'rejected' | 'completed'

export interface OperatorPayload {
  operator_id?: string
  operator_name?: string
  operator_role?: string
}

export interface OrderItemPayload {
  tool_id?: number | string
  serial_no: string
  tool_name: string
  drawing_no?: string
  spec_model?: string
  apply_qty?: number
  remark?: string
}

export interface OrderCreatePayload {
  order_type: OrderType
  initiator_id: string
  initiator_name: string
  initiator_role: string
  department?: string
  project_code?: string
  usage_purpose?: string
  planned_use_time?: string
  planned_return_time?: string
  target_location_id?: number | string
  target_location_text?: string
  remark?: string
  items: OrderItemPayload[]
}

export interface OrderDraftUpdatePayload {
  order_type?: OrderType
  department?: string
  project_code?: string
  usage_purpose?: string
  planned_use_time?: string
  planned_return_time?: string
  target_location_id?: number | string
  target_location_text?: string
  remark?: string
  items?: OrderItemPayload[]
}

export interface KeeperConfirmItemPayload {
  serial_no: string
  location_id?: number
  location_text?: string
  check_result: string
  check_remark?: string
  approved_qty?: number
  status: 'approved' | 'rejected'
}

export interface KeeperConfirmPayload extends Required<OperatorPayload> {
  keeper_id: string
  keeper_name: string
  transport_type?: string
  transport_assignee_id?: string
  transport_assignee_name?: string
  items: KeeperConfirmItemPayload[]
}

export interface AssignTransportPayload extends OperatorPayload {
  transport_type?: string
  transport_assignee_id?: string
  transport_assignee_name?: string
}

export interface RejectOrderPayload extends Required<OperatorPayload> {
  reject_reason: string
}

export interface NotificationPayload extends OperatorPayload {
  notify_type?: string
  notify_channel?: string
  receiver?: string
  title?: string
  content?: string
  copy_text?: string
}

export interface TransportIssuePayload {
  issue_type: string
  description?: string
  image_urls?: string[]
}

export interface ResolveTransportIssuePayload {
  handle_reply: string
}

export interface OrderListParams {
  order_type?: OrderType
  order_status?: OrderStatus | string
  initiator_id?: string
  keeper_id?: string
  keyword?: string
  date_from?: string
  date_to?: string
  page_no?: number
  page_size?: number
}

export interface OrderLogRecord extends Record<string, unknown> {
  action_type?: string
  operator_name?: string
  operator_role?: string
  content?: string
  action_time?: string
  before_status?: string
  after_status?: string
}

export interface NotificationRecord extends Record<string, unknown> {
  notify_type?: string
  notify_channel?: string
  receiver?: string
  title?: string
  notify_title?: string
  content?: string
  notify_content?: string
  copy_text?: string
  send_status?: string
  send_result?: string
  send_time?: string
  created_at?: string
}

export interface OrderItemRecord extends Record<string, unknown> {
  tool_id?: number | string
  serial_no?: string | null
  tool_code?: string | null
  tool_name?: string
  drawing_no?: string
  spec_model?: string
  current_version?: string
  apply_qty?: number
  approved_qty?: number
  split_quantity?: number | null
  item_status?: ItemStatus | string
  status?: ItemStatus | string
  status_text?: string
  available_status?: string
  valid_status?: string
  io_status?: string
  current_location_text?: string
  location_info?: string
  application_history?: string
  owner_name?: string
  work_package?: string
  main_material?: string
  manufacturer?: string
  inspection_expiry_date?: string
  keeper_confirm_location_text?: string
  keeper_check_result?: string
  check_result?: string
  keeper_check_remark?: string
  check_remark?: string
  confirm_person?: string
  confirm_time?: string
  reject_reason?: string
}

export interface OrderRecord extends Record<string, unknown> {
  order_no?: string
  order_type?: OrderType
  order_status?: OrderStatus | string
  initiator_id?: string
  initiator_name?: string
  initiator_role?: string
  department?: string
  project_code?: string
  usage_purpose?: string
  target_location_text?: string
  keeper_id?: string
  keeper_name?: string
  transport_type?: string
  transport_operator_id?: string
  transport_assignee_id?: string
  transport_operator_name?: string
  transport_assignee_name?: string
  tool_count?: number
  approved_count?: number
  created_at?: string
  updated_at?: string
  submitted_at?: string
  keeper_request_text?: string
  transport_notice_text?: string
  wechat_copy_text?: string
  remark?: string
  reject_reason?: string
  items?: OrderItemRecord[]
  logs?: OrderLogRecord[]
  notification_records?: NotificationRecord[]
  notifications?: NotificationRecord[]
}

export interface NormalizedOrderItem {
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

export interface NormalizedOrderLog {
  actionType: string
  operatorName: string
  operatorRole: string
  content: string
  actionTime: string
  beforeStatus: string
  afterStatus: string
}

export interface NormalizedNotificationRecord {
  notifyType: string
  notifyChannel: string
  receiver: string
  title: string
  content: string
  copyText: string
  sendStatus: string
  sendResult: string
  sendTime: string
}

export interface NormalizedOrder {
  orderNo: string
  orderType: string
  orderStatus: string
  initiatorId: string
  initiatorName: string
  initiatorRole: string
  department: string
  projectCode: string
  usagePurpose: string
  targetLocationText: string
  keeperId: string
  keeperName: string
  transportType: string
  transportOperatorId: string
  transportOperatorName: string
  toolCount: number
  approvedCount: number
  createdAt: string
  updatedAt: string
  submittedAt: string
  keeperRequestText: string
  transportNoticeText: string
  wechatCopyText: string
  remark: string
  rejectReason: string
  items: NormalizedOrderItem[]
  logs: NormalizedOrderLog[]
  notificationRecords: NormalizedNotificationRecord[]
}

export interface OrderActionResponse extends ApiResponse<unknown> {
  order_no?: string
}

export interface OrderListResponse extends PaginatedResponse<OrderRecord> {}

export interface NormalizedOrderListResponse extends ApiResponse<NormalizedOrder[]> {
  total?: number
  page_no?: number
  page_size?: number
}

export interface OrderDetailResponse extends ApiResponse<OrderRecord | null> {}

export interface NormalizedOrderDetailResponse extends ApiResponse<NormalizedOrder | null> {}

export interface OrderLogsResponse extends ApiResponse<OrderLogRecord[]> {}

export interface NotificationRecordsResponse extends ApiResponse<NotificationRecord[]> {}

export interface TextPreviewResponse extends ApiResponse<never> {
  text?: string
  wechat_text?: string
  copy_text?: string
}

export interface FinalConfirmAvailabilityResponse extends ApiResponse<unknown> {
  can_confirm?: boolean
  order_type?: OrderType
  current_role?: string
}

export interface TransportIssueRecord extends Record<string, unknown> {
  id?: number
  issue_type?: string
  description?: string
  image_urls?: string[]
  reporter_name?: string
  report_time?: string | null
  status?: string
  handler_name?: string | null
  handle_time?: string | null
  handle_reply?: string | null
}

export interface TransportIssuesResponse extends ApiResponse<TransportIssueRecord[]> {
  issues?: TransportIssueRecord[]
}

export interface PreTransportOrder extends Record<string, unknown> {
  order_no?: string
  order_type?: OrderType
  destination?: string
  status?: OrderStatus | string
  status_text?: string
  expected_tools?: number
  submit_time?: string | null
  submitter_name?: string
  estimated_transport_time?: string | null
  keeper_confirmed_time?: string | null
}

export interface PreTransportOrdersResponse extends ApiResponse<unknown> {
  orders?: PreTransportOrder[]
}
