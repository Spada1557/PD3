<template>
  <div>
    <div class="toolbar">
      <el-button @click="$router.back()" style="cursor:pointer"><el-icon><ArrowLeft /></el-icon> Назад</el-button>
      <h2>{{ isEdit ? 'Редактирование' : 'Новый товар' }}</h2>
    </div>
    <div class="form-card">
      <el-form :model="form" label-width="160px" @submit.prevent="saveProduct">
        <div class="form-grid">
          <el-form-item label="Наименование" required>
            <el-input v-model="form.name" maxlength="255" />
          </el-form-item>
          <el-form-item label="Артикул" required>
            <el-input v-model="form.article" maxlength="20" placeholder="KAS-2L" />
          </el-form-item>
          <el-form-item label="Категория">
            <el-select v-model="form.category_id" clearable placeholder="Выбрать...">
              <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="Единица измерения">
            <el-select v-model="form.unit_id" clearable placeholder="Выбрать...">
              <el-option v-for="u in units" :key="u.id" :label="u.name" :value="u.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="Цена продажи" required>
            <el-input-number v-model="form.price" :min="0" :precision="2" />
          </el-form-item>
          <el-form-item label="Себестоимость">
            <el-input-number v-model="form.cost" :min="0" :precision="2" />
          </el-form-item>
          <el-form-item label="Мин. остаток">
            <el-input-number v-model="form.min_stock" :min="0" />
          </el-form-item>
          <el-form-item label="Статус">
            <el-select v-model="form.status">
              <el-option label="Активен" value="active" />
              <el-option label="Неактивен" value="inactive" />
            </el-select>
          </el-form-item>
        </div>
        <el-form-item label="Фото">
          <el-upload :action="`/api/v1/products/${productId}/image`" :headers="uploadHeaders" :on-success="onUploadSuccess" :before-upload="beforeUpload" accept=".jpg,.jpeg,.png" :show-file-list="false">
            <el-button type="primary" size="small">Загрузить</el-button>
          </el-upload>
          <div v-if="form.image_path" style="margin-top:8px">
            <img :src="`/uploads/${form.image_path}`" style="max-width:200px;border-radius:var(--radius-sm)" />
          </div>
        </el-form-item>
        <el-form-item style="margin-top:24px">
          <el-button type="primary" native-type="submit" :loading="saving" style="cursor:pointer">Сохранить</el-button>
          <el-button @click="$router.back()" style="cursor:pointer">Отмена</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const productId = computed(() => route.params.id !== 'new' ? route.params.id : null)
const isEdit = computed(() => !!productId.value)
const categories = ref([])
const units = ref([])
const saving = ref(false)

const form = ref({
  name: '', article: '', category_id: null, unit_id: null,
  price: 0, cost: 0, min_stock: 10, status: 'active', image_path: null,
})

const uploadHeaders = computed(() => ({ Authorization: `Bearer ${localStorage.getItem('token')}` }))

function beforeUpload(file) {
  if (file.size > 2 * 1024 * 1024) { ElMessage.error('Файл должен быть менее 2МБ'); return false }
  if (!['image/jpeg', 'image/png'].includes(file.type)) { ElMessage.error('Только JPG/PNG'); return false }
  return true
}

function onUploadSuccess(res) {
  form.value.image_path = res.image_path
  ElMessage.success('Фото загружено')
}

async function loadProduct() {
  if (!productId.value) return
  const res = await api.get(`/products/${productId.value}`)
  form.value = res.data
}

async function saveProduct() {
  if (!form.value.name || !form.value.article) { ElMessage.warning('Заполните обязательные поля'); return }
  saving.value = true
  try {
    if (isEdit.value) {
      await api.put(`/products/${productId.value}`, form.value)
    } else {
      await api.post('/products', form.value)
    }
    ElMessage.success('Сохранено')
    router.push('/products')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail?.message || e.response?.data?.message || 'Ошибка сохранения')
  } finally { saving.value = false }
}

onMounted(async () => {
  const [catRes, unitRes] = await Promise.all([api.get('/categories/all'), api.get('/units/all')])
  categories.value = Array.isArray(catRes.data) ? catRes.data : catRes.data.data || []
  units.value = Array.isArray(unitRes.data) ? unitRes.data : unitRes.data.data || []
  if (isEdit.value) await loadProduct()
})
</script>