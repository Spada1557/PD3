<template>
  <div>
    <div class="toolbar">
      <el-input v-model="search" placeholder="Поиск поставщика" prefix-icon="Search" clearable style="width:300px" @input="debounceSearch" />
      <el-button type="primary" @click="showDialog = true; editItem = null; resetForm()" style="cursor:pointer">
        <el-icon><Plus /></el-icon> Добавить
      </el-button>
    </div>
    <div class="data-table">
      <el-table :data="suppliers" stripe v-loading="loading">
        <el-table-column prop="name" label="Наименование" min-width="200" />
        <el-table-column prop="inn" label="ИНН" width="140" />
        <el-table-column prop="kpp" label="КПП" width="110" />
        <el-table-column prop="contact_person" label="Контакт" width="180" />
        <el-table-column prop="phone" label="Телефон" width="150" />
        <el-table-column prop="email" label="Email" width="200" />
        <el-table-column label="" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)" style="cursor:pointer">Ред.</el-button>
            <el-button link type="danger" @click="deleteSupplier(row)" style="cursor:pointer">Удал.</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="display:flex;justify-content:flex-end;margin-top:16px">
        <el-pagination v-model:current-page="page" v-model:page-size="perPage" :page-sizes="[10,25,50]" :total="total" layout="total, sizes, prev, pager, next" @current-change="loadSuppliers" @size-change="loadSuppliers" />
      </div>
    </div>

    <el-dialog v-model="showDialog" :title="editItem ? 'Редактировать поставщика' : 'Новый поставщик'" width="550">
      <el-form :model="form" label-width="160px">
        <el-form-item label="Наименование" required><el-input v-model="form.name" maxlength="255" /></el-form-item>
        <el-form-item label="ИНН"><el-input v-model="form.inn" maxlength="12" /></el-form-item>
        <el-form-item label="КПП"><el-input v-model="form.kpp" maxlength="9" /></el-form-item>
        <el-form-item label="Контактное лицо"><el-input v-model="form.contact_person" /></el-form-item>
        <el-form-item label="Телефон"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item label="Email"><el-input v-model="form.email" /></el-form-item>
        <el-form-item label="Адрес"><el-input v-model="form.address" type="textarea" /></el-form-item>
        <el-form-item label="Комментарий"><el-input v-model="form.comment" type="textarea" maxlength="1000" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false" style="cursor:pointer">Отмена</el-button>
        <el-button type="primary" @click="saveSupplier" :loading="saving" style="cursor:pointer">Сохранить</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const suppliers = ref([])
const loading = ref(false)
const page = ref(1)
const perPage = ref(10)
const total = ref(0)
const search = ref('')
const showDialog = ref(false)
const editItem = ref(null)
const saving = ref(false)
const form = ref({ name: '', inn: '', kpp: '', contact_person: '', phone: '', email: '', address: '', comment: '' })

let debounceTimer = null
function debounceSearch() { clearTimeout(debounceTimer); debounceTimer = setTimeout(loadSuppliers, 300) }

function resetForm() {
  form.value = { name: '', inn: '', kpp: '', contact_person: '', phone: '', email: '', address: '', comment: '' }
}

async function loadSuppliers() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: perPage.value }
    if (search.value) params.search = search.value
    const res = await api.get('/suppliers', { params })
    suppliers.value = res.data.data
    total.value = res.data.total
  } finally { loading.value = false }
}

function openEdit(row) {
  editItem.value = row
  form.value = { name: row.name, inn: row.inn || '', kpp: row.kpp || '', contact_person: row.contact_person || '', phone: row.phone || '', email: row.email || '', address: row.address || '', comment: row.comment || '' }
  showDialog.value = true
}

async function saveSupplier() {
  saving.value = true
  try {
    if (editItem.value) {
      await api.put(`/suppliers/${editItem.value.id}`, form.value)
    } else {
      await api.post('/suppliers', form.value)
    }
    ElMessage.success('Сохранено')
    showDialog.value = false
    await loadSuppliers()
  } catch (e) { ElMessage.error(e.response?.data?.detail?.message || 'Ошибка') }
  finally { saving.value = false }
}

async function deleteSupplier(row) {
  await ElMessageBox.confirm(`Удалить поставщика "${row.name}"?`, 'Подтверждение')
  try { await api.delete(`/suppliers/${row.id}`); await loadSuppliers(); ElMessage.success('Удалено') }
  catch (e) { ElMessage.error(e.response?.data?.detail?.message || 'Ошибка') }
}

onMounted(loadSuppliers)
</script>