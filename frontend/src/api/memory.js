/** 回忆相关API */
import request from '@/utils/request'

// 获取回忆空间及事件列表
export const getMemory = () => {
  return request({
    url: '/memories',
    method: 'get'
  })
}

// 创建回忆空间
export const createMemory = (data) => {
  return request({
    url: '/memories',
    method: 'post',
    data
  })
}

// 更新回忆空间（对象名/头像/寄语）
export const updateMemory = (data) => {
  return request({
    url: '/memories',
    method: 'put',
    data
  })
}

// 新建回忆事件
export const createEvent = (data) => {
  return request({
    url: '/memories/events',
    method: 'post',
    data
  })
}

// 更新回忆事件
export const updateEvent = (eventId, data) => {
  return request({
    url: `/memories/events/${eventId}`,
    method: 'put',
    data
  })
}

// 删除回忆事件
export const deleteEvent = (eventId) => {
  return request({
    url: `/memories/events/${eventId}`,
    method: 'delete'
  })
}

// 为事件上传照片（批量）
export const uploadEventPhotos = (eventId, files) => {
  const formData = new FormData()
  files.forEach(file => {
    formData.append('files', file)
  })
  return request({
    url: `/memories/events/${eventId}/photos`,
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 删除单张照片
export const deletePhoto = (photoId) => {
  return request({
    url: `/memories/photos/${photoId}`,
    method: 'delete'
  })
}
