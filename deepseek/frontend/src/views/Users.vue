<template>
  <div class="card">
    <div class="table-actions">
      <el-select v-model="filterRole" placeholder="Все роли" clearable style="width:170px" @change="load"><el-option label="Admin" value="admin" /><el-option label="Manager" value="manager" /><el-option label="Warehouse" value="warehouse" /></el-select>
      <el-select v-model="filterStatus" placeholder="Все статусы" clearable style="width:170px" @change="load"><el-option label="Активные" value="active" /><el-option label="Неактивные" value="inactive" /></el-select>
      <el-button type="primary" @click="openCreate" style="margin-left:auto">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:5px"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        Добавить пользователя
      </el-button>
    </div>
    <el-table :data="items" v-loading="loading" size="default" style="width:100%">
      <el-table-column prop="name" label="Имя" min-width="250" show-overflow-tooltip>
        <template #default="{row}">
          <span :title="row.name">{{ row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="email" label="Email" width="180" show-overflow-tooltip>
        <template #default="{row}"><span style="color:var(--text-secondary);font-weight:500">{{ row.email }}</span></template>
      </el-table-column>
      <el-table-column prop="role" label="Роль" width="140" align="center">
        <template #default="{row}"><el-tag :type="row.role === 'admin' ? '' : row.role === 'manager' ? 'success' : 'warning'" size="small" effect="plain">{{ roleLabel(row.role) }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="status" label="Статус" width="140" align="center">
        <template #default="{row}"><el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small" effect="plain">{{ row.status === 'active' ? 'Активен' : 'Неактивен' }}</el-tag></template>
      </el-table-column>
      <el-table-column label="Создан" width="130">
        <template #default="{row}">{{ formatDate(row.created_at) }}</template>
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
    <el-dialog v-model="showForm" :title="editing?'Редактировать пользователя':'Новый пользователь'" width="500px" @closed="resetForm" :close-on-click-modal="false">
      <el-form :model="form" label-width="130px">
        <el-form-item label="Имя"><el-input v-model="form.name" maxlength="255" /></el-form-item>
        <el-form-item label="Email"><el-input v-model="form.email" maxlength="255" /></el-form-item>
        <el-form-item label="Пароль"><el-input v-model="form.password" type="password" maxlength="100" :placeholder="editing ? 'Оставьте пустым' : 'Введите пароль'" /></el-form-item>
        <el-form-item label="Роль"><el-select v-model="form.role" style="width:100%" :teleported="false"><el-option label="Admin" value="admin" /><el-option label="Manager" value="manager" /><el-option label="Warehouse" value="warehouse" /></el-select></el-form-item>
        <el-form-item label="Статус"><el-select v-model="form.status" style="width:100%" :teleported="false"><el-option label="Активен" value="active" /><el-option label="Неактивен" value="inactive" /></el-select></el-form-item>
      </el-form>
      <template #footer><el-button @click="showForm=false">Отмена</el-button><el-button type="primary" @click="save" :loading="saving">Сохранить</el-button></template>
    </el-dialog>
  </div>
</template>
<script setup>
import {ref,reactive,onMounted} from 'vue';import api from '../api/client';import {ElMessage} from 'element-plus';import {formatDate} from '../utils/format'
const items=ref([]),loading=ref(false),saving=ref(false),page=ref(1),perPage=ref(10),total=ref(0)
const filterRole=ref(null),filterStatus=ref(null),showForm=ref(false),editing=ref(false),editingId=ref(null)
const form=reactive({name:'',email:'',password:'',role:'manager',status:'active'})
function roleLabel(r) { return r === 'admin' ? 'Admin' : r === 'manager' ? 'Manager' : 'Warehouse' }
async function load(){loading.value=true;try{const params={page:page.value,per_page:perPage.value};if(filterRole.value)params.role=filterRole.value;if(filterStatus.value)params.status=filterStatus.value;const{data}=await api.get('/users',{params});items.value=data.data;total.value=data.total}catch(e){}finally{loading.value=false}}
function openCreate(){editing.value=false;resetForm();showForm.value=true}
function editItem(r){editing.value=true;editingId.value=r.id;form.name=r.name;form.email=r.email;form.password='';form.role=r.role;form.status=r.status;showForm.value=true}
function resetForm(){Object.assign(form,{name:'',email:'',password:'',role:'manager',status:'active'})}
async function save(){saving.value=true;try{const payload={...form};if(!payload.password)delete payload.password;if(editing.value){await api.put(`/users/${editingId.value}`,payload)}else{await api.post('/users',payload)}showForm.value=false;ElMessage.success('Сохранено');load()}catch(e){ElMessage.error(e.response?.data?.detail?.message||'')}finally{saving.value=false}}
async function delItem(id){try{await api.delete(`/users/${id}`);ElMessage.success('Деактивирован');load()}catch(e){ElMessage.error(e.response?.data?.detail?.message||'')}}
onMounted(load)
</script>