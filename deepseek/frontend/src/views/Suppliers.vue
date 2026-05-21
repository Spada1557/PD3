<template>
  <div class="card">
    <div class="table-actions">
      <el-input v-model="search" placeholder="Поиск по названию, ИНН..." class="search-input" clearable @input="onSearch">
        <template #prefix>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        </template>
      </el-input>
      <el-button type="primary" @click="openCreate" style="margin-left:auto">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:5px"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        Добавить
      </el-button>
    </div>
    <el-table :data="items" v-loading="loading" size="default" style="width:100%">
      <el-table-column prop="name" label="Название" min-width="200" show-overflow-tooltip>
        <template #default="{row}">
          <span :title="row.name">{{ row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="inn" label="ИНН" width="140">
        <template #default="{row}"><code style="background:var(--bg-surface);padding:2px 8px;border-radius:4px;font-weight:600;white-space:nowrap">{{ row.inn || '—' }}</code></template>
      </el-table-column>
      <el-table-column prop="contact_person" label="Конт.лицо" width="130" show-overflow-tooltip>
        <template #default="{row}"><span :style="{ color: row.contact_person ? 'var(--text-primary)' : 'var(--text-muted)' }">{{ row.contact_person || '—' }}</span></template>
      </el-table-column>
      <el-table-column prop="phone" label="Телефон" width="160">
        <template #default="{row}"><span style="white-space:nowrap">{{ row.phone || '—' }}</span></template>
      </el-table-column>
      <el-table-column prop="email" label="Email" width="200" show-overflow-tooltip>
        <template #default="{row}"><span style="color:var(--accent);font-weight:500">{{ row.email || '—' }}</span></template>
      </el-table-column>
      <el-table-column prop="status" label="Статус" width="140" align="center">
        <template #default="{row}"><el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small" effect="plain">{{ row.status === 'active' ? 'Активен' : 'Неактивен' }}</el-tag></template>
      </el-table-column>
      <el-table-column label="" width="100" fixed="right">
        <template #default="{row}">
          <div class="flex-row" style="gap:6px">
            <el-button size="small" type="primary" plain @click="editItem(row)" style="font-weight:600">Изм.</el-button>
            <el-popconfirm title="Деактивировать?" @confirm="delItem(row.id)"><template #reference><el-button size="small" type="danger" plain style="font-weight:600">Уд.</el-button></template></el-popconfirm>
          </div>
        </template>
      </el-table-column>
    </el-table>
    <div class="flex-row mt-20" style="justify-content:flex-end"><el-pagination v-model:current-page="page" :page-size="perPage" :total="total" @current-change="load" layout="prev, pager, next, total" /></div>
    <el-dialog v-model="showForm" :title="editing?'Редактировать поставщика':'Новый поставщик'" width="560px" @closed="resetForm" :close-on-click-modal="false">
      <el-form :model="form" label-width="140px">
        <el-form-item label="Название"><el-input v-model="form.name" maxlength="255"/></el-form-item>
        <div class="form-row">
          <el-form-item label="ИНН"><el-input v-model="form.inn" maxlength="12"/></el-form-item>
          <el-form-item label="КПП"><el-input v-model="form.kpp" maxlength="9"/></el-form-item>
        </div>
        <el-form-item label="Контактное лицо"><el-input v-model="form.contact_person" maxlength="255"/></el-form-item>
        <div class="form-row">
          <el-form-item label="Телефон"><el-input v-model="form.phone" maxlength="50"/></el-form-item>
          <el-form-item label="Email"><el-input v-model="form.email" maxlength="255"/></el-form-item>
        </div>
        <el-form-item label="Адрес"><el-input v-model="form.address" maxlength="500" type="textarea" :rows="2"/></el-form-item>
      </el-form>
      <template #footer><el-button @click="showForm=false">Отмена</el-button><el-button type="primary" @click="save">Сохранить</el-button></template>
    </el-dialog>
  </div>
</template>
<script setup>
import {ref,reactive,onMounted} from 'vue';import api from '../api/client';import {ElMessage} from 'element-plus';import {debounce} from '../utils/format'
const items=ref([]),loading=ref(false),page=ref(1),perPage=ref(10),total=ref(0),search=ref('')
const showForm=ref(false),editing=ref(false),editingId=ref(null)
const form=reactive({name:'',inn:'',kpp:'',contact_person:'',phone:'',email:'',address:''})
async function load(){loading.value=true;try{const{data}=await api.get('/suppliers',{params:{page:page.value,per_page:perPage.value,search:search.value}});items.value=data.data;total.value=data.total}catch(e){}finally{loading.value=false}}
const onSearch=debounce(()=>{page.value=1;load()},300)
function openCreate(){editing.value=false;resetForm();showForm.value=true}
function editItem(r){editing.value=true;editingId.value=r.id;Object.assign(form,r);showForm.value=true}
function resetForm(){Object.assign(form,{name:'',inn:'',kpp:'',contact_person:'',phone:'',email:'',address:''})}
async function save(){try{if(editing.value){await api.put(`/suppliers/${editingId.value}`,form)}else{await api.post('/suppliers',form)}showForm.value=false;ElMessage.success('Сохранено');load()}catch(e){ElMessage.error(e.response?.data?.detail?.message||'')}}
async function delItem(id){try{await api.delete(`/suppliers/${id}`);ElMessage.success('Деактивирован');load()}catch(e){ElMessage.error(e.response?.data?.detail?.message||'')}}
onMounted(load)
</script>