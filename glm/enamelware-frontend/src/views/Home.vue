<template>
  <div>
    <div class="toolbar"><h2>Дашборд</h2></div>
    <div style="color:#909399;text-align:center;padding:40px 0">
      Перенаправление на дашборд...
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()
onMounted(() => router.push('/dashboard'))
</script>