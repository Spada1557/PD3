<template>
  <div>
    <div class="toolbar">
      <div class="toolbar-left">
        <el-select v-model="filters.status" placeholder="Статус" clearable @change="loadSales" style="width:160px">
          <el-option label="Черновик" value="draft" />
          <el-option label="Проведён" value="posted" />
          <el-option label="Отменён" value="cancelled" />
        </el-select>
        <el-date-picker v-model="dateRange" type="daterange" range-separator="—" start-placeholder="С" end-placeholder="По" format="DD.MM.YYYY" value-format="YYYY-MM-DD" @change="loadSales" style="width:300px" />
      </div>
      <el-button type="primary" @click="$router.push('/sales/new')" style="cursor:pointer">
        <el-icon><Plus /></el-icon> Новая продажа
      </el-button>
    </div>
    <div class="data-table">
      <el-table :data="sales" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="number" label="Номер" width="110">
          <template #default="{ row }"><span style="font-weight:600;color:var(--primary-light)">{{ row.number }}</span></template>
        </el-table-column>
        <el-table-column prop="date" label="Дата" width="140">
          <template #default="{ row }">{{ formatDate(row.date) }}</template>
        </el-table-column>
        <el-table-column prop="client_name" label="Клиент" min-width="180">
          <template #default="{ row }">{{ row.client_name || '—' }}</template>
        </el-table-column>
        <el-table-column prop="total_amount" label="Сумма" width="130" align="right">
          <template #default="{ row }"><span style="font-weight:600">{{ formatCurrency(row.total_amount) }}</span></template>
        </el-table-column>
        <el-table-column prop="profit_amount" label="Прибыль" width="130" align="right">
          <template #default="{ row }">
            <span :style="{ fontWeight: 600, color: row.profit_amount >= 0 ? '#10B981' : '#EF4444' }">
              {{ formatCurrency(row.profit_amount) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Статус" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status).type" effect="dark" size="small">{{ statusTag(row.status).label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="$router.push(`/sales/${row.id}`)" style="cursor:pointer">Открыть</el-button>
            <el-button v-if="row.status === 'draft'" link type="success" size="small" @click="postSale(row)" style="cursor:pointer">Провести</el-button>
            <el-button v-if="row.status === 'posted'" link type="warning" size="small" @click="cancelSale(row)" style="cursor:pointer">Отменить</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="display:flex;justify-content:flex-end;margin-top:16px">
        <el-pagination v-model:current-page="page" v-model:page-size="perPage" :page-sizes="[10,25,50]" :total="total" layout="total, sizes, prev, pager, next" @current-change="loadSales" @size-change="loadSales" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import { formatCurrency, formatDate, statusTag } from '../utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'

const sales = ref([])
const loading = ref(false)
const page = ref(1)
const perPage = ref(10)
const total = ref(0)
const filters = ref({ status: null })
const dateRange = ref(null)

async function loadSales() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: perPage.value }
    if (filters.value.status) params.status = filters.value.status
    if (dateRange.value) { params.date_from = dateRange.value[0]; params.date_to = dateRange.value[1] }
    const res = await api.get('/sales', { params })
    sales.value = res.data.data
    total.value = res.data.total
  } finally { loading.value = false }
}

async function postSale(row) {
  await ElMessageBox.confirm('Провести продажу? Остатки товаров будут уменьшены.', 'Подтверждение')
  try { await api.post(`/sales/${row.id}/post`); ElMessage.success('Продажа проведена'); await loadSales() }
  catch (e) { ElMessage.error(e.response?.data?.detail?.message || 'Ошибка') }
}

async function cancelSale(row) {
  await ElMessageBox.confirm('Отменить проведение? Остатки будут возвращены.', 'Подтверждение')
  try { await api.post(`/sales/${row.id}/cancel`); ElMessage.success('Отменено'); await loadSales() }
  catch (e) { ElMessage.error(e.response?.data?.detail?.message || 'Ошибка') }
}

onMounted(loadSales)
</script>