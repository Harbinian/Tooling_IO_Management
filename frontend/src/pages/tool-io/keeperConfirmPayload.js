export function getKeeperConfirmItemId(item) {
  return item?.item_id ?? item?.id ?? null
}

export function collectKeeperConfirmItemsMissingId(items) {
  return (items || []).filter((item) => !getKeeperConfirmItemId(item))
}

export function buildKeeperConfirmItems(items, keeperRemark, resolveItemLocationText) {
  return (items || []).map((item) => ({
    item_id: getKeeperConfirmItemId(item),
    serial_no: item.serial_no || item.serialNo || '',
    location_id: null,
    location_text: resolveItemLocationText(item),
    check_result: item.status,
    check_remark: item.checkRemark || keeperRemark,
    approved_qty: item.status === 'approved' ? (item.split_quantity ?? item.applyQty ?? 1) : 0,
    status: item.status
  }))
}

export function buildKeeperConfirmPayload({
  confirmItems,
  confirmForm,
  resolveItemLocationText,
  session
}) {
  return {
    keeper_id: session.userId,
    keeper_name: session.userName,
    transport_type: confirmForm.transportType,
    transport_assignee_id: confirmForm.transportAssigneeId,
    transport_assignee_name: confirmForm.transportAssigneeName,
    keeper_remark: confirmForm.keeperRemark,
    items: buildKeeperConfirmItems(confirmItems, confirmForm.keeperRemark, resolveItemLocationText),
    operator_id: session.userId,
    operator_name: session.userName,
    operator_role: session.role
  }
}
