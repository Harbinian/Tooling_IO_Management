<template>
  <div v-if="logs.length" class="space-y-4 text-foreground">
    <article
      v-for="(item, index) in logs"
      :key="`${item.actionTime}-${index}`"
      class="relative rounded-2xl border border-border bg-card p-4 pl-6 shadow-sm"
    >
      <div class="absolute left-3 top-5 h-2.5 w-2.5 rounded-full bg-muted-foreground/40" />
      <div class="space-y-2">
        <div class="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p class="text-sm font-semibold text-foreground">{{ item.actionType || '操作' }}</p>
            <p class="text-xs uppercase tracking-[0.16em] text-muted-foreground">
              {{ item.operatorName || '-' }} · {{ item.operatorRole || '-' }}
            </p>
          </div>
          <p class="text-xs text-muted-foreground/60">{{ formatDateTime(item.actionTime) }}</p>
        </div>
        <p v-if="item.content" class="text-sm leading-6 text-muted-foreground">{{ item.content }}</p>
      </div>
    </article>
  </div>
  <div
    v-else
    class="flex min-h-40 items-center justify-center rounded-2xl border border-dashed border-border bg-muted/20 px-6 py-10 text-center text-sm text-muted-foreground"
  >
    暂无操作日志。
  </div>
</template>

<script setup>
import { formatDateTime } from '@/utils/toolIO'

defineProps({
  logs: {
    type: Array,
    default: () => []
  }
})
</script>
