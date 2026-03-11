<template>
  <div class="selection-panel">
    <div class="panel-title">
      <span>已选工装</span>
      <el-tag type="success">{{ modelValue.length }}</el-tag>
    </div>
    <el-table :data="modelValue" border empty-text="请先从搜索结果中选择工装">
      <el-table-column prop="toolCode" label="工装编码" min-width="140" />
      <el-table-column prop="toolName" label="工装名称" min-width="180" show-overflow-tooltip />
      <el-table-column prop="drawingNo" label="图号" min-width="180" show-overflow-tooltip />
      <el-table-column prop="specModel" label="机型" min-width="110" />
      <el-table-column prop="currentVersion" label="当前版次" min-width="110" />
      <el-table-column prop="currentLocationText" label="库位" min-width="120" show-overflow-tooltip />
      <el-table-column width="100" label="操作" fixed="right">
        <template #default="{ $index }">
          <el-button link type="danger" @click="$emit('remove', $index)">移除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: Array,
    default: () => []
  }
})

defineEmits(['remove'])
</script>

<style scoped>
.selection-panel {
  display: grid;
  gap: 12px;
}

.panel-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
