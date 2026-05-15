<template>
  <div class="page-view">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">Продажи</h1>
        <p class="page-subtitle">Документы реализации товаров</p>
      </div>
      <div class="page-header-actions">
        <el-input v-model="searchNumber" placeholder="Номер" clearable style="width:180px" />
        <el-select v-model="filterStatus" placeholder="Статус" clearable style="width:140px">
          <el-option label="Черновик" value="draft" />
          <el-option label="Проведен" value="posted" />
          <el-option label="Отменен" value="cancelled" />
        </el-select>
        <el-button type="primary" @click="openForm">
          <el-icon size="16" style="margin-right:6px"><Plus /></el-icon>
          Новая продажа
        </el-button>
      </div>
    </div>
    <el-card shadow="never">
      <el-table :data="items" v-loading="loading" style="width:100%">
        <el-table-column prop="number" label="#"><template #default="{ row }"><span class="col-nowrap">{{ row.number }}</span></template></el-table-column>
        <el-table-column prop="date" label="Дата">
          <template #default="{ row }"><span class="col-nowrap">{{ formatDate(row.date) }}</span></template>
        </el-table-column>
        <el-table-column prop="client.name" label="Клиент" min-width="220" show-overflow-tooltip />
        <el-table-column :formatter="(r) => formatMoney(r.total_amount)" label="Сумма" align="right">
          <template #default="{ row }"><span class="col-nowrap">{{ formatMoney(row.total_amount) }}</span></template>
        </el-table-column>
        <el-table-column prop="status" label="Статус" width="105">
          <template #default="{ row }">
            <el-tag size="small" :type="statusTag(row.status)" class="status-tag">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="" width="120" align="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-tooltip content="Просмотреть" :show-after="300">
                <el-button class="action-btn view-btn" @click="$router.push('/sales/' + row.id)"><el-icon size="14"><View /></el-icon></el-button>
              </el-tooltip>
              <el-tooltip v-if="row.status === 'draft'" content="Провести" :show-after="300">
                <el-button class="action-btn post-btn" @click="post(row.id)"><el-icon size="14"><Check /></el-icon></el-button>
              </el-tooltip>
              <el-tooltip content="Удалить" :show-after="300">
                <el-button class="action-btn delete-btn" @click="remove(row.id)"><el-icon size="14"><Delete /></el-icon></el-button>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination background layout="prev, pager, next" :total="total" :page-size="perPage" v-model:current-page="page" @current-change="load" style="margin-top:16px" />
    </el-card>

    <!-- Dialog — CSS Grid Form -->
    <el-dialog v-model="dialogVisible" :title="'Новая продажа'" width="860" :close-on-click-modal="false">
      <div class="sale-form">
        <!-- Header Grid -->
        <div class="form-grid header-grid">
          <el-form-item label="Клиент" class="form-item-client" required>
            <el-select v-model="form.client_id" filterable placeholder="Выберите клиента" class="field-full">
              <el-option v-for="s in clients" :key="s.id" :label="s.name" :value="s.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="Дата" class="form-item-date">
            <el-date-picker v-model="form.date" type="datetime" class="field-full" />
          </el-form-item>
        </div>

        <!-- Comment -->
        <div class="form-grid comment-grid">
          <el-form-item label="Комментарий" class="form-item-comment">
            <el-input v-model="form.comment" type="textarea" :rows="2" placeholder="Дополнительная информация..." />
          </el-form-item>
        </div>

        <!-- Items Section -->
        <div class="items-section">
          <div class="items-header">
            <span class="items-title">Товарные позиции</span>
            <el-button size="small" type="primary" plain @click="addRow" class="btn-add-item">
              <el-icon size="14"><Plus /></el-icon> Добавить позицию
            </el-button>
          </div>
          <el-table :data="form.items" size="small" class="items-table">
            <el-table-column label="Товар" width="280">
              <template #default="{ $index }">
                <el-select v-model="form.items[$index].product_id" filterable placeholder="Выберите товар" class="field-full" @change="fillPrice($index)">
                  <el-option v-for="p in products" :key="p.id" :label="`${p.article} — ${p.name}`" :value="p.id" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="Кол-во" width="110">
              <template #default="{ $index }">
                <el-input-number v-model="form.items[$index].quantity" :min="0.01" :precision="2" class="field-full" />
              </template>
            </el-table-column>
            <el-table-column label="Цена" width="130">
              <template #default="{ $index }">
                <el-input-number v-model="form.items[$index].price" :min="0" :precision="2" class="field-full" />
              </template>
            </el-table-column>
            <el-table-column label="Сумма" width="120" align="right">
              <template #default="{ $index }">
                <span class="row-total">{{ formatMoney(form.items[$index].quantity * form.items[$index].price) }}</span>
              </template>
            </el-table-column>
            <el-table-column width="48" align="center">
              <template #default="{ $index }">
                <el-button type="danger" text circle class="btn-remove-row" @click="removeRow($index)">
                  <el-icon size="14"><Delete /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false" class="btn-cancel">Отмена</el-button>
          <el-button type="primary" @click="save" class="btn-create">
            <el-icon size="16"><Plus /></el-icon>
            Создать продажу
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { salesApi, referencesApi, productsApi } from '../api'
import { Plus, Delete, View, Check } from '@element-plus/icons-vue'

const items = ref([])
const total = ref(0)
const page = ref(1)
const perPage = ref(10)
const loading = ref(false)
const searchNumber = ref('')
const filterStatus = ref('')
const dialogVisible = ref(false)
const clients = ref([])
const products = ref([])

const form = reactive({ client_id: null, date: null, comment: '', items: [] })

const load = async () => {
  loading.value = true
  const res = await salesApi.list({ page: page.value, per_page: perPage.value, status: filterStatus.value || undefined, number: searchNumber.value || undefined })
  items.value = res.data.data
  total.value = res.data.total
  loading.value = false
}

const openForm = () => {
  Object.assign(form, { client_id: null, date: new Date(), comment: '', items: [{ product_id: null, quantity: 1, price: 0 }] })
  dialogVisible.value = true
}

const addRow = () => form.items.push({ product_id: null, quantity: 1, price: 0 })
const removeRow = (i) => form.items.splice(i, 1)
const fillPrice = (idx) => {
  const pid = form.items[idx].product_id
  const p = products.value.find(x => x.id === pid)
  if (p) form.items[idx].price = p.price
}
const save = async () => {
  try {
    await salesApi.create({ ...form, date: form.date ? new Date(form.date).toISOString() : null })
    ElMessage.success('Сохранено')
    dialogVisible.value = false
    load()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || 'Ошибка')
  }
}

const post = async (id) => {
  try { await salesApi.post(id); ElMessage.success('Проведено'); load() }
  catch (e){ ElMessage.error(e.response?.data?.message || 'Ошибка') }
}

const remove = async (id) => {
  try {
    await ElMessageBox.confirm('Удалить документ?', 'Подтверждение')
    await salesApi.remove(id)
    ElMessage.success('Удалено')
    load()
  } catch (e) { if (e !== 'cancel') ElMessage.error(e.response?.data?.message || 'Ошибка') }
}

function formatMoney(v){ return new Intl.NumberFormat('ru-RU',{style:'currency', currency:'RUB', maximumFractionDigits:0}).format(v) }
function formatDate(d){ return d ? new Date(d).toLocaleDateString('ru-RU') : '' }
function statusTag(s){ return {draft:'info', posted:'success', cancelled:'danger'}[s]||'' }
function statusLabel(s){ return {draft:'Черновик', posted:'Проведен', cancelled:'Отменен'}[s]||s }

onMounted(async () => {
  load()
  const s = await referencesApi.clients({ per_page: 1000 })
  clients.value = s.data.data
  const p = await productsApi.list({ per_page: 1000 })
  products.value = p.data.data
})
watch([searchNumber, filterStatus], () => { page.value = 1; load() })
</script>

<style scoped>
/* CSS Grid Layout for Dialog */
.sale-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-grid {
  display: grid;
  gap: 16px;
}

.header-grid {
  grid-template-columns: 2fr 1fr;
  align-items: start;
}

.comment-grid {
  grid-template-columns: 1fr;
}

.form-item-client,
.form-item-date,
.form-item-comment {
  margin-bottom: 0 !important;
}

.field-full {
  width: 100% !important;
}

/* Items Section */
.items-section {
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: 16px;
  background: var(--surface-overlay);
}

.items-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.items-title {
  font-weight: 700;
  font-size: 14px;
  color: var(--text-primary);
}

.btn-add-item {
  font-weight: 600;
}

.items-table :deep(.el-table__header th) {
  background: transparent !important;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
  font-weight: 600;
  padding: 8px 4px !important;
}

.items-table :deep(.el-table__row td) {
  padding: 6px 4px !important;
  background: transparent !important;
}

.items-table :deep(.el-input-number) {
  width: 100% !important;
}

.row-total {
  font-weight: 700;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
  font-size: 13px;
}

.btn-remove-row {
  color: var(--danger) !important;
}
.btn-remove-row:hover {
  background: var(--danger-light) !important;
}

/* Dialog Footer */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-cancel {
  font-weight: 600;
}

.btn-create {
  font-weight: 700;
  padding-left: 20px;
  padding-right: 20px;
}

@media (max-width: 768px) {
  .header-grid {
    grid-template-columns: 1fr;
  }
}
</style>