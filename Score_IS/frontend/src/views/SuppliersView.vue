<template>
  <div class="page-view">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">Поставщики</h1>
        <p class="page-subtitle">Справочник поставщиков</p>
      </div>
      <div class="page-header-actions">
        <el-input v-model="search" placeholder="Поиск" clearable style="width:260px" @input="debounceLoad" />
        <el-button type="primary" @click="openForm">
          <el-icon size="16" style="margin-right:6px"><Plus /></el-icon>
          Добавить
        </el-button>
      </div>
    </div>
    <el-card shadow="never">
      <el-table :data="items" v-loading="loading" style="width:100%">
        <el-table-column prop="name" label="Название" min-width="220" show-overflow-tooltip />
        <el-table-column prop="inn" label="ИНН">
          <template #default="{ row }"><span class="col-nowrap">{{ row.inn }}</span></template>
        </el-table-column>
        <el-table-column prop="contact_phone" label="Телефон">
          <template #default="{ row }"><span class="col-nowrap">{{ row.contact_phone }}</span></template>
        </el-table-column>
        <el-table-column prop="contact_email" label="Email" show-overflow-tooltip />
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
      <el-pagination background layout="prev, pager, next" :total="total" :page-size="perPage" v-model:current-page="page" @current-change="load" style="margin-top:16px" />
    </el-card>

    <!-- Form -->
    <el-dialog v-model="dialogVisible" :title="isEdit?'Редактировать':'Новый поставщик'" width="480">
      <el-form :model="form" ref="formRef" label-width="120px">
        <el-form-item label="Название" required><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="ИНН"><el-input v-model="form.inn" /></el-form-item>
        <el-form-item label="Телефон"><el-input v-model="form.contact_phone" /></el-form-item>
        <el-form-item label="Email"><el-input v-model="form.contact_email" /></el-form-item>
        <el-form-item label="Адрес"><el-input v-model="form.address" type="textarea" rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">Отмена</el-button>
        <el-button type="primary" @click="save">Сохранить</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { referencesApi } from '../api'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'

const items = ref([])
const total = ref(0)
const page = ref(1)
const perPage = ref(10)
const loading = ref(false)
const search = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)
const form = reactive({ id: null, name: '', inn: '', contact_phone: '', contact_email: '', address: '' })

const load = async () => {
  loading.value = true
  const res = await referencesApi.suppliers({ page: page.value, per_page: perPage.value, search: search.value || undefined })
  items.value = res.data.data
  total.value = res.data.total
  loading.value = false
}

let timer
const debounceLoad = () => { clearTimeout(timer); timer = setTimeout(() => { page.value = 1; load() }, 300) }

const openForm = () => { isEdit.value = false; Object.assign(form, { id: null, name: '', inn: '', contact_phone: '', contact_email: '', address: '' }); dialogVisible.value = true }
const edit = (row) => { isEdit.value = true; Object.assign(form, row); dialogVisible.value = true }

const save = async () => {
  try {
    if (isEdit.value) await referencesApi.updateSupplier(form.id, form)
    else await referencesApi.createSupplier(form)
    ElMessage.success('Сохранено')
    dialogVisible.value = false
    load()
  } catch (e) { ElMessage.error(e.response?.data?.message || 'Ошибка') }
}

const remove = async (id) => {
  try { await ElMessageBox.confirm('Удалить?', 'Подтверждение'); await referencesApi.removeSupplier(id); ElMessage.success('Удалено'); load() }
  catch (e) { if (e !== 'cancel') ElMessage.error(e.response?.data?.message || 'Ошибка') }
}

onMounted(load)
</script>

<style scoped>

</style>
