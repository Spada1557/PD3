<template>
  <div class="stock-page">
    <!-- Header -->
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">Складские остатки</h1>
        <p class="page-subtitle">Управление остатками и перемещениями товаров</p>
      </div>
      <div class="page-header-actions">
        <el-select v-model="warehouseId" placeholder="Все склады" clearable style="width:200px" @change="load">
          <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
        </el-select>
        <el-button type="primary" @click="openMoveDialog">
          <el-icon size="16" style="margin-right:6px"><Right /></el-icon>
          Перемещение
        </el-button>
        <el-button @click="openInventoryDialog">
          <el-icon size="16" style="margin-right:6px"><EditPen /></el-icon>
          Инвентаризация
        </el-button>
      </div>
    </div>

    <!-- Stats -->
    <div class="stats-row">
      <div class="stat-card" v-for="s in statCards" :key="s.label">
        <div class="stat-icon" :style="{ background: s.gradient }">
          <el-icon size="20" color="#fff"><component :is="s.icon" /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ s.value }}</div>
          <div class="stat-label">{{ s.label }}</div>
        </div>
      </div>
    </div>

    <!-- Content grid -->
    <div class="content-grid">
      <div class="chart-section">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <div class="card-title-group">
                <span class="card-title">Структура остатков</span>
                <el-tag size="small" type="info">По товарам</el-tag>
              </div>
              <div class="chart-toggle">
                <el-button-group>
                  <el-button :type="chartMode === 'value' ? 'primary' : 'default'" size="small" @click="chartMode = 'value'">Стоимость</el-button>
                  <el-button :type="chartMode === 'qty' ? 'primary' : 'default'" size="small" @click="chartMode = 'qty'">Количество</el-button>
                </el-button-group>
              </div>
            </div>
          </template>
          <div class="chart-container">
            <ChartCanvas v-if="doughnutData.labels.length > 0" type="doughnut" :data="doughnutData" :options="doughnutOpts" />
            <div v-else class="chart-empty">
              <el-icon size="48" color="#D4D0E0"><PieChart /></el-icon>
              <div class="chart-empty-text">Нет данных для отображения</div>
              <div class="chart-empty-sub">Добавьте товары на склад для построения графика</div>
            </div>
          </div>
        </el-card>
      </div>

      <div class="table-section">
        <el-card shadow="never" class="table-card">
          <template #header>
            <div class="card-header">
              <div class="card-title-group">
                <span class="card-title">Товары на складе</span>
                <el-tag size="small" type="info">{{ total }} записей</el-tag>
              </div>
            </div>
          </template>
          <el-table :data="stock" v-loading="loading" stripe style="width:100%">
            <el-table-column label="Товар" min-width="240" show-overflow-tooltip>
              <template #default="{ row }">
                <div class="product-cell">
                  <div class="product-name">{{ productName(row) }}</div>
                  <div class="product-article">{{ productArticle(row) }}</div>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="Склад">
              <template #default="{ row }">
                <el-tag size="small" effect="plain" style="white-space:nowrap">{{ warehouseName(row) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Факт" align="right">
              <template #default="{ row }">
                <span class="qty-value col-nowrap">{{ row.quantity }}</span>
              </template>
            </el-table-column>
            <el-table-column label="Резерв" align="right">
              <template #default="{ row }">
                <span class="reserved-value col-nowrap">{{ row.reserved }}</span>
              </template>
            </el-table-column>
            <el-table-column label="Доступно" align="right">
              <template #default="{ row }">
                <span :class="['available-value', row.available <= 0 ? 'zero' : '']">{{ row.available }}</span>
              </template>
            </el-table-column>
            <el-table-column label="Ср. себест." align="right">
              <template #default="{ row }">
                <span class="money-value col-nowrap">{{ formatMoney(row.avg_cost) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="Стоимость" align="right">
              <template #default="{ row }">
                <span class="money-value total-value col-nowrap">{{ formatMoney(row.quantity * row.avg_cost) }}</span>
              </template>
            </el-table-column>
          </el-table>
          <div class="pagination-wrap">
            <el-pagination background layout="prev, pager, next" :total="total" :page-size="perPage" v-model:current-page="page" @current-change="load" />
          </div>
        </el-card>
      </div>
    </div>

    <!-- Dialogs -->
    <el-dialog v-model="moveVisible" title="Перемещение товара" width="480" :close-on-click-modal="false">
      <el-form :model="moveForm" label-width="140px" class="premium-form">
        <el-form-item label="Товар" required>
          <el-select v-model="moveForm.product_id" filterable placeholder="Выберите товар" style="width:100%">
            <el-option v-for="p in allProducts" :key="p.id" :label="`${p.article} ${p.name}`" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Со склада" required>
          <el-select v-model="moveForm.from_warehouse_id" placeholder="Исходный склад" style="width:100%">
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="На склад" required>
          <el-select v-model="moveForm.to_warehouse_id" placeholder="Целевой склад" style="width:100%">
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Количество" required>
          <el-input-number v-model="moveForm.quantity" :min="0.01" :precision="2" style="width:100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="moveVisible = false">Отмена</el-button>
        <el-button type="primary" @click="doMove">Переместить</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="invVisible" title="Инвентаризация" width="520" :close-on-click-modal="false">
      <el-form :model="invForm" label-width="160px" class="premium-form">
        <el-form-item label="Склад" required>
          <el-select v-model="invForm.warehouse_id" placeholder="Выберите склад" style="width:100%">
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Товар" required>
          <el-select v-model="invForm.product_id" filterable placeholder="Выберите товар" style="width:100%">
            <el-option v-for="p in allProducts" :key="p.id" :label="`${p.article} ${p.name}`" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Факт. количество" required>
          <el-input-number v-model="invForm.fact_quantity" :min="0" :precision="2" style="width:100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="invVisible = false">Отмена</el-button>
        <el-button type="primary" @click="doInventory">Применить</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { stockApi, referencesApi, productsApi } from '../api'
import ChartCanvas from '../components/ChartCanvas.vue'

const stock = ref([])
const allStock = ref([])
const total = ref(0)
const page = ref(1)
const perPage = ref(15)
const loading = ref(false)
const warehouses = ref([])
const warehouseId = ref(null)
const allProducts = ref([])
const chartMode = ref('value')

const moveVisible = ref(false)
const moveForm = reactive({ product_id: null, from_warehouse_id: null, to_warehouse_id: null, quantity: 1 })

const invVisible = ref(false)
const invForm = reactive({ warehouse_id: null, product_id: null, fact_quantity: 0 })

const COLORS = ['#6D28D9', '#059669', '#D97706', '#4F46E5', '#E11D48', '#0891B2', '#DB2777', '#0D9488']

const load = async () => {
  loading.value = true
  try {
    const res = await stockApi.list({ page: page.value, per_page: perPage.value, warehouse_id: warehouseId.value })
    stock.value = res.data.data.map(s => ({ ...s, available: s.quantity - s.reserved }))
    total.value = res.data.total
  } catch (e) {
    ElMessage.error(e.response?.data?.message || 'Ошибка загрузки')
  } finally {
    loading.value = false
  }
}

const loadAllStock = async () => {
  try {
    const res = await stockApi.list({ per_page: 1000, warehouse_id: warehouseId.value })
    allStock.value = res.data.data.map(s => ({ ...s, available: s.quantity - s.reserved }))
  } catch (e) {
    console.error(e)
  }
}

const productName = (row) => {
  if (row.product?.name) return row.product.name
  const p = allProducts.value.find(x => x.id === row.product_id)
  return p?.name || '—'
}

const productArticle = (row) => {
  if (row.product?.article) return row.product.article
  const p = allProducts.value.find(x => x.id === row.product_id)
  return p?.article || ''
}

const warehouseName = (row) => {
  if (row.warehouse?.name) return row.warehouse.name
  const w = warehouses.value.find(x => x.id === row.warehouse_id)
  return w?.name || '—'
}

const statCards = computed(() => {
  const src = allStock.value.length ? allStock.value : stock.value
  const totalQty = src.reduce((a, s) => a + s.quantity, 0)
  const totalReserved = src.reduce((a, s) => a + s.reserved, 0)
  const totalAvailable = totalQty - totalReserved
  const totalValue = src.reduce((a, s) => a + s.quantity * s.avg_cost, 0)
  return [
    { label: 'Общий остаток', value: totalQty.toLocaleString('ru-RU'), icon: 'Box', gradient: 'linear-gradient(135deg, #6D28D9, #5B21B6)' },
    { label: 'В резерве', value: totalReserved.toLocaleString('ru-RU'), icon: 'Lock', gradient: 'linear-gradient(135deg, #4F46E5, #4338CA)' },
    { label: 'Доступно', value: totalAvailable.toLocaleString('ru-RU'), icon: 'Unlock', gradient: 'linear-gradient(135deg, #059669, #047857)' },
    { label: 'Стоимость', value: formatMoneyShort(totalValue), icon: 'Wallet', gradient: 'linear-gradient(135deg, #D97706, #B45309)' },
  ]
})

const doughnutData = computed(() => {
  const src = allStock.value.length ? allStock.value : stock.value
  const byProduct = {}
  for (const s of src) {
    const key = productName(s)
    if (!byProduct[key]) byProduct[key] = 0
    byProduct[key] += chartMode.value === 'value' ? s.quantity * s.avg_cost : s.quantity
  }
  const labels = Object.keys(byProduct)
  const data = Object.values(byProduct)
  return {
    labels,
    datasets: [{
      data,
      backgroundColor: COLORS.slice(0, labels.length),
      borderWidth: 0,
      hoverOffset: 10,
      borderRadius: 6,
    }],
  }
})

const doughnutOpts = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  cutout: '68%',
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        usePointStyle: true,
        padding: 18,
        font: { size: 12, family: 'Inter', weight: '600' },
        color: '#334155',
      },
    },
    tooltip: {
      backgroundColor: '#0F172A',
      titleFont: { size: 13, family: 'Inter', weight: '700' },
      bodyFont: { size: 12, family: 'Inter', weight: '600' },
      padding: 14,
      cornerRadius: 14,
      callbacks: {
        label: (ctx) => {
          const val = ctx.parsed
          return chartMode.value === 'value'
            ? ` ${ctx.label}: ${formatMoney(val)}`
            : ` ${ctx.label}: ${val.toLocaleString('ru-RU')} шт.`
        },
      },
    },
  },
}))

const openMoveDialog = () => { moveVisible.value = true }
const openInventoryDialog = () => { invVisible.value = true }

const doMove = async () => {
  try {
    await stockApi.move(moveForm)
    ElMessage.success('Перемещение выполнено')
    moveVisible.value = false
    load()
    loadAllStock()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || 'Ошибка перемещения')
  }
}

const doInventory = async () => {
  try {
    await stockApi.inventory([{
      product_id: invForm.product_id,
      warehouse_id: invForm.warehouse_id,
      fact_quantity: invForm.fact_quantity,
    }])
    ElMessage.success('Инвентаризация применена')
    invVisible.value = false
    load()
    loadAllStock()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || 'Ошибка инвентаризации')
  }
}

onMounted(async () => {
  load()
  loadAllStock()
  const [w, p] = await Promise.all([
    referencesApi.warehouses(),
    productsApi.list({ per_page: 1000 }),
  ])
  warehouses.value = w.data
  allProducts.value = p.data.data
})

function formatMoney(v) {
  if (v === undefined || v === null) return '—'
  return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 0 }).format(v)
}

function formatMoneyShort(v) {
  if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(1)} млн ₽`
  if (v >= 1_000) return `${(v / 1_000).toFixed(0)} тыс. ₽`
  return formatMoney(v)
}
</script>

<style scoped>
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--surface-solid);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: var(--transition);
  cursor: default;
}

.stat-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.stat-icon {
  width: 46px;
  height: 46px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-value {
  font-size: 22px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.4px;
}

.stat-label {
  font-size: 11px;
  color: var(--text-muted);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  margin-top: 2px;
}

.content-grid {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 20px;
}

.chart-section { min-width: 0; }
.table-section { min-width: 0; }

.chart-card {
  height: 100%;
  min-height: 460px;
}

.chart-container {
  height: 340px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
}

.chart-empty-text {
  margin-top: 14px;
  font-size: 14px;
  font-weight: 700;
  color: var(--text-secondary);
}

.chart-empty-sub {
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 500;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.card-title-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-title {
  font-weight: 800;
  font-size: 15px;
  color: var(--text-primary);
  letter-spacing: -0.2px;
}

.product-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.product-name {
  font-weight: 700;
  font-size: 13px;
  color: var(--text-primary);
}

.product-article {
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: 0.3px;
  font-weight: 500;
}

.qty-value {
  font-weight: 700;
  color: var(--text-primary);
}

.reserved-value {
  color: var(--info);
  font-weight: 600;
}

.available-value {
  font-weight: 800;
  color: var(--success);
}

.available-value.zero {
  color: var(--danger);
}

.money-value {
  font-variant-numeric: tabular-nums;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 600;
}

.total-value {
  color: var(--text-primary);
  font-weight: 700;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.premium-form :deep(.el-form-item__label) {
  font-weight: 600;
  color: var(--text-secondary) !important;
}

@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  .chart-container {
    height: 280px;
  }
}

@media (max-width: 768px) {
  .page-header-actions {
    width: 100%;
  }
}
</style>