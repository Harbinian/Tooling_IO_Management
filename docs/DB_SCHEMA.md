# 鏁版嵁搴撴灦鏋勬枃妗?

## 姒傝堪

鏈枃妗ｅ畾涔夊伐瑁呭嚭鍏ュ簱绠＄悊绯荤粺鐨勬暟鎹簱琛ㄧ粨鏋勩€傚熀浜庨」鐩疄闄呭瓨鍦ㄧ殑 SQL Server 鏁版嵁搴撴ā鍧椼€?

**娉ㄦ剰锛?* 鏈枃浠朵腑寮曠敤鐨?line numbers (濡?`database.py:307-343`) 宸茶繃鏃讹紝璇峰弬鑰冨疄闄呯殑 `backend/database/schema/schema_manager.py` 涓殑 CREATE TABLE 璇彞鑾峰彇鏈€鏂颁綅缃€?

---

## 1. 琛ㄦ竻鍗?

### 1.1 宸插疄鐜扮殑琛?

| 琛ㄥ悕锛堜腑鏂囷級 | 閫昏緫鍒悕 | 璇存槑 | 鐘舵€?|
|--------------|----------|------|------|
| 宸ヨ鍑哄叆搴撳崟_涓昏〃 | ToolIOOrder | 鍑哄叆搴撳崟涓昏〃 | 鉁?宸插疄鐜?|
| 宸ヨ鍑哄叆搴撳崟_鏄庣粏 | ToolIOOrderItem | 鍑哄叆搴撳崟鏄庣粏 | 鉁?宸插疄鐜?|
| 宸ヨ鍑哄叆搴撳崟_鎿嶄綔鏃ュ織 | ToolIOLog | 鎿嶄綔鏃ュ織 | 鉁?宸插疄鐜?|
| 宸ヨ鍑哄叆搴撳崟_閫氱煡璁板綍 | ToolIONotify | 閫氱煡璁板綍 | 鉁?宸插疄鐜?|
| 宸ヨ鍑哄叆搴撳崟_浣嶇疆 | ToolLocation | 宸ヨ浣嶇疆锛堟敞鎰忥細鏃ф枃妗ｆ浘鐢ㄥ悕 `宸ヨ浣嶇疆琛╜锛?| 鉁?宸插疄鐜?|
| 宸ヨ韬唤鍗涓昏〃 | ToolMaster | 宸ヨ涓绘暟鎹紙涓氬姟婧愯〃锛?| 鉁?宸插瓨鍦?|
| tool_io_feedback | ToolIOFeedback | 鐢ㄦ埛鍙嶉琛?| 鉁?宸插疄鐜?|
| tool_io_feedback_reply | ToolIOFeedbackReply | Admin reply records for feedback | ✅ 已实现 |
| tool_status_change_history | ToolStatusHistory | 宸ヨ鐘舵€佸彉鏇磋褰?| 鉁?宸插疄鐜?|
| sys_org | SysOrg | 缁勭粐琛?| 鉁?宸插疄鐜?|
| sys_user | SysUser | 绯荤粺鐢ㄦ埛琛?| 鉁?宸插疄鐜?|
| sys_role | SysRole | 瑙掕壊琛?| 鉁?宸插疄鐜?|
| sys_permission | SysPermission | 鏉冮檺琛?| 鉁?宸插疄鐜?|
| sys_user_role_rel | SysUserRoleRel | 鐢ㄦ埛瑙掕壊鍏崇郴 | 鉁?宸插疄鐜?|
| sys_role_permission_rel | SysRolePermissionRel | 瑙掕壊鏉冮檺鍏崇郴 | 鉁?宸插疄鐜?|
| sys_role_data_scope_rel | SysRoleDataScopeRel | 瑙掕壊鏁版嵁鑼冨洿鍏崇郴 | 鉁?宸插疄鐜?|
| sys_user_password_change_log | SysUserPasswordChangeLog | 瀵嗙爜淇敼瀹¤鏃ュ織 | 鉁?宸插疄鐜?|
| sys_user_org_rel | SysUserOrgRel | 鐢ㄦ埛缁勭粐鍏崇郴 | 鉁?宸插疄鐜?|

---

## 2. 琛ㄧ粨鏋勮缁嗚璁?

### 2.1 宸ヨ鍑哄叆搴撳崟_涓昏〃 (ToolIOOrder)

**涓枃琛ㄥ悕锛?* 宸ヨ鍑哄叆搴撳崟_涓昏〃

**閫昏緫鍒悕锛?* tool_io_order

**鍒涘缓鑴氭湰浣嶇疆锛?* database.py:307-343

#### 宸插疄鐜板瓧娈?

| 瀛楁鍚嶏紙涓枃锛?| 瀛楁鍚嶏紙鑻辨枃鍒悕锛?| 鏁版嵁绫诲瀷 | 蹇呭～ | 璇存槑 |
|----------------|-------------------|----------|------|------|
| id | id | BIGINT | 鏄?| 涓婚敭锛岃嚜澧?|
| 鍑哄叆搴撳崟鍙?| order_no | VARCHAR(64) | 鏄?| 鍗曞彿锛屽敮涓€ |
| 鍗曟嵁绫诲瀷 | order_type | VARCHAR(16) | 鏄?| outbound/inbound |
| 鍗曟嵁鐘舵€?| order_status | VARCHAR(32) | 鏄?| 鐘舵€?|
| 鍙戣捣浜篒D | initiator_id | VARCHAR(64) | 鏄?| 鐢宠浜篒D |
| 鍙戣捣浜哄鍚?| initiator_name | VARCHAR(64) | 鏄?| 鐢宠浜哄鍚?|
| 鍙戣捣浜鸿鑹?| initiator_role | VARCHAR(32) | 鏄?| 瑙掕壊 |
| 閮ㄩ棬 | department | VARCHAR(64) | 鍚?| 閮ㄩ棬 |
| 椤圭洰浠ｅ彿 | project_code | VARCHAR(64) | 鍚?| 椤圭洰浠ｅ彿 |
| 鐢ㄩ€?| usage_purpose | VARCHAR(255) | 鍚?| 鐢ㄩ€?|
| 璁″垝浣跨敤鏃堕棿 | planned_use_time | DATETIME | 鍚?| 璁″垝浣跨敤鏃堕棿 |
| 璁″垝褰掕繕鏃堕棿 | planned_return_time | DATETIME | 鍚?| 璁″垝褰掕繕鏃堕棿 |
| 鐩爣浣嶇疆ID | target_location_id | BIGINT | 鍚?| 鐩爣浣嶇疆ID |
| 鐩爣浣嶇疆鏂囨湰 | target_location_text | VARCHAR(255) | 鍚?| 鐩爣浣嶇疆鏂囨湰 |
| 淇濈鍛業D | keeper_id | VARCHAR(64) | 鍚?| 淇濈鍛業D |
| 淇濈鍛樺鍚?| keeper_name | VARCHAR(64) | 鍚?| 淇濈鍛樺鍚?|
| 杩愯緭绫诲瀷 | transport_type | VARCHAR(32) | 鍚?| 杩愯緭绫诲瀷 |
| 杩愯緭浜篒D | transport_operator_id | VARCHAR(64) | 鍚?| 杩愯緭浜篒D |
| 杩愯緭浜哄鍚?| transport_operator_name | VARCHAR(64) | 鍚?| 杩愯緭浜哄鍚?|
| 淇濈鍛橀渶姹傛枃鏈?| keeper_demand_text | TEXT | 鍚?| 淇濈鍛橀渶姹傛枃鏈?|
| 杩愯緭閫氱煡鏂囨湰 | transport_notify_text | TEXT | 鍚?| 杩愯緭閫氱煡鏂囨湰 |
| 寰俊澶嶅埗鏂囨湰 | wechat_copy_text | TEXT | 鍚?| 寰俊澶嶅埗鏂囨湰 |
| 淇濈鍛樼‘璁ゆ椂闂?| keeper_confirm_time | DATETIME | 鍚?| 淇濈鍛樼‘璁ゆ椂闂?|
| 杩愯緭閫氱煡鏃堕棿 | transport_notify_time | DATETIME | 鍚?| 杩愯緭閫氱煡鏃堕棿 |
| 鏈€缁堢‘璁ゆ椂闂?| final_confirm_time | DATETIME | 鍚?| 鏈€缁堢‘璁ゆ椂闂?|
| 椹冲洖鍘熷洜 | reject_reason | VARCHAR(500) | 鍚?| 椹冲洖鍘熷洜 |
| 澶囨敞 | remark | VARCHAR(500) | 鍚?| 澶囨敞 |
| 鍒涘缓鏃堕棿 | created_at | DATETIME | 鏄?| 鍒涘缓鏃堕棿 |
| 淇敼鏃堕棿 | updated_at | DATETIME | 鏄?| 淇敼鏃堕棿 |
| 鍒涘缓浜?| created_by | VARCHAR(64) | 鍚?| 鍒涘缓浜?|
| 淇敼浜?| updated_by | VARCHAR(64) | 鍚?| 淇敼浜?|
| IS_DELETED | is_deleted | TINYINT | 鏄?| 杞垹闄ゆ爣璁?|

#### 鈿狅笍 缂哄け瀛楁锛堜唬鐮佷腑寮曠敤浣嗘湭鍦–REATE TABLE涓畾涔夛級

| 瀛楁鍚?| 鏁版嵁绫诲瀷 | 寮曠敤浣嶇疆 | 寤鸿 |
|--------|----------|----------|------|
| 宸ヨ鏁伴噺 | INT | database.py:519 | 闇€瑕佹坊鍔?|
| 宸茬‘璁ゆ暟閲?| confirmed_count | INT | database.py:785 | 闇€瑕佹坊鍔?|
| 鏈€缁堢‘璁や汉 | final_confirm_by | VARCHAR(64) | database.py:842 | 闇€瑕佹坊鍔?|
| org_id | org_id | VARCHAR(64) | backend/database/repositories/order_repository.py | 鏃ф暟鎹簱蹇呴』閫氳繃 schema alignment 鑷姩琛ラ綈锛屽惁鍒欏垱寤鸿鍗曚細鎶ュ垪缂哄け |

---

### 2.2 宸ヨ鍑哄叆搴撳崟_鏄庣粏 (ToolIOOrderItem)

**涓枃琛ㄥ悕锛?* 宸ヨ鍑哄叆搴撳崟_鏄庣粏

**閫昏緫鍒悕锛?* tool_io_order_item

**鍒涘缓鑴氭湰浣嶇疆锛?* database.py:346-374

#### 宸插疄鐜板瓧娈?

| 瀛楁鍚嶏紙涓枃锛?| 瀛楁鍚嶏紙鑻辨枃鍒悕锛?| 鏁版嵁绫诲瀷 | 蹇呭～ | 璇存槑 |
|----------------|-------------------|----------|------|------|
| id | id | BIGINT | 鏄?| 涓婚敭锛岃嚜澧?|
| 鍑哄叆搴撳崟鍙?| order_no | VARCHAR(64) | 鏄?| 澶栭敭 |
| 宸ヨID | tool_id | BIGINT | 鍚?| 宸ヨID |
| 搴忓垪鍙?| tool_code | VARCHAR(64) | 鏄?| 宸ヨ缂栫爜 |
| 宸ヨ鍚嶇О | tool_name | VARCHAR(128) | 鏄?| 宸ヨ鍚嶇О |
| 宸ヨ鍥惧彿 | drawing_no | VARCHAR(64) | 鍚?| 宸ヨ鍥惧彿 |
| 鏈哄瀷 | spec_model | VARCHAR(128) | 鍚?| 瑙勬牸鍨嬪彿 |
| 鐢宠鏁伴噺 | apply_qty | DECIMAL(10,2) | 鍚?| 榛樿1 |
| 纭鏁伴噺 | confirmed_qty | DECIMAL(10,2) | 鍚?| 纭鏁伴噺 |
| 鏄庣粏鐘舵€?| item_status | VARCHAR(32) | 鏄?| pending_check/approved/rejected/completed |
| 宸ヨ蹇収鐘舵€?| tool_snapshot_status | VARCHAR(32) | 鍚?| 宸ヨ蹇収鐘舵€?|
| 宸ヨ蹇収浣嶇疆ID | tool_snapshot_location_id | BIGINT | 鍚?| 蹇収浣嶇疆ID |
| 宸ヨ蹇収浣嶇疆鏂囨湰 | tool_snapshot_location_text | VARCHAR(255) | 鍚?| 蹇収浣嶇疆鏂囨湰 |
| 淇濈鍛樼‘璁や綅缃甀D | keeper_confirm_location_id | BIGINT | 鍚?| 纭浣嶇疆ID |
| 淇濈鍛樼‘璁や綅缃枃鏈?| keeper_confirm_location_text | VARCHAR(255) | 鍚?| 纭浣嶇疆鏂囨湰 |
| 淇濈鍛樻鏌ョ粨鏋?| keeper_check_result | VARCHAR(32) | 鍚?| 妫€鏌ョ粨鏋?|
| 淇濈鍛樻鏌ュ娉?| keeper_check_remark | VARCHAR(500) | 鍚?| 妫€鏌ュ娉?|
| 褰掕繕妫€鏌ョ粨鏋?| return_check_result | VARCHAR(32) | 鍚?| 褰掕繕妫€鏌ョ粨鏋?|
| 褰掕繕妫€鏌ュ娉?| return_check_remark | VARCHAR(500) | 鍚?| 褰掕繕妫€鏌ュ娉?|
| 鎺掑簭鍙?| sort_order | INT | 鍚?| 鎺掑簭鍙?|
| 鍒涘缓鏃堕棿 | created_at | DATETIME | 鏄?| 鍒涘缓鏃堕棿 |
| 淇敼鏃堕棿 | updated_at | DATETIME | 鏄?| 淇敼鏃堕棿 |

#### 鈿狅笍 缂哄け瀛楁锛堜唬鐮佷腑寮曠敤浣嗘湭鍦–REATE TABLE涓畾涔夛級

| 瀛楁鍚?| 鏁版嵁绫诲瀷 | 寮曠敤浣嶇疆 | 寤鸿 |
|--------|----------|----------|------|
| 纭鏃堕棿 | confirm_time | DATETIME | database.py:755 | 闇€瑕佹坊鍔?|
| 鍑哄叆搴撳畬鎴愭椂闂?| complete_time | DATETIME | database.py:853 | 闇€瑕佹坊鍔?|

---

### 2.3 宸ヨ鍑哄叆搴撳崟_鎿嶄綔鏃ュ織 (ToolIOLog)

**涓枃琛ㄥ悕锛?* 宸ヨ鍑哄叆搴撳崟_鎿嶄綔鏃ュ織

**閫昏緫鍒悕锛?* tool_io_log

**鍒涘缓鑴氭湰浣嶇疆锛?* database.py:377-394

#### 宸插疄鐜板瓧娈?

| 瀛楁鍚嶏紙涓枃锛?| 瀛楁鍚嶏紙鑻辨枃鍒悕锛?| 鏁版嵁绫诲瀷 | 蹇呭～ | 璇存槑 |
|----------------|-------------------|----------|------|------|
| id | id | BIGINT | 鏄?| 涓婚敭锛岃嚜澧?|
| 鍑哄叆搴撳崟鍙?| order_no | VARCHAR(64) | 鏄?| 澶栭敭 |
| 鏄庣粏ID | item_id | BIGINT | 鍚?| 鏄庣粏ID |
| 鎿嶄綔绫诲瀷 | operation_type | VARCHAR(64) | 鏄?| 鎿嶄綔绫诲瀷 |
| 鎿嶄綔浜篒D | operator_id | VARCHAR(64) | 鏄?| 鎿嶄綔浜篒D |
| 鎿嶄綔浜哄鍚?| operator_name | VARCHAR(64) | 鏄?| 鎿嶄綔浜哄鍚?|
| 鎿嶄綔浜鸿鑹?| operator_role | VARCHAR(32) | 鍚?| 鎿嶄綔浜鸿鑹?|
| 鍙樻洿鍓嶇姸鎬?| from_status | VARCHAR(32) | 鍚?| 鍙樻洿鍓嶇姸鎬?|
| 鍙樻洿鍚庣姸鎬?| to_status | VARCHAR(32) | 鍚?| 鍙樻洿鍚庣姸鎬?|
| 鎿嶄綔鍐呭 | operation_content | TEXT | 鍚?| 鎿嶄綔鍐呭 |
| 鎿嶄綔鏃堕棿 | operation_time | DATETIME | 鏄?| 鎿嶄綔鏃堕棿 |

---

### 2.4 宸ヨ鍑哄叆搴撳崟_閫氱煡璁板綍 (ToolIONotify)

**涓枃琛ㄥ悕锛?* 宸ヨ鍑哄叆搴撳崟_閫氱煡璁板綍

**閫昏緫鍒悕锛?* tool_io_notification

**鍒涘缓鑴氭湰浣嶇疆锛?* database.py:397-416

#### 宸插疄鐜板瓧娈?

| 瀛楁鍚嶏紙涓枃锛?| 瀛楁鍚嶏紙鑻辨枃鍒悕锛?| 鏁版嵁绫诲瀷 | 蹇呭～ | 璇存槑 |
|----------------|-------------------|----------|------|------|
| id | id | BIGINT | 鏄?| 涓婚敭锛岃嚜澧?|
| 鍑哄叆搴撳崟鍙?| order_no | VARCHAR(64) | 鏄?| 澶栭敭 |
| 閫氱煡绫诲瀷 | notify_type | VARCHAR(32) | 鏄?| 閫氱煡绫诲瀷 |
| 閫氱煡娓犻亾 | notify_channel | VARCHAR(32) | 鏄?| feishu/wechat/email |
| 鎺ユ敹浜?| receiver | VARCHAR(255) | 鍚?| 鎺ユ敹浜?|
| 閫氱煡鏍囬 | notify_title | VARCHAR(100) | 鍚?| 閫氱煡鏍囬 |
| 閫氱煡鍐呭 | notify_content | TEXT | 鏄?| 閫氱煡鍐呭 |
| 澶嶅埗鏂囨湰 | copy_text | TEXT | 鍚?| 澶嶅埗鏂囨湰 |
| 鍙戦€佺姸鎬?| send_status | VARCHAR(32) | 鏄?| pending/success/failed |
| 鍙戦€佹椂闂?| send_time | DATETIME | 鍚?| 鍙戦€佹椂闂?|
| 鍙戦€佺粨鏋?| send_result | TEXT | 鍚?| 鍙戦€佺粨鏋?|
| 閲嶈瘯娆℃暟 | retry_count | INT | 鍚?| 閲嶈瘯娆℃暟锛岄粯璁? |
| 鍒涘缓鏃堕棿 | created_at | DATETIME | 鏄?| 鍒涘缓鏃堕棿 |

---

### 2.5 宸ヨ鍑哄叆搴撳崟_浣嶇疆 (ToolLocation)

**涓枃琛ㄥ悕锛?* 宸ヨ鍑哄叆搴撳崟_浣嶇疆

**閫昏緫鍒悕锛?* tool_location

**鍒涘缓鑴氭湰浣嶇疆锛?* `backend/database/schema/schema_manager.py:252-263`

**娉ㄦ剰锛?* 姝よ〃鏇剧敤鍚?`宸ヨ浣嶇疆琛╜锛岀幇缁熶竴浣跨敤 `宸ヨ鍑哄叆搴撳崟_浣嶇疆`銆?

#### 宸插疄鐜板瓧娈?

| 瀛楁鍚嶏紙涓枃锛?| 瀛楁鍚嶏紙鑻辨枃鍒悕锛?| 鏁版嵁绫诲瀷 | 蹇呭～ | 璇存槑 |
|----------------|-------------------|----------|------|------|
| id | id | BIGINT | 鏄?| 涓婚敭锛岃嚜澧?|
| 浣嶇疆缂栫爜 | location_code | VARCHAR(64) | 鏄?| 浣嶇疆缂栫爜 |
| 浣嶇疆鍚嶇О | location_name | VARCHAR(255) | 鏄?| 浣嶇疆鍚嶇О |
| 浣嶇疆鎻忚堪 | location_desc | VARCHAR(255) | 鍚?| 浣嶇疆鎻忚堪 |
| 搴撳尯 | warehouse_area | VARCHAR(64) | 鍚?| 搴撳尯 |
| 搴撲綅 | storage_slot | VARCHAR(64) | 鍚?| 搴撲綅 |
| 璐ф灦 | shelf | VARCHAR(255) | 鍚?| 璐ф灦 |
| 澶囨敞 | remark | VARCHAR(500) | 鍚?| 澶囨敞 |

---

### 2.6 宸ヨ韬唤鍗涓昏〃 (ToolMaster)

**涓枃琛ㄥ悕锛?* 宸ヨ韬唤鍗涓昏〃

**閫昏緫鍒悕锛?* tool_master

**璇存槑锛?* 杩欐槸宸叉湁鐨勪笟鍔℃簮琛紝鐢ㄤ簬宸ヨ鎼滅储銆傝〃缁撴瀯鐢卞閮ㄧ郴缁熺鐞嗭紝鏈郴缁熷彧璇汇€?

#### 涓昏瀛楁锛堢敤浜庢悳绱級

| 瀛楁鍚嶏紙涓枃锛?| 瀛楁鍚嶏紙鑻辨枃鍒悕锛?| 璇存槑 |
|----------------|-------------------|------|
| 搴忓垪鍙?| tool_code | 宸ヨ缂栫爜 |
| 宸ヨ鍥惧彿 | drawing_no | 宸ヨ鍥惧彿 |
| 宸ヨ鍚嶇О | tool_name | 宸ヨ鍚嶇О |
| 瑙勬牸鍨嬪彿 | spec_model | 瑙勬牸鍨嬪彿 |
| 褰撳墠鐗堟 | version | 褰撳墠鐗堟 |
| 瀹氭灞炴€?| category | 瀹氭灞炴€?|
| 瀹氭鏈夋晥鎴 | expiry_date | 瀹氭鏈夋晥鎴 |
| 搴旂敤鍘嗗彶 | location_info | 浣嶇疆淇℃伅 |

---

## 3. 鐘舵€佹灇涓?

### 3.1 璁㈠崟鐘舵€?(order_status)

瀹氫箟浣嶇疆锛歞atabase.py:266-277

| 鐘舵€佸€?| 涓枃 | 璇存槑 |
|--------|------|------|
| draft | 鑽夌 | 璁㈠崟鍒氬垱寤?|
| submitted | 宸叉彁浜?| 宸叉彁浜ょ粰淇濈鍛?|
| keeper_confirmed | 淇濈鍛樺凡纭 | 淇濈鍛樺凡纭 |
| partially_confirmed | 閮ㄥ垎纭 | 閮ㄥ垎鏄庣粏宸茬‘璁?|
| transport_notified | 宸查€氱煡杩愯緭 | 宸插彂閫佽繍杈撻€氱煡 |
| final_confirmation_pending | 寰呮渶缁堢‘璁?| 绛夊緟鏈€缁堢‘璁?|
| completed | 宸插畬鎴?| 璁㈠崟瀹屾垚 |
| rejected | 宸叉嫆缁?| 璁㈠崟琚嫆缁?|
| cancelled | 宸插彇娑?| 璁㈠崟宸插彇娑?|

### 3.2 鏄庣粏鐘舵€?(item_status)

瀹氫箟浣嶇疆锛歞atabase.py:280-283

| 鐘舵€佸€?| 涓枃 | 璇存槑 |
|--------|------|------|
| pending_check | 寰呯‘璁?| 绛夊緟纭 |
| approved | 宸茬‘璁?| 宸茬‘璁ら€氳繃 |
| rejected | 宸叉嫆缁?| 宸叉嫆缁?|
| completed | 宸插畬鎴?| 宸插畬鎴?|

---

## 4. Schema 涓嶄竴鑷存姤鍛?

### 4.1 宸蹭慨澶嶇殑涓昏〃缂哄け瀛楁 (2026-03-19)

浠ヤ笅瀛楁宸插湪 `backend/database/schema/schema_manager.py` 鐨?CREATE TABLE 涓ˉ榻愶細

| 瀛楁 | 绫诲瀷 | 鐘舵€?|
|------|------|------|
| org_id | VARCHAR(64) | 鉁?宸茶ˉ榻?|
| 宸茬‘璁ゆ暟閲?| INT | 鉁?宸茶ˉ榻?|
| 鏈€缁堢‘璁や汉 | VARCHAR(64) | 鉁?宸茶ˉ榻?|

### 4.2 宸蹭慨澶嶇殑鏄庣粏琛ㄧ己澶卞瓧娈?(2026-03-19)

| 瀛楁 | 绫诲瀷 | 鐘舵€?|
|------|------|------|
| 纭鏃堕棿 | VARCHAR(500) | 鉁?宸茶ˉ榻愶紙绫诲瀷涓?VARCHAR 鑰岄潪 DATETIME锛?|
| 鍑哄叆搴撳畬鎴愭椂闂?| DATETIME | 鉁?宸茶ˉ榻?|

---

## 5. 鏈潵鍙€夊寮?

| 澧炲己椤?| 璇存槑 | 浼樺厛绾?|
|--------|------|--------|
| 宸ヨ鍥剧墖瀛楁 | 澧炲姞宸ヨ鍥剧墖瀛樺偍 | 浣?|
| 闄勪欢鏀寔 | 鏀寔涓婁紶闄勪欢 | 浣?|
| 瀹℃壒娴佺▼ | 澶氱骇瀹℃壒鏀寔 | 浣?|
| 鎵撳嵃妯℃澘 | 鎵撳嵃鍗曟嵁妯℃澘 | 浣?|

---

## 6. 鐩稿叧鏂囨。

- [API瑙勬牸鏂囨。](./API_SPEC.md)
- [缁ф壙鏁版嵁搴撹闂鏌(./INHERITED_DB_ACCESS_REVIEW.md)
- [浜у搧闇€姹傛枃妗(./PRD.md)
- [鏋舵瀯鏂囨。](./ARCHITECTURE.md)
鏂板缁勭粐褰掑睘瀛楁:

- `org_id`: 璁㈠崟鎵€灞炵粍缁囷紝鐢ㄤ簬 RBAC `ORG` / `ORG_AND_CHILDREN` 鏁版嵁鑼冨洿杩囨护

鍘嗗彶鏁版嵁杩佺Щ瑙勫垯:

- 褰撳巻鍙茶鍗曠己灏?`org_id` 鏃讹紝浼樺厛鍥炲～鍙戣捣浜虹殑涓昏鑹?`org_id`
- 濡傛灉涓昏鑹茬粍缁囦负绌猴紝鍒欏洖濉彂璧蜂汉鐨?`default_org_id`

---

## 7. RBAC Password Audit Schema (2026-03-19)

### 7.1 sys_user_password_change_log

This table stores audit records for user self-service password change attempts and outcomes.

| Column | Type | Nullable | Description |
|---|---|---|---|
| id | BIGINT IDENTITY(1,1) PRIMARY KEY | No | Surrogate key |
| user_id | NVARCHAR(64) | No | User whose password was changed |
| changed_by | NVARCHAR(64) | No | Operator user id (self in current implementation) |
| change_result | NVARCHAR(20) | No | `success` or `failed` |
| remark | NVARCHAR(500) | Yes | Failure or operation note |
| client_ip | NVARCHAR(64) | Yes | Source client IP from request |
| changed_at | DATETIME2 | No | Operation timestamp |

### 7.2 Indexes

- `IX_sys_user_password_change_user_time` on `(user_id, changed_at DESC)`

---

## 8. Feedback Persistence Schema (2026-03-19)

### 8.1 tool_io_feedback

Stores user feedback submitted from settings page, persisted in SQL Server instead of browser local storage.

| Column | Type | Nullable | Description |
|---|---|---|---|
| id | BIGINT IDENTITY(1,1) PRIMARY KEY | No | Surrogate key |
| category | VARCHAR(32) | No | `bug` / `feature` / `ux` / `other` |
| subject | NVARCHAR(200) | No | Feedback title |
| content | NVARCHAR(2000) | No | Feedback body |
| login_name | VARCHAR(100) | No | Submitter login name |
| user_name | NVARCHAR(100) | No | Submitter display name |
| status | VARCHAR(32) | No | `pending` / `reviewed` / `resolved` |
| created_at | DATETIME2 | No | Creation timestamp |
| updated_at | DATETIME2 | No | Last update timestamp |

### 8.2 Indexes

- `IX_tool_io_feedback_login_name` on `(login_name)`
- `IX_tool_io_feedback_created_at` on `(created_at)`

### 8.3 tool_io_feedback_reply

Stores admin reply records for feedback processing history.

| Column | Type | Nullable | Description |
|---|---|---|---|
| id | BIGINT IDENTITY(1,1) PRIMARY KEY | No | Surrogate key |
| feedback_id | BIGINT | No | Reference to `tool_io_feedback.id` |
| reply_content | NVARCHAR(1000) | No | Reply body |
| replier_login_name | VARCHAR(100) | No | Admin login name |
| replier_user_name | NVARCHAR(100) | No | Admin display name |
| created_at | DATETIME2 | No | Reply timestamp |

Foreign key:
- `FK_feedback_reply` on `feedback_id` -> `tool_io_feedback(id)` with `ON DELETE CASCADE`

Indexes:
- `IX_tool_io_feedback_reply_feedback_id` on `(feedback_id)`

---

## 9. Organization Schema (2026-03-19)

### 9.1 sys_org

Stores organization hierarchy for RBAC data scope control.

| Column | Type | Nullable | Description |
|---|---|---|---|
| id | BIGINT IDENTITY(1,1) PRIMARY KEY | No | Surrogate key |
| org_id | NVARCHAR(64) | No | Organization identifier, unique |
| org_name | NVARCHAR(100) | No | Organization display name |
| org_code | NVARCHAR(100) | Yes | Organization code |
| org_type | NVARCHAR(50) | No | Type: company/factory/workshop/team/warehouse/project_group |
| parent_org_id | NVARCHAR(64) | Yes | Parent organization ID |
| sort_no | INT | Yes | Sort order |
| status | NVARCHAR(20) | No | `active` or `disabled` |
| remark | NVARCHAR(500) | Yes | Remark |
| created_at | DATETIME2 | No | Creation timestamp |
| created_by | NVARCHAR(64) | Yes | Creator |
| updated_at | DATETIME2 | Yes | Last update timestamp |
| updated_by | NVARCHAR(64) | Yes | Last updater |

**Indexes:**
- `UX_sys_org_org_id` UNIQUE on `(org_id)`
- `IX_sys_org_parent_org_id` on `(parent_org_id)`

### 9.2 sys_user_org_rel

Maps users to organizations for data scope control.

| Column | Type | Nullable | Description |
|---|---|---|---|
| id | BIGINT IDENTITY(1,1) PRIMARY KEY | No | Surrogate key |
| user_id | NVARCHAR(64) | No | User identifier |
| org_id | NVARCHAR(64) | No | Organization identifier |
| is_primary | BIT | No | Is primary organization (1=yes) |
| status | NVARCHAR(20) | No | `active` or `disabled` |
| created_at | DATETIME2 | No | Creation timestamp |
| created_by | NVARCHAR(64) | Yes | Creator |
| updated_at | DATETIME2 | Yes | Last update timestamp |
| updated_by | NVARCHAR(64) | Yes | Last updater |

---

## 10. Tool Status Change History Schema (2026-03-19)

### 9.1 tool_status_change_history

Stores keeper/system-admin initiated tool status updates and preserves change traceability.

| Column | Type | Nullable | Description |
|---|---|---|---|
| id | BIGINT IDENTITY(1,1) PRIMARY KEY | No | Surrogate key |
| tool_code | NVARCHAR(100) | No | Tool serial/code |
| old_status | NVARCHAR(50) | No | Previous status |
| new_status | NVARCHAR(50) | No | Updated status |
| remark | NVARCHAR(500) | Yes | Optional operation remark |
| operator_id | NVARCHAR(64) | No | Operator user id |
| operator_name | NVARCHAR(100) | No | Operator display name |
| change_time | DATETIME2 | No | Change timestamp |
| client_ip | NVARCHAR(64) | Yes | Source IP |

### 9.2 Indexes

- `IX_tool_status_change_history_tool_code_time` on `(tool_code, change_time)`

