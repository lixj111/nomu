/** 导出相关API */
import request from '@/utils/request'

/**
 * 导出账本账单为Excel
 * @param {number} ledgerId - 账本ID
 * @param {Object} params - 查询参数
 * @param {string} params.start_date - 开始日期 (可选)
 * @param {string} params.end_date - 结束日期 (可选)
 * @returns {Blob} Excel文件
 */
export const exportAccounts = (ledgerId, params = {}) => {
  return request({
    url: `/export/accounts/${ledgerId}`,
    method: 'get',
    params,
    responseType: 'blob'
  })
}
