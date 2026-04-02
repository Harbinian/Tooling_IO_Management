import client from './client'

function unwrap(response) {
  return response.data
}

export async function getMplList(params = {}) {
  return unwrap(await client.get('/mpl', { params }))
}

export async function getMplByTool(drawingNo, revision) {
  return unwrap(await client.get('/mpl/by-tool', { params: { drawing_no: drawingNo, revision }, suppressErrorMessage: true }))
}

export async function getMplDetail(mplNo) {
  return unwrap(await client.get(`/mpl/${encodeURIComponent(mplNo)}`))
}

export async function createMpl(payload) {
  return unwrap(await client.post('/mpl', payload))
}

export async function updateMpl(mplNo, payload) {
  return unwrap(await client.put(`/mpl/${encodeURIComponent(mplNo)}`, payload))
}

export async function deleteMpl(mplNo) {
  return unwrap(await client.delete(`/mpl/${encodeURIComponent(mplNo)}`))
}
