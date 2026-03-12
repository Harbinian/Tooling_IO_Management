<template>
  <Card :class="cn('h-full bg-white/50 backdrop-blur-sm border-white/20 shadow-shimmer flex flex-col', props.class)">
    <CardHeader class="border-b border-slate-100/50 bg-slate-50/30 py-3 shrink-0">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <component :is="typeIcon" class="h-4 w-4 text-slate-400" />
          <CardTitle class="text-[11px] font-bold uppercase tracking-wider text-slate-500">{{ displayTitle }}</CardTitle>
        </div>
        <Button
          variant="ghost"
          size="sm"
          class="h-7 px-2 text-[10px] font-bold uppercase tracking-tight text-slate-400 hover:text-slate-900 hover:bg-slate-100 transition-all"
          :disabled="!content || loading"
          @click="handleCopy"
        >
          <Copy class="mr-1 h-3 w-3" />
          {{ copied ? '已复制' : '复制' }}
        </Button>
      </div>
    </CardHeader>

    <CardContent class="p-0 flex-1 relative min-h-[160px]">
      <div v-if="loading" class="absolute inset-0 bg-white/60 backdrop-blur-[1px] flex items-center justify-center z-10">
        <RefreshCw class="h-5 w-5 text-slate-300 animate-spin" />
      </div>

      <div class="p-4 h-full">
        <div v-if="content" class="h-full animate-in fade-in duration-300">
          <pre class="preview-text">{{ content }}</pre>
        </div>

        <div v-else class="h-full flex flex-col items-center justify-center text-center opacity-40 py-8">
          <FileText class="h-8 w-8 text-slate-300 mb-2" />
          <p class="text-[11px] text-slate-500 font-medium">
            {{ emptyText || '暂无预览内容' }}
          </p>
        </div>
      </div>
    </CardContent>

    <div v-if="content && showHint" class="px-4 py-2 bg-slate-50/50 border-t border-slate-50 shrink-0">
      <p class="text-[10px] text-slate-400 flex items-center gap-1.5">
        <Info class="h-3 w-3" />
        当前文本已按结构化格式生成，可直接复制发送。
      </p>
    </div>
  </Card>
</template>

<script setup>
import { computed, ref } from 'vue'
import {
  Copy,
  FileText,
  RefreshCw,
  Info,
  UserCheck,
  Truck,
  MessageSquare
} from 'lucide-vue-next'
import { cn } from '@/lib/utils'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import CardContent from '@/components/ui/CardContent.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'

// Temporary notification helper
const showToast = (msg) => {
  console.log('[Toast]', msg)
  alert(msg)
}


const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  content: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'generic'
  },
  loading: {
    type: Boolean,
    default: false
  },
  emptyText: {
    type: String,
    default: ''
  },
  showHint: {
    type: Boolean,
    default: true
  },
  class: {
    type: String,
    default: ''
  }
})

const copied = ref(false)

const typeIcon = computed(() => {
  switch (props.type) {
    case 'keeper':
      return UserCheck
    case 'transport':
      return Truck
    case 'wechat':
      return MessageSquare
    default:
      return FileText
  }
})

const displayTitle = computed(() => {
  if (props.title) return props.title
  switch (props.type) {
    case 'keeper':
      return '保管员通知预览'
    case 'transport':
      return '运输通知预览'
    case 'wechat':
      return '微信复制文本'
    default:
      return '文本预览'
  }
})

async function handleCopy() {
  if (!props.content) return

  try {
    await navigator.clipboard.writeText(props.content)
    copied.value = true
    showToast('复制成功')
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch {
    showToast('复制失败')
  }
}
</script>

<style scoped>
.preview-text {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 12px;
  line-height: 1.6;
  color: #475569;
}
</style>
