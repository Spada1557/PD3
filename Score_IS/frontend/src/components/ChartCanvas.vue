<template>
  <div class="chart-canvas-wrap">
    <canvas ref="canvas" :key="canvasKey"></canvas>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, watch, computed } from 'vue'
import { Chart } from 'chart.js/auto'

const props = defineProps({ type: String, data: Object, options: Object })
const canvas = ref()
let chart = null

const canvasKey = computed(() => `${props.type}-${JSON.stringify(props.data?.labels)}-${Date.now()}`)

const render = () => {
  if (chart) {
    chart.destroy()
    chart = null
  }
  if (!canvas.value) return
  chart = new Chart(canvas.value, {
    type: props.type,
    data: JSON.parse(JSON.stringify(props.data)),
    options: {
      ...props.options,
      animation: {
        duration: 600,
        easing: 'easeOutQuart',
      },
    },
  })
}

onMounted(render)

watch(
  () => [props.type, JSON.stringify(props.data), JSON.stringify(props.options)],
  () => {
    render()
  },
  { flush: 'post' }
)

onUnmounted(() => {
  if (chart) {
    chart.destroy()
    chart = null
  }
})
</script>

<style scoped>
.chart-canvas-wrap {
  position: relative;
  width: 100%;
  height: 100%;
}

.chart-canvas-wrap canvas {
  display: block;
  width: 100% !important;
  height: 100% !important;
}
</style>