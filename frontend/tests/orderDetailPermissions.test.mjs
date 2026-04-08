import test from 'node:test'
import assert from 'node:assert/strict'

import { canNotifyKeeper } from '../src/pages/tool-io/orderDetailPermissions.js'

test('canNotifyKeeper requires notification:send_feishu permission', () => {
  assert.equal(canNotifyKeeper('submitted', false), false)
  assert.equal(canNotifyKeeper('keeper_confirmed', false), false)
})

test('canNotifyKeeper allows submitted and keeper_confirmed for authorized users', () => {
  assert.equal(canNotifyKeeper('submitted', true), true)
  assert.equal(canNotifyKeeper('keeper_confirmed', true), true)
})

test('canNotifyKeeper rejects unsupported statuses', () => {
  assert.equal(canNotifyKeeper('draft', true), false)
  assert.equal(canNotifyKeeper('transport_notified', true), false)
})
