<template>
  <div>
    <div class="toolbar">
      <h2>Пользователи</h2>
      <el-button type="primary" @click="showDialog = true; editItem = null; resetForm()" style="cursor:pointer">
        <el-icon><Plus /></el-icon> Добавить
      </el-button>
    </div>
    <div class="data-table">
      <el-table :data="users" stripe v-loading="loading">
        <el-table-column prop="name" label="Имя" min-width="180" />
        <el-table-column prop="email" label="Email" width="220" />
        <el-table-column prop="role" label="Роль" width="140">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : row.role === 'manager' ? 'warning' : 'info'" size="small">{{ roleLabel(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Статус" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">{{ row.status === 'active' ? 'Активен' : 'Неактивен' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="Создан" width="170">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)" style="cursor:pointer">Ред.</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="display:flex;justify-content:flex-end;margin-top:16px">
        <el-pagination v-model:current-page="page" v-model:page-size="perPage" :page-sizes="[10,25,50]" :total="total" layout="total, sizes, prev, pager, next" @current-change="loadUsers" @size-change="loadUsers" />
      </div>
    </div>

    <el-dialog v-model="showDialog" :title="editItem ? 'Редактировать пользователя' : 'Новый пользователь'" width="480">
      <el-form :model="form" label-width="120px">
        <el-form-item label="Имя" required><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="Email" required><el-input v-model="form.email" type="email" /></el-form-item>
        <el-form-item label="Пароль" v-if="!editItem" required><el-input v-model="form.password" type="password" show-password /></el-form-item>
        <el-form-item label="Роль">
          <el-select v-model="form.role">
            <el-option label="Администратор" value="admin" />
            <el-option label="Менеджер" value="manager" />
            <el-option label="Кладовщик" value="warehouse" />
          </el-select>
        </el-form-item>
        <el-form-item label="Статус" v-if="editItem">
          <el-select v-model="form.status">
            <el-option label="Активен" value="active" />
            <el-option label="Неактивен" value="inactive" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false" style="cursor:pointer">Отмена</el-button>
        <el-button type="primary" @click="saveUser" :loading="saving" style="cursor:pointer">Сохранить</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import { formatDateTime, roleLabel } from '../utils/format'
import { ElMessage } from 'element-plus'

const users = ref([])
const loading = ref(false)
const page = ref(1)
const perPage = ref(10)
const total = ref(0)
const showDialog = ref(false)
const editItem = ref(null)
const saving = ref(false)
const form = ref({ name: '', email: '', password: '', role: 'manager', status: 'active' })

function resetForm() {
  form.value = { name: '', email: '', password: '', role: 'manager', status: 'active' }
}

async function loadUsers() {
  loading.value = true
  try {
    const res = await api.get('/users', { params: { page: page.value, per_page: perPage.value } })
    users.value = res.data.data
    total.value = res.data.total
  } finally { loading.value = false }
}

function openEdit(row) {
  editItem.value = row
  form.value = { name: row.name, email: row.email, role: row.role, status: row.status }
  showDialog.value = true
}

async function saveUser() {
  saving.value = true
  try {
    if (editItem.value) {
      await api.put(`/users/${editItem.value.id}`, form.value)
    } else {
      await api.post('/users', form.value)
    }
    ElMessage.success('Сохранено')
    showDialog.value = false
    await loadUsers()
  } catch (e) { ElMessage.error(e.response?.data?.detail?.message || 'Ошибка') }
  finally { saving.value = false }
}

onMounted(loadUsers)
</script>