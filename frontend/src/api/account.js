/** 账单相关API */
import request from '@/utils/request'

// 获取账单列表（分页）
export const getAccounts = (params) => {
  return request({
    url: '/accounts',
    method: 'get',
    params
  })
}

// 获取账单详情
export const getAccount = (id) => {
  return request({
    url: `/accounts/${id}`,
    method: 'get'
  })
}

// 创建账单
export const createAccount = (data) => {
  return request({
    url: '/accounts',
    method: 'post',
    data
  })
}

// 更新账单
export const updateAccount = (id, data) => {
  return request({
    url: `/accounts/${id}`,
    method: 'put',
    data
  })
}

// 删除账单
export const deleteAccount = (id) => {
  return request({
    url: `/accounts/${id}`,
    method: 'delete'
  })
}

// 按日期获取账单
export const getAccountsByDate = (year, month, ledgerId) => {
  return request({
    url: `/accounts/by-date/${year}/${month}`,
    method: 'get',
    params: { ledger_id: ledgerId }
  })
}
