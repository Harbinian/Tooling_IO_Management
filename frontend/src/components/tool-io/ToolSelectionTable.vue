<template>
  <div class="space-y-3">
    <div class="flex items-center justify-between">
      <span class="text-sm font-bold text-slate-900">已选工装</span>
      <Badge variant="secondary" class="bg-emerald-50 text-emerald-700 border-emerald-100">
        {{ modelValue.length }}
      </Badge>
    </div>

    <div class="rounded-xl border border-slate-200 overflow-hidden bg-white shadow-sm">
      <div class="overflow-x-auto">
        <table class="w-full text-sm text-left border-collapse">
          <thead class="bg-slate-50 text-slate-500 text-[11px] font-bold uppercase tracking-wider">
            <tr>
              <th class="px-4 py-3">序列号</th>
              <th class="px-4 py-3">工装名称</th>
              <th class="px-4 py-3">工装图号</th>
              <th class="px-4 py-3">工作包</th>
              <th class="px-4 py-3 text-right">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-if="!modelValue.length">
              <td colspan="5" class="px-4 py-10 text-center text-slate-400">尚未选择工装</td>
            </tr>
            <tr v-for="(item, index) in modelValue" :key="item.toolCode" class="hover:bg-slate-50 transition-colors">
              <td class="px-4 py-3 font-mono text-xs font-semibold text-slate-900">{{ item.toolCode }}</td>
              <td class="px-4 py-3 text-slate-600 truncate max-w-[200px]" :title="item.toolName">{{ item.toolName }}</td>
              <td class="px-4 py-3 text-slate-600 truncate max-w-[200px]" :title="item.drawingNo">{{ item.drawingNo || '-' }}</td>
              <td class="px-4 py-3 text-slate-600">{{ item.workPackage || '-' }}</td>
              <td class="px-4 py-3 text-right">
                <Button variant="ghost" size="sm" class="text-rose-600 hover:text-rose-700 hover:bg-rose-50" @click="$emit('remove', index)">
                  移除
                </Button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'

defineProps({
  modelValue: {
    type: Array,
    default: () => []
  }
})

defineEmits(['remove'])
</script>
