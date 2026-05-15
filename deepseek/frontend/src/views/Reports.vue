<template>
  <div>
    <div class="card">
      <div class="table-actions">
        <el-date-picker v-model="dateRange" type="daterange" range-separator="—" start-placeholder="С" end-placeholder="По" value-format="YYYY-MM-DD" style="width:280px" />
        <el-select v-model="reportType" placeholder="Тип отчёта" style="width:200px" @change="load">
          <el-option label="Продажи" value="sales" />
          <el-option label="Остатки" value="stock" />
          <el-option label="Топ товаров" value="top" />
          <el-option label="Закупки" value="purchases" />
        </el-select>
        <el-button type="primary" @click="load">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:5px"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
          Сформировать
        </el-button>
        <el-button v-if="reportType === 'sales'" type="default" @click="exportSales" style="margin-left:auto">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:5px"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          Экспорт XLSX
        </el-button>
        <el-button v-if="reportType === 'stock'" type="default" @click="exportStock" style="margin-left:auto">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:5px"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          Экспорт XLSX
        </el-button>
      </div>

      <div v-if="reportType === 'sales'">
        <el-table :data="reportData" size="default" style="width:100%">
          <el-table-column prop="number" label="№ документа" width="180">
            <template #default="{row}"><span class="amount" style="white-space:nowrap">{{ row.number }}</span></template>
          </el-table-column>
          <el-table-column label="Дата" width="130"><template #default="{row}">{{ formatDate(row.date) }}</template></el-table-column>
          <el-table-column prop="client" label="Клиент" min-width="250" show-overflow-tooltip />
          <el-table-column label="Выручка" width="160" align="right"><template #default="{row}"><span class="amount" style="white-space:nowrap">{{ formatCurrency(row.total_amount) }}</span></template></el-table-column>
          <el-table-column label="Себест." width="160" align="right"><template #default="{row}"><span style="color:var(--text-muted);font-weight:600;white-space:nowrap">{{ formatCurrency(row.total_cost) }}</span></template></el-table-column>
          <el-table-column label="Прибыль" width="160" align="right"><template #default="{row}"><span :class="row.total_profit >= 0 ? 'positive' : 'negative'" style="white-space:nowrap">{{ formatCurrency(row.total_profit) }}</span></template></el-table-column>
          <el-table-column label="Маржа" width="90" align="center"><template #default="{row}"><el-tag :type="row.margin >= 10 ? 'success' : row.margin >= 0 ? 'warning' : 'danger'" size="small" style="white-space:nowrap">{{ row.margin }}%</el-tag></template></el-table-column>
        </el-table>
      </div>
      <div v-else-if="reportType === 'stock'">
        <div class="stock-summary-banner">
          <div class="summary-item">
            <span class="summary-label">Общая стоимость остатков</span>
            <span class="summary-value">{{ formatCurrency(stockTotalValue) }}</span>
          </div>
        </div>
        <el-table :data="reportData" size="default" style="width:100%">
          <el-table-column prop="product_name" label="Товар" min-width="250" show-overflow-tooltip />
          <el-table-column prop="article" label="Артикул" width="110" />
          <el-table-column prop="category" label="Категория" width="130" />
          <el-table-column prop="warehouse" label="Склад" width="130" />
          <el-table-column prop="quantity" label="Кол-во" width="85" align="center" />
          <el-table-column prop="available" label="Доступно" width="90" align="center" />
          <el-table-column label="Ср.себест." width="160" align="right"><template #default="{row}"><span style="white-space:nowrap">{{ formatCurrency(row.avg_cost) }}</span></template></el-table-column>
          <el-table-column label="Стоимость" width="160" align="right"><template #default="{row}"><span class="amount" style="white-space:nowrap">{{ formatCurrency(row.value) }}</span></template></el-table-column>
        </el-table>
      </div>
      <div v-else-if="reportType === 'top'">
        <el-radio-group v-model="topOrder" @change="load" class="mb-20">
          <el-radio-button value="revenue">По выручке</el-radio-button>
          <el-radio-button value="quantity">По количеству</el-radio-button>
        </el-radio-group>
        <el-table :data="reportData" size="default" style="width:100%">
          <el-table-column type="index" label="#" width="50" />
          <el-table-column prop="product_name" label="Товар" min-width="250" show-overflow-tooltip />
          <el-table-column prop="article" label="Артикул" width="110" />
          <el-table-column prop="total_quantity" label="Продано" width="85" align="center" />
          <el-table-column label="Выручка" width="160" align="right"><template #default="{row}"><span class="amount" style="white-space:nowrap">{{ formatCurrency(row.total_revenue) }}</span></template></el-table-column>
          <el-table-column label="Прибыль" width="160" align="right"><template #default="{row}"><span class="amount" style="white-space:nowrap">{{ formatCurrency(row.total_profit) }}</span></template></el-table-column>
          <el-table-column label="Маржа" width="90" align="center"><template #default="{row}"><el-tag :type="row.margin >= 10 ? 'success' : row.margin >= 0 ? 'warning' : 'danger'" size="small" style="white-space:nowrap">{{ row.margin }}%</el-tag></template></el-table-column>
        </el-table>
      </div>
      <div v-else-if="reportType === 'purchases'">
        <el-table :data="reportData" size="default" style="width:100%">
          <el-table-column prop="number" label="№ документа" width="180">
            <template #default="{row}"><span class="amount" style="white-space:nowrap">{{ row.number }}</span></template>
          </el-table-column>
          <el-table-column label="Дата" width="130"><template #default="{row}">{{ formatDate(row.date) }}</template></el-table-column>
          <el-table-column prop="supplier" label="Поставщик" min-width="250" show-overflow-tooltip />
          <el-table-column label="Сумма" width="160" align="right"><template #default="{row}"><span class="amount" style="white-space:nowrap">{{ formatCurrency(row.total_amount) }}</span></template></el-table-column>
          <el-table-column prop="items_count" label="Позиций" width="85" align="center" />
        </el-table>
      </div>
      <div class="flex-row mt-20" style="justify-content:flex-end">
        <el-pagination v-if="reportType !== 'stock'" v-model:current-page="page" :page-size="perPage" :total="total" @current-change="load" layout="prev, pager, next, total" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api/client'
import { formatCurrency, formatDate } from '../utils/format'
import { ElMessage } from 'element-plus'

const dateRange = ref([])
const reportType = ref('sales')
const reportData = ref([])
const stockTotalValue = ref(0)
const page = ref(1), perPage = ref(10), total = ref(0)
const topOrder = ref('revenue')

async function load() {
  try {
    const params = { page: page.value, per_page: perPage.value }
    if (dateRange.value?.[0]) params.date_from = dateRange.value[0]
    if (dateRange.value?.[1]) params.date_to = dateRange.value[1]
    if (topOrder.value) params.order_by = topOrder.value

    if (reportType.value === 'sales') {
      const { data } = await api.get('/reports/sales', { params })
      reportData.value = data.data; total.value = data.total
    } else if (reportType.value === 'stock') {
      const { data } = await api.get('/reports/stock-snapshot', { params })
      reportData.value = data.data; stockTotalValue.value = data.total_value; total.value = data.data.length
    } else if (reportType.value === 'top') {
      const { data } = await api.get('/reports/top-products', { params })
      reportData.value = data.data; total.value = data.data.length
    } else if (reportType.value === 'purchases') {
      const { data } = await api.get('/reports/purchases', { params })
      reportData.value = data.data; total.value = data.total
    }
  } catch (e) { ElMessage.error('Ошибка загрузки отчёта') }
}

function exportSales() {
  const params = {}
  if (dateRange.value?.[0]) params.date_from = dateRange.value[0]
  if (dateRange.value?.[1]) params.date_to = dateRange.value[1]
  const qs = new URLSearchParams(params).toString()
  window.open(`/api/v1/reports/export/sales?${qs}`, '_blank')
}
function exportStock() {
  window.open('/api/v1/reports/export/stock', '_blank')
}

onMounted(load)
</script>

<style scoped>
.stock-summary-banner {
  display: flex;
  padding: 20px 24px;
  margin-bottom: 20px;
  background: linear-gradient(135deg, var(--success-soft), #FFF);
  border-radius: var(--radius-lg);
  border: 1px solid #A7F3D0;
}
.summary-item { display: flex; flex-direction: column; gap: 4px; }
.summary-label { font-size: 13px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.4px; }
.summary-value { font-size: 32px; font-weight: 800; color: var(--success); letter-spacing: -0.5px; }
</style>