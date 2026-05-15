<template>
  <div>
    <div class="card">
      <div class="table-actions">
        <el-select v-model="filterStatus" placeholder="Все статусы" clearable style="width:170px" @change="load">
          <el-option label="Черновик" value="draft" />
          <el-option label="Проведён" value="posted" />
          <el-option label="Отменён" value="cancelled" />
        </el-select>
        <el-select v-model="filterSupplier" placeholder="Все поставщики" clearable style="width:260px" filterable @change="load">
          <el-option v-for="s in suppliers" :key="s.id" :label="s.name" :value="s.id" />
        </el-select>
        <el-button type="primary" @click="openCreate" style="margin-left:auto">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:5px"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          Создать закупку
        </el-button>
      </div>

      <el-table :data="items" v-loading="loading" highlight-current-row @row-click="openDetail" style="width:100%;cursor:pointer">
        <el-table-column prop="number" label="Номер" width="180">
          <template #default="{row}"><span style="font-weight:700;color:var(--text-primary);white-space:nowrap">{{ row.number }}</span></template>
        </el-table-column>
        <el-table-column label="Дата" width="130">
          <template #default="{row}">{{ formatDate(row.date) }}</template>
        </el-table-column>
        <el-table-column label="Поставщик" min-width="250" show-overflow-tooltip>
          <template #default="{row}">
            <span :title="row.supplier?.name">{{ row.supplier?.name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Сумма" width="160" align="right">
          <template #default="{row}"><span class="amount" style="font-size:14px;white-space:nowrap">{{ formatCurrency(row.total_amount) }}</span></template>
        </el-table-column>
        <el-table-column label="Статус" width="140" align="center">
          <template #default="{row}">
            <el-tag :type="row.status === 'posted' ? 'success' : row.status === 'draft' ? 'warning' : 'danger'" size="small" effect="plain">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <div class="flex-row mt-20" style="justify-content:flex-end">
        <el-pagination v-model:current-page="page" :page-size="perPage" :total="total" @current-change="load" layout="prev, pager, next, total" />
      </div>
    </div>

    <el-dialog v-model="showForm" :title="readOnly ? `Закупка ${readOnly.number}` : (editing ? 'Редактирование закупки' : 'Новая закупка')" width="900px" @closed="resetForm" :close-on-click-modal="false" class="doc-dialog">
      <el-form :model="form" label-width="110px">
        <div class="form-row" style="margin-bottom:4px">
          <el-form-item label="Поставщик">
            <el-select v-model="form.supplier_id" style="width:100%" filterable :disabled="!!readOnly" :teleported="false">
              <el-option v-for="s in suppliers" :key="s.id" :label="s.name" :value="s.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="Дата">
            <el-date-picker v-model="form.date" type="datetime" value-format="YYYY-MM-DDTHH:mm:ssZ" style="width:100%" :disabled="!!readOnly" />
          </el-form-item>
        </div>
        <el-form-item label="Комментарий">
          <el-input v-model="form.comment" maxlength="1000" type="textarea" :rows="2" :disabled="!!readOnly" />
        </el-form-item>

        <el-divider>Позиции документа</el-divider>

        <div v-for="(item, idx) in form.items" :key="idx" class="item-row" :class="{ 'item-row-disabled': !!readOnly }">
          <div class="item-row-index">{{ idx + 1 }}</div>
          <el-select v-model="item.product_id" placeholder="Товар" filterable class="item-product" :disabled="!!readOnly" @change="onProductSelect(idx)" :teleported="false">
            <el-option v-for="p in products" :key="p.id" :label="`${p.name} [${p.article}]`" :value="p.id" />
          </el-select>
          <el-input-number v-model="item.quantity" placeholder="Кол-во" :min="0.01" :step="1" class="item-qty" :disabled="!!readOnly" @change="calcAmount(idx)" />
          <el-input-number v-model="item.price" placeholder="Цена" :min="0" :step="0.01" class="item-price" :disabled="!!readOnly" @change="calcAmount(idx)" />
          <div class="item-amount-tag">
            {{ formatCurrency(item.amount) }}
          </div>
          <el-button v-if="!readOnly" type="danger" plain circle size="small" class="item-del" @click="form.items.splice(idx,1)">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </el-button>
        </div>

        <el-button v-if="!readOnly" type="default" @click="form.items.push({product_id:null,quantity:1,price:0,amount:0})" style="width:100%;border-style:dashed">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:5px"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          Добавить позицию
        </el-button>

        <div v-if="readOnly" class="doc-lifecycle">
          <div class="lifecycle-row">
            <div class="lifecycle-step" :class="{ active: readOnly.status === 'draft', done: readOnly.status !== 'draft' }">
              <div class="lifecycle-dot"></div>
              <span>Черновик</span>
            </div>
            <div class="lifecycle-line" :class="{ done: readOnly.status !== 'draft' }"></div>
            <div class="lifecycle-step" :class="{ active: readOnly.status === 'posted', done: readOnly.status === 'cancelled' }">
              <div class="lifecycle-dot"></div>
              <span>Проведён</span>
            </div>
            <div class="lifecycle-line" :class="{ done: readOnly.status === 'cancelled' }"></div>
            <div class="lifecycle-step" :class="{ active: readOnly.status === 'cancelled' }">
              <div class="lifecycle-dot"></div>
              <span>Отменён</span>
            </div>
          </div>
          <div class="lifecycle-actions">
            <el-button v-if="readOnly.status === 'draft'" type="success" @click="postDoc(readOnly.id)" size="large">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:6px"><polyline points="20 6 9 17 4 12"/></svg>
              Провести документ
            </el-button>
            <el-button v-if="readOnly.status === 'posted'" type="warning" @click="cancelDoc(readOnly.id)" size="large">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:6px"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/></svg>
              Отменить проведение
            </el-button>
          </div>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="showForm=false">Закрыть</el-button>
        <el-button v-if="!readOnly" type="primary" @click="saveDoc" :loading="saving">Сохранить</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../api/client'
import { formatCurrency, formatDate } from '../utils/format'
import { ElMessage } from 'element-plus'

const items = ref([]), suppliers = ref([]), products = ref([])
const loading = ref(false), saving = ref(false), page = ref(1), perPage = ref(10), total = ref(0)
const filterStatus = ref(null), filterSupplier = ref(null)
const showForm = ref(false), editing = ref(false), readOnly = ref(null)
const form = reactive({ supplier_id: null, date: new Date().toISOString(), comment: '', items: [{ product_id: null, quantity: 1, price: 0, amount: 0 }] })

function statusLabel(s) { return s === 'posted' ? 'Проведён' : s === 'draft' ? 'Черновик' : 'Отменён' }

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: perPage.value }
    if (filterStatus.value) params.status = filterStatus.value
    if (filterSupplier.value) params.supplier_id = filterSupplier.value
    const { data } = await api.get('/purchases', { params })
    items.value = data.data; total.value = data.total
  } catch (e) {} finally { loading.value = false }
}
async function loadRefs() {
  try {
    const [s, p] = await Promise.all([api.get('/suppliers', { params: { per_page: 100 } }), api.get('/products', { params: { per_page: 100 } })])
    suppliers.value = s.data.data; products.value = p.data.data
  } catch (e) { ElMessage.error('Ошибка загрузки справочников') }
}
function openCreate() { editing.value = false; readOnly.value = null; resetForm(); showForm.value = true }
async function openDetail(row) {
  try {
    const { data } = await api.get(`/purchases/${row.id}`)
    form.supplier_id = data.supplier_id; form.date = data.date; form.comment = data.comment || ''
    form.items = data.items.map(i => ({ product_id: i.product_id, quantity: i.quantity, price: i.price, amount: i.amount }))
    editing.value = true; readOnly.value = data
    showForm.value = true
  } catch (e) { ElMessage.error('Ошибка загрузки') }
}
function resetForm() { editing.value = false; readOnly.value = null; Object.assign(form, { supplier_id: null, date: new Date().toISOString(), comment: '', items: [{ product_id: null, quantity: 1, price: 0, amount: 0 }] }) }
function calcAmount(idx) { const item = form.items[idx]; item.amount = Math.round((item.quantity || 0) * (item.price || 0) * 100) / 100 }
function onProductSelect(idx) {
  const item = form.items[idx]
  if (item.product_id) {
    const product = products.value.find(p => p.id === item.product_id)
    if (product) { item.price = product.cost; calcAmount(idx) }
  }
}
async function saveDoc() {
  saving.value = true
  const payload = { supplier_id: form.supplier_id, date: form.date, comment: form.comment, items: form.items.filter(i => i.product_id).map(i => ({ product_id: i.product_id, quantity: i.quantity, price: i.price, amount: Math.round(i.quantity * i.price * 100) / 100 })) }
  try {
    if (editing.value && readOnly.value) { await api.put(`/purchases/${readOnly.value.id}`, payload) }
    else { await api.post('/purchases', payload) }
    showForm.value = false; ElMessage.success('Сохранено'); load()
  } catch (e) { ElMessage.error(e.response?.data?.detail?.message || 'Ошибка') } finally { saving.value = false }
}
async function postDoc(id) {
  try { await api.post(`/purchases/${id}/post`); ElMessage.success('Документ проведён'); showForm.value = false; load() }
  catch (e) { ElMessage.error(e.response?.data?.detail?.message || 'Ошибка') }
}
async function cancelDoc(id) {
  try { await api.post(`/purchases/${id}/cancel`); ElMessage.success('Проведение отменено'); showForm.value = false; load() }
  catch (e) { ElMessage.error(e.response?.data?.detail?.message || 'Ошибка') }
}
onMounted(() => { loadRefs(); load() })
</script>

<style scoped>
.item-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  margin-bottom: 14px;
  padding: 12px 14px;
  background: var(--bg-surface);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}
.item-row:hover { background: #E2E8F0; }
.item-row-disabled { opacity: 0.85; pointer-events: none; }
.item-row-index {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--warning);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  flex-shrink: 0;
}
.item-product { flex: 2 1 200px; min-width: 180px; }
.item-qty { flex: 0 1 115px; min-width: 100px; }
.item-price { flex: 0 1 130px; min-width: 110px; }
.item-amount-tag {
  flex: 0 0 auto;
  min-width: 100px;
  text-align: right;
  font-weight: 800;
  font-size: 15px;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}
.item-del { flex: 0 0 auto; }

.doc-lifecycle {
  margin-top: 24px;
  padding: 24px;
  background: linear-gradient(135deg, var(--bg-surface), #FFF);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
}
.lifecycle-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  margin-bottom: 20px;
}
.lifecycle-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}
.lifecycle-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--border);
  transition: all var(--transition-base);
}
.lifecycle-step.active .lifecycle-dot {
  background: var(--warning);
  box-shadow: 0 0 0 4px var(--warning-soft);
  width: 16px;
  height: 16px;
}
.lifecycle-step.done .lifecycle-dot {
  background: var(--success);
  box-shadow: 0 0 0 4px var(--success-soft);
}
.lifecycle-step span { font-size: 12px; font-weight: 600; color: var(--text-muted); }
.lifecycle-step.active span { color: var(--text-primary); }
.lifecycle-step.done span { color: var(--text-primary); }
.lifecycle-line { width: 60px; height: 2px; background: var(--border); margin: 0 8px 20px; transition: all var(--transition-base); }
.lifecycle-line.done { background: var(--success); }
.lifecycle-actions { display: flex; justify-content: center; gap: 10px; }

@media (max-width: 600px) {
  .item-row { gap: 6px; padding: 10px; }
  .item-product { flex: 1 1 100%; }
  .item-qty, .item-price { flex: 1 1 45%; min-width: 80px; }
  .item-row-index { display: none; }
}
</style>