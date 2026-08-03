/** 回忆状态管理 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as memoryApi from '@/api/memory'

export const useMemoryStore = defineStore('memory', () => {
  const memory = ref(null) // 回忆空间对象
  const events = ref([])   // 事件列表（含照片）
  const loading = ref(false)

  // 拉取回忆空间及事件列表
  const fetchMemory = async () => {
    loading.value = true
    try {
      const res = await memoryApi.getMemory()
      memory.value = res.data.memory
      events.value = res.data.events || []
    } catch (error) {
      console.log('获取回忆失败:', error.message)
      memory.value = null
      events.value = []
    } finally {
      loading.value = false
    }
  }

  // 创建回忆空间
  const initMemory = async (data) => {
    const res = await memoryApi.createMemory(data)
    memory.value = res.data
    return res.data
  }

  // 更新回忆空间
  const updateMemory = async (data) => {
    const res = await memoryApi.updateMemory(data)
    memory.value = res.data
    return res.data
  }

  // 新建事件（插入到列表头部，保持倒序）
  const addEvent = async (data) => {
    const res = await memoryApi.createEvent(data)
    events.value = [res.data, ...events.value]
    return res.data
  }

  // 更新事件
  const updateEvent = async (eventId, data) => {
    const res = await memoryApi.updateEvent(eventId, data)
    const index = events.value.findIndex(e => e.id === eventId)
    if (index !== -1) {
      events.value[index] = res.data
      // 触发响应式更新
      events.value = [...events.value]
    }
    return res.data
  }

  // 删除事件
  const removeEvent = async (eventId) => {
    await memoryApi.deleteEvent(eventId)
    events.value = events.value.filter(e => e.id !== eventId)
  }

  // 为事件上传照片
  const addPhotos = async (eventId, files) => {
    const res = await memoryApi.uploadEventPhotos(eventId, files)
    const event = events.value.find(e => e.id === eventId)
    if (event) {
      event.photos = [...(event.photos || []), ...res.data]
    }
    return res.data
  }

  // 删除单张照片
  const removePhoto = async (eventId, photoId) => {
    await memoryApi.deletePhoto(photoId)
    const event = events.value.find(e => e.id === eventId)
    if (event) {
      event.photos = (event.photos || []).filter(p => p.id !== photoId)
    }
  }

  return {
    memory,
    events,
    loading,
    fetchMemory,
    initMemory,
    updateMemory,
    addEvent,
    updateEvent,
    removeEvent,
    addPhotos,
    removePhoto
  }
})
