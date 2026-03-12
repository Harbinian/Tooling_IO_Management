# 閺嬭埖鐎槐銏犵穿 / Architecture Index

瀹搞儴顥婇崙鍝勫弳鎼存挾顓搁悶鍡欓兇缂佺喐鐏﹂弸鍕瀮濡楋絼鑵戣箛鍐ㄥ弳閸?

---

## 濮掑倽鍫?/ Overview

閺堫剚鏋冨锝嗘Ц缁崵绮洪弸鑸电€弬鍥ㄣ€傞惃?*娑擃厼绺鹃崣鍌濃偓鍐ㄦ勾閸?*閵? This document serves as the **central reference map for system architecture documentation**.

閹碘偓閺堝濮涢懗钘夌杽閻滄澘绻€妞よ寮懓鍐╂拱閺嬭埖鐎槐銏犵穿閵? All feature implementations must reference this architecture index.

---

## 缁崵绮洪弸鑸电€弬鍥ㄣ€?/ System Architecture Documents

### 閺嶇绺鹃弸鑸电€?/ Core Architecture

| 閺傚洦銆?/ Document | 閹诲繗鍫?/ Description |
|----------------|-------------------|
| docs/ARCHITECTURE.md | 缁崵绮洪幀璁崇秼閺嬭埖鐎?/ System overall architecture |
| docs/ARCHITECTURE_REVIEW.md | 閺嬭埖鐎€光剝鐓＄拋鏉跨秿 / Architecture review records |
| docs/DB_SCHEMA.md | 閺佺増宓佹惔?Schema 鐎规矮绠?/ Database schema definition |
| docs/API_SPEC.md | API 鐟欏嫯瀵?/ API specification |
| docs/PRD.md | 娴溠冩惂闂団偓濮瑰倹鏋冨?/ Product requirements document |

---

## 鐎瑰鍙忔稉?RBAC / Security & RBAC

| 閺傚洦銆?/ Document | 閹诲繗鍫?/ Description |
|----------------|-------------------|
| docs/RBAC_DESIGN.md | RBAC 鐠佹崘顓哥憴鍕瘱 / RBAC design specification |
| docs/RBAC_DATABASE_SCHEMA.md | RBAC 閺佺増宓佹惔?Schema / RBAC database schema |
| docs/RBAC_INIT_DATA.md | RBAC 閸掓繂顫愰崠鏍ㄦ殶閹?/ RBAC initialization data |
| docs/AUTHENTICATION_IMPLEMENTATION.md | 鐠併倛鐦夌€圭偟骞囩拠瀛樻 / Authentication implementation |
| docs/ORG_STRUCTURE_IMPLEMENTATION.md | 缂佸嫮绮愮紒鎾寸€€圭偟骞?/ Organization structure implementation |
| docs/RBAC_ROLE_ASSIGNMENT_AND_ACCOUNT_ADMIN_PAGE.md | administrator account management and role assignment flow |

**闁插秷顩? 娴犺缍嶆稉?RBAC 閻╃鍙ч惃鍕纯閺€鐟扮箑妞よ鍘涢梼鍛邦嚢 RBAC_DESIGN.md**/ **Important: Any RBAC-related changes must read RBAC_DESIGN.md first**

---

## 閺佺増宓佹惔鎾诡啎鐠?/ Database Design

| 閺傚洦銆?/ Document | 閹诲繗鍫?/ Description |
|----------------|-------------------|
| docs/DB_SCHEMA.md | 娑撶粯鏆熼幑顔肩氨 Schema / Main database schema |
| docs/RBAC_DATABASE_SCHEMA.md | RBAC 閺佺増宓佹惔?Schema / RBAC database schema |
| docs/SQLSERVER_SCHEMA_REVISION.md | SQL Server Schema 娣囶喛顓?/ SQL Server schema revision |
| docs/DATABASE_ALIGNMENT_IMPLEMENTATION.md | 閺佺増宓佹惔鎾愁嚠姒绘劕鐤勯悳?/ Database alignment implementation |
| docs/DATABASE_SETTINGS_COMPATIBILITY_FIX.md | 閺佺増宓佹惔鎾诡啎缂冾喖鍚嬬€硅鈧傛叏婢?/ Database settings compatibility fix |
| docs/INHERITED_DB_ACCESS_REVIEW.md | 缂佈勫閺佺増宓佹惔鎾诡問闂傤喖顓搁弻?/ Inherited database access review |

**闁插秷顩? 娴犺缍嶉弫鐗堝祦鎼存挻娲块弨鐟扮箑妞よ鍘涢梼鍛邦嚢 RBAC_DATABASE_SCHEMA.md**/ **Important: Any database changes must read RBAC_DATABASE_SCHEMA.md first**

---

## 瀹搞儰缍斿ù浣风瑢娑撴艾濮熼柅鏄忕帆 / Workflow & Business Logic

| 閺傚洦銆?/ Document | 閹诲繗鍫?/ Description |
|----------------|-------------------|
| docs/ORDER_SUBMISSION_IMPLEMENTATION.md | 鐠併垹宕熼幓鎰唉濞翠胶鈻肩€圭偟骞?/ Order submission workflow implementation |
| docs/KEEPER_CONFIRMATION_IMPLEMENTATION.md | 娣囨繄顓搁崨妯尖€樼拋銈嗙ウ缁?/ Keeper confirmation workflow |
| docs/FINAL_CONFIRMATION_IMPLEMENTATION.md | 閺堚偓缂佸牏鈥樼拋銈嗙ウ缁?/ Final confirmation workflow |
| docs/NOTIFICATION_SERVICE_FRAMEWORK.md | notification service framework / internal notification design |
| docs/NOTIFICATION_RECORD_USAGE_IMPLEMENTATION.md | 闁氨鐓＄拋鏉跨秿娴ｈ法鏁?/ Notification record usage |
| docs/FEISHU_NOTIFICATION_ADAPTER.md | Feishu notification adapter / external notification delivery |
| docs/FEISHU_INTEGRATION_IMPLEMENTATION.md | 妞嬬偘鍔熼梿鍡樺灇鐎圭偟骞?/ Feishu integration implementation |
| docs/OPERATION_AUDIT_LOG_SYSTEM.md | operation audit log system / operation audit log implementation |
| docs/TRANSPORT_WORKFLOW_STATE.md | transport workflow state / transport lifecycle design |
| docs/TOOL_LOCATION_MANAGEMENT.md | tool location management / workflow-driven location consistency |

---

## 閸撳秶顏弸鑸电€?/ Frontend Architecture

| 閺傚洦銆?/ Document | 閹诲繗鍫?/ Description |
|----------------|-------------------|
| docs/FRONTEND_DESIGN.md | 閸撳秶顏拋鎹愵吀 / Frontend design |
| docs/FRONTEND_UI_COMPONENT_MAP.md | 閸撳秶顏?UI 缂佸嫪娆㈤弰鐘茬殸 / Frontend UI component map |
| docs/FRONTEND_UI_FOUNDATION_IMPLEMENTATION.md | 閸撳秶顏?UI 閸╄櫣顢呯€圭偟骞?/ Frontend UI foundation implementation |
| docs/FRONTEND_STYLE_MIGRATION_PLAN.md | 閸撳秶顏弽宄扮础鏉╀胶些鐠佲€冲灊 / Frontend style migration plan |
| docs/ORDER_LIST_UI_MIGRATION.md | 鐠併垹宕熼崚妤勩€?UI 鏉╀胶些 / Order list UI migration |
| docs/ORDER_DETAIL_UI_MIGRATION.md | 鐠併垹宕熺拠锔藉剰 UI 鏉╀胶些 / Order detail UI migration |
| docs/ORDER_CREATE_UI_MIGRATION.md | 鐠併垹宕熼崚娑樼紦 UI 鏉╀胶些 / Order create UI migration |
| docs/KEEPER_PROCESS_UI_MIGRATION.md | 娣囨繄顓搁崨妯荤ウ缁?UI 鏉╀胶些 / Keeper process UI migration |
| docs/STRUCTURED_MESSAGE_PREVIEW_UI.md | 缂佹挻鐎崠鏍ㄧХ閹垶顣╃憴?UI / Structured message preview UI |
| docs/TOOL_SEARCH_DIALOG_IMPLEMENTATION.md | 瀹搞儴顥婇幖婊呭偍鐎电鐦藉鍡楃杽閻?/ Tool search dialog implementation |
| docs/TOOL_MASTER_FIELD_MAPPING.md | 瀹搞儴顥婃稉缁樻殶閹诡喖鐡у▓鍨Ё鐏?/ Tool master field mapping |
| docs/TOOL_SEARCH_DB_INTEGRATION.md | 瀹搞儴顥婇幖婊呭偍閺佺増宓佹惔鎾绘肠閹?/ Tool search database integration |

---

## AI 瀵偓閸欐垵浼愭担婊勭ウ / AI Development Workflow

| 閺傚洦銆?/ Document | 閹诲繗鍫?/ Description |
|----------------|-------------------|
| docs/AI_DEVOPS_ARCHITECTURE.md | AI DevOps 閺嬭埖鐎?/ AI DevOps architecture |
| docs/AI_DEVOPS_SYSTEM_ARCHITECTURE.md | AI DevOps 缁崵绮洪弸鑸电€?/ AI DevOps system architecture |
| docs/AI_PIPELINE.md | AI 濞翠焦鎸夌痪?/ AI pipeline |
| docs/PROMPT_TASK_CONVENTION.md | 閹绘劗銇氱拠宥勬崲閸斅ゎ潐閼?/ Prompt task convention |
| docs/COLLABORATION.md | 閸楀繋缍旂憴鍕瘱 / Collaboration guidelines |

---

## Bug 婢跺嫮鎮?/ Bug Handling

| 閺傚洦銆?/ Document | 閹诲繗鍫?/ Description |
|----------------|-------------------|
| docs/BUG_WORKFLOW_RULES.md | Bug 瀹搞儰缍斿ù浣筋潐閸?/ Bug workflow rules |
| docs/INCIDENT_RESPONSE_FLOW.md | 娴滃娆㈤崫宥呯安濞翠胶鈻?/ Incident response flow |
| docs/TROUBLESHOOTING_FRONTEND_API_ERRORS.md | 閸撳秶顏?API 闁挎瑨顕ら幒鎺撶叀 / Frontend API error troubleshooting |
| docs/RELEASE_PRECHECK_REPORT.md | 閸欐垵绔锋０鍕梾閹躲儱鎲?/ Release precheck report |

### Bug 娣囶喖顦茬拋鏉跨秿 / Bug Fix Records

| 閺傚洦銆?/ Document | 閹诲繗鍫?/ Description |
|----------------|-------------------|
| docs/BUG_TOOL_SEARCH_REQUEST_ROUTING.md | 瀹搞儴顥婇幖婊呭偍鐠囬攱鐪扮捄顖滄暠 Bug / Tool search request routing bug |
| docs/BUG_VITE_ENTRY_COMPILE_FAILURE.md | Vite 閸忋儱褰涚紓鏍槯婢惰精瑙?Bug / Vite entry compile failure bug |
| docs/BUG_ORDER_LIST_API_500.md | 鐠併垹宕熼崚妤勩€?API 500 闁挎瑨顕?Bug / Order list API 500 error bug |
| docs/BUG_DUPLICATE_SIDEBAR_LAYOUT_CONFLICT.md | 闁插秴顦叉笟褑绔熼弽蹇撶鐏炩偓閸愯尙鐛?Bug / Duplicate sidebar layout conflict bug |

---

## 妞ゅ湱娲扮粻锛勬倞 / Project Management

| 閺傚洦銆?/ Document | 閹诲繗鍫?/ Description |
|----------------|-------------------|
| docs/TASKS.md | 娴犺濮熼崚妤勩€?/ Task list |
| docs/README_AI_SYSTEM.md | AI 缁崵绮洪懛顏囧牚 / AI system README |

---

## 閺嬭埖鐎担璺ㄦ暏鐟欏嫬鍨?/ Architecture Usage Rules

### RBAC 閻╃鍙?/ RBAC Related

1. 娴犺缍嶆稉?RBAC 閻╃鍙ч惃鍕纯閺€鐟扮箑妞よ鍘涢梼鍛邦嚢 `docs/RBAC_DESIGN.md`閵?
   / Any RBAC-related changes must read `docs/RBAC_DESIGN.md` first.

2. 娴犺缍嶉弶鍐閻╃鍙ч惃鍕纯閺€鐟扮箑妞よ鍘涢梼鍛邦嚢 `docs/RBAC_DATABASE_SCHEMA.md`閵?
   / Any permission-related changes must read `docs/RBAC_DATABASE_SCHEMA.md` first.

3. 娴犺缍嶉弶鍐閸掓繂顫愰崠鏍х箑妞よ寮懓?`docs/RBAC_INIT_DATA.md`閵?
   / Any permission initialization must reference `docs/RBAC_INIT_DATA.md`.

4. 缁備焦顒涢崷銊︽弓濡偓閺屻儴绻栨禍娑欐瀮濡楋絿娈戦幆鍛枌娑撳鍣搁弬鏉跨暰娑?RBAC 闁槒绶妴?
   / No model should redefine RBAC logic without checking these documents.

### 閺佺増宓佹惔鎾舵祲閸?/ Database Related

1. 娴犺缍嶉弫鐗堝祦鎼?Schema 閺囧瓨鏁艰箛鍛淬€忛崗鍫ユ鐠?`docs/RBAC_DATABASE_SCHEMA.md`閵?
   / Any database schema changes must read `docs/RBAC_DATABASE_SCHEMA.md` first.

2. 娴犺缍嶉弫鐗堝祦鎼存挻娲块弨鐟扮箑妞よ寮懓?`docs/DB_SCHEMA.md`閵?
   / Any database changes must reference `docs/DB_SCHEMA.md`.

3. SQL Server 閻楃懓鐣鹃弴瀛樻暭韫囧懘銆忛崣鍌濃偓?`docs/SQLSERVER_SCHEMA_REVISION.md`閵?
   / SQL Server-specific changes must reference `docs/SQLSERVER_SCHEMA_REVISION.md`.

### API 閻╃鍙?/ API Related

1. 娴犺缍?API 閺囧瓨鏁艰箛鍛淬€忛崗鍫ユ鐠?`docs/API_SPEC.md`閵?
   / Any API changes must read `docs/API_SPEC.md` first.

2. 娴犺缍嶉弬鎵伂閻愮懓鐤勯悳鏉跨箑妞よ绗?API 鐟欏嫯瀵栫€靛綊缍堥妴?
   / Any new endpoint implementation must align with the API specification.

### 閸撳秶顏惄绋垮彠 / Frontend Related

1. 娴犺缍嶉崜宥囶伂 UI 閺囧瓨鏁艰箛鍛淬€忛崣鍌濃偓?`docs/FRONTEND_UI_COMPONENT_MAP.md`閵?
   / Any frontend UI changes must reference `docs/FRONTEND_UI_COMPONENT_MAP.md`.

2. 娴犺缍嶉弽宄扮础閺囧瓨鏁艰箛鍛淬€忛崣鍌濃偓?`docs/FRONTEND_STYLE_MIGRATION_PLAN.md`閵?
   / Any style changes must reference `docs/FRONTEND_STYLE_MIGRATION_PLAN.md`.

---

## AI 濡€崇€峰銉ょ稊濞?/ AI Model Workflow

### 鐎圭偟骞囬崜宥呯箑妞よ濮炴潪鐣屾畱閺傚洦銆?/ Documents to Load Before Implementation

閸︺劌鐤勯悳棰佹崲娴ｆ洖鎮楃粩顖炩偓鏄忕帆娑斿澧犻敍灞灸侀崹瀣箑妞ゅ顩婚崗鍫濆鏉? / Before implementing any backend logic, models must first load:

1. `docs/ARCHITECTURE_INDEX.md` (閺堫剚鏋冨? / (this document)
2. 閻掕泛鎮楅弽瑙勫祦娴犺濮熺猾璇茬€烽崝鐘烘祰閻╃鍙ч弸鑸电€弬鍥ㄣ€?/ Then load relevant architecture documents based on task type

### 閸忚渹缍嬫禒璇插缁鐎?/ Specific Task Types

| 娴犺濮熺猾璇茬€?/ Task Type | 韫囧懘銆忛崝鐘烘祰閻ㄥ嫭鏋冨?/ Required Documents |
|---------------------|-----------------------------------|
| 鐠併倛鐦?/ Authentication | docs/RBAC_DESIGN.md, docs/API_SPEC.md |
| 閹哄牊娼?/ Authorization | docs/RBAC_DESIGN.md, docs/RBAC_DATABASE_SCHEMA.md |
| 閺佺増宓佹惔?Schema / Database Schema | docs/RBAC_DATABASE_SCHEMA.md, docs/DB_SCHEMA.md |
| 閻樿埖鈧焦婧€ / State Machine | docs/ARCHITECTURE.md, docs/API_SPEC.md |
| 閸撳秶顏?UI / Frontend UI | docs/FRONTEND_UI_COMPONENT_MAP.md, docs/FRONTEND_DESIGN.md |
| Bug 娣囶喖顦?/ Bug Fix | docs/BUG_WORKFLOW_RULES.md, 閻╃鍙?Bug 閺傚洦銆?/ Related bug document |

### RUNPROMPT 闂嗗棙鍨?/ RUNPROMPT Integration

閸︺劍澧界悰灞兼崲娴ｆ洘褰佺粈楦跨槤娴犺濮熸稊瀣: / Before executing any prompt task:

1. 閸旂姾娴?`docs/ARCHITECTURE_INDEX.md`
2. 鐠囧棗鍩嗛惄绋垮彠閺嬭埖鐎弬鍥ㄣ€?
3. 閸旂姾娴囬惄绋垮彠閺傚洦銆?
4. 瀵偓婵鐤勯悳?

---

## 閺傚洦銆傞悧鍫熸拱 / Document Version

| 閻楀牊婀?/ Version | 閺冦儲婀?/ Date | 閹诲繗鍫?/ Description |
|---------------|-------------|-------------------|
| 1.0 | 2026-03-12 | 閸掓繂顫愰悧鍫熸拱 / Initial version |

---

## 缂佸瓨濮?/ Maintenance

閺堫剛鍌ㄥ鏇熸瀮濡楋絿鏁遍弸鑸电€敮鍫㈡樊閹躲們鈧? This index document is maintained by the architect.

娴犺缍嶉弬鏉款杻閺嬭埖鐎弬鍥ㄣ€傛惔鏃€娲块弬鐗堟拱閺傚洦銆傞妴? Any new architecture documents should update this document.

**闁插秷顩? 閸︺劌鐤勯悳棰佹崲娴ｆ洖濮涢懗鎴掔閸撳稄绱濇慨瀣矒閸忓牆寮懓鍐╂拱閺嬭埖鐎槐銏犵穿**/ **Important: Always reference this architecture index before implementing any feature**

