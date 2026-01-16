/** 上传相关API */
import request from '@/utils/request'

// 上传并识别账单
export const uploadReceipt = (file, ledgerId) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('ledger_id', ledgerId)

  return request({
    url: '/upload/receipt',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 批量上传账单
export const batchUploadReceipts = (files, ledgerId) => {
  const formData = new FormData()
  files.forEach(file => {
    formData.append('files', file)
  })
  formData.append('ledger_id', ledgerId)

  return request({
    url: '/upload/receipts/batch',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
