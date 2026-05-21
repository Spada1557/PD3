<template>
  <el-card class="list-card" shadow="never">
    <template #header>
      <div class="list-header">
        <div class="list-title">
          <div class="list-icon" v-if="icon">
            <el-icon size="15" color="#fff"><component :is="icon" /></el-icon>
          </div>
          <span>{{ title }}</span>
        </div>
      </div>
    </template>
    <div class="list-body">
      <slot />
    </div>
  </el-card>
</template>

<script setup>
const props = defineProps({ title: String, icon: String })
</script>

<style scoped>
.list-card {
  border-radius: var(--radius-lg) !important;
  border: 1px solid var(--border-light) !important;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.list-card:hover {
  box-shadow: var(--shadow-md) !important;
}

.list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.list-title {
  font-weight: 700;
  font-size: 15px;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 10px;
}

.list-icon {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  display: flex;
  align-items: center;
  justify-content: center;
}

.list-body {
  margin-top: -6px;
}
</style>