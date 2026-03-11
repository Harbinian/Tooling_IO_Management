<script setup>
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import CardContent from '@/components/ui/CardContent.vue'
import { cn } from '@/lib/utils'

const props = defineProps({
  stats: {
    type: Array,
    required: true,
    // Each item: { title: string, value: string | number, description: string, icon: any, trend?: string }
  },
  class: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <div :class="cn('grid gap-4 md:grid-cols-2 lg:grid-cols-4', props.class)">
    <Card v-for="(item, index) in stats" :key="index" class="overflow-hidden bg-white/50 backdrop-blur-sm border-white/20 shadow-shimmer">
      <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle class="text-[11px] font-bold uppercase tracking-wider text-slate-500">
          {{ item.title }}
        </CardTitle>
        <component v-if="item.icon" :is="item.icon" class="h-4 w-4 text-slate-400" />
      </CardHeader>
      <CardContent>
        <div class="text-2xl font-bold tracking-tight text-slate-900">{{ item.value }}</div>
        <div v-if="item.description || item.trend" class="flex items-center gap-1.5 mt-1">
          <span v-if="item.trend" :class="cn('text-[10px] font-bold px-1.5 py-0.5 rounded-full', item.trend.startsWith('+') ? 'bg-emerald-50 text-emerald-600' : 'bg-rose-50 text-rose-600')">
            {{ item.trend }}
          </span>
          <p v-if="item.description" class="text-[11px] text-slate-400 font-medium">
            {{ item.description }}
          </p>
        </div>
      </CardContent>
    </Card>
  </div>
</template>
