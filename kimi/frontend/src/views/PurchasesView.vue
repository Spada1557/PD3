<template>
  <div class="page-view">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">Закупки</h1>
        <p class="page-subtitle">Документы поступления товаров</p>
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
          Новый приход
        </el-button>
      </div>
    </div>
    <el-card shadow="never">
      <el-table :data="items" v-loading="loading" style="width:100%">
        <el-table-column prop="number" label="#"><template #default="{ row }"><span class="col-nowrap">{{ row.number }}</span></template></el-table-column>
        <el-table-column prop="date" label="Дата">
          <template #default="{ row }"><span class="col-nowrap">{{ formatDate(row.date) }}</span></template>
        </el-table-column>
        <el-table-column prop="supplier.name" label="Поставщик" min-width="220" show-overflow-tooltip />
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
                <el-button class="action-btn view-btn" @click="$router.push('/purchases/' + row.id)"><el-icon size="14"><View /></el-icon></el-button>
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

    <!-- Form -->
    <el-dialog v-model="dialogVisible" title="Новый приход" width="720">
      <el-form :model="form" ref="formRef" label-width="100px">
        <el-form-item label="Поставщик" required>
          <el-select v-model="form.supplier_id" filterable style="width:100%">
            <el-option v-for="s in suppliers" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Дата">
          <el-date-picker v-model="form.date" type="datetime" style="width:100%" />
        </el-form-item>
        <el-form-item label="Комментарий">
          <el-input v-model="form.comment" type="textarea" rows="2" />
        </el-form-item>
      </el-form>
      <div class="form-section-header">
        <span class="section-label">Позиции</span>
        <el-button size="small" type="primary" plain @click="addRow">
          <el-icon size="14"><Plus /></el-icon> Добавить
        </el-button>
      </div>
      <el-table :data="form.items" size="small">
        <el-table-column label="Товар" min-width="220">
          <template #default="{ $index }">
            <el-select v-model="form.items[$index].product_id" filterable style="width:100%" @change="fillCost($index)">
              <el-option v-for="p in products" :key="p.id" :label="`${p.article} ${p.name}`" :value="p.id" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="Кол-во" width="90">
          <template #default="{ $index }">
            <el-input-number v-model="form.items[$index].quantity" :min="0.01" :precision="2" style="width:100%" @change="calcRow($index)" />
          </template>
        </el-table-column>
        <el-table-column label="Цена" width="110">
          <template #default="{ $index }">
            <el-input-number v-model="form.items[$index].price" :min="0" :precision="2" style="width:100%" @change="calcRow($index)" />
          </template>
        </el-table-column>
        <el-table-column label="Сумма" width="110">
          <template #default="{ $index }">
            <span class="row-total">{{ formatMoney(form.items[$index].quantity * form.items[$index].price) }}</span>
          </template>
        </el-table-column>
        <el-table-column width="50">
          <template #default="{ $index }">
            <el-button type="danger" text circle @click="removeRow($index)">
              <el-icon size="14"><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="dialogVisible = false">Отмена</el-button>
        <el-button type="primary" @click="save">Сохранить</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { purchasesApi, referencesApi, productsApi } from '../api'
import { Plus, Delete, View, Check } from '@element-plus/icons-vue'

const items = ref([])
const total = ref(0)
const page = ref(1)
const perPage = ref(10)
const loading = ref(false)
const searchNumber = ref('')
const filterStatus = ref('')
const dialogVisible = ref(false)
const suppliers = ref([])
const products = ref([])

const form = reactive({ supplier_id: null, date: null, comment: '', items: [] })

const load = async () => {
  loading.value = true
  const res = await purchasesApi.list({ page: page.value, per_page: perPage.value, status: filterStatus.value || undefined, number: searchNumber.value || undefined })
  items.value = res.data.data
  total.value = res.data.total
  loading.value = false
}

const openForm = () => {
  Object.assign(form, { supplier_id: null, date: new Date(), comment: '', items: [{ product_id: null, quantity: 1, price: 0 }] })
  dialogVisible.value = true
}

const addRow = () => form.items.push({ product_id: null, quantity: 1, price: 0 })
const removeRow = (i) => form.items.splice(i, 1)
const calcRow = (i) => {
  const r = form.items[i]
  r.amount = (r.quantity || 0) * (r.price || 0)
}
const fillCost = (idx) => {
  const pid = form.items[idx].product_id
  const p = products.value.find(x => x.id === pid)
  if (p) form.items[idx].price = p.cost
}

const save = async () => {
  try {
    await purchasesApi.create({ ...form, date: form.date ? new Date(form.date).toISOString() : null })
    ElMessage.success('Сохранено')
    dialogVisible.value = false
    load()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || 'Ошибка')
  }
}

const post = async (id) => {
  try {
    await purchasesApi.post(id)
    ElMessage.success('Проведено')
    load()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || 'Ошибка')
  }
}

const remove = async (id) => {
  try {
    await ElMessageBox.confirm('Удалить документ?', 'Подтверждение')
    await purchasesApi.remove(id)
    ElMessage.success('Удалено')
    load()
  } catch (e) { if (e !== 'cancel') ElMessage.error(e.response?.data?.message || 'Ошибка') }
}

function formatMoney(v) { return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 0 }).format(v) }
function formatDate(d) { return d ? new Date(d).toLocaleDateString('ru-RU') : '' }
function statusTag(s) { return { draft: 'info', posted: 'success', cancelled: 'danger' }[s] || '' }
function statusLabel(s) { return { draft: 'Черновик', posted: 'Проведен', cancelled: 'Отменен' }[s] || s }

onMounted(async () => {
  load()
  const s = await referencesApi.suppliers({ per_page: 1000 })
  suppliers.value = s.data.data
  const p = await productsApi.list({ per_page: 1000 })
  products.value = p.data.data
})
watch([searchNumber, filterStatus], () => { page.value = 1; load() })
</script>

<style scoped>
.section-label {
  font-weight: 700;
  font-size: 14px;
  color: var(--text-primary);
  margin-right: 8px;
}

.form-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 16px 0 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-light);
}

.row-total {
  font-weight: 700;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
  font-size: 13px;
}
</style>
