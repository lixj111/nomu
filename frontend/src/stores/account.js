/** 账单状态管理 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as accountApi from '@/api/account'
import { useLedgerStore } from './ledger'

export const useAccountStore = defineStore('account', () => {
  const accounts = ref([])
  const accountsByDate = ref({})
  const statistics = ref({})
  const pagination = ref({
    total: 0,
    page: 1,
    pageSize: 20,
    pages: 0
  })
  const loading = ref(false)

  // 获取账单列表
  const fetchAccounts = async (params = {}) => {
    const ledgerStore = useLedgerStore()
    if (!ledgerStore.currentLedgerId) return

    loading.value = true
    try {
      const res = await accountApi.getAccounts({
        ledger_id: ledgerStore.currentLedgerId,
        ...params
      })
      accounts.value = res.data.items
      pagination.value = {
        total: res.data.total,
        page: res.data.page,
        pageSize: res.data.page_size,
        pages: res.data.pages
      }
    } catch (error) {
      console.log('获取账单列表失败:', error.message)
      accounts.value = []
    } finally {
      loading.value = false
    }
  }

  // 按日期获取账单
  const fetchAccountsByDate = async (year, month) => {
    const ledgerStore = useLedgerStore()
    if (!ledgerStore.currentLedgerId) return

    loading.value = true
    try {
      const res = await accountApi.getAccountsByDate(year, month, ledgerStore.currentLedgerId)
      accountsByDate.value = res.data
    } catch (error) {
      console.log('获取账单列表失败:', error.message)
      accountsByDate.value = {}
    } finally {
      loading.value = false
    }
  }

  // 创建账单
  const createAccount = async (data) => {
    const res = await accountApi.createAccount(data)
    accounts.value.unshift(res.data)
    return res.data
  }

  // 更新账单
  const updateAccount = async (id, data) => {
    const res = await accountApi.updateAccount(id, data)
    const index = accounts.value.findIndex(a => a.id === id)
    if (index !== -1) {
      accounts.value[index] = res.data
    }
    return res.data
  }

  // 删除账单
  const deleteAccount = async (id) => {
    await accountApi.deleteAccount(id)
    accounts.value = accounts.value.filter(a => a.id !== id)
  }

  // 刷新列表
  const refresh = () => {
    fetchAccounts({
      page: pagination.value.page,
      page_size: pagination.value.pageSize
    })
  }

  return {
    accounts,
    accountsByDate,
    statistics,
    pagination,
    loading,
    fetchAccounts,
    fetchAccountsByDate,
    createAccount,
    updateAccount,
    deleteAccount,
    refresh
  }
})
