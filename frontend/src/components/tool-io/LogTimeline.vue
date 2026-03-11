<template>
  <div v-if="logs.length" class="space-y-4">
    <article
      v-for="(item, index) in logs"
      :key="`${item.actionTime}-${index}`"
      class="relative rounded-2xl border border-slate-200 bg-white/80 p-4 pl-6 shadow-[0_18px_45px_-38px_rgba(15,23,42,0.45)]"
    >
      <div class="absolute left-3 top-5 h-2.5 w-2.5 rounded-full bg-slate-400" />
      <div class="space-y-2">
        <div class="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p class="text-sm font-semibold text-slate-900">{{ item.actionType || 'Action' }}</p>
            <p class="text-xs uppercase tracking-[0.16em] text-slate-400">
              {{ item.operatorName || '-' }} / {{ item.operatorRole || '-' }}
            </p>
          </div>
          <p class="text-xs text-slate-500">{{ formatDateTime(item.actionTime) }}</p>
        </div>
        <p v-if="item.content" class="text-sm leading-6 text-slate-600">{{ item.content }}</p>
      </div>
    </article>
  </div>
  <div
    v-else
    class="flex min-h-40 items-center justify-center rounded-2xl border border-dashed border-slate-200 bg-slate-50/80 px-6 py-10 text-center text-sm text-slate-500"
  >
    No operation logs yet.
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
