<template>
  <div class="page-view">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">Пользователи</h1>
        <p class="page-subtitle">Управление учетными записями</p>
      </div>
      <div class="page-header-actions">
        <el-button type="primary" @click="openForm">
          <el-icon size="16" style="margin-right:6px"><Plus /></el-icon>
          Пользователь
        </el-button>
      </div>
    </div>
    <el-card shadow="never">
      <el-table :data="items" v-loading="loading" style="width:100%">
        <el-table-column prop="name" label="Имя" min-width="160" show-overflow-tooltip />
        <el-table-column prop="email" label="Email" show-overflow-tooltip />
        <el-table-column prop="role" label="Роль" />
        <el-table-column prop="status" label="Статус" width="105">
          <template #default="{ row }">
            <el-tag size="small" :type="row.status==='active'?'success':'danger'" class="status-tag">{{ row.status==='active'?'Активен':'Неактивен' }}</el-tag>
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
      <el-pagination background layout="prev, pager, next" :total="total" :page-size="perPage" v-model:current-page="page" @current-change="load" style="margin-top:16px" />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? 'Редактировать' : 'Новый пользователь'" width="480">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="Имя" prop="name"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="Email" prop="email"><el-input v-model="form.email" /></el-form-item>
        <el-form-item label="Пароль" prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="Минимум 6 символов" />
        </el-form-item>
        <el-form-item label="Роль" prop="role">
          <el-select v-model="form.role" style="width:100%">
            <el-option label="Администратор" value="admin" />
            <el-option label="Менеджер" value="manager" />
            <el-option label="Кладовщик" value="warehouse" />
          </el-select>
        </el-form-item>
        <el-form-item label="Статус" prop="status">
          <el-select v-model="form.status" style="width:100%">
            <el-option label="Активен" value="active" />
            <el-option label="Неактивен" value="inactive" />
          </el-select>
        </el-form-item>
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
import { usersApi } from '../api'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'

const items = ref([])
const total = ref(0)
const page = ref(1)
const perPage = ref(10)
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()
const form = reactive({ id: null, name: '', email: '', password: '', role: 'warehouse', status: 'active' })

const rules = {
  name: [{ required: true, message: 'Введите имя' }],
  email: [{ required: true, type: 'email', message: 'Введите email' }],
  role: [{ required: true, message: 'Выберите роль' }],
}

const load = async () => {
  loading.value = true
  const res = await usersApi.list({ page: page.value, per_page: perPage.value })
  items.value = res.data.data
  total.value = res.data.total
  loading.value = false
}

const openForm = () => {
  isEdit.value = false
  Object.assign(form, { id: null, name: '', email: '', password: '', role: 'warehouse', status: 'active' })
  dialogVisible.value = true
}

const edit = (row) => {
  isEdit.value = true
  Object.assign(form, { ...row, password: '' })
  dialogVisible.value = true
}

const save = async () => {
  const ok = await formRef.value.validate().catch(() => false)
  if (!ok) return
  try {
    if (isEdit.value) {
      const data = { ...form }
      if (!data.password) delete data.password
      await usersApi.update(form.id, data)
    } else {
      await usersApi.create({ ...form })
    }
    ElMessage.success('Сохранено')
    dialogVisible.value = false
    load()
  } catch (e) { ElMessage.error(e.response?.data?.message || 'Ошибка') }
}

const remove = async (id) => {
  try {
    await ElMessageBox.confirm('Удалить пользователя?', 'Подтверждение')
    await usersApi.remove(id)
    ElMessage.success('Удалено')
    load()
  } catch (e) { if (e !== 'cancel') ElMessage.error(e.response?.data?.message || 'Ошибка') }
}

onMounted(load)
</script>

<style scoped>

</style>
