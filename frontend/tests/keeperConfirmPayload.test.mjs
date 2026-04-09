import test from 'node:test'
import assert from 'node:assert/strict'

import {
  buildKeeperConfirmPayload,
  collectKeeperConfirmItemsMissingId
} from '../src/pages/tool-io/keeperConfirmPayload.js'

test('buildKeeperConfirmPayload keeps item_id in keeper-confirm items', () => {
  const payload = buildKeeperConfirmPayload({
    confirmItems: [
      {
        item_id: 11,
        serial_no: 'SN-11',
        status: 'approved',
        split_quantity: 2,
        checkRemark: ''
      }
    ],
    confirmForm: {
      transportType: '叉车',
      transportAssigneeId: 'u-2',
      transportAssigneeName: 'Keeper A',
      keeperRemark: 'checked'
    },
    resolveItemLocationText: () => 'LOC-01',
    session: {
      userId: 'u-1',
      userName: 'Keeper',
      role: 'keeper'
    }
  })

  assert.equal(payload.items[0].item_id, 11)
  assert.equal(payload.items[0].serial_no, 'SN-11')
  assert.equal(payload.items[0].approved_qty, 2)
  assert.equal(payload.operator_id, 'u-1')
})

test('buildKeeperConfirmPayload falls back to legacy id when item_id is absent', () => {
  const payload = buildKeeperConfirmPayload({
    confirmItems: [
      {
        id: 23,
        serialNo: 'SN-23',
        status: 'approved',
        applyQty: 1,
        checkRemark: 'ok'
      }
    ],
    confirmForm: {
      transportType: '叉车',
      transportAssigneeId: '',
      transportAssigneeName: '',
      keeperRemark: ''
    },
    resolveItemLocationText: () => 'LOC-02',
    session: {
      userId: 'u-9',
      userName: 'Keeper',
      role: 'keeper'
    }
  })

  assert.equal(payload.items[0].item_id, 23)
  assert.equal(payload.items[0].serial_no, 'SN-23')
})

test('collectKeeperConfirmItemsMissingId returns items without item_id or id', () => {
  const missing = collectKeeperConfirmItemsMissingId([
    { item_id: 1, serial_no: 'ok-1' },
    { id: 2, serialNo: 'ok-2' },
    { serial_no: 'missing-1' }
  ])

  assert.equal(missing.length, 1)
  assert.equal(missing[0].serial_no, 'missing-1')
})
