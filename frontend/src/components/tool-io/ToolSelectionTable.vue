<template>
  <div class="space-y-3 text-foreground">
    <div class="flex items-center justify-between">
      <span class="text-sm font-bold text-foreground">已选工装</span>
      <Badge variant="secondary" class="bg-emerald-500/10 text-emerald-500 border-emerald-500/20">
        {{ modelValue.length }}
      </Badge>
    </div>

    <div class="rounded-xl border border-border overflow-hidden bg-card shadow-sm">
      <div class="overflow-x-auto">
        <table class="w-full text-sm text-left border-collapse">
          <thead class="bg-muted/50 text-muted-foreground text-[11px] font-bold uppercase tracking-wider">
            <tr>
              <th class="px-4 py-3">序列号</th>
              <th class="px-4 py-3">工装名称</th>
              <th class="px-4 py-3">工装图号</th>
              <th class="px-4 py-3">工作包</th>
              <th class="px-4 py-3 text-right">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border">
            <tr v-if="!modelValue.length">
              <td colspan="5" class="px-4 py-10 text-center text-muted-foreground">尚未选择工装</td>
            </tr>
            <tr v-for="(item, index) in modelValue" :key="item.serialNo" class="hover:bg-muted/30 transition-colors">
              <td class="px-4 py-3 font-mono text-xs font-semibold text-foreground">{{ item.serialNo }}</td>
              <td class="px-4 py-3 text-muted-foreground truncate max-w-[200px]" :title="item.toolName">{{ item.toolName }}</td>
              <td class="px-4 py-3 text-muted-foreground truncate max-w-[200px]" :title="item.drawingNo">{{ item.drawingNo || '-' }}</td>
              <td class="px-4 py-3 text-muted-foreground">{{ item.workPackage || '-' }}</td>
              <td class="px-4 py-3 text-right">
                <Button variant="ghost" size="sm" class="text-rose-500 hover:text-rose-600 hover:bg-rose-500/10" @click="$emit('remove', index)">
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
