/** 账本相关API */
import request from '@/utils/request'

// 获取账本列表
export const getLedgers = () => {
  return request({
    url: '/ledgers',
    method: 'get'
  })
}

// 创建账本
export const createLedger = (data) => {
  return request({
    url: '/ledgers',
    method: 'post',
    data
  })
}

// 更新账本
export const updateLedger = (id, data) => {
  return request({
    url: `/ledgers/${id}`,
    method: 'put',
    data
  })
}

// 删除账本
export const deleteLedger = (id) => {
  return request({
    url: `/ledgers/${id}`,
    method: 'delete'
  })
}

// 设置默认账本
export const setDefaultLedger = (id) => {
  return request({
    url: `/ledgers/${id}/default`,
    method: 'patch'
  })
}
