<template>
  <div>
    <div class="toolbar">
      <div class="toolbar-left">
        <el-select v-model="filters.warehouse" placeholder="Склад" clearable @change="loadStock" style="width:200px">
          <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
        </el-select>
        <el-input v-model="filters.search" placeholder="Поиск товара" prefix-icon="Search" clearable style="width:250px" @input="debounceSearch" />
      </div>
      <div style="display:flex;gap:8px">
        <el-button @click="showTransfer = true" style="border-radius:10px;cursor:pointer">Перемещение</el-button>
        <el-button @click="showInventory = true" style="border-radius:10px;cursor:pointer">Инвентаризация</el-button>
      </div>
    </div>

    <div class="card-grid" v-if="summaryCards.length">
      <div v-for="card in summaryCards" :key="card.label" class="stat-card">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
          <div class="stat-icon" :class="card.cls"><el-icon><component :is="card.icon" /></el-icon></div>
        </div>
        <div class="label">{{ card.label }}</div>
        <div class="value">{{ card.value }}</div>
      </div>
    </div>

    <div class="charts-row">
      <div class="chart-card">
        <h3>Остатки товаров</h3>
        <div class="stock-chart-container" :style="{ height: chartHeight + 'px' }">
          <Bar :data="stockBarChartData" :options="stockBarOptions" />
        </div>
      </div>
      <div class="chart-card">
        <h3>Структура остатков по категориям</h3>
        <div style="height:340px;position:relative">
          <Doughnut :data="structureChartData" :options="doughnutOptions" />
        </div>
      </div>
    </div>

    <div class="data-table">
      <el-table :data="stockData" stripe v-loading="loading">
        <el-table-column prop="product_name" label="Товар" min-width="200" />
        <el-table-column prop="warehouse_name" label="Склад" width="140" />
        <el-table-column prop="quantity" label="Факт" width="100" />
        <el-table-column prop="reserved" label="Резерв" width="100" />
        <el-table-column prop="available" label="Доступно" width="100">
          <template #default="{ row }">
            <span :style="{ color: row.available < 5 ? 'var(--danger)' : 'var(--text-primary)', fontWeight: row.available < 5 ? '600' : '400' }">{{ row.available }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="avg_cost" label="Ср. себестоимость" width="150">
          <template #default="{ row }">{{ formatCurrency(row.avg_cost) }}</template>
        </el-table-column>
      </el-table>
      <div style="display:flex;justify-content:flex-end;margin-top:14px">
        <el-pagination v-model:current-page="page" v-model:page-size="perPage" :page-sizes="[10,25,50]" :total="total" layout="total, sizes, prev, pager, next" @current-change="loadStock" @size-change="loadStock" />
      </div>
    </div>

    <div class="charts-row-equal">
      <div class="chart-card">
        <h3>Последние движения</h3>
        <el-table :data="lastMovements" size="small" v-if="lastMovements.length">
          <el-table-column prop="product_name" label="Товар" min-width="140" />
          <el-table-column prop="type" label="Тип" width="80">
            <template #default="{ row }">
              <el-tag :type="row.type === 'in' ? 'success' : row.type === 'out' ? 'danger' : 'warning'" size="small" effect="dark">
                {{ row.type === 'in' ? '+' : row.type === 'out' ? '-' : '→' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="quantity" label="Кол-во" width="80" />
          <el-table-column prop="created_at" label="Дата" width="150">
            <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
          </el-table-column>
        </el-table>
        <div v-else class="empty-state"><p>Нет данных о движениях</p></div>
      </div>
    </div>

    <el-dialog v-model="showTransfer" title="Перемещение между складами" width="500">
      <el-form :model="transferForm" label-width="140px">
        <el-form-item label="Товар">
          <el-select v-model="transferForm.product_id" filterable placeholder="Выбрать...">
            <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Со склада">
          <el-select v-model="transferForm.from_warehouse_id" placeholder="Выбрать...">
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="На склад">
          <el-select v-model="transferForm.to_warehouse_id" placeholder="Выбрать...">
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Количество">
          <el-input-number v-model="transferForm.quantity" :min="0.01" :precision="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTransfer = false" style="cursor:pointer">Отмена</el-button>
        <el-button type="primary" @click="doTransfer" :loading="transferring" style="cursor:pointer">Переместить</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showInventory" title="Инвентаризация" width="600">
      <el-table :data="inventoryItems" size="small">
        <el-table-column prop="name" label="Товар" />
        <el-table-column prop="current" label="Текущий остаток" width="130" />
        <el-table-column label="Фактический" width="150">
          <template #default="{ row }">
            <el-input-number v-model="row.actual" size="small" :precision="2" />
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="showInventory = false" style="cursor:pointer">Отмена</el-button>
        <el-button type="primary" @click="doInventory" :loading="inventing" style="cursor:pointer">Провести</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../api'
import { formatCurrency, formatDateTime } from '../utils/format'
import { ElMessage } from 'element-plus'
import { Doughnut, Bar } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js'
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement)

const stockData = ref([])
const allStockData = ref([])
const warehouses = ref([])
const products = ref([])
const loading = ref(false)
const page = ref(1)
const perPage = ref(10)
const total = ref(0)
const filters = ref({ warehouse: null, search: '' })
const lastMovements = ref([])
const structureData = ref({ labels: [], values: [] })
const showTransfer = ref(false)
const showInventory = ref(false)
const transferring = ref(false)
const inventing = ref(false)

const transferForm = ref({ product_id: null, from_warehouse_id: null, to_warehouse_id: null, quantity: 1 })
const inventoryItems = ref([])

const CHART_COLORS = [
  '#818CF8', '#10B981', '#F59E0B', '#EF4444', '#3B82F6',
  '#A78BFA', '#EC4899', '#06B6D4', '#F97316', '#84CC16',
  '#14B8A6', '#E879F9', '#FB923C', '#38BDF8', '#FBBF24'
]

const summaryCards = computed(() => {
  const totalQty = allStockData.value.reduce((s, r) => s + (r.quantity || 0), 0)
  const totalAvailable = allStockData.value.reduce((s, r) => s + (r.available || 0), 0)
  const totalReserved = allStockData.value.reduce((s, r) => s + (r.reserved || 0), 0)
  const totalValue = allStockData.value.reduce((s, r) => s + (r.quantity || 0) * (r.avg_cost || 0), 0)
  return [
    { label: 'Общий остаток', value: totalQty.toLocaleString('ru-RU') + ' шт', cls: 'stock', icon: 'Box' },
    { label: 'Доступно', value: totalAvailable.toLocaleString('ru-RU') + ' шт', cls: 'revenue', icon: 'Goods' },
    { label: 'В резерве', value: totalReserved.toLocaleString('ru-RU') + ' шт', cls: 'cost', icon: 'Lock' },
    { label: 'Стоимость остатков', value: formatCurrency(totalValue), cls: 'profit', icon: 'Coin' },
  ]
})

const sortedStockForChart = computed(() => {
  return [...allStockData.value]
    .filter(r => r.quantity > 0 && r.product_name)
    .sort((a, b) => b.quantity - a.quantity)
    .slice(0, 15)
})

const stockBarChartData = computed(() => {
  const sorted = sortedStockForChart.value

  if (!sorted.length) {
    return { labels: ['Нет данных'], datasets: [{ data: [0], backgroundColor: ['rgba(148,163,184,0.15)'], borderRadius: 6, barThickness: 24 }] }
  }

  const isHorizontal = sorted.length > 8

  return {
    labels: sorted.map(r => r.product_name),
    datasets: [{
      label: 'Остаток',
      data: sorted.map(r => r.quantity),
      backgroundColor: sorted.map((_, i) => CHART_COLORS[i % CHART_COLORS.length]),
      borderRadius: 6,
      barThickness: isHorizontal ? 18 : Math.max(14, Math.min(32, 320 / sorted.length)),
    }]
  }
})

const chartHeight = computed(() => {
  const count = sortedStockForChart.value.length || 1
  if (count > 8) {
    return Math.min(480, Math.max(340, count * 36 + 80))
  }
  return 340
})

const stockBarOptions = computed(() => {
  const sorted = sortedStockForChart.value
  const itemCount = sorted.length
  const isHorizontal = itemCount > 8

  return {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: isHorizontal ? 'y' : 'x',
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
        borderColor: 'rgba(148, 163, 184, 0.12)',
        borderWidth: 1,
        padding: 12,
        cornerRadius: 10,
        titleFont: { family: "'DM Sans'", size: 13, weight: '600' },
        bodyFont: { family: "'DM Sans'", size: 12 },
        callbacks: {
          label: (ctx) => `Остаток: ${new Intl.NumberFormat('ru-RU').format(ctx.parsed.y ?? ctx.parsed.x)} шт`
        }
      }
    },
    scales: {
      x: {
        grid: { color: 'rgba(148, 163, 184, 0.04)', drawBorder: false },
        ticks: { font: { family: "'DM Sans'", size: 11 }, color: '#64748B', maxRotation: 45, ...(isHorizontal ? { callback: (v) => new Intl.NumberFormat('ru-RU', { notation: 'compact' }).format(v) } : {}) },
        border: { display: false },
        ...(isHorizontal ? { beginAtZero: true } : {})
      },
      y: {
        grid: { color: 'rgba(148, 163, 184, 0.04)', drawBorder: false },
        ticks: { font: { family: "'DM Sans'", size: 11 }, color: '#64748B', ...(!isHorizontal ? { callback: (v) => new Intl.NumberFormat('ru-RU', { notation: 'compact' }).format(v) } : {}) },
        border: { display: false },
        ...(!isHorizontal ? { beginAtZero: true } : {})
      }
    }
  }
})

const structureChartData = computed(() => ({
  labels: structureData.value.labels,
  datasets: [{
    data: structureData.value.values,
    backgroundColor: CHART_COLORS.slice(0, structureData.value.labels.length),
    borderWidth: 0,
    hoverOffset: 8,
  }]
}))

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '66%',
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        usePointStyle: true,
        pointStyle: 'circle',
        padding: 16,
        font: { family: "'DM Sans'", size: 11 },
        color: '#94A3B8',
      }
    },
    tooltip: {
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: 'rgba(148, 163, 184, 0.12)',
      borderWidth: 1,
      padding: 12,
      cornerRadius: 10,
      titleFont: { family: "'DM Sans'", size: 13, weight: '600' },
      bodyFont: { family: "'DM Sans'", size: 12 },
      callbacks: {
        label: (ctx) => {
          const total = ctx.dataset.data.reduce((a, b) => a + b, 0)
          const pct = total > 0 ? ((ctx.parsed / total) * 100).toFixed(1) : 0
          return `${ctx.label}: ${new Intl.NumberFormat('ru-RU').format(ctx.parsed)} ₽ (${pct}%)`
        }
      }
    }
  }
}

let debounceTimer = null
function debounceSearch() { clearTimeout(debounceTimer); debounceTimer = setTimeout(loadStock, 300) }

async function loadStock() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: perPage.value }
    if (filters.value.warehouse) params.warehouse_id = filters.value.warehouse
    if (filters.value.search) params.search = filters.value.search
    const res = await api.get('/stock', { params })
    stockData.value = res.data.data
    total.value = res.data.total
  } finally { loading.value = false }
}

async function loadAllStock() {
  try {
    const params = { per_page: 1000 }
    if (filters.value.warehouse) params.warehouse_id = filters.value.warehouse
    if (filters.value.search) params.search = filters.value.search
    const res = await api.get('/stock', { params })
    let data = res.data.data || res.data
    if (!Array.isArray(data)) data = []
    allStockData.value = data
  } catch { allStockData.value = [] }
}

async function loadAux() {
  const [wRes, pRes, mRes, sRes] = await Promise.all([
    api.get('/warehouses/all'),
    api.get('/products/all'),
    api.get('/stock/last-movements'),
    api.get('/stock/structure'),
  ])
  warehouses.value = Array.isArray(wRes.data) ? wRes.data : wRes.data.data || []
  products.value = Array.isArray(pRes.data) ? pRes.data : pRes.data.data || []
  lastMovements.value = mRes.data
  structureData.value = sRes.data
}

async function doTransfer() {
  transferring.value = true
  try {
    await api.post('/stock/transfer', transferForm.value)
    ElMessage.success('Перемещение выполнено')
    showTransfer.value = false
    await Promise.all([loadStock(), loadAllStock()])
  } catch (e) { ElMessage.error(e.response?.data?.detail?.message || 'Ошибка') }
  finally { transferring.value = false }
}

async function doInventory() {
  inventing.value = true
  try {
    const adjustments = inventoryItems.value
      .filter(i => i.actual !== i.current)
      .map(i => ({ product_id: i.id, actual_quantity: i.actual }))
    if (!adjustments.length) { ElMessage.info('Нет расхождений'); showInventory.value = false; return }
    await api.post('/stock/inventory', adjustments, { params: { warehouse_id: transferForm.value.from_warehouse_id || warehouses.value[0]?.id } })
    ElMessage.success('Инвентаризация проведена')
    showInventory.value = false
    await Promise.all([loadStock(), loadAllStock()])
  } catch (e) { ElMessage.error(e.response?.data?.detail?.message || 'Ошибка') }
  finally { inventing.value = false }
}

onMounted(async () => {
  await loadAux()
  await Promise.all([loadStock(), loadAllStock()])
  inventoryItems.value = products.value.map(p => ({ id: p.id, name: p.name, current: 0, actual: 0 }))
})
</script>

<style scoped>
</style>