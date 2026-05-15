<template>
  <div>
    <div class="toolbar">
      <el-button @click="$router.back()" style="cursor:pointer"><el-icon><ArrowLeft /></el-icon> Назад</el-button>
      <h2>{{ isEdit ? `Закупка ${form.number || ''}` : 'Новая закупка' }}</h2>
      <div style="margin-left:auto;display:flex;gap:8px" v-if="isEdit">
        <el-button v-if="form.status === 'draft'" type="success" @click="postPurchase" style="cursor:pointer">Провести</el-button>
        <el-button v-if="form.status === 'posted'" type="warning" @click="cancelPurchase" style="cursor:pointer">Отменить проведение</el-button>
      </div>
    </div>
    <div class="form-card">
      <el-form :model="form" label-width="140px">
        <div class="form-grid">
          <el-form-item label="Поставщик">
            <el-select v-model="form.supplier_id" clearable filterable placeholder="Выбрать...">
              <el-option v-for="s in suppliers" :key="s.id" :label="s.name" :value="s.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="Дата">
            <el-date-picker v-model="form.date" type="datetime" format="DD.MM.YYYY HH:mm" value-format="YYYY-MM-DDTHH:mm:ss" />
          </el-form-item>
          <el-form-item label="Комментарий">
            <el-input v-model="form.comment" type="textarea" maxlength="1000" />
          </el-form-item>
        </div>
        <el-divider content-position="left">Товары</el-divider>
        <el-table :data="form.items" border size="small">
          <el-table-column label="Товар" min-width="200">
            <template #default="{ row }">
              <el-select v-model="row.product_id" filterable placeholder="Выбрать..." @change="val => onProductChange(row, val)">
                <el-option v-for="p in products" :key="p.id" :label="`${p.article} — ${p.name}`" :value="p.id" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="Кол-во" width="120">
            <template #default="{ row }">
              <el-input-number v-model="row.quantity" :min="0.01" :precision="2" size="small" @change="calcAmount(row)" />
            </template>
          </el-table-column>
          <el-table-column label="Цена" width="130">
            <template #default="{ row }">
              <el-input-number v-model="row.price" :min="0" :precision="2" size="small" @change="calcAmount(row)" />
            </template>
          </el-table-column>
          <el-table-column label="Сумма" width="130">
            <template #default="{ row }">{{ formatCurrency(row.amount) }}</template>
          </el-table-column>
          <el-table-column width="60">
            <template #default="{ $index }">
              <el-button link type="danger" @click="form.items.splice($index, 1)" style="cursor:pointer"><el-icon><Delete /></el-icon></el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-button type="primary" link @click="addItem" style="margin-top:8px;cursor:pointer">+ Добавить строку</el-button>
        <div style="text-align:right;margin-top:16px;font-size:16px;font-weight:700;letter-spacing:-0.01em">
          Итого: {{ formatCurrency(totalAmount) }}
        </div>
        <el-form-item style="margin-top:20px" v-if="form.status === 'draft' || !isEdit">
          <el-button type="primary" @click="savePurchase" :loading="saving" style="cursor:pointer">Сохранить</el-button>
          <el-button @click="$router.back()" style="cursor:pointer">Отмена</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'
import { formatCurrency } from '../utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const purchaseId = computed(() => route.params.id !== 'new' ? route.params.id : null)
const isEdit = computed(() => !!purchaseId.value)
const suppliers = ref([])
const products = ref([])
const saving = ref(false)

const form = ref({
  supplier_id: null, date: null, comment: '', items: [{ product_id: null, quantity: 1, price: 0, amount: 0 }]
})

const totalAmount = computed(() => form.value.items.reduce((s, i) => s + (i.amount || 0), 0))

function calcAmount(row) {
  row.amount = Math.round((row.quantity || 0) * (row.price || 0) * 100) / 100
}

function onProductChange(row, val) {
  const p = products.value.find(p => p.id === val)
  if (p) { row.price = p.cost; calcAmount(row) }
}

function addItem() {
  form.value.items.push({ product_id: null, quantity: 1, price: 0, amount: 0 })
}

async function savePurchase() {
  if (!form.value.items.length || !form.value.items.some(i => i.product_id)) {
    ElMessage.warning('Добавьте хотя бы один товар'); return
  }
  saving.value = true
  try {
    const payload = { ...form.value, items: form.value.items.filter(i => i.product_id) }
    if (isEdit.value) {
      await api.put(`/purchases/${purchaseId.value}`, payload)
    } else {
      await api.post('/purchases', payload)
    }
    ElMessage.success('Сохранено')
    router.push('/purchases')
  } catch (e) { ElMessage.error(e.response?.data?.detail?.message || 'Ошибка') }
  finally { saving.value = false }
}

async function postPurchase() {
  await ElMessageBox.confirm('Провести закупку?', 'Подтверждение')
  try { await api.post(`/purchases/${purchaseId.value}/post`); ElMessage.success('Проведено'); await loadPurchase() }
  catch (e) { ElMessage.error(e.response?.data?.detail?.message || 'Ошибка') }
}

async function cancelPurchase() {
  await ElMessageBox.confirm('Отменить проведение?', 'Подтверждение')
  try { await api.post(`/purchases/${purchaseId.value}/cancel`); ElMessage.success('Отменено'); await loadPurchase() }
  catch (e) { ElMessage.error(e.response?.data?.detail?.message || 'Ошибка') }
}

async function loadPurchase() {
  const res = await api.get(`/purchases/${purchaseId.value}`)
  form.value = { ...res.value || res.data, date: res.data?.date, items: (res.data?.items || []).map(i => ({ ...i })) }
}

onMounted(async () => {
  const [sRes, pRes] = await Promise.all([api.get('/suppliers/all'), api.get('/products/all')])
  suppliers.value = Array.isArray(sRes.data) ? sRes.data : sRes.data.data || []
  products.value = Array.isArray(pRes.data) ? pRes.data : pRes.data.data || []
  if (isEdit.value) await loadPurchase()
})
</script>