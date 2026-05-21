<template>
  <div class="card">
    <div class="table-actions">
      <el-checkbox v-model="unreadOnly" @change="load" label="Только непрочитанные" border />
      <el-button type="default" @click="markAllRead" style="margin-left:auto">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:5px"><polyline points="20 6 9 17 4 12"/></svg>
        Прочитать все
      </el-button>
    </div>
    <el-table :data="items" v-loading="loading" size="default" style="width:100%">
      <el-table-column label="" min-width="40" align="center">
        <template #default="{row}">
          <div v-if="!row.is_read" style="width:8px;height:8px;border-radius:50%;background:var(--accent);display:inline-block;box-shadow:0 0 6px rgba(124,58,237,0.5)"></div>
        </template>
      </el-table-column>
      <el-table-column label="Тип" min-width="100">
        <template #default="{row}">
          <el-tag :type="row.type === 'warning' ? 'warning' : row.type === 'error' ? 'danger' : 'info'" size="small" effect="plain">{{ row.type || 'info' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="Заголовок" min-width="180">
        <template #default="{row}"><span :style="{ fontWeight: row.is_read ? '500' : '700', color: row.is_read ? 'var(--text-secondary)' : 'var(--text-primary)' }">{{ row.title }}</span></template>
      </el-table-column>
      <el-table-column prop="message" label="Сообщение" min-width="220">
        <template #default="{row}"><span :style="{ color: row.is_read ? 'var(--text-muted)' : 'var(--text-secondary)' }">{{ row.message }}</span></template>
      </el-table-column>
      <el-table-column label="Дата" min-width="140">
        <template #default="{row}">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="Статус" min-width="90" align="center">
        <template #default="{row}"><el-tag :type="row.is_read ? 'success' : 'warning'" size="small">{{ row.is_read ? 'Прочитано' : 'Новое' }}</el-tag></template>
      </el-table-column>
      <el-table-column label="" min-width="100">
        <template #default="{row}">
          <el-button v-if="!row.is_read" size="small" type="primary" plain @click="markRead(row.id)">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:4px"><polyline points="20 6 9 17 4 12"/></svg>
            Прочитано
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="flex-row mt-20" style="justify-content:flex-end">
      <el-pagination v-model:current-page="page" :page-size="perPage" :total="total" @current-change="load" layout="prev, pager, next, total" />
    </div>
  </div>
</template>
<script setup>
import {ref,onMounted} from 'vue';import api from '../api/client';import {ElMessage} from 'element-plus';import {formatDate} from '../utils/format'
const items=ref([]),loading=ref(false),page=ref(1),perPage=ref(10),total=ref(0),unreadOnly=ref(false)
async function load(){loading.value=true;try{const{data}=await api.get('/notifications',{params:{page:page.value,per_page:perPage.value,unread_only:unreadOnly.value}});items.value=data.data;total.value=data.total}catch(e){}finally{loading.value=false}}
async function markRead(id){try{await api.post(`/notifications/${id}/read`);load()}catch(e){}}
async function markAllRead(){try{await api.post('/notifications/read-all');ElMessage.success('Все уведомления отмечены');load()}catch(e){}}
onMounted(load)
</script>