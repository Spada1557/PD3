<template>
  <div>
    <div class="flex-between mb-20">
      <div class="flex-row" style="gap:12px">
        <el-date-picker v-model="dateRange" type="daterange" range-separator="—" start-placeholder="С" end-placeholder="По" value-format="YYYY-MM-DD" @change="load" size="default" style="width:280px" />
        <el-button type="default" @click="load" style="gap:6px">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
          Обновить
        </el-button>
      </div>
      <span class="card-badge" style="display:flex;align-items:center;gap:6px">
        <span style="width:7px;height:7px;border-radius:50%;background:var(--success);display:inline-block;animation:pulse-dot 2s ease-in-out infinite"></span>
        Данные в реальном времени
      </span>
    </div>

    <div class="stat-grid">
      <div class="stat-card">
        <div class="stat-icon blue">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
        </div>
        <span class="stat-label">Выручка</span>
        <span class="stat-value">{{ formatCurrency(data.revenue) }}</span>
        <span class="stat-change">
          <span class="change-icon" :class="data.revenue_change >= 0 ? 'change-up' : 'change-down'">
            <svg v-if="data.revenue_change >= 0" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"/></svg>
            <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
          </span>
          {{ formatPercent(data.revenue_change) }} к прошлому периоду
        </span>
      </div>
      <div class="stat-card">
        <div class="stat-icon amber">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5 21"/></svg>
        </div>
        <span class="stat-label">Себестоимость</span>
        <span class="stat-value">{{ formatCurrency(data.cost) }}</span>
        <span class="stat-change">
          <span class="change-icon" :class="data.cost_change <= 0 ? 'change-up' : 'change-down'">
            <svg v-if="data.cost_change <= 0" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"/></svg>
            <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
          </span>
          {{ formatPercent(data.cost_change) }} к прошлому периоду
        </span>
      </div>
      <div class="stat-card">
        <div class="stat-icon" :style="{ background: data.profit >= 0 ? '#ECFDF5' : '#FEF2F2', color: data.profit >= 0 ? '#10B981' : '#EF4444' }">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20V10"/><path d="M18 20V4"/><path d="M6 20v-4"/></svg>
        </div>
        <span class="stat-label">Прибыль</span>
        <span class="stat-value" :style="{ color: data.profit >= 0 ? '#10B981' : '#EF4444' }">{{ formatCurrency(data.profit) }}</span>
        <span class="stat-change">
          <span class="change-icon" :class="data.profit_change >= 0 ? 'change-up' : 'change-down'">
            <svg v-if="data.profit_change >= 0" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"/></svg>
            <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
          </span>
          {{ formatPercent(data.profit_change) }} к прошлому периоду
        </span>
      </div>
      <div class="stat-card">
        <div class="stat-icon teal">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
        </div>
        <span class="stat-label">Остатки на складе</span>
        <span class="stat-value-sm">{{ data.stock_count }} поз.</span>
        <span class="stat-change" style="color:#14B8A6;font-weight:600">{{ formatCurrency(data.stock_value) }}</span>
      </div>
      <div class="stat-card">
        <div class="stat-icon indigo">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        </div>
        <span class="stat-label">Заказы</span>
        <span class="stat-value-sm">{{ data.orders_count }}</span>
        <span class="stat-change">
          <span class="change-icon" :class="data.orders_change >= 0 ? 'change-up' : 'change-down'">
            <svg v-if="data.orders_change >= 0" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"/></svg>
            <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
          </span>
          {{ formatPercent(data.orders_change) }} к прошлому периоду
        </span>
      </div>
    </div>

    <div class="charts-row">
      <div class="card">
        <div class="card-header">
          <h4>Динамика продаж</h4>
          <span class="card-badge">30 дней</span>
        </div>
        <div class="chart-container"><canvas ref="salesChartRef"></canvas></div>
      </div>
      <div class="card">
        <div class="card-header">
          <h4>Структура по категориям</h4>
          <span class="card-badge">Текущий период</span>
        </div>
        <div class="chart-container"><canvas ref="pieChartRef"></canvas></div>
      </div>
    </div>

    <div class="grid-3">
      <div class="card">
        <div class="card-header"><h4>Топ товаров</h4><span class="card-badge" style="background:var(--info-soft);color:var(--info)">По продажам</span></div>
        <el-table :data="data.top_products" size="small">
          <el-table-column prop="name" label="Товар" min-width="140" show-overflow-tooltip />
          <el-table-column prop="quantity" label="Кол-во" width="65" align="right" />
          <el-table-column label="Выручка" width="100" align="right">
            <template #default="{row}">{{ formatCurrency(row.revenue) }}</template>
          </el-table-column>
        </el-table>
      </div>
      <div class="card">
        <div class="card-header"><h4>Последние документы</h4></div>
        <el-table :data="data.top_documents" size="small">
          <el-table-column prop="number" label="№" width="120" />
          <el-table-column prop="client" label="Клиент" min-width="120" show-overflow-tooltip />
          <el-table-column label="Сумма" width="100" align="right">
            <template #default="{row}">{{ formatCurrency(row.amount) }}</template>
          </el-table-column>
        </el-table>
      </div>
      <div class="card" style="border-color:#FECACA">
        <div class="card-header">
          <h4 style="color:var(--danger)">Низкие остатки</h4>
          <span class="card-badge" style="background:var(--danger-soft);color:var(--danger)">{{ data.low_stock.length }} поз.</span>
        </div>
        <el-table :data="data.low_stock" size="small">
          <el-table-column prop="name" label="Товар" min-width="120" show-overflow-tooltip />
          <el-table-column prop="article" label="Артикул" width="95" />
          <el-table-column label="Остаток" width="80" align="right">
            <template #default="{row}"><span :style="{ color: row.quantity <= row.min_stock / 2 ? '#EF4444' : '#F59E0B', fontWeight: 700 }">{{ row.quantity }} / {{ row.min_stock }}</span></template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import api from '../api/client'
import { formatCurrency, formatPercent } from '../utils/format'

Chart.register(...registerables)

const data = reactive({
  revenue: 0, revenue_change: 0,
  cost: 0, cost_change: 0,
  profit: 0, profit_change: 0,
  stock_count: 0, stock_value: 0,
  orders_count: 0, orders_change: 0,
  sales_chart: [], category_distribution: [],
  top_products: [], top_documents: [], low_stock: []
})

const dateRange = ref([])
const salesChartRef = ref(null)
const pieChartRef = ref(null)
let salesChart = null, pieChart = null

async function load() {
  const params = {}
  if (dateRange.value?.[0]) params.date_from = dateRange.value[0]
  if (dateRange.value?.[1]) params.date_to = dateRange.value[1]
  try {
    const { data: d } = await api.get('/dashboard', { params })
    Object.assign(data, d)
    await nextTick()
    renderCharts()
  } catch (e) { /* ignore */ }
}

function renderCharts() {
  const colors = {
    blue: '#7C3AED',
    green: '#10B981',
    amber: '#F59E0B',
    red: '#EF4444',
    indigo: '#6366F1',
    teal: '#14B8A6',
    pink: '#EC4899',
    slate: '#64748B',
  }
  const donutColors = ['#7C3AED', '#10B981', '#F59E0B', '#EF4444', '#6366F1', '#14B8A6', '#EC4899']

  if (salesChart) salesChart.destroy()
  if (salesChartRef.value) {
    const ctx = salesChartRef.value.getContext('2d')
    const gradient = ctx.createLinearGradient(0, 0, 0, 300)
    gradient.addColorStop(0, 'rgba(124, 58, 237, 0.15)')
    gradient.addColorStop(0.5, 'rgba(124, 58, 237, 0.05)')
    gradient.addColorStop(1, 'rgba(124, 58, 237, 0)')
    salesChart = new Chart(salesChartRef.value, {
      type: 'line',
      data: {
        labels: data.sales_chart.map(d => d.date),
        datasets: [{
          label: 'Выручка',
          data: data.sales_chart.map(d => d.amount),
          borderColor: colors.blue,
          backgroundColor: gradient,
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          pointBackgroundColor: '#fff',
          pointBorderColor: colors.blue,
          pointBorderWidth: 2,
          pointHoverRadius: 7,
          pointHoverBackgroundColor: colors.blue,
          pointHoverBorderColor: '#fff',
          pointHoverBorderWidth: 3,
          borderWidth: 2.5,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#0F172A',
            titleFont: { family: "'DM Sans', sans-serif", weight: '600', size: 13 },
            bodyFont: { family: "'DM Sans', sans-serif", size: 12 },
            padding: 12,
            cornerRadius: 8,
          },
        },
        scales: {
          y: {
            grid: { color: '#F1F5F9' },
            ticks: { callback: v => v >= 1000 ? v / 1000 + 'k' : v, font: { family: "'DM Sans', sans-serif", size: 11 } },
            border: { display: false },
          },
          x: {
            grid: { display: false },
            ticks: { font: { family: "'DM Sans', sans-serif", size: 11 } },
          },
        },
      },
    })
  }

  if (pieChart) pieChart.destroy()
  if (pieChartRef.value && data.category_distribution.length) {
    pieChart = new Chart(pieChartRef.value, {
      type: 'doughnut',
      data: {
        labels: data.category_distribution.map(d => d.name),
        datasets: [{
          data: data.category_distribution.map(d => d.amount),
          backgroundColor: donutColors,
          borderColor: '#fff',
          borderWidth: 4,
          hoverBorderWidth: 5,
          hoverBorderColor: '#fff',
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '62%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              padding: 22,
              usePointStyle: true,
              pointStyleWidth: 10,
              pointStyleHeight: 10,
              font: { family: "'DM Sans', sans-serif", size: 12, weight: '500' },
              generateLabels: (chart) => {
                const datasets = chart.data.datasets[0]
                const labels = chart.data.labels
                return labels.map((label, i) => ({
                  text: label,
                  fillStyle: datasets.backgroundColor[i],
                  strokeStyle: datasets.backgroundColor[i],
                  lineWidth: 0,
                  hidden: false,
                  index: i,
                  pointStyle: 'circle',
                  rotation: 0,
                }))
              },
            },
          },
          tooltip: {
            backgroundColor: '#0F172A',
            padding: 12,
            cornerRadius: 8,
          },
        },
      },
    })
  }
}

onMounted(load)
</script>

<style scoped>
.chart-container {
  position: relative;
  width: 100%;
  height: 330px;
  max-height: 390px;
}
canvas {
  width: 100% !important;
  height: 100% !important;
  max-height: 390px;
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
@media (max-width: 480px) {
  .chart-container { height: 260px; }
}
</style>