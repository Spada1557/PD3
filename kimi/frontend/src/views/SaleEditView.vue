<template>
  <div class="page-view">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">Продажа</h1>
        <p class="page-subtitle">Детали документа реализации</p>
      </div>
    </div>
    <el-card v-if="doc" shadow="never">
      <template #header>
        <div class="doc-header">
          <div class="doc-number">Документ: <span>{{ doc.number }}</span></div>
          <el-tag :type="statusTag(doc.status)">{{ statusLabel(doc.status) }}</el-tag>
        </div>
      </template>
      <div class="info">
        <div class="info-item">
          <div class="info-label">Клиент</div>
          <div class="info-value">{{ doc.client?.name }}</div>
        </div>
        <div class="info-item">
          <div class="info-label">Дата</div>
          <div class="info-value">{{ formatDate(doc.date) }}</div>
        </div>
        <div class="info-item">
          <div class="info-label">Сумма</div>
          <div class="info-value">{{ formatMoney(doc.total_amount) }}</div>
        </div>
        <div class="info-item">
          <div class="info-label">Себест.</div>
          <div class="info-value">{{ formatMoney(doc.total_cost) }}</div>
        </div>
        <div class="info-item full">
          <div class="info-label">Комментарий</div>
          <div class="info-value">{{ doc.comment || '—' }}</div>
        </div>
      </div>

      <div class="section-label">Позиции</div>
      <el-table :data="doc.items" size="small">
        <el-table-column prop="product.article" label="Артикул" />
        <el-table-column prop="product.name" label="Товар" show-overflow-tooltip />
        <el-table-column prop="quantity" label="Кол-во" />
        <el-table-column prop="price" label="Цена" />
        <el-table-column prop="amount" label="Сумма" />
      </el-table>
      <div class="doc-actions">
        <el-button type="success" v-if="doc.status==='draft'" @click="post">Провести</el-button>
        <el-button type="danger" v-if="doc.status==='posted'" @click="cancel">Отменить проведение</el-button>
        <el-button @click="$router.push('/sales')">Назад</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { salesApi } from '../api'
const route = useRoute()
const doc = ref(null)
const load = async () => { const res = await salesApi.get(route.params.id); doc.value = res.data }
const post = async () => {
  try { await salesApi.post(route.params.id); ElMessage.success('Проведено'); load() }
  catch (e){ ElMessage.error(e.response?.data?.detail || e.response?.data?.message || 'Ошибка проведения') }
}
const cancel = async () => {
  try { await salesApi.cancel(route.params.id); ElMessage.success('Отменено'); load() }
  catch (e){ ElMessage.error(e.response?.data?.detail || e.response?.data?.message || 'Ошибка отмены') }
}
function formatMoney(v){ return new Intl.NumberFormat('ru-RU',{style:'currency', currency:'RUB', maximumFractionDigits:0}).format(v) }
function formatDate(d){ return d ? new Date(d).toLocaleDateString('ru-RU') : '' }
function statusTag(s){ return {draft:'info', posted:'success', cancelled:'danger'}[s]||'' }
function statusLabel(s){ return {draft:'Черновик', posted:'Проведен', cancelled:'Отменен'}[s]||s }
onMounted(load)
</script>

<style scoped>
.doc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}
.doc-number {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
}
.doc-number span {
  color: var(--text-secondary);
  font-weight: 800;
}
.info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}
.info-item {
  background: var(--surface-overlay);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: 14px 16px;
}
.info-item.full {
  grid-column: 1 / -1;
}
.info-label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: var(--text-muted);
  margin-bottom: 6px;
}
.info-value {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
}
.section-label {
  font-weight: 800;
  font-size: 14px;
  color: var(--text-primary);
  margin-bottom: 12px;
  letter-spacing: -0.2px;
}
.doc-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
</style>
