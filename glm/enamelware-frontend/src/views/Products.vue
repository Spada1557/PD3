<template>
  <div>
    <div class="toolbar">
      <div class="toolbar-left">
        <el-input v-model="search" placeholder="Поиск по названию/артикулу" prefix-icon="Search" clearable style="width:300px" @input="debounceSearch" />
        <el-select v-model="filters.category" placeholder="Категория" clearable @change="loadProducts" style="width:180px">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-select v-model="filters.status" placeholder="Статус" clearable @change="loadProducts" style="width:140px">
          <el-option label="Активен" value="active" />
          <el-option label="Неактивен" value="inactive" />
        </el-select>
      </div>
      <el-button type="primary" @click="$router.push('/products/new')" style="cursor:pointer">
        <el-icon><Plus /></el-icon> Добавить
      </el-button>
    </div>

    <div class="data-table">
      <el-table :data="products" stripe v-loading="loading" @sort-change="handleSort">
        <el-table-column prop="article" label="Артикул" width="120" sortable />
        <el-table-column prop="name" label="Наименование" min-width="200" />
        <el-table-column prop="price" label="Цена" width="120" sortable>
          <template #default="{ row }">{{ formatCurrency(row.price) }}</template>
        </el-table-column>
        <el-table-column prop="cost" label="Себестоимость" width="130">
          <template #default="{ row }">{{ formatCurrency(row.cost) }}</template>
        </el-table-column>
        <el-table-column prop="min_stock" label="Мин. остаток" width="120" />
        <el-table-column prop="status" label="Статус" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status).type" size="small" effect="dark">{{ statusTag(row.status).label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="$router.push(`/products/${row.id}`)" style="cursor:pointer">Ред.</el-button>
            <el-button link type="danger" @click="deleteProduct(row)" style="cursor:pointer">Удал.</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="display:flex;justify-content:flex-end;margin-top:16px">
        <el-pagination v-model:current-page="page" v-model:page-size="perPage" :page-sizes="[10,25,50]" :total="total" layout="total, sizes, prev, pager, next" @current-change="loadProducts" @size-change="loadProducts" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import { formatCurrency, statusTag } from '../utils/format'
import { ElMessage } from 'element-plus'

const router = useRouter()
const products = ref([])
const categories = ref([])
const loading = ref(false)
const search = ref('')
const page = ref(1)
const perPage = ref(10)
const total = ref(0)
const filters = ref({ category: null, status: null })
let debounceTimer = null

function debounceSearch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => { page.value = 1; loadProducts() }, 300)
}

async function loadProducts() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: perPage.value }
    if (search.value) params.search = search.value
    if (filters.value.category) params.category = filters.value.category
    if (filters.value.status) params.status = filters.value.status
    const res = await api.get('/products', { params })
    products.value = res.data.data
    total.value = res.data.total
  } finally { loading.value = false }
}

async function loadCategories() {
  const res = await api.get('/categories/all')
  categories.value = Array.isArray(res.data) ? res.data : res.data.data
}

async function deleteProduct(row) {
  try {
    await api.delete(`/products/${row.id}`)
    await loadProducts()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || 'Ошибка удаления')
  }
}

function handleSort({ prop, order }) {
  page.value = 1
  loadProducts()
}

onMounted(() => { loadProducts(); loadCategories() })
</script>