<template>
  <div class="page-view">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">Справочники</h1>
        <p class="page-subtitle">Категории, единицы измерения и склады</p>
      </div>
    </div>
    <el-tabs type="border-card">
      <el-tab-pane label="Категории">
        <div class="toolbar">
          <el-button type="primary" @click="addCategory">
            <el-icon size="16" style="margin-right:6px"><Plus /></el-icon>
            Категория
          </el-button>
        </div>
        <el-table :data="categories" size="small">
          <el-table-column prop="name" label="Название" />
          <el-table-column>
            <template #default="{ }">
              <el-button link disabled />
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="Ед. изм.">
        <div class="toolbar">
          <el-button type="primary" @click="addUnit">
            <el-icon size="16" style="margin-right:6px"><Plus /></el-icon>
            Единица
          </el-button>
        </div>
        <el-table :data="units" size="small">
          <el-table-column prop="name" label="Название" />
          <el-table-column width="100">
            <template #default="{ row }">
              <el-button text type="danger" @click="delUnit(row.id)">Удал.</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="Склады">
        <div class="toolbar">
          <el-button type="primary" @click="addWarehouse">
            <el-icon size="16" style="margin-right:6px"><Plus /></el-icon>
            Склад
          </el-button>
        </div>
        <el-table :data="warehouses" size="small">
          <el-table-column prop="name" label="Название" />
          <el-table-column prop="is_default" label="По умолчанию">
            <template #default="{ row }">
              <el-tag :type="row.is_default ? 'success' : 'info'">{{ row.is_default ? 'Да' : 'Нет' }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- Small dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="360">
      <el-form :model="form" ref="formRef">
        <el-form-item label="Название" required>
          <el-input v-model="form.name" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">Отмена</el-button>
        <el-button type="primary" @click="saveDialog">Сохранить</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { referencesApi } from '../api'
import { Plus } from '@element-plus/icons-vue'

const categories = ref([])
const units = ref([])
const warehouses = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const dialogType = ref('')
const form = reactive({ name: '' })

const load = async () => {
  const [c, u, w] = await Promise.all([
    referencesApi.categories(),
    referencesApi.units(),
    referencesApi.warehouses(),
  ])
  categories.value = c.data
  units.value = u.data
  warehouses.value = w.data
}

const addCategory = () => { dialogType.value = 'category'; dialogTitle.value = 'Новая категория'; form.name = ''; dialogVisible.value = true }
const addUnit = () => { dialogType.value = 'unit'; dialogTitle.value = 'Новая ед. изм.'; form.name = ''; dialogVisible.value = true }
const addWarehouse = () => { dialogType.value = 'warehouse'; dialogTitle.value = 'Новый склад'; form.name = ''; dialogVisible.value = true }

const saveDialog = async () => {
  try {
    if (dialogType.value === 'category') await referencesApi.createCategory(form)
    if (dialogType.value === 'unit') await referencesApi.createUnit(form)
    if (dialogType.value === 'warehouse') await referencesApi.createWarehouse({ ...form, is_default: 0 })
    dialogVisible.value = false
    ElMessage.success('Сохранено')
    load()
  } catch (e) { ElMessage.error(e.response?.data?.message || 'Ошибка') }
}

const delCategory = async (id) => {
  try { await ElMessageBox.confirm('Удалить категорию?');
    await referencesApi.api?.delete(`/references/categories/${id}`)
    ElMessage.success('Удалено'); load()
  } catch (e) { if (e !== 'cancel') ElMessage.error('Ошибка удаления') }
}

onMounted(load)
</script>

<style scoped>
.toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 14px;
  align-items: center;
}
</style>
