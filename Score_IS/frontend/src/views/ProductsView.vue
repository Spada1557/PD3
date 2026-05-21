<template>
  <div class="page-view">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">Продукция</h1>
        <p class="page-subtitle">Справочник товаров и продукции</p>
      </div>
      <div class="page-header-actions">
        <el-input v-model="search" placeholder="Поиск по названию или артикулу" clearable style="width:280px" @input="debouncedSearch" :prefix-icon="Search" />
        <el-select v-model="filterCategory" placeholder="Категория" clearable style="width:180px">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-button type="primary" @click="openForm">
          <el-icon size="16" style="margin-right:6px"><Plus /></el-icon>
          Добавить
        </el-button>
      </div>
    </div>
    <el-card shadow="never">
      <el-table :data="products" v-loading="loading" style="width:100%">
        <el-table-column prop="article" label="Артикул">
          <template #default="{ row }"><span class="col-nowrap">{{ row.article }}</span></template>
        </el-table-column>
        <el-table-column prop="name" label="Наименование" min-width="200" show-overflow-tooltip />
        <el-table-column :formatter="(r) => r.category?.name" label="Категория">
          <template #default="{ row }"><span class="col-nowrap">{{ row.category?.name }}</span></template>
        </el-table-column>
        <el-table-column :formatter="(r) => r.unit?.name" label="Ед.">
          <template #default="{ row }"><span class="col-nowrap">{{ row.unit?.name }}</span></template>
        </el-table-column>
        <el-table-column prop="price" label="Цена" align="right">
          <template #default="{ row }"><span class="col-nowrap">{{ formatMoney(row.price) }}</span></template>
        </el-table-column>
        <el-table-column prop="cost" label="Себест." align="right">
          <template #default="{ row }"><span class="col-nowrap">{{ formatMoney(row.cost) }}</span></template>
        </el-table-column>
        <el-table-column prop="status" label="Статус" width="105">
          <template #default="{ row }">
            <el-tag size="small" :type="row.status === 'active' ? 'success' : 'info'" class="status-tag">{{ row.status === 'active' ? 'Активен' : 'Неактивен' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="" width="120" align="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-tooltip content="Редактировать" :show-after="300">
                <el-button class="action-btn edit-btn" @click="edit(row)"><el-icon size="14"><Edit /></el-icon></el-button>
              </el-tooltip>
              <el-tooltip content="Удалить" :show-after="300">
                <el-button class="action-btn delete-btn" @click="remove(row.id)"><el-icon size="14"><Delete /></el-icon></el-button>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <div style="display:flex;justify-content:flex-end;margin-top:16px">
        <el-pagination background layout="prev, pager, next" :total="total" :page-size="perPage" v-model:current-page="page" @current-change="load" />
      </div>
    </el-card>

    <!-- Form dialog -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? 'Редактировать продукцию' : 'Новая продукция'" width="520">
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="120px">
        <el-form-item label="Название" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="Артикул" prop="article">
          <el-input v-model="form.article" />
        </el-form-item>
        <el-form-item label="Категория" prop="category_id">
          <el-select v-model="form.category_id" style="width:100%">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Ед. изм." prop="unit_id">
          <el-select v-model="form.unit_id" style="width:100%">
            <el-option v-for="u in units" :key="u.id" :label="u.name" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Цена" prop="price">
          <el-input-number v-model="form.price" :min="0" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="Себестоимость" prop="cost">
          <el-input-number v-model="form.cost" :min="0" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="Мин. запас" prop="min_stock">
          <el-input-number v-model="form.min_stock" :min="0" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="Статус" prop="status">
          <el-select v-model="form.status" style="width:100%">
            <el-option label="Активен" value="active" />
            <el-option label="Неактивен" value="inactive" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Отмена</el-button>
        <el-button type="primary" @click="save">Сохранить</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { productsApi, referencesApi } from '../api'
import { Search, Plus, Edit, Delete } from '@element-plus/icons-vue'

const search = ref('')
const filterCategory = ref(null)
const products = ref([])
const total = ref(0)
const page = ref(1)
const perPage = ref(10)
const loading = ref(false)
const categories = ref([])
const units = ref([])

const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()
const form = reactive({ id: null, name: '', article: '', category_id: null, unit_id: null, price: 0, cost: 0, min_stock: 0, status: 'active' })

const formRules = {
  name: [{ required: true, message: 'Введите название' }],
  article: [{ required: true, message: 'Введите артикул' }],
  category_id: [{ required: true, message: 'Выберите категорию' }],
  unit_id: [{ required: true, message: 'Выберите единицу' }],
}

const load = async () => {
  loading.value = true
  try {
    const res = await productsApi.list({
      page: page.value,
      per_page: perPage.value,
      search: search.value || undefined,
      category_id: filterCategory.value || undefined,
    })
    products.value = res.data.data
    total.value = res.data.total
  } catch (e) {
    ElMessage.error(e.response?.data?.message || 'Ошибка загрузки')
  } finally {
    loading.value = false
  }
}

let timeout
const debouncedSearch = () => {
  clearTimeout(timeout)
  timeout = setTimeout(() => { page.value = 1; load() }, 300)
}

const openForm = () => {
  isEdit.value = false
  Object.assign(form, { id: null, name: '', article: '', category_id: null, unit_id: null, price: 0, cost: 0, min_stock: 0, status: 'active' })
  dialogVisible.value = true
}

const edit = (row) => {
  isEdit.value = true
  Object.assign(form, {
    id: row.id,
    name: row.name,
    article: row.article,
    category_id: row.category_id,
    unit_id: row.unit_id,
    price: row.price,
    cost: row.cost,
    min_stock: row.min_stock,
    status: row.status,
  })
  dialogVisible.value = true
}

const save = async () => {
  const ok = await formRef.value.validate().catch(() => false)
  if (!ok) return
  try {
    const data = {
      name: form.name,
      article: form.article,
      category_id: form.category_id,
      unit_id: form.unit_id,
      price: form.price,
      cost: form.cost,
      min_stock: form.min_stock,
      status: form.status,
    }
    if (isEdit.value) {
      await productsApi.update(form.id, data)
    } else {
      await productsApi.create(data)
    }
    ElMessage.success('Сохранено')
    dialogVisible.value = false
    load()
  } catch (e) {
    const detail = e.response?.data?.detail
    let msg
    if (Array.isArray(detail)) {
      msg = detail.map(d => `${d.loc?.join('.') || ''}: ${d.msg}`).join('; ')
    } else if (typeof detail === 'string') {
      msg = detail
    } else {
      msg = e.response?.data?.message || 'Ошибка сохранения'
    }
    ElMessage.error(msg)
  }
}

const remove = async (id) => {
  try {
    await ElMessageBox.confirm('Удалить продукцию?', 'Подтверждение')
    await productsApi.remove(id)
    ElMessage.success('Удалено')
    load()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.message || 'Ошибка удаления')
    }
  }
}

const loadReferences = async () => {
  const [cats, un] = await Promise.all([referencesApi.categories(), referencesApi.units()])
  categories.value = cats.data
  units.value = un.data
}

function formatMoney(v) {
  return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 0 }).format(v)
}

onMounted(() => { load(); loadReferences() })
watch(filterCategory, () => { page.value = 1; load() })
</script>

<style scoped>

</style>
