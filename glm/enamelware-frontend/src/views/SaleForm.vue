<template>
  <div>
    <div class="toolbar">
      <el-button @click="$router.back()" style="cursor:pointer"><el-icon><ArrowLeft /></el-icon> Назад</el-button>
      <h2>{{ isEdit ? `Продажа ${form.number || ''}` : 'Новая продажа' }}</h2>
      <div style="margin-left:auto;display:flex;gap:8px;align-items:center" v-if="isEdit">
        <el-tag :type="statusTag(form.status).type" effect="dark" size="large">{{ statusTag(form.status).label }}</el-tag>
        <el-button v-if="form.status === 'draft'" type="primary" @click="postSale" style="cursor:pointer">
          <el-icon><Check /></el-icon> Провести
        </el-button>
        <el-button v-if="form.status === 'posted'" type="warning" @click="cancelSale" style="cursor:pointer">
          <el-icon><RefreshLeft /></el-icon> Отменить
        </el-button>
      </div>
    </div>
    <div class="form-card">
      <el-form :model="form" label-width="150px">
        <div class="form-grid">
          <el-form-item label="Клиент">
            <el-select v-model="form.client_id" clearable filterable placeholder="Выбрать клиента" style="width:100%">
              <el-option v-for="c in clients" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="Дата">
            <el-date-picker v-model="form.date" type="datetime" format="DD.MM.YYYY HH:mm" value-format="YYYY-MM-DDTHH:mm:ss" style="width:100%" />
          </el-form-item>
          <el-form-item label="Комментарий">
            <el-input v-model="form.comment" type="textarea" maxlength="1000" :rows="2" />
          </el-form-item>
        </div>

        <el-divider content-position="left">Товары</el-divider>
        <el-table :data="form.items" border style="width:100%" size="default">
          <el-table-column label="Товар" min-width="220">
            <template #default="{ row }">
              <el-select v-model="row.product_id" filterable placeholder="Выбрать..." @change="val => onProductChange(row, val)" style="width:100%">
                <el-option v-for="p in products" :key="p.id" :label="`${p.article} — ${p.name}`" :value="p.id" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="Доступно" width="100" v-if="isEdit && form.status === 'draft'">
            <template #default="{ row }">
              <span style="font-size:11px;color:var(--text-muted)">{{ getAvailable(row.product_id) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Кол-во" width="120">
            <template #default="{ row }">
              <el-input-number v-model="row.quantity" :min="0.01" :precision="2" size="small" @change="calcRow(row)" style="width:100%" />
            </template>
          </el-table-column>
          <el-table-column label="Цена продажи" width="140">
            <template #default="{ row }">
              <el-input-number v-model="row.price" :min="0" :precision="2" size="small" @change="calcRow(row)" style="width:100%" />
            </template>
          </el-table-column>
          <el-table-column label="Сумма" width="120" align="right">
            <template #default="{ row }">
              <span style="font-weight:600">{{ formatCurrency(row.amount) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Себестоимость" width="120" align="right">
            <template #default="{ row }">
              <span style="color:var(--text-muted)">{{ formatCurrency(row.cost) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Прибыль" width="120" align="right">
            <template #default="{ row }">
              <span :style="{ fontWeight: 600, color: row.profit >= 0 ? '#10B981' : '#EF4444' }">{{ formatCurrency(row.profit) }}</span>
            </template>
          </el-table-column>
          <el-table-column width="50" v-if="form.status === 'draft' || !isEdit">
            <template #default="{ $index }">
              <el-button link type="danger" size="small" @click="form.items.splice($index, 1)" style="cursor:pointer"><el-icon><Delete /></el-icon></el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-button v-if="form.status === 'draft' || !isEdit" type="primary" link @click="addItem" style="margin-top:12px;cursor:pointer">
          <el-icon><Plus /></el-icon> Добавить строку
        </el-button>

        <div style="display:flex;justify-content:flex-end;margin-top:24px;gap:32px">
          <div style="text-align:right">
            <div style="font-size:12px;color:var(--text-muted);letter-spacing:0.02em">Сумма</div>
            <div style="font-size:16px;font-weight:700;color:var(--text-primary)">{{ formatCurrency(totalAmount) }}</div>
          </div>
          <div style="text-align:right">
            <div style="font-size:12px;color:var(--text-muted);letter-spacing:0.02em">Себестоимость</div>
            <div style="font-size:16px;font-weight:600;color:var(--warning)">{{ formatCurrency(totalCost) }}</div>
          </div>
          <div style="text-align:right;padding-left:20px;border-left:2px solid var(--border)">
            <div style="font-size:12px;color:var(--text-muted);letter-spacing:0.02em">Прибыль</div>
            <div style="font-size:20px;font-weight:800" :style="{ color: totalProfit >= 0 ? '#10B981' : '#EF4444' }">{{ formatCurrency(totalProfit) }}</div>
          </div>
        </div>

        <el-form-item style="margin-top:28px" v-if="form.status === 'draft' || !isEdit">
          <el-button type="primary" @click="saveSale" :loading="saving" size="large" style="cursor:pointer">
            <el-icon><Check /></el-icon> Сохранить
          </el-button>
          <el-button @click="$router.back()" size="large" style="cursor:pointer">Отмена</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'
import { formatCurrency, statusTag } from '../utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const saleId = computed(() => route.params.id !== 'new' ? route.params.id : null)
const isEdit = computed(() => !!saleId.value)
const clients = ref([])
const products = ref([])
const stockData = ref([])
const saving = ref(false)

const form = ref({
  client_id: null, date: null, comment: '', status: 'draft', number: '',
  items: [{ product_id: null, quantity: 1, price: 0, amount: 0, cost: 0, profit: 0, cost_per_unit: 0 }]
})

const totalAmount = computed(() => form.value.items.reduce((s, i) => s + (i.amount || 0), 0))
const totalCost = computed(() => form.value.items.reduce((s, i) => s + (i.cost || 0), 0))
const totalProfit = computed(() => form.value.items.reduce((s, i) => s + (i.profit || 0), 0))

function getAvailable(productId) {
  if (!productId) return '-'
  const s = stockData.value.find(s => s.product_id === productId && s.warehouse_id === 1)
  return s ? (s.quantity - s.reserved).toFixed(2) : '?'
}

function calcRow(row) {
  row.amount = Math.round((row.quantity || 0) * (row.price || 0) * 100) / 100
  row.cost = Math.round((row.quantity || 0) * (row.cost_per_unit || 0) * 100) / 100
  row.profit = Math.round((row.amount - row.cost) * 100) / 100
}

function onProductChange(row, val) {
  const p = products.value.find(p => p.id === val)
  if (p) {
    row.price = p.price
    row.cost_per_unit = p.cost
    const s = stockData.value.find(s => s.product_id === val && s.warehouse_id === 1)
    row.cost_per_unit = s ? s.avg_cost : p.cost
    calcRow(row)
  }
}

function addItem() {
  form.value.items.push({ product_id: null, quantity: 1, price: 0, amount: 0, cost: 0, cost_per_unit: 0, profit: 0 })
}

async function saveSale() {
  const validItems = form.value.items.filter(i => i.product_id)
  if (!validItems.length) { ElMessage.warning('Добавьте хотя бы один товар'); return }
  saving.value = true
  try {
    const payload = { ...form.value, items: validItems.map(({ cost_per_unit, ...rest }) => rest) }
    if (isEdit.value) {
      await api.put(`/sales/${saleId.value}`, payload)
    } else {
      await api.post('/sales', payload)
    }
    ElMessage.success('Сохранено')
    router.push('/sales')
  } catch (e) {
    const msg = e.response?.data?.detail?.message || e.response?.data?.message || 'Ошибка сохранения'
    ElMessage.error(msg)
  } finally { saving.value = false }
}

async function postSale() {
  await ElMessageBox.confirm('Провести продажу? После проведения складские остатки будут уменьшены.', 'Подтверждение')
  try {
    await api.post(`/sales/${saleId.value}/post`)
    ElMessage.success('Продажа проведена')
    await loadSale()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail?.message || 'Невозможно провести')
  }
}

async function cancelSale() {
  await ElMessageBox.confirm('Отменить проведение? Остатки будут возвращены на склад.', 'Подтверждение')
  try {
    await api.post(`/sales/${saleId.value}/cancel`)
    ElMessage.success('Проведение отменено')
    await loadSale()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail?.message || 'Ошибка')
  }
}

async function loadSale() {
  const res = await api.get(`/sales/${saleId.value}`)
  const data = res.data
  form.value = {
    client_id: data.client_id, date: data.date, comment: data.comment,
    status: data.status, number: data.number,
    items: (data.items || []).map(i => ({
      ...i, cost_per_unit: i.quantity > 0 ? i.cost / i.quantity : 0
    }))
  }
}

onMounted(async () => {
  const [cRes, pRes, sRes] = await Promise.all([
    api.get('/clients/all'), api.get('/products/all'), api.get('/stock?per_page=100')
  ])
  clients.value = Array.isArray(cRes.data) ? cRes.data : cRes.data.data || []
  products.value = Array.isArray(pRes.data) ? pRes.data : pRes.data.data || []
  stockData.value = sRes.data.data || []
  if (isEdit.value) await loadSale()
})
</script>