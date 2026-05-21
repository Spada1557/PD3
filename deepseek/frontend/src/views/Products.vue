<template>
  <div>
    <div class="card">
      <div class="table-actions">
        <el-input v-model="search" placeholder="Поиск по названию или артикулу..." class="search-input" clearable @input="onSearch">
          <template #prefix>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          </template>
        </el-input>
        <el-select v-model="filterCategory" placeholder="Все категории" clearable style="width:190px" @change="load">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="Все статусы" clearable style="width:160px" @change="load">
          <el-option label="Активные" value="active" />
          <el-option label="Архив" value="inactive" />
        </el-select>
        <div style="margin-left:auto;display:flex;gap:8px">
          <el-button type="primary" @click="showCreate = true; editingProduct = null">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:5px"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            Добавить товар
          </el-button>
          <el-upload :before-upload="handleImport" :show-file-list="false" accept=".xlsx,.csv">
            <el-button>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:5px"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
              Импорт Excel
            </el-button>
          </el-upload>
        </div>
      </div>

      <el-table :data="products" v-loading="loading" size="default" style="width:100%">
        <el-table-column prop="name" label="Наименование" min-width="150" show-overflow-tooltip>
          <template #default="{row}">
            <span :title="row.name">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="article" label="Артикул" width="150" align="center">
          <template #default="{row}"><code style="font-size:12px;background:var(--bg-surface);padding:2px 8px;border-radius:4px;color:var(--text-secondary);font-weight:600;white-space:nowrap">{{ row.article || '—' }}</code></template>
        </el-table-column>
        <el-table-column label="Категория" width="160" align="center">
          <template #default="{row}"><el-tag size="small" type="info" effect="plain" style="white-space:nowrap">{{ row.category?.name }}</el-tag></template>
        </el-table-column>
        <el-table-column label="Цена" width="150" align="right">
          <template #default="{row}"><span class="amount" style="color:var(--text-primary);white-space:nowrap">{{ formatCurrency(row.price) }}</span></template>
        </el-table-column>
        <el-table-column label="Себест." width="150" align="right">
          <template #default="{row}"><span style="color:var(--text-muted);font-weight:600;white-space:nowrap">{{ formatCurrency(row.cost) }}</span></template>
        </el-table-column>
        <el-table-column prop="min_stock" label="Мин.ост." width="140" align="center" />
        <el-table-column prop="status" label="Статус" width="140" align="center">
          <template #default="{row}"><el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">{{ row.status === 'active' ? 'Активен' : 'Архив' }}</el-tag></template>
        </el-table-column>
        <el-table-column label="" width="100" fixed="right">
          <template #default="{row}">
            <div class="flex-row" style="gap:6px">
              <el-button size="small" type="primary" plain @click="editProduct(row)" style="font-weight:600">Изм.</el-button>
              <el-popconfirm title="Удалить товар?" @confirm="deleteProduct(row.id)">
                <template #reference><el-button size="small" type="danger" plain style="font-weight:600">Уд.</el-button></template>
              </el-popconfirm>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <div class="flex-row mt-20" style="justify-content:flex-end">
        <el-pagination v-model:current-page="page" :page-size="perPage" :total="total" @current-change="load" layout="prev, pager, next, total" />
      </div>
    </div>

    <el-dialog v-model="showCreate" :title="editingProduct ? 'Редактировать товар' : 'Новый товар'" width="600px" @closed="resetForm" :close-on-click-modal="false">
      <el-form :model="form" label-width="140px" class="product-form">
        <el-form-item label="Наименование"><el-input v-model="form.name" maxlength="255" /></el-form-item>
        <el-form-item label="Артикул"><el-input v-model="form.article" maxlength="20" /></el-form-item>
        <div class="form-row">
          <el-form-item label="Категория"><el-select v-model="form.category_id" style="width:100%" :teleported="false"><el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" /></el-select></el-form-item>
          <el-form-item label="Ед. измерения"><el-select v-model="form.unit_id" style="width:100%" :teleported="false"><el-option v-for="u in units" :key="u.id" :label="u.name" :value="u.id" /></el-select></el-form-item>
        </div>
        <div class="form-row">
          <el-form-item label="Цена (₽)"><el-input-number v-model="form.price" :min="0" :precision="2" style="width:100%" /></el-form-item>
          <el-form-item label="Себестоимость (₽)"><el-input-number v-model="form.cost" :min="0" :precision="2" style="width:100%" /></el-form-item>
        </div>
        <el-form-item label="Мин. остаток"><el-input-number v-model="form.min_stock" :min="0" :precision="0" style="width:100%" /></el-form-item>
        <el-form-item label="Описание"><el-input v-model="form.description" maxlength="1000" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">Отмена</el-button>
        <el-button type="primary" @click="saveProduct" :loading="saving">{{ editingProduct ? 'Сохранить изменения' : 'Создать товар' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../api/client'
import { formatCurrency, debounce } from '../utils/format'
import { ElMessage } from 'element-plus'

const products = ref([])
const categories = ref([])
const units = ref([])
const loading = ref(false)
const saving = ref(false)
const page = ref(1)
const perPage = ref(10)
const total = ref(0)
const search = ref('')
const filterCategory = ref(null)
const filterStatus = ref(null)
const showCreate = ref(false)
const editingProduct = ref(null)
const form = reactive({ name: '', article: '', category_id: null, unit_id: null, price: 0, cost: 0, min_stock: 10, description: '' })

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: perPage.value }
    if (search.value) params.search = search.value
    if (filterCategory.value) params.category_id = filterCategory.value
    if (filterStatus.value) params.status = filterStatus.value
    const { data } = await api.get('/products', { params })
    products.value = data.data
    total.value = data.total
  } catch (e) { ElMessage.error('Ошибка загрузки') } finally { loading.value = false }
}

const onSearch = debounce(() => { page.value = 1; load() }, 300)

async function loadRefs() {
  const [cat, un] = await Promise.all([api.get('/categories', { params: { per_page: 100 } }), api.get('/units', { params: { per_page: 100 } })])
  categories.value = cat.data.data
  units.value = un.data.data
}

function editProduct(p) {
  editingProduct.value = p
  Object.assign(form, { name: p.name, article: p.article || '', category_id: p.category_id, unit_id: p.unit_id, price: p.price, cost: p.cost, min_stock: p.min_stock, description: p.description || '' })
  showCreate.value = true
}

function resetForm() {
  editingProduct.value = null
  Object.assign(form, { name: '', article: '', category_id: null, unit_id: null, price: 0, cost: 0, min_stock: 10, description: '' })
}

async function saveProduct() {
  saving.value = true
  try {
    if (editingProduct.value) {
      await api.put(`/products/${editingProduct.value.id}`, form)
    } else {
      await api.post('/products', form)
    }
    showCreate.value = false
    ElMessage.success('Сохранено')
    load()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail?.message || 'Ошибка')
  } finally { saving.value = false }
}

async function deleteProduct(id) {
  try {
    await api.delete(`/products/${id}`)
    ElMessage.success('Удалено')
    load()
  } catch (e) { ElMessage.error(e.response?.data?.detail?.message || 'Ошибка удаления') }
}

async function handleImport(file) {
  const fd = new FormData()
  fd.append('file', file)
  try {
    const { data } = await api.post('/products/import', fd)
    ElMessage.success(`Импортировано: ${data.imported}`)
    if (data.errors.length) ElMessage.warning(`Ошибок: ${data.errors.length}`)
    load()
  } catch (e) { ElMessage.error('Ошибка импорта') }
  return false
}

onMounted(() => { loadRefs(); load() })
</script>

<style scoped>
.product-form .el-form-item { margin-bottom: 18px; }
</style>