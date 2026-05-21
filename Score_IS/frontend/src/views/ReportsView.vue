<template>
  <div class="page-view">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">Отчеты</h1>
        <p class="page-subtitle">Аналитика по продажам, остаткам и закупкам</p>
      </div>
    </div>
    <el-tabs type="border-card">
      <el-tab-pane label="Продажи">
        <div class="toolbar">
          <el-date-picker v-model="salesRange" type="daterange" range-separator="—" start-placeholder="От" end-placeholder="До" format="DD.MM.YYYY" value-format="YYYY-MM-DD" />
          <el-button type="primary" @click="loadSales">Загрузить</el-button>
          <el-button @click="exportSalesXlsx">Экспорт .xlsx</el-button>
        </div>
        <el-table :data="salesData" size="small" v-loading="salesLoading">
          <el-table-column prop="number" label="Номер" />
          <el-table-column prop="date" label="Дата" />
          <el-table-column prop="client" label="Клиент" />
          <el-table-column prop="product" label="Товар" />
          <el-table-column prop="quantity" label="Кол-во" />
          <el-table-column prop="amount" label="Сумма" />
          <el-table-column prop="margin" label="Маржа" />
          <el-table-column prop="margin_percent" label="Марж.%" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="Остатки">
        <div class="toolbar">
          <el-button type="primary" @click="loadStock">Обновить</el-button>
          <el-button @click="exportStockXlsx">Экспорт .xlsx</el-button>
        </div>
        <el-table :data="stockData" size="small" v-loading="stockLoading">
          <el-table-column prop="product" label="Товар" />
          <el-table-column prop="article" label="Артикул" />
          <el-table-column prop="warehouse" label="Склад" />
          <el-table-column prop="quantity" label="Факт" />
          <el-table-column prop="available" label="Доступно" />
          <el-table-column prop="avg_cost" label="Ср. себест." />
          <el-table-column prop="value" label="Стоимость" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="Топ товаров">
        <div class="toolbar">
          <el-date-picker v-model="topRange" type="daterange" range-separator="—" start-placeholder="От" end-placeholder="До" format="DD.MM.YYYY" value-format="YYYY-MM-DD" />
          <el-button type="primary" @click="loadTop">Загрузить</el-button>
        </div>
        <el-table :data="topData" size="small" v-loading="topLoading">
          <el-table-column prop="name" label="Товар" />
          <el-table-column prop="article" label="Артикул" />
          <el-table-column prop="quantity" label="Кол-во" />
          <el-table-column prop="revenue" label="Выручка" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="Закупки">
        <div class="toolbar">
          <el-date-picker v-model="purchaseRange" type="daterange" range-separator="—" start-placeholder="От" end-placeholder="До" format="DD.MM.YYYY" value-format="YYYY-MM-DD" />
          <el-button type="primary" @click="loadPurchases">Загрузить</el-button>
          <el-button @click="exportPurchasesXlsx">Экспорт .xlsx</el-button>
        </div>
        <el-table :data="purchasesData" size="small" v-loading="purchaseLoading">
          <el-table-column prop="number" label="Номер" />
          <el-table-column prop="date" label="Дата" />
          <el-table-column prop="supplier" label="Поставщик" />
          <el-table-column prop="product" label="Товар" />
          <el-table-column prop="quantity" label="Кол-во" />
          <el-table-column prop="amount" label="Сумма" />
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { reportsApi } from '../api'
import { saveAs } from 'file-saver'

const salesRange = ref([])
const stockData = ref([])
const salesData = ref([])
const topData = ref([])
const purchasesData = ref([])
const salesLoading = ref(false)
const stockLoading = ref(false)
const topLoading = ref(false)
const purchaseLoading = ref(false)
const topRange = ref([])
const purchaseRange = ref([])

const loadSales = async () => {
  salesLoading.value = true
  const res = await reportsApi.sales({ date_from: salesRange.value?.[0], date_to: salesRange.value?.[1] })
  salesData.value = res.data.data
  salesLoading.value = false
}

const loadStock = async () => {
  stockLoading.value = true
  const res = await reportsApi.stock()
  stockData.value = res.data.data
  stockLoading.value = false
}

const loadTop = async () => {
  topLoading.value = true
  const res = await reportsApi.topProducts({ date_from: topRange.value?.[0], date_to: topRange.value?.[1] })
  topData.value = res.data.data
  topLoading.value = false
}

const loadPurchases = async () => {
  purchaseLoading.value = true
  const res = await reportsApi.purchases({ date_from: purchaseRange.value?.[0], date_to: purchaseRange.value?.[1] })
  purchasesData.value = res.data.data
  purchaseLoading.value = false
}

const exportSalesXlsx = async () => {
  const res = await reportsApi.sales({ format: 'xlsx', date_from: salesRange.value?.[0], date_to: salesRange.value?.[1] })
  saveAs(new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }), 'sales_report.xlsx')
}
const exportStockXlsx = async () => {
  const res = await reportsApi.stock({ format: 'xlsx' })
  saveAs(new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }), 'stock_report.xlsx')
}
const exportPurchasesXlsx = async () => {
  const res = await reportsApi.purchases({ format: 'xlsx', date_from: purchaseRange.value?.[0], date_to: purchaseRange.value?.[1] })
  saveAs(new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }), 'purchases_report.xlsx')
}

loadStock()
</script>

<style scoped>
.toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 14px;
  align-items: center;
  flex-wrap: wrap;
}
</style>
