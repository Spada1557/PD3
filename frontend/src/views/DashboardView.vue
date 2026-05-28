<template>
  <div v-if="dashboardData" class="dashboard">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">Дашборд</h1>
        <p class="page-subtitle">Обзор ключевых показателей бизнеса</p>
      </div>
    </div>

    <div class="summary-grid">
      <SummaryCard title="Выручка" :value="formatMoney(dashboardData.summary.revenue)" :change="dashboardData.summary.revenue_change_percent" icon="TrendCharts" color="blue" />
      <SummaryCard title="Себестоимость" :value="formatMoney(dashboardData.summary.cost)" icon="Wallet" color="purple" />
      <SummaryCard title="Прибыль" :value="formatMoney(dashboardData.summary.profit)" :change="dashboardData.summary.profit_change_percent" icon="Coin" color="green" />
      <SummaryCard title="Остатки" :value="formatMoney(dashboardData.summary.stock_value)" icon="Box" color="amber" />
      <SummaryCard title="Заказы" :value="dashboardData.summary.orders_count" icon="Document" color="rose" />
    </div>

    <div class="charts-row">
      <el-card shadow="never" class="chart-card">
        <template #header>
          <div class="card-header">
            <div class="card-title-group">
              <span class="card-title">Динамика продаж</span>
              <el-tag size="small" type="info">30 дней</el-tag>
            </div>
          </div>
        </template>
        <div class="chart-wrap">
          <ChartCanvas type="bar" :data="barData" :options="barOpts" />
        </div>
      </el-card>
      <el-card shadow="never" class="chart-card doughnut-card">
        <template #header>
          <div class="card-header">
            <div class="card-title-group">
              <span class="card-title">Выручка по категориям</span>
            </div>
          </div>
        </template>
        <div class="chart-wrap doughnut-wrap">
          <ChartCanvas type="doughnut" :data="doughnutData" :options="doughnutOpts" />
        </div>
      </el-card>
    </div>

    <div class="lists-row">
      <ListCard title="Топ-5 товаров" icon="Trophy">
        <div class="list-items" v-if="dashboardData.top_products && dashboardData.top_products.length">
          <div v-for="(p, i) in dashboardData.top_products" :key="p.product_id" class="list-item">
            <div class="list-item-rank" :class="i < 3 ? 'rank-top' : ''">{{ i + 1 }}</div>
            <div class="list-item-info">
              <div class="list-item-name">{{ p.name }}</div>
              <div class="list-item-meta">{{ p.article }}</div>
            </div>
            <div class="list-item-value">
              <div class="list-item-revenue">{{ formatMoney(p.revenue) }}</div>
              <div class="list-item-qty">{{ p.quantity }} шт.</div>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <el-icon size="32" color="#D4D0E0"><Goods /></el-icon>
          <div class="empty-text">Нет данных</div>
        </div>
      </ListCard>
      <ListCard title="Топ-5 документов" icon="DocumentChecked">
        <div class="list-items" v-if="dashboardData.top_documents && dashboardData.top_documents.length">
          <div v-for="(d, i) in dashboardData.top_documents" :key="d.document_id" class="list-item">
            <div class="list-item-rank" :class="i < 3 ? 'rank-top' : ''">{{ i + 1 }}</div>
            <div class="list-item-info">
              <div class="list-item-name">{{ d.number }}</div>
              <div class="list-item-meta">{{ d.date }}</div>
            </div>
            <div class="list-item-value">
              <div class="list-item-revenue">{{ formatMoney(d.total_amount) }}</div>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <el-icon size="32" color="#D4D0E0"><Document /></el-icon>
          <div class="empty-text">Нет данных</div>
        </div>
      </ListCard>
      <ListCard title="Низкие остатки" icon="Warning">
        <div v-if="dashboardData.low_stock && dashboardData.low_stock.length">
          <div class="list-items">
            <div v-for="item in dashboardData.low_stock" :key="item.product_id" class="list-item">
              <div class="list-item-info">
                <div class="list-item-name">{{ item.name }}</div>
                <div class="list-item-meta">{{ item.article }}</div>
              </div>
              <div class="list-item-value">
                <div :class="['list-item-revenue', item.quantity <= item.min_stock ? 'text-danger' : '']">{{ item.quantity }} шт.</div>
                <div class="list-item-qty">мин: {{ item.min_stock }}</div>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <el-icon size="32" color="#D4D0E0"><Box /></el-icon>
          <div class="empty-text">Все запасы в норме</div>
        </div>
      </ListCard>
    </div>
  </div>
  <div v-else class="dashboard-loading">
    <el-skeleton :rows="3" animated />
    <div style="height:20px"></div>
    <el-skeleton :rows="2" animated />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useDashboardStore } from '../stores/dashboard'
import SummaryCard from '../components/SummaryCard.vue'
import ListCard from '../components/ListCard.vue'
import ChartCanvas from '../components/ChartCanvas.vue'

const dash = useDashboardStore()
const dashboardData = computed(() => dash.data)

onMounted(() => dash.load())

function formatMoney(v) {
  if (v === undefined || v === null) return '—'
  return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 0 }).format(v)
}

const barData = computed(() => {
  const labels = dash.data?.sales_chart?.map(d => d.date) || []
  const revenues = dash.data?.sales_chart?.map(d => d.revenue) || []
  const profits = dash.data?.sales_chart?.map(d => d.profit) || []
  return {
    labels,
    datasets: [
      { label: 'Выручка', data: revenues, backgroundColor: '#6D28D9', borderRadius: 8, barThickness: 14 },
      { label: 'Прибыль', data: profits, backgroundColor: '#059669', borderRadius: 8, barThickness: 14 },
    ],
  }
})

const barOpts = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'top', labels: { usePointStyle: true, padding: 16, font: { size: 12, family: 'Inter', weight: '600' }, color: '#4A4458' } },
    tooltip: {
      backgroundColor: '#1E1B2E',
      titleFont: { size: 13, family: 'Inter', weight: '700' },
      bodyFont: { size: 12, family: 'Inter', weight: '600' },
      padding: 14,
      cornerRadius: 14,
    },
  },
  scales: {
    x: { grid: { display: false }, ticks: { font: { size: 11, family: 'Inter' }, color: '#8B8696' } },
    y: { border: { display: false }, grid: { color: '#F0EDF5' }, ticks: { font: { size: 11, family: 'Inter' }, color: '#8B8696' } },
  },
}

const doughnutData = computed(() => {
  const labels = dash.data?.categories_chart?.map(d => d.category) || []
  const data = dash.data?.categories_chart?.map(d => d.revenue) || []
  return {
    labels,
    datasets: [{ data, backgroundColor: ['#6D28D9', '#059669', '#D97706', '#E11D48', '#4F46E5', '#0891B2', '#DB2777', '#0D9488'], borderWidth: 0, hoverOffset: 10, borderRadius: 6 }],
  }
})

const doughnutOpts = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '68%',
  plugins: {
    legend: { position: 'bottom', labels: { usePointStyle: true, padding: 16, font: { size: 11, family: 'Inter', weight: '600' }, color: '#4A4458' } },
    tooltip: {
      backgroundColor: '#1E1B2E',
      titleFont: { size: 13, family: 'Inter', weight: '700' },
      bodyFont: { size: 12, family: 'Inter', weight: '600' },
      padding: 14,
      cornerRadius: 14,
    },
  },
}
</script>

<style scoped>
.dashboard {
  animation: pageIn 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.charts-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  min-height: 420px;
}

.doughnut-card {
  min-height: 420px;
}

.chart-wrap {
  height: 340px;
}

.doughnut-wrap {
  height: 320px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
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

.lists-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
}

.list-items {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.list-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-light);
  transition: var(--transition);
}

.list-item:last-child {
  border-bottom: none;
}

.list-item-rank {
  width: 30px;
  height: 30px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 800;
  background: var(--surface-overlay);
  color: var(--text-muted);
  flex-shrink: 0;
}

.list-item-rank.rank-top {
  background: linear-gradient(135deg, #6D28D9, #7C3AED);
  color: #fff;
}

.list-item-info {
  flex: 1;
  min-width: 0;
}

.list-item-name {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.list-item-meta {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
  font-weight: 500;
}

.list-item-value {
  text-align: right;
  flex-shrink: 0;
}

.list-item-revenue {
  font-size: 13px;
  font-weight: 800;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}

.list-item-qty {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
  font-weight: 500;
}

.text-danger {
  color: var(--danger) !important;
  font-weight: 700;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
}

.empty-text {
  margin-top: 12px;
  font-size: 13px;
  color: var(--text-muted);
  font-weight: 500;
}

.dashboard-loading {
  padding: 20px 0;
}

@media (max-width: 900px) {
  .charts-row {
    grid-template-columns: 1fr;
  }
  .lists-row {
    grid-template-columns: 1fr;
  }
}
</style>
