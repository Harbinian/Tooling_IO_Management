import client from './client'
import { normalizeItem } from '@/utils/toolIO'

function unwrap(response) {
  return response.data
}

/**
 * 搜索工装
 * @param {Object} params { keyword, tool_code, tool_name, ... }
 */
export async function searchTools(params) {
  const result = unwrap(await client.get('/tools/search', { params }))
  return {
    ...result,
    data: Array.isArray(result.data)
      ? result.data.map((item) =>
          normalizeItem({
            ...item,
            tool_id: item.tool_id ?? item.tool_code,
            current_location_text:
              item.current_location_text ?? item.location ?? item.location_info ?? item.application_history ?? '',
            status_text:
              item.status_text ?? item.io_status ?? item.available_status ?? item.valid_status ?? ''
          })
        )
      : []
  }
}

/**
 * 批量查询工装
 * @param {string[]} toolCodes 
 */
export async function batchQueryTools(toolCodes) {
  const result = unwrap(await client.post('/tools/batch-query', { tool_codes: toolCodes }))
  return {
    ...result,
    data: Array.isArray(result.data) ? result.data.map((item) => normalizeItem(item)) : []
  }
}
