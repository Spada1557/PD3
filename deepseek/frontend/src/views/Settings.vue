<template>
  <div>
    <div class="grid-2">
      <div class="card">
        <div class="card-header"><h4>Реквизиты предприятия</h4></div>
        <el-form :model="company" label-width="180px">
          <el-form-item v-for="field in companyFields" :key="field.key" :label="field.label">
            <el-input v-model="company[field.key]" :maxlength="field.max || 255" />
          </el-form-item>
          <el-form-item><el-button type="primary" @click="saveCompany">Сохранить реквизиты</el-button></el-form-item>
        </el-form>
      </div>
      <div class="card">
        <div class="card-header"><h4>Общие настройки</h4></div>
        <el-form label-width="220px">
          <el-form-item label="Мин. остаток по умолчанию">
            <el-input-number v-model="defaultMinStock" :min="1" style="width:200px" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveDefaultMinStock">Сохранить</el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <div class="card mb-24">
      <div class="card-header">
        <h4>Настройка подключения к базе данных</h4>
        <el-tag :type="dbStatus === 'connected' ? 'success' : dbStatus === 'error' ? 'danger' : 'info'" size="small">{{ dbStatusText || 'Не проверено' }}</el-tag>
      </div>
      <el-form label-width="240px">
        <el-form-item label="Текущая БД">
          <el-input :model-value="currentDbUrl" disabled />
        </el-form-item>
        <el-form-item label="Новая строка подключения">
          <el-input v-model="dbUrl" placeholder="sqlite:///./db/warehouse.db или postgresql://user:pass@host:5432/dbname" style="width:100%" />
        </el-form-item>
        <el-form-item>
          <div class="flex-row" style="gap:12px">
            <el-button type="default" @click="testConnection" :loading="testing" :disabled="!dbUrl">Проверить подключение</el-button>
            <el-button type="warning" @click="switchDatabase" :loading="switching" :disabled="!dbUrl">Переключить БД</el-button>
          </div>
        </el-form-item>
        <el-alert title="Внимание" type="warning" description="После переключения потребуется перезапуск сервера. Текущие данные не мигрируются автоматически." show-icon :closable="false" style="margin-top:12px" />
      </el-form>
    </div>

    <div class="card">
      <div class="card-header"><h4>Все параметры системы</h4></div>
      <el-table :data="settingsList" size="default">
        <el-table-column prop="key" label="Ключ" width="300" />
        <el-table-column prop="value" label="Значение" min-width="220" />
        <el-table-column prop="description" label="Описание" min-width="280" />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../api/client'
import { ElMessage } from 'element-plus'

const company = reactive({
  company_name: '', company_inn: '', company_kpp: '',
  company_address: '', company_phone: '', company_email: '',
})
const companyFields = [
  { key: 'company_name', label: 'Наименование', max: 255 },
  { key: 'company_inn', label: 'ИНН', max: 12 },
  { key: 'company_kpp', label: 'КПП', max: 9 },
  { key: 'company_address', label: 'Юридический адрес', max: 500 },
  { key: 'company_phone', label: 'Телефон', max: 50 },
  { key: 'company_email', label: 'Email', max: 255 },
]
const defaultMinStock = ref(10)
const dbUrl = ref('')
const currentDbUrl = ref('')
const dbStatus = ref('')
const dbStatusText = ref('')
const testing = ref(false)
const switching = ref(false)
const settingsList = ref([])

async function loadSettings() {
  try {
    const { data } = await api.get('/settings')
    const all = data.data
    for (const f of companyFields) {
      if (all[f.key] !== undefined) company[f.key] = all[f.key]
    }
    if (all.default_min_stock) defaultMinStock.value = parseInt(all.default_min_stock) || 10
    currentDbUrl.value = all.current_database_url || '—'

    settingsList.value = Object.entries(all)
      .filter(([k]) => !k.startsWith('current_'))
      .map(([key, value]) => ({ key, value, description: '' }))
  } catch (e) { /* ignore */ }
}

async function saveCompany() {
  try {
    const payload = {}
    for (const f of companyFields) payload[f.key] = company[f.key]
    await api.put('/settings/batch', payload)
    ElMessage.success('Реквизиты сохранены')
  } catch (e) { ElMessage.error('Ошибка сохранения') }
}

async function saveDefaultMinStock() {
  try {
    await api.put('/settings', { key: 'default_min_stock', value: String(defaultMinStock.value) })
    ElMessage.success('Сохранено')
  } catch (e) { ElMessage.error('Ошибка') }
}

async function testConnection() {
  if (!dbUrl.value) { ElMessage.warning('Введите строку подключения'); return }
  testing.value = true
  try {
    await api.post('/settings/database/test', { database_url: dbUrl.value })
    dbStatus.value = 'connected'
    dbStatusText.value = 'Подключение успешно'
    ElMessage.success('Подключение успешно')
  } catch (e) {
    dbStatus.value = 'error'
    dbStatusText.value = 'Ошибка подключения'
    ElMessage.error(e.response?.data?.detail?.message || 'Ошибка')
  } finally { testing.value = false }
}

async function switchDatabase() {
  if (!dbUrl.value) return
  switching.value = true
  try {
    await api.post('/settings/database/switch', { database_url: dbUrl.value })
    ElMessage.success('Строка подключения обновлена. Перезапустите сервер.')
    currentDbUrl.value = dbUrl.value
  } catch (e) {
    ElMessage.error(e.response?.data?.detail?.message || 'Ошибка')
  } finally { switching.value = false }
}

onMounted(loadSettings)
</script>