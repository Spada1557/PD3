<template>
  <el-card class="summary-card" shadow="never">
    <div class="top">
      <div class="icon" :style="{ background: colorConfig.gradient }">
        <el-icon :size="20" color="#fff"><component :is="icon" /></el-icon>
      </div>
      <div class="meta">
        <div class="title">{{ title }}</div>
        <div class="value">{{ value }}</div>
      </div>
    </div>
    <div v-if="change !== undefined" class="change" :class="change >= 0 ? 'up' : 'down'">
      <svg v-if="change >= 0" width="12" height="12" viewBox="0 0 12 12" fill="none">
        <path d="M6 2.5V9.5M6 2.5L3 5.5M6 2.5L9 5.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <svg v-else width="12" height="12" viewBox="0 0 12 12" fill="none">
        <path d="M6 9.5V2.5M6 9.5L9 6.5M6 9.5L3 6.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      {{ Math.abs(change) }}%
      <span class="change-label">к прошлому периоду</span>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ title: String, value: [String, Number], change: Number, icon: String, color: { type: String, default: 'blue' } })
const colors = {
  blue: { gradient: 'linear-gradient(135deg, #8B5CF6, #7C3AED)', glow: 'rgba(139,92,246,0.35)', bg: '#F3E8FF' },
  purple: { gradient: 'linear-gradient(135deg, #6366F1, #4F46E5)', glow: 'rgba(99,102,241,0.35)', bg: '#EEF2FF' },
  green: { gradient: 'linear-gradient(135deg, #34D399, #059669)', glow: 'rgba(52,211,153,0.35)', bg: '#ECFDF5' },
  amber: { gradient: 'linear-gradient(135deg, #FBBF24, #D97706)', glow: 'rgba(251,191,36,0.35)', bg: '#FFFBEB' },
  orange: { gradient: 'linear-gradient(135deg, #FB923C, #EA580C)', glow: 'rgba(251,146,60,0.35)', bg: '#FFF7ED' },
  red: { gradient: 'linear-gradient(135deg, #FB7185, #E11D48)', glow: 'rgba(251,113,133,0.35)', bg: '#FFF1F2' },
  rose: { gradient: 'linear-gradient(135deg, #F472B6, #DB2777)', glow: 'rgba(244,114,182,0.35)', bg: '#FDF2F8' },
}
const colorConfig = computed(() => colors[props.color] || colors.blue)
</script>

<style scoped>
.summary-card {
  border-radius: var(--radius-lg) !important;
  padding: 4px 0;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: default;
  border: 1px solid var(--border-light) !important;
  background: var(--surface-solid) !important;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md) !important;
}

.top {
  display: flex;
  align-items: center;
  gap: 14px;
}

.icon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 14px v-bind('colorConfig.glow');
  flex-shrink: 0;
  transition: transform 0.2s ease;
}

.summary-card:hover .icon {
  transform: scale(1.08);
}

.meta {
  flex: 1;
  min-width: 0;
}

.title {
  color: var(--text-muted);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  margin-bottom: 6px;
}

.value {
  font-size: 22px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.4px;
  line-height: 1.1;
}

.change {
  margin-top: 14px;
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 700;
  font-size: 12px;
}

.up { color: #059669; }
.down { color: #E11D48; }

.change-label {
  color: var(--text-muted);
  font-weight: 500;
  margin-left: 2px;
  font-size: 11px;
}
</style>