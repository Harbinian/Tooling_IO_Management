export function canNotifyKeeper(orderStatus, hasSendFeishuPermission) {
  return Boolean(hasSendFeishuPermission) && ['submitted', 'keeper_confirmed'].includes(orderStatus)
}
