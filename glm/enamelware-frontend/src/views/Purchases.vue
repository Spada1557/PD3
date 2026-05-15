<template>
  <div>
    <div class="toolbar">
      <div class="toolbar-left">
        <el-select v-model="filters.status" placeholder="Статус" clearable @change="loadPurchases" style="width:150px">
          <el-option label="Черновик" value="draft" />
          <el-option label="Проведён" value="posted" />
          <el-option label="Отменён" value="cancelled" />
        </el-select>
        <el-date-picker v-model="dateRange" type="daterange" range-separator="—" start-placeholder="С" end-placeholder="По" format="DD.MM.YYYY" value-format="YYYY-MM-DD" @change="loadPurchases" />
      </div>
      <el-button type="primary" @click="$router.push('/purchases/new')" style="cursor:pointer">
        <el-icon><Plus /></el-icon> Новая закупка
      </el-button>
    </div>
    <div class="data-table">
      <el-table :data="purchases" stripe v-loading="loading">
        <el-table-column prop="number" label="Номер" width="110" />
        <el-table-column prop="date" label="Дата" width="140">
          <template #default="{ row }">{{ formatDate(row.date) }}</template>
        </el-table-column>
        <el-table-column prop="supplier_name" label="Поставщик" min-width="180" />
        <el-table-column prop="total_amount" label="Сумма" width="130">
          <template #default="{ row }">{{ formatCurrency(row.total_amount) }}</template>
        </el-table-column>
        <el-table-column prop="status" label="Статус" width="110">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status).type" size="small">{{ statusTag(row.status).label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="$router.push(`/purchases/${row.id}`)" style="cursor:pointer">Открыть</el-button>
            <el-button v-if="row.status === 'draft'" link type="success" @click="postPurchase(row)" style="cursor:pointer">Провести</el-button>
            <el-button v-if="row.status === 'posted'" link type="warning" @click="cancelPurchase(row)" style="cursor:pointer">Отменить</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="display:flex;justify-content:flex-end;margin-top:16px">
        <el-pagination v-model:current-page="page" v-model:page-size="perPage" :page-sizes="[10,25,50]" :total="total" layout="total, sizes, prev, pager, next" @current-change="loadPurchases" @size-change="loadPurchases" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import { formatCurrency, formatDate, statusTag } from '../utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const purchases = ref([])
const loading = ref(false)
const page = ref(1)
const perPage = ref(10)
const total = ref(0)
const filters = ref({ status: null })
const dateRange = ref(null)

async function loadPurchases() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: perPage.value }
    if (filters.value.status) params.status = filters.value.status
    if (dateRange.value) { params.date_from = dateRange.value[0]; params.date_to = dateRange.value[1] }
    const res = await api.get('/purchases', { params })
    purchases.value = res.data.data
    total.value = res.data.total
  } finally { loading.value = false }
}

async function postPurchase(row) {
  await ElMessageBox.confirm('Провести закупку?', 'Подтверждение')
  try {
    await api.post(`/purchases/${row.id}/post`)
    ElMessage.success('Закупка проведена')
    await loadPurchases()
  } catch (e) { ElMessage.error(e.response?.data?.detail?.message || 'Ошибка') }
}

async function cancelPurchase(row) {
  await ElMessageBox.confirm('Отменить проведение?', 'Подтверждение')
  try {
    await api.post(`/purchases/${row.id}/cancel`)
    ElMessage.success('Проведение отменено')
    await loadPurchases()
  } catch (e) { ElMessage.error(e.response?.data?.detail?.message || 'Ошибка') }
}

onMounted(loadPurchases)
</script>