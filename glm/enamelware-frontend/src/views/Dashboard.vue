<template>
  <div>
    <div class="toolbar">
      <div class="toolbar-left">
        <el-date-picker v-model="dateRange" type="daterange" range-separator="—" start-placeholder="Начало" end-placeholder="Конец" format="DD.MM.YYYY" value-format="YYYY-MM-DD" @change="loadData" style="width:340px" />
      </div>
    </div>

    <div class="card-grid">
      <div class="stat-card">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
          <div class="stat-icon revenue"><el-icon><TrendCharts /></el-icon></div>
          <div class="change" v-if="stats.revenue_change !== 0" :class="stats.revenue_change >= 0 ? 'positive' : 'negative'">
            {{ stats.revenue_change >= 0 ? '+' : '' }}{{ stats.revenue_change }}%
          </div>
        </div>
        <div class="label">Выручка</div>
        <div class="value">{{ formatCurrency(stats.revenue) }}</div>
      </div>
      <div class="stat-card">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
          <div class="stat-icon cost"><el-icon><Coin /></el-icon></div>
          <div class="change" :class="stats.cost_change >= 0 ? 'negative' : 'positive'">
            <span v-if="stats.cost_change !== 0">{{ stats.cost_change >= 0 ? '+' : '' }}{{ stats.cost_change }}%</span>
            <span v-else style="color:var(--text-muted)">—</span>
          </div>
        </div>
        <div class="label">Себестоимость</div>
        <div class="value">{{ formatCurrency(stats.cost) }}</div>
      </div>
      <div class="stat-card">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
          <div class="stat-icon profit"><el-icon><Histogram /></el-icon></div>
          <div class="change" :class="stats.profit_change >= 0 ? 'positive' : 'negative'">
            <span v-if="stats.profit_change !== 0">{{ stats.profit_change >= 0 ? '+' : '' }}{{ stats.profit_change }}%</span>
            <span v-else style="color:var(--text-muted)">—</span>
          </div>
        </div>
        <div class="label">Прибыль</div>
        <div class="value">{{ formatCurrency(stats.profit) }}</div>
      </div>
      <div class="stat-card">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
          <div class="stat-icon stock"><el-icon><Box /></el-icon></div>
        </div>
        <div class="label">Остатки (стоимость)</div>
        <div class="value">{{ formatCurrency(stats.stock_value) }}</div>
      </div>
      <div class="stat-card">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
          <div class="stat-icon orders"><el-icon><Document /></el-icon></div>
        </div>
        <div class="label">Продаж (провед.)</div>
        <div class="value">{{ stats.orders_count }}</div>
      </div>
    </div>

    <div class="charts-row">
      <div class="chart-card">
        <h3>Динамика продаж</h3>
        <div style="height:310px;position:relative">
          <Line ref="salesChartRef" :data="salesChartData" :options="lineOptions" />
        </div>
      </div>
      <div class="chart-card">
        <h3>Структура выручки по категориям</h3>
        <div style="height:310px;position:relative">
          <Doughnut ref="categoryChartRef" :data="categoryChartData" :options="doughnutOptions" />
        </div>
      </div>
    </div>

    <div class="charts-row-equal">
      <div class="chart-card">
        <h3>Топ-5 товаров по выручке</h3>
        <ul class="top-list" v-if="topProducts.length">
          <li v-for="(p, idx) in topProducts" :key="p.id">
            <div style="display:flex;align-items:center">
              <span class="rank">{{ idx + 1 }}</span>
              <span class="item-name">{{ p.name }}</span>
            </div>
            <span class="item-value">{{ formatCurrency(p.value) }}</span>
          </li>
        </ul>
        <div v-else class="empty-state"><p>Нет данных за выбранный период</p></div>
      </div>
      <div class="chart-card">
        <h3>Низкие остатки</h3>
        <div v-if="lowStock.length">
          <div v-for="p in lowStock" :key="p.id" class="low-stock-item">
            <div>
              <div style="font-weight:600;color:var(--text-primary);font-size:13px">{{ p.name }}</div>
              <div style="font-size:11px;color:var(--text-muted);letter-spacing:0.01em">{{ p.article }}</div>
            </div>
            <el-tag :type="p.quantity === 0 ? 'danger' : 'warning'" size="small" effect="dark">
              {{ p.quantity }} / {{ p.min_stock }}
            </el-tag>
          </div>
        </div>
        <div v-else class="empty-state"><p>Все остатки в норме</p></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'
import { formatCurrency } from '../utils/format'
import { Line, Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement,
  ArcElement, Title, Tooltip, Legend, Filler
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, ArcElement, Title, Tooltip, Legend, Filler)

const dateRange = ref(null)
const stats = ref({ revenue: 0, cost: 0, profit: 0, stock_value: 0, orders_count: 0, revenue_change: 0, cost_change: 0, profit_change: 0, stock_change: 0 })
const salesChart = ref({ labels: [], revenue: [], cost: [], profit: [] })
const categoryChart = ref({ labels: [], values: [] })
const topProducts = ref([])
const lowStock = ref([])
const salesChartRef = ref(null)
const categoryChartRef = ref(null)

const salesChartData = computed(() => ({
  labels: salesChart.value.labels.length ? salesChart.value.labels : ['Нет данных'],
  datasets: [
    {
      label: 'Выручка',
      data: salesChart.value.revenue.length ? salesChart.value.revenue : [0],
      borderColor: '#818CF8',
      backgroundColor: (ctx) => {
        const gradient = ctx.chart.ctx.createLinearGradient(0, 0, 0, ctx.chart.height)
        gradient.addColorStop(0, 'rgba(129, 140, 248, 0.12)')
        gradient.addColorStop(1, 'rgba(129, 140, 248, 0)')
        return gradient
      },
      fill: true,
      tension: 0.4,
      borderWidth: 2.5,
      pointRadius: 0,
      pointHoverRadius: 5,
      pointBackgroundColor: '#818CF8',
      pointBorderColor: '#818CF8',
      pointHoverBackgroundColor: '#818CF8',
      pointHoverBorderColor: '#fff',
      pointHoverBorderWidth: 2,
    },
    {
      label: 'Себестоимость',
      data: salesChart.value.cost.length ? salesChart.value.cost : [0],
      borderColor: '#F59E0B',
      backgroundColor: 'rgba(245, 158, 11, 0.04)',
      fill: true,
      tension: 0.4,
      borderWidth: 2,
      pointRadius: 0,
      pointHoverRadius: 5,
      pointBackgroundColor: '#F59E0B',
      pointBorderColor: '#F59E0B',
    },
    {
      label: 'Прибыль',
      data: salesChart.value.profit.length ? salesChart.value.profit : [0],
      borderColor: '#10B981',
      backgroundColor: 'rgba(16, 185, 129, 0.04)',
      fill: true,
      tension: 0.4,
      borderWidth: 2,
      pointRadius: 0,
      pointHoverRadius: 5,
      pointBackgroundColor: '#10B981',
      pointBorderColor: '#10B981',
    },
  ]
}))

const categoryChartData = computed(() => {
  const labels = categoryChart.value.labels.length ? categoryChart.value.labels : ['Нет данных']
  const values = categoryChart.value.values.length ? categoryChart.value.values : [1]
  return {
    labels,
    datasets: [{
      data: values,
      backgroundColor: ['#818CF8', '#10B981', '#F59E0B', '#EF4444', '#3B82F6', '#A78BFA', '#EC4899', '#06B6D4', '#F97316'],
      borderWidth: 0,
      hoverOffset: 8,
    }]
  }
})

const lineOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: { position: 'top', labels: { usePointStyle: true, pointStyle: 'circle', padding: 20, font: { family: "'DM Sans'", size: 11, weight: '500' }, color: '#94A3B8' } },
    tooltip: {
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      titleFont: { family: "'DM Sans'", size: 12, weight: '600' },
      bodyFont: { family: "'DM Sans'", size: 11 },
      padding: 12,
      cornerRadius: 10,
      borderColor: 'rgba(148, 163, 184, 0.12)',
      borderWidth: 1,
      displayColors: true,
      boxPadding: 4,
      callbacks: { label: (ctx) => `${ctx.dataset.label}: ${new Intl.NumberFormat('ru-RU').format(ctx.parsed.y)} ₽` }
    }
  },
  scales: {
    x: { grid: { color: 'rgba(148, 163, 184, 0.04)', drawBorder: false }, ticks: { font: { family: "'DM Sans'", size: 11 }, color: '#64748B' }, border: { display: false } },
    y: { grid: { color: 'rgba(148, 163, 184, 0.04)', drawBorder: false }, ticks: { font: { family: "'DM Sans'", size: 11 }, color: '#64748B', callback: (v) => new Intl.NumberFormat('ru-RU', { notation: 'compact' }).format(v) }, border: { display: false } }
  }
}

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '66%',
  plugins: {
    legend: { position: 'bottom', labels: { usePointStyle: true, pointStyle: 'circle', padding: 16, font: { family: "'DM Sans'", size: 11 }, color: '#94A3B8' } },
    tooltip: {
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: 'rgba(148, 163, 184, 0.12)',
      borderWidth: 1,
      padding: 12,
      cornerRadius: 10,
      titleFont: { family: "'DM Sans'", size: 12, weight: '600' },
      bodyFont: { family: "'DM Sans'", size: 11 },
      callbacks: { label: (ctx) => `${ctx.label}: ${new Intl.NumberFormat('ru-RU').format(ctx.parsed)} ₽` }
    }
  }
}

async function loadData() {
  const params = {}
  if (dateRange.value) {
    params.date_from = dateRange.value[0]
    params.date_to = dateRange.value[1]
  }
  try {
    const [statsRes, salesRes, catRes, topRes, lowRes] = await Promise.all([
      api.get('/dashboard/stats', { params }),
      api.get('/dashboard/sales-chart', { params }),
      api.get('/dashboard/category-chart', { params }),
      api.get('/dashboard/top-products', { params }),
      api.get('/dashboard/low-stock'),
    ])
    stats.value = statsRes.data
    salesChart.value = salesRes.data
    categoryChart.value = catRes.data
    topProducts.value = topRes.data
    lowStock.value = lowRes.data
  } catch (e) {
    console.error('Dashboard load error:', e)
  }
}

onMounted(loadData)
</script>

<style scoped>
</style>