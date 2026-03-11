<script setup>
import Card from '@/components/ui/Card.vue'
import CardHeader from '@/components/ui/CardHeader.vue'
import CardTitle from '@/components/ui/CardTitle.vue'
import CardContent from '@/components/ui/CardContent.vue'
import Button from '@/components/ui/Button.vue'
import { cn } from '@/lib/utils'

const props = defineProps({
  features: {
    type: Array,
    required: true,
    // Each item: { title: string, description: string, icon: any, link: string, actionText: string }
  },
  class: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <div :class="cn('grid gap-4 md:grid-cols-2 lg:grid-cols-3', props.class)">
    <Card v-for="(item, index) in features" :key="index" class="flex flex-col border-dashed hover:border-solid bg-white/50 backdrop-blur-sm border-slate-200/60 hover:bg-white transition-all">
      <CardHeader>
        <div v-if="item.icon" class="mb-3 w-10 h-10 flex items-center justify-center rounded-xl bg-slate-900 text-white shadow-lg shadow-slate-200/50">
          <component :is="item.icon" class="h-5 w-5" />
        </div>
        <CardTitle class="text-base font-bold text-slate-900 tracking-tight">{{ item.title }}</CardTitle>
      </CardHeader>
      <CardContent class="flex-1 flex flex-col justify-between">
        <p class="text-[13px] leading-relaxed text-slate-500 mb-6">
          {{ item.description }}
        </p>
        <router-link :to="item.link" class="mt-auto">
          <Button variant="outline" size="sm" class="w-full justify-center font-bold text-slate-600 border-slate-200/60 hover:bg-slate-900 hover:text-white hover:border-slate-900 transition-all">
            {{ item.actionText }}
          </Button>
        </router-link>
      </CardContent>
    </Card>
  </div>
</template>
