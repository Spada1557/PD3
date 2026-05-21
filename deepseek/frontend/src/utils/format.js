function formatCurrency(value) {
  if (value == null || isNaN(value)) return '0 ₽'
  const parts = Math.abs(value).toFixed(2).split('.')
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
  return (value < 0 ? '-' : '') + parts.join(',') + ' ₽'
}

function formatDate(isoStr) {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  return d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function formatPercent(value) {
  if (value == null) return '0%'
  return `${value >= 0 ? '+' : ''}${value.toFixed(1)}%`
}

function debounce(fn, ms) {
  let timer
  return (...args) => {
    clearTimeout(timer)
    timer = setTimeout(() => fn(...args), ms)
  }
}

export { formatCurrency, formatDate, formatPercent, debounce }
