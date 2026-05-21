<template>
  <div>
    <div class="toolbar"><h2>Настройки</h2></div>

    <div class="settings-section">
      <h3>Реквизиты предприятия</h3>
      <el-form :model="settings" label-width="200px">
        <el-form-item label="Название компании">
          <el-input v-model="settings.company_name" />
        </el-form-item>
        <el-form-item label="ИНН">
          <el-input v-model="settings.company_inn" />
        </el-form-item>
        <el-form-item label="Адрес">
          <el-input v-model="settings.company_address" type="textarea" />
        </el-form-item>
        <el-form-item label="Телефон">
          <el-input v-model="settings.company_phone" />
        </el-form-item>
        <el-form-item label="Мин. остаток по умолчанию">
          <el-input-number v-model="settings.min_stock_default" :min="0" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveSettings" :loading="saving" style="cursor:pointer">Сохранить</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="settings-section">
      <h3>Подключение к базе данных</h3>
      <el-alert type="warning" :closable="false" style="margin-bottom:16px">
        Изменение строки подключения требует перезапуска сервера. Текущее подключение: SQLite (для локального старта). Для переключения на PostgreSQL используйте формат: postgresql://user:password@host:port/dbname
      </el-alert>
      <el-form :model="settings" label-width="200px">
        <el-form-item label="Строка подключения">
          <el-input v-model="settings.db_connection_string" placeholder="sqlite:///./enamelware.db">
            <template #append>
              <el-button @click="testConnection" :loading="testing" style="cursor:pointer">Проверить</el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveSettings" :loading="saving" style="cursor:pointer">Применить</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="settings-section">
      <h3>Импорт продукции</h3>
      <el-alert type="info" :closable="false" style="margin-bottom:16px">
        Поддерживаются файлы .xlsx и .csv (UTF-8, разделитель ;). Формат: Наименование, Артикул, Категория, Единица, Цена, Себестоимость, Мин. остаток
      </el-alert>
      <el-upload :action="`/api/v1/import/products`" :headers="uploadHeaders" :on-success="onImportSuccess" :on-error="onImportError" accept=".xlsx,.csv" :show-file-list="false">
        <el-button type="primary" style="cursor:pointer">Загрузить файл</el-button>
      </el-upload>
    </div>

    <div class="settings-section">
      <h3>Справочники</h3>
      <div style="display:flex;gap:12px;flex-wrap:wrap">
        <el-card v-for="ref in references" :key="ref.name" shadow="hover" style="min-width:180px;cursor:pointer" @click="$router.push(ref.path)">
          <div style="text-align:center">
            <el-icon :size="28" :color="'var(--primary-light)'"><component :is="ref.icon" /></el-icon>
            <div style="margin-top:8px;font-weight:600;font-size:13px">{{ ref.name }}</div>
            <div style="font-size:11px;color:var(--text-muted);margin-top:2px">{{ ref.count }} записей</div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import { ElMessage } from 'element-plus'

const settings = ref({
  company_name: '', company_inn: '', company_address: '', company_phone: '',
  min_stock_default: 10, db_connection_string: '',
})
const saving = ref(false)
const testing = ref(false)
const references = ref([])

const uploadHeaders = { Authorization: `Bearer ${localStorage.getItem('token')}` }

async function loadSettings() {
  try {
    const res = await api.get('/settings')
    settings.value = res.data
  } catch {}
  const [catRes, unitRes, whRes] = await Promise.all([
    api.get('/categories/all'), api.get('/units/all'), api.get('/warehouses/all'),
  ])
  const cats = Array.isArray(catRes.data) ? catRes.data : catRes.data.data || []
  const units = Array.isArray(unitRes.data) ? unitRes.data : unitRes.data.data || []
  const whs = Array.isArray(whRes.data) ? whRes.data : whRes.data.data || []
  references.value = [
    { name: 'Категории', count: cats.length, icon: 'Menu', path: '/products' },
    { name: 'Единицы', count: units.length, icon: 'Coin', path: '/products' },
    { name: 'Склады', count: whs.length, icon: 'Box', path: '/stock' },
  ]
}

async function saveSettings() {
  saving.value = true
  try {
    await api.put('/settings', settings.value)
    ElMessage.success('Настройки сохранены')
  } catch (e) { ElMessage.error('Ошибка сохранения') }
  finally { saving.value = false }
}

async function testConnection() {
  testing.value = true
  try {
    await api.get('/categories/all')
    ElMessage.success('Подключение успешно')
  } catch { ElMessage.error('Ошибка подключения') }
  finally { testing.value = false }
}

function onImportSuccess(res) {
  ElMessage.success(`Импортировано: ${res.created}. Ошибок: ${res.errors?.length || 0}`)
}
function onImportError() { ElMessage.error('Ошибка импорта') }

onMounted(loadSettings)
</script>