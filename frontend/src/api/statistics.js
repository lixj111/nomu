/** 统计相关API */
import request from '@/utils/request'

// 获取概览统计
export const getOverviewStats = (ledgerId) => {
  return request({
    url: `/statistics/overview/${ledgerId}`,
    method: 'get'
  })
}

// 获取分类统计
export const getCategoryStats = (ledgerId, params) => {
  return request({
    url: `/statistics/category/${ledgerId}`,
    method: 'get',
    params
  })
}

// 获取趋势统计
export const getTrendStats = (ledgerId, params) => {
  return request({
    url: `/statistics/trend/${ledgerId}`,
    method: 'get',
    params
  })
}
