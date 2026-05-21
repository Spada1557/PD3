<template>
  <div class="card">
    <div class="card-header">
      <h4>Категории продукции</h4>
      <el-button type="primary" @click="openCreate" size="default">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:5px"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        Добавить
      </el-button>
    </div>
    <el-table :data="items" v-loading="loading" size="default" style="width:100%">
      <el-table-column prop="name" label="Название" min-width="250" show-overflow-tooltip>
        <template #default="{row}">
          <span :title="row.name">{{ row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="Описание" width="250" show-overflow-tooltip>
        <template #default="{row}"><span style="color:var(--text-muted)" :title="row.description">{{ row.description || '—' }}</span></template>
      </el-table-column>
      <el-table-column label="" width="100" fixed="right">
        <template #default="{row}">
          <div class="flex-row" style="gap:6px">
            <el-button size="small" type="primary" plain @click="editItem(row)" style="font-weight:600">Изм.</el-button>
            <el-popconfirm title="Удалить категорию?" @confirm="delItem(row.id)"><template #reference><el-button size="small" type="danger" plain style="font-weight:600">Уд.</el-button></template></el-popconfirm>
          </div>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="showForm" :title="editing ? 'Редактировать категорию' : 'Новая категория'" width="500px" @closed="resetForm" :close-on-click-modal="false">
      <el-form :model="form" label-width="120px">
        <el-form-item label="Название"><el-input v-model="form.name" maxlength="255" /></el-form-item>
        <el-form-item label="Описание"><el-input v-model="form.description" maxlength="1000" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="showForm=false">Отмена</el-button><el-button type="primary" @click="save">Сохранить</el-button></template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, reactive, onMounted } from 'vue'; import api from '../api/client'; import { ElMessage } from 'element-plus'
const items=ref([]), loading=ref(false), showForm=ref(false), editing=ref(false), editingId=ref(null)
const form=reactive({name:'',description:''})
async function load(){loading.value=true;try{const{data}=await api.get('/categories',{params:{per_page:100}});items.value=data.data}catch(e){}finally{loading.value=false}}
function openCreate(){editing.value=false;editingId.value=null;resetForm();showForm.value=true}
function editItem(r){editing.value=true;editingId.value=r.id;form.name=r.name;form.description=r.description||'';showForm.value=true}
function resetForm(){form.name='';form.description=''}
async function save(){try{if(editing.value){await api.put(`/categories/${editingId.value}`,form)}else{await api.post('/categories',form)}showForm.value=false;ElMessage.success('Сохранено');load()}catch(e){ElMessage.error(e.response?.data?.detail?.message||'')}}
async function delItem(id){try{await api.delete(`/categories/${id}`);ElMessage.success('Удалено');load()}catch(e){ElMessage.error(e.response?.data?.detail?.message||'')}}
onMounted(load)
</script>