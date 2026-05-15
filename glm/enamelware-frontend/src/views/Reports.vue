<template>
  <div>
    <div class="toolbar">
      <div class="toolbar-left">
        <el-select v-model="reportType" placeholder="Тип отчёта" style="width:200px">
          <el-option label="Продажи (марж.)" value="sales" />
          <el-option label="Остатки на дату" value="stock" />
          <el-option label="Топ товаров" value="top-products" />
          <el-option label="Закупки" value="purchases" />
        </el-select>
        <el-date-picker v-model="dateRange" type="daterange" range-separator="—" start-placeholder="С" end-placeholder="По" format="DD.MM.YYYY" value-format="YYYY-MM-DD" />
        <el-select v-model="sortBy" placeholder="Сортировка" style="width:150px" v-if="reportType === 'top-products'">
          <el-option label="По выручке" value="revenue" />
          <el-option label="По количеству" value="quantity" />
        </el-select>
      </div>
      <el-button type="success" @click="exportReport('xlsx')" style="cursor:pointer">Экспорт XLSX</el-button>
    </div>
    <div class="data-table">
      <el-table :data="reportData" stripe v-loading="loading">
        <el-table-column v-for="col in columns" :key="col.key" :prop="col.key" :label="col.label" :width="col.width" :min-width="col.minWidth">
          <template #default="{ row }" v-if="col.format === 'currency'">{{ formatCurrency(row[col.key]) }}</template>
        </el-table-column>
      </el-table>
      <div v-if="totals" style="margin-top:16px;text-align:right;font-size:15px;font-weight:700;letter-spacing:-0.01em">
        <div v-for="(val, key) in totals" :key="key">{{ key }}: {{ typeof val === 'number' ? formatCurrency(val) : val }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import api from '../api'
import { formatCurrency } from '../utils/format'

const reportType = ref('sales')
const dateRange = ref(null)
const sortBy = ref('revenue')
const loading = ref(false)
const reportData = ref([])
const columns = ref([])
const totals = ref(null)

const reportConfigs = {
  sales: {
    columns: [
      { key: 'sale_number', label: '№ Продажи', width: 120 },
      { key: 'date', label: 'Дата', width: 140 },
      { key: 'product', label: 'Товар', minWidth: 200 },
      { key: 'quantity', label: 'Кол-во', width: 100 },
      { key: 'amount', label: 'Сумма', width: 130, format: 'currency' },
      { key: 'cost', label: 'Себестоимость', width: 150, format: 'currency' },
      { key: 'profit', label: 'Прибыль', width: 130, format: 'currency' },
      { key: 'margin', label: 'Маржа %', width: 100 },
    ],
  },
  stock: {
    columns: [
      { key: 'product', label: 'Товар', minWidth: 200 },
      { key: 'article', label: 'Артикул', width: 120 },
      { key: 'category', label: 'Категория', width: 150 },
      { key: 'quantity', label: 'Кол-во', width: 100 },
      { key: 'reserved', label: 'Резерв', width: 100 },
      { key: 'available', label: 'Доступно', width: 100 },
      { key: 'avg_cost', label: 'Ср.стоимость', width: 140, format: 'currency' },
      { key: 'total_value', label: 'Сумма', width: 130, format: 'currency' },
    ],
  },
  'top-products': {
    columns: [
      { key: 'product', label: 'Товар', minWidth: 200 },
      { key: 'article', label: 'Артикул', width: 120 },
      { key: 'revenue', label: 'Выручка', width: 130, format: 'currency' },
      { key: 'quantity', label: 'Кол-во', width: 100 },
    ],
  },
  purchases: {
    columns: [
      { key: 'number', label: '№ Закупки', width: 120 },
      { key: 'date', label: 'Дата', width: 140 },
      { key: 'supplier', label: 'Поставщик', minWidth: 200 },
      { key: 'total_amount', label: 'Сумма', width: 130, format: 'currency' },
      { key: 'status', label: 'Статус', width: 100 },
    ],
  },
}

async function loadReport() {
  loading.value = true
  try {
    columns.value = reportConfigs[reportType.value].columns
    const params = { format: 'json' }
    if (dateRange.value) { params.date_from = dateRange.value[0]; params.date_to = dateRange.value[1] }
    if (reportType.value === 'top-products') params.by = sortBy.value
    const res = await api.get(`/reports/${reportType.value}`, { params })
    reportData.value = res.data.data || res.data
    totals.value = res.data.totals || (res.data.total_amount ? { 'Итого': res.data.total_amount } : res.data.total_value ? { 'Итого стоимость': res.data.total_value } : null)
  } catch { reportData.value = []; totals.value = null }
  finally { loading.value = false }
}

function exportReport(format) {
  const params = { format: 'xlsx' }
  if (dateRange.value) { params.date_from = dateRange.value[0]; params.date_to = dateRange.value[1] }
  if (reportType.value === 'top-products') params.by = sortBy.value
  window.open(`/api/v1/reports/${reportType.value}?${new URLSearchParams(params).toString()}`, '_blank')
}

watch([reportType, sortBy], loadReport)
onMounted(loadReport)
</script>