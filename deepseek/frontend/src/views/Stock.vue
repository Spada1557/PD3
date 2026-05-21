<template>
  <div>
    <div class="card">
      <div class="table-actions">
        <el-select v-model="filterWarehouse" placeholder="Все склады" clearable style="width:200px" @change="load">
          <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
        </el-select>
        <el-checkbox v-model="lowStockOnly" @change="load" label="Только низкие остатки" border />
        <el-button type="primary" @click="showInventory = true" style="margin-left:auto">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:5px"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
          Инвентаризация
        </el-button>
        <el-button type="default" @click="showTransfer = true">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:5px"><polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/></svg>
          Перемещение
        </el-button>
      </div>

      <div class="stock-chart-panel mb-24">
        <div class="card-header"><h4>Структура остатков</h4><span class="card-badge">По категориям</span></div>
        <div style="position:relative;width:100%;height:280px">
          <canvas ref="structChartRef"></canvas>
        </div>
      </div>

      <div class="card-header mb-16"><h4>Последние движения</h4></div>
      <el-table :data="movements" size="small" style="width:100%;margin-bottom:24px">
        <el-table-column label="Дата" width="130">
          <template #default="{row}">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="Товар" min-width="200" show-overflow-tooltip>
          <template #default="{row}"><span :title="row.product?.name">{{ row.product?.name }}</span></template>
        </el-table-column>
        <el-table-column prop="type" label="Тип" width="100" align="center" />
        <el-table-column prop="quantity" label="Кол-во" width="120" align="center" />
        <el-table-column prop="direction" label="+/–" width="80" align="center" />
      </el-table>

      <el-table :data="stocks" v-loading="loading" size="default" style="width:100%">
        <el-table-column label="Товар" min-width="250" show-overflow-tooltip>
          <template #default="{row}">
            <span :title="row.product?.name">{{ row.product?.name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Артикул" width="140">
          <template #default="{row}"><code style="background:var(--bg-surface);padding:2px 8px;border-radius:4px;font-weight:600;white-space:nowrap">{{ row.product?.article }}</code></template>
        </el-table-column>
        <el-table-column label="Склад" width="130" show-overflow-tooltip>
          <template #default="{row}"><el-tag size="small" type="info" effect="plain" style="white-space:nowrap">{{ row.warehouse?.name }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="quantity" label="Факт" width="85" align="center" />
        <el-table-column prop="reserved" label="Резерв" width="90" align="center" />
        <el-table-column label="Доступно" width="95" align="center">
          <template #default="{row}">
            <span :style="{ color: row.available <= 0 ? '#EF4444' : '#10B981', fontWeight: 700 }">{{ row.available }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Ср.себест." width="160" align="right">
          <template #default="{row}"><span class="amount" style="white-space:nowrap">{{ formatCurrency(row.avg_cost) }}</span></template>
        </el-table-column>
      </el-table>
      <div class="flex-row mt-20" style="justify-content:flex-end">
        <el-pagination v-model:current-page="page" :page-size="perPage" :total="total" @current-change="load" layout="prev, pager, next, total" />
      </div>
    </div>

    <el-dialog v-model="showInventory" title="Инвентаризация" width="720px" :close-on-click-modal="false">
      <div style="margin-bottom:20px;padding:16px;background:var(--accent-soft);border-radius:var(--radius-md)">
        <div style="display:flex;align-items:center;gap:10px;color:var(--accent);font-weight:600;font-size:13px">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          Укажите фактические остатки. Система автоматически рассчитает расхождения.
        </div>
      </div>
      <el-form label-width="80px">
        <el-form-item label="Склад">
          <el-select v-model="invWarehouse" style="width:100%" :teleported="false">
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <div v-for="(item, idx) in invItems" :key="idx" class="inv-row">
        <div class="inv-row-index">{{ idx + 1 }}</div>
        <el-select v-model="item.product_id" placeholder="Товар" filterable style="flex:1" :teleported="false">
          <el-option v-for="s in stocks" :key="s.product_id" :label="`${s.product?.name} (факт: ${s.quantity})`" :value="s.product_id" />
        </el-select>
        <el-input-number v-model="item.fact_quantity" placeholder="Факт" :min="0" :step="1" style="width:150px" />
        <el-button type="danger" plain circle size="small" @click="invItems.splice(idx,1)">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </el-button>
      </div>
      <el-button type="default" @click="invItems.push({product_id:null,fact_quantity:0})" style="width:100%;border-style:dashed;margin-top:4px">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:5px"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        Добавить строку
      </el-button>
      <template #footer><el-button @click="showInventory=false">Отмена</el-button><el-button type="primary" @click="runInventory">Провести инвентаризацию</el-button></template>
    </el-dialog>

    <el-dialog v-model="showTransfer" title="Перемещение между складами" width="500px" :close-on-click-modal="false">
      <el-form label-width="130px">
        <el-form-item label="Товар">
          <el-select v-model="transf.product_id" filterable style="width:100%" :teleported="false">
            <el-option v-for="s in stocks" :key="s.product_id" :label="`${s.product?.name} (${s.warehouse?.name}: ${s.quantity})`" :value="s.product_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Со склада">
          <el-select v-model="transf.from_warehouse_id" style="width:100%" :teleported="false">
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="На склад">
          <el-select v-model="transf.to_warehouse_id" style="width:100%" :teleported="false">
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Количество">
          <el-input-number v-model="transf.quantity" :min="1" style="width:100%" />
        </el-form-item>
      </el-form>
      <template #footer><el-button @click="showTransfer=false">Отмена</el-button><el-button type="primary" @click="runTransfer">Переместить</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import api from '../api/client'
import { formatCurrency, formatDate } from '../utils/format'
import { ElMessage } from 'element-plus'

Chart.register(...registerables)

const stocks = ref([]), warehouses = ref([]), movements = ref([])
const loading = ref(false), page = ref(1), perPage = ref(10), total = ref(0)
const filterWarehouse = ref(null), lowStockOnly = ref(false)
const showInventory = ref(false), showTransfer = ref(false)
const invWarehouse = ref(1), invItems = reactive([{ product_id: null, fact_quantity: 0 }])
const transf = reactive({ product_id: null, from_warehouse_id: 1, to_warehouse_id: 2, quantity: 1 })
const structChartRef = ref(null)
let structChart = null

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: perPage.value }
    if (filterWarehouse.value) params.warehouse_id = filterWarehouse.value
    if (lowStockOnly.value) params.low_stock = true
    const { data } = await api.get('/stock', { params })
    stocks.value = data.data; total.value = data.total
  } catch (e) { ElMessage.error('Ошибка') } finally { loading.value = false }
}

async function loadRefs() {
  const { data: w } = await api.get('/warehouses', { params: { per_page: 100 } })
  warehouses.value = w.data
  const { data: m } = await api.get('/stock/movements', { params: { per_page: 5 } })
  movements.value = m.data
}

async function loadStructure() {
  const { data } = await api.get('/stock/structure', { params: filterWarehouse.value ? { warehouse_id: filterWarehouse.value } : {} })
  if (structChart) structChart.destroy()
  await nextTick()
  if (structChartRef.value && data.data.length) {
    structChart = new Chart(structChartRef.value, {
      type: 'doughnut',
      data: {
        labels: data.data.map(d => d.category),
        datasets: [{
          data: data.data.map(d => d.quantity),
          backgroundColor: ['#7C3AED','#10B981','#F59E0B','#EF4444','#6366F1','#14B8A6','#EC4899'],
          borderColor: '#fff',
          borderWidth: 4,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '62%',
        plugins: { legend: { position: 'bottom', labels: { padding: 18, usePointStyle: true, pointStyleWidth: 10, font: { family: "'DM Sans', sans-serif", size: 12, weight: '500' } } } },
      },
    })
  }
}

async function runInventory() {
  try {
    await api.post('/stock/inventory', { warehouse_id: invWarehouse.value, items: invItems.filter(i => i.product_id) })
    ElMessage.success('Инвентаризация проведена')
    showInventory.value = false; load()
  } catch (e) { ElMessage.error(e.response?.data?.detail?.message || 'Ошибка') }
}

async function runTransfer() {
  try {
    await api.post('/stock/transfer', transf)
    ElMessage.success('Перемещение выполнено')
    showTransfer.value = false; load()
  } catch (e) { ElMessage.error(e.response?.data?.detail?.message || 'Ошибка') }
}

onMounted(async () => { await loadRefs(); await load(); await loadStructure() })
</script>

<style scoped>
.stock-chart-panel {
  background: var(--bg-surface);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  padding: 20px;
  min-width: 0;
}
.inv-row {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 12px;
  padding: 10px 12px;
  background: var(--bg-surface);
  border-radius: var(--radius-md);
}
.inv-row-index {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--accent);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  flex-shrink: 0;
}
@media (max-width: 768px) {
  .stock-chart-panel { padding: 14px; }
}
</style>