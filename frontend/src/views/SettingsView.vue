<template>
  <div class="page-view">
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">Настройки</h1>
        <p class="page-subtitle">Глобальные параметры системы</p>
      </div>
    </div>
    <el-card class="settings-card" shadow="never">
      <template #header>
        <div class="settings-title">Настройки системы</div>
      </template>
      <el-form :model="form" label-width="200px">
        <el-divider content-position="left">Глобальные реквизиты предприятия</el-divider>
        <el-form-item label="Название предприятия">
          <el-input v-model="form.company_name" placeholder="ООО Эмалированная посуда" />
        </el-form-item>
        <el-form-item label="ИНН">
          <el-input v-model="form.company_inn" placeholder="1234567890" />
        </el-form-item>
        <el-form-item label="КПП">
          <el-input v-model="form.company_kpp" placeholder="123456789" />
        </el-form-item>
        <el-form-item label="Адрес">
          <el-input v-model="form.company_address" placeholder="г. Москва, ул. Примерная, 1" />
        </el-form-item>
        <el-form-item label="Телефон">
          <el-input v-model="form.company_phone" placeholder="+7 (495) 000-00-00" />
        </el-form-item>
        <el-form-item label="Email">
          <el-input v-model="form.company_email" placeholder="info@example.com" />
        </el-form-item>

        <el-divider content-position="left">Склад и запасы</el-divider>
        <el-form-item label="Мин. запас по умолчанию">
          <el-input-number v-model="form.default_min_stock" :min="0" :precision="2" style="width:100%" />
        </el-form-item>

        <el-divider content-position="left">Подключение к базе данных</el-divider>
        <div style="color:var(--text-muted); font-size:12px; margin-bottom:10px; padding-left:40px">
          Изменение строки подключения требует перезагрузки сервиса. Для миграции на PostgreSQL укажите строку вида: postgresql://user:password@host:5432/dbname
        </div>
        <el-form-item label="Строка подключения">
          <el-input v-model="form.db_url" placeholder="sqlite:///./app.db" />
        </el-form-item>

        <div style="display:flex; justify-content:flex-end">
          <el-button type="primary" @click="save">
            <el-icon size="16" style="margin-right:6px"><Check /></el-icon>
            Сохранить настройки
          </el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { settingsApi } from '../api'
import { Check } from '@element-plus/icons-vue'

const form = reactive({ company_name: '', company_inn: '', company_kpp: '', company_address: '', company_phone: '', company_email: '', default_min_stock: 0, db_url: '' })

const load = async () => {
  const res = await settingsApi.get()
  Object.assign(form, res.data)
}

const save = async () => {
  try {
    await settingsApi.update({ ...form })
    ElMessage.success('Настройки сохранены')
  } catch (e) { ElMessage.error(e.response?.data?.message || 'Ошибка') }
}

onMounted(load)
</script>

<style scoped>
.settings-card {
  border-radius: var(--radius-lg);
}
.settings-title {
  font-size: 18px;
  font-weight: 800;
  letter-spacing: -0.2px;
}
</style>
