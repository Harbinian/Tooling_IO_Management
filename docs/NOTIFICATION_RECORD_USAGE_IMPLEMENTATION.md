# 閫氱煡璁板綍浣跨敤瀹炵幇 / Notification Record Usage Implementation

## Schema 妫€鏌ユ憳瑕?/ Schema inspection summary

宸ヤ綔娴佷娇鐢ㄩ€氳繃 `database.py` 涓殑 `add_tool_io_notification()` 鍜?`update_notification_status()` 瀹炵幇鐨勭幇鏈夐€氱煡琛ㄣ€?
The workflow uses the existing notification table implemented in `database.py` via `add_tool_io_notification()` and `update_notification_status()`.

浠庣湡瀹?schema 鍜岃緟鍔?SQL 纭鐨勫綋鍓嶅瓨鍌ㄥ瓧娈碉細

Current storage fields confirmed from the real schema and helper SQL:

- `order_no`锛氬皢璁板綍鍏宠仈鍒颁竴涓伐瑁呭嚭鍏ュ簱璁㈠崟 / associates the record with one Tool IO order
- `notify_type`锛氫笟鍔＄被鍒紝濡備繚绠″憳璇锋眰鎴栬繍杈撻€氱煡 / business category such as keeper request or transport notice
- `notify_channel`锛氭姇閫掓笭閬撴爣璁帮紱鏈换鍔′娇鐢?`internal` / delivery channel marker; this task uses `internal`
- `receiver`锛氫繚鐣欑殑鎺ユ敹浜烘爣璇嗙鎴栧鍚?/ reserved receiver identifier or name
- `title`锛氱煭閫氱煡鏍囬 / short notification title
- `content`锛氱粨鏋勫寲閫氱煡姝ｆ枃 / structured notification body
- `copy_text`锛氱敤浜庤亰澶╁伐鍏风殑鍙€夌揣鍑戝鍒跺潡 / optional compact copy block for chat tools
- `send_status`锛氬綋鍓嶆姇閫掔姸鎬侊紱鎻掑叆榛樿涓?`pending` / current delivery state; inserts default to `pending`
- `send_time`锛氫繚鐣欎緵灏嗘潵澶栭儴鍙戦€佸畬鎴愪娇鐢?/ reserved for future external send completion
- `send_result`锛氫繚鐣欎緵鎶曢€掔粨鏋滄枃鏈娇鐢?/ reserved for delivery result text
- `retry_count`锛氫繚鐣欎緵浠ュ悗閲嶈瘯闆嗘垚浣跨敤 / reserved for later retry integration
- `created_at`锛氳褰曞垱寤烘椂闂?/ record creation time

## 褰撳墠宸ヤ綔娴佷娇鐢ㄧ殑瀛楁 / Fields used in the current workflow

褰撳墠浠呭唴閮ㄥ伐浣滄祦绉瀬浣跨敤锛?
The current internal-only workflow actively uses:

- `order_no`
- `notify_type`
- `notify_channel`
- `receiver`
- `title`
- `content`
- `copy_text`
- `send_status`
- `created_at`

宸ヤ綔娴佸皻鏈墽琛岀湡瀹炲閮ㄦ姇閫掞紝鍥犳 `send_time`銆乣send_result` 鍜?`retry_count` 淇濈暀渚涘皢鏉ラ涔︽垨寰俊闆嗘垚浣跨敤銆?
The workflow does not perform real external delivery yet, so `send_time`, `send_result`, and `retry_count` remain reserved for future Feishu or WeChat integration.

## 鍒涘缓瑙﹀彂鐐?/ Creation trigger points

閫氱煡璁板綍鐜板湪鍦ㄧ湡瀹炲伐浣滄祦鐐瑰垱寤猴紝鑰屼笉鏄绔嬬殑棰勮鏁版嵁锛?
Notification records are now created at real workflow points instead of being isolated preview data:

- `generate_keeper_text(order_no)`
  - 瀛樺偍 `keeper_request` 璁板綍锛屼娇鐢?`internal` 娓犻亾 / stores a `keeper_request` record with `internal` channel
- `generate_transport_text(order_no)`
  - 瀛樺偍 `transport_preview` 璁板綍锛屼娇鐢?`internal` 娓犻亾鍜?`copy_text` / stores a `transport_preview` record with `internal` channel and `copy_text`
- `notify_transport(order_no, payload)`
  - 瀛樺偍瀹為檯宸ヤ綔娴佷簨浠剁殑 `transport_notice` 椋庢牸璁板綍 / stores a `transport_notice` style record for the actual workflow event
  - 鏍规嵁鐪熷疄鍙戦€佺粨鏋滄洿鏂?`send_status` / updates `send_status` based on the real send result
  - 浠呭湪鐪熷疄鍙戦€佹垚鍔熷悗鏇存柊璁㈠崟澶撮儴涓?`transport_notified` / only updates the order header to `transport_notified` after a successful send
  - 鍐欏叆涓庡彂閫佺粨鏋滀竴鑷寸殑鎿嶄綔鏃ュ織 / writes an operation log entry aligned with the send result

## 鏌ヨ鍜屾樉绀洪泦鎴?/ Query and display integration

鍚庣鏌ヨ璺緞锛?
Backend query paths:

- 璁㈠崟璇︽儏杩愯鏃跺凡杩斿洖 `notification_records` / order detail runtime already returns `notification_records`
- 鏂扮鐐癸細`GET /api/tool-io-orders/<order_no>/notification-records` / new endpoint: `GET /api/tool-io-orders/<order_no>/notification-records`
- 鏈嶅姟鍖呰鍣細`get_notification_records(order_no)` / service wrapper: `get_notification_records(order_no)`

鍓嶇闆嗘垚锛?
Frontend integration:

- `frontend/src/api/toolIO.js` 娣诲姞 `getNotificationRecords(orderNo)` / adds `getNotificationRecords(orderNo)`
- `frontend/src/pages/tool-io/OrderDetail.vue` 鐜板湪鍦ㄨ幏鍙栬鎯呮椂鏄庣‘鍔犺浇閫氱煡璁板綍 / now loads notification records explicitly during detail fetch
- 璁㈠崟璇︽儏椤电户缁覆鏌撻€氱煡鍘嗗彶锛屽寘鎷被鍨嬨€佹爣棰樸€佸唴瀹规憳瑕併€佸彂閫佺姸鎬佸拰鍙戦€佹椂闂?/ continues to render notification history with type, title, content summary, send status, and send time

## 鐘舵€佸鐞嗙瓥鐣?/ Status handling strategy

鏈换鍔′繚鎸侀€氱煡鐘舵€佷互鍐呴儴浼樺厛鍜岀敓浜у畨鍏ㄤ负瀵煎悜銆?
This task keeps notification status internal-first and production-safe.

褰撳墠瀹為檯琛屼负锛?
Current practical behavior:

- 鏂板垱寤虹殑閫氱煡璁板綍榛樿涓?`pending` / newly created notification records default to `pending`
- 棰勮鐢熸垚鍦ㄧ湡瀹炲彂閫佸墠灏卞瓨鍌ㄥ唴瀹逛互淇濇寔鍙拷婧? / preview generation stores content before real delivery for traceability
- 杩愯緭閫氱煡鍦ㄥ疄闄呭彂閫佸皾璇曞悗鏇存柊涓?`send_status = sent` 鎴?`failed` / transport notify updates to `send_status = sent` or `failed` after the real send attempt
- 浠呭湪 `send_status = sent` 鏃舵墠鎺ㄨ繘璁㈠崟鍒?`transport_notified` / the order advances to `transport_notified` only when `send_status = sent`

杩欎繚鎸佷簡娓呮磥鐨勭姸鎬佹ā鍨嬶紝鑰屼笉鏄亣瑁呭閮ㄦ秷鎭凡琚姇閫掋€?
This preserves a clean state model without pretending that an external message was delivered.

## 鍓嶇鏄剧ず闆嗘垚 / Frontend display integration

閲嶇敤鑰屼笉鏄噸鏂拌璁＄幇鏈夌殑璇︽儏椤甸€氱煡閮ㄥ垎銆?
The existing detail page notification section was reused rather than redesigned.

鏄剧ず瀛楁锛?
Displayed fields:

- 鏍囬鎴栭€氱煡绫诲瀷 / title or notification type
- 閫氱煡娓犻亾 / notify channel
- 鎺ユ敹浜?/ receiver
- 鍙戦€佺姸鎬?/ send status
- 鍙戦€佹椂闂?/ send time
- 鍐呭姝ｆ枃 / content body
- 瀛樺湪鏃剁殑澶嶅埗鏂囨湰 / copy text when present

棰勮鍗＄墖浠嶇劧鍙敤浜庝繚绠″憳璇锋眰鏂囨湰銆佽繍杈撴枃鏈拰澶嶅埗鏂囨湰锛岃€岄€氱煡鍘嗗彶閮ㄥ垎鐜板湪鍙嶆槧鏄庣‘鐨勫悗绔煡璇㈢粨鏋溿€?
The preview cards remain available for keeper request text, transport text, and copy text, while the notification history section now reflects explicit backend query results.

## 椋炰功闆嗘垚鍓嶇殑闄愬埗 / Limitations before Feishu integration

褰撳墠瀹炵幇浼氬皾璇曞彂閫侀涔?Webhook锛屽井淇″鍒舵枃鏈仛涓鸿緟鍔╁唴瀹瑰瓨鍌ㄣ€?
The current implementation attempts to send a Feishu webhook, while the WeChat copy text is stored only as auxiliary content.

褰撳墠闄愬埗锛?
Current limitations:

- `notify_transport()` 浠呭湪鍙戦€佹垚鍔熸椂鎵嶆帹杩涘伐浣滄祦鐘舵€? / only advances workflow state when the send succeeds
- 灏氭湭瀛樺偍澶栭儴鍝嶅簲姝ｆ枃 / no external response body is stored yet
- `send_time` 鐢卞綋鍓嶅彂閫佸皾璇曟洿鏂帮紝鑰屼笉鏄洿缁嗙矑搴︾殑鎶曢€掑洖鎵? / `send_time` is updated by the current send attempt rather than a richer delivery receipt
- 閲嶈瘯閫昏緫鏈縺娲?/ retry logic is not active
- 鎺ユ敹浜洪獙璇佷繚鎸佽交閲忥紝鍥犱负灏氭棤澶栭儴鎻愪緵鑰呭绾?/ receiver validation remains lightweight because there is no external provider contract yet

杩欎簺绾︽潫鏄湁鎰忕殑锛屽苟浣垮伐浣滄祦涓轰互鍚庝笓闂ㄧ殑椋炰功闆嗘垚浠诲姟鍋氬ソ鍑嗗銆?
These constraints are intentional and keep the workflow ready for a later dedicated Feishu integration task.

