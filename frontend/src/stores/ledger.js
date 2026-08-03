/** 账本状态管理 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as ledgerApi from '@/api/ledger'

export const useLedgerStore = defineStore('ledger', () => {
  const ledgers = ref([])
  const storedLedgerId = localStorage.getItem('currentLedgerId')
  const currentLedgerId = ref(storedLedgerId ? Number(storedLedgerId) : null)
  const loading = ref(false)

  // 当前账本
  const currentLedger = computed(() => {
    return ledgers.value.find(l => l.id === currentLedgerId.value) || ledgers.value[0]
  })

  // 默认账本
  const defaultLedger = computed(() => {
    return ledgers.value.find(l => l.is_default) || ledgers.value[0]
  })

  // 获取账本列表
  const fetchLedgers = async () => {
    loading.value = true
    try {
      const res = await ledgerApi.getLedgers()
      ledgers.value = res.data

      // 如果没有选中的账本ID，使用默认账本
      if (!currentLedgerId.value && defaultLedger.value) {
        currentLedgerId.value = defaultLedger.value.id
        saveCurrentLedgerId()
      }

      // 如果当前选中的账本ID不在列表中（如被删除），切换到默认账本
      const currentLedgerExists = ledgers.value.find(l => l.id === currentLedgerId.value)
      if (!currentLedgerExists && defaultLedger.value) {
        currentLedgerId.value = defaultLedger.value.id
        saveCurrentLedgerId()
      }
    } catch (error) {
      // 未登录或API错误时，静默处理
      console.log('获取账本列表失败:', error.message)
      ledgers.value = []
    } finally {
      loading.value = false
    }
  }

  // 切换账本
  const switchLedger = (ledgerId) => {
    currentLedgerId.value = ledgerId
    saveCurrentLedgerId()
  }

  // 保存当前账本ID到localStorage
  const saveCurrentLedgerId = () => {
    if (currentLedgerId.value) {
      localStorage.setItem('currentLedgerId', currentLedgerId.value)
    }
  }

  // 创建账本
  const createLedger = async (data) => {
    const res = await ledgerApi.createLedger(data)
    ledgers.value.push(res.data)
    return res.data
  }

  // 更新账本
  const updateLedger = async (id, data) => {
    const res = await ledgerApi.updateLedger(id, data)
    const index = ledgers.value.findIndex(l => l.id === id)
    if (index !== -1) {
      ledgers.value[index] = res.data
    }
    return res.data
  }

  // 删除账本
  const deleteLedger = async (id) => {
    await ledgerApi.deleteLedger(id)
    ledgers.value = ledgers.value.filter(l => l.id !== id)

    // 如果删除的是当前账本，切换到默认账本
    if (currentLedgerId.value === id) {
      currentLedgerId.value = defaultLedger.value?.id || null
      saveCurrentLedgerId()
    }
  }

  // 设置默认账本
  const setDefaultLedger = async (id) => {
    await ledgerApi.setDefaultLedger(id)
    // 刷新账本列表
    await fetchLedgers()
  }

  return {
    ledgers,
    currentLedgerId,
    currentLedger,
    defaultLedger,
    loading,
    fetchLedgers,
    switchLedger,
    createLedger,
    updateLedger,
    deleteLedger,
    setDefaultLedger
  }
})
