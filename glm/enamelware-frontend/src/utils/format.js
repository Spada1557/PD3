export function formatCurrency(value) {
  if (value === null || value === undefined) return '0 ₽'
  return new Intl.NumberFormat('ru-RU', {
    style: 'decimal',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(value) + ' ₽'
}

export function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

export function formatDateTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' }) +
    ' ' + d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
}

export function statusTag(status) {
  const map = {
    draft: { type: 'info', label: 'Черновик' },
    posted: { type: 'success', label: 'Проведён' },
    cancelled: { type: 'danger', label: 'Отменён' },
    active: { type: 'success', label: 'Активен' },
    inactive: { type: 'danger', label: 'Неактивен' },
  }
  return map[status] || { type: 'info', label: status }
}

export function roleLabel(role) {
  const map = { admin: 'Администратор', manager: 'Менеджер', warehouse: 'Кладовщик' }
  return map[role] || role
}