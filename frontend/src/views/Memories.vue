<template>
  <div class="memories-page">
    <!-- 回忆头 -->
    <div class="memory-header">
      <template v-if="memoryStore.memory">
        <div class="header-top">
          <div class="avatar-group">
            <div class="avatar user-avatar">{{ userInitial }}</div>
            <HeartFilled class="heart-icon" />
            <div class="avatar partner-avatar">
              <img v-if="partnerAvatarUrl" :src="partnerAvatarUrl" class="avatar-img" />
              <span v-else>{{ partnerInitial }}</span>
            </div>
          </div>
          <div class="header-text">
            <div class="partner-name">{{ memoryStore.memory.partner_name }}</div>
            <div v-if="memoryStore.memory.story" class="story-text">{{ memoryStore.memory.story }}</div>
          </div>
          <a-button shape="circle" size="small" class="edit-btn" @click="openMemoryEdit">
            <template #icon><EditOutlined /></template>
          </a-button>
        </div>
        <!-- 日期筛选 -->
        <div v-if="memoryStore.events.length" class="filter-bar">
          <a-date-picker
            v-model:value="filterStart"
            value-format="YYYY-MM-DD"
            placeholder="开始"
            allow-clear
            size="small"
            class="filter-date"
          />
          <span class="range-sep">~</span>
          <a-date-picker
            v-model:value="filterEnd"
            value-format="YYYY-MM-DD"
            placeholder="结束"
            allow-clear
            size="small"
            class="filter-date"
          />
        </div>
      </template>

      <!-- 首次：创建回忆空间 -->
      <div v-else-if="!memoryStore.loading" class="empty-hero">
        <HeartFilled class="empty-heart" />
        <p class="empty-title">开始记录你们的回忆</p>
        <p class="empty-desc">添加一个对象，把共同的时光珍藏起来</p>
        <a-button type="primary" shape="round" size="large" @click="openMemoryCreate">
          <template #icon><PlusOutlined /></template>
          添加对象
        </a-button>
      </div>

      <div v-else class="header-loading">
        <a-spin />
      </div>
    </div>

    <!-- 对话式时间线 -->
    <div v-if="memoryStore.memory" class="chat-list">
      <div v-if="memoryStore.events.length === 0 && !memoryStore.loading" class="chat-empty">
        <a-empty description="还没有事件，点击右下角添加第一段回忆" />
      </div>
      <div v-else-if="filteredEvents.length === 0" class="chat-empty">
        <a-empty description="该月份暂无回忆" />
      </div>

      <div
        v-for="event in filteredEvents"
        :key="event.id"
        class="chat-row"
        :class="event.author === 'partner' ? 'is-partner' : 'is-user'"
      >
        <!-- 头像 -->
        <div class="chat-avatar" :class="event.author === 'partner' ? 'partner' : 'user'">
          {{ event.author === 'partner' ? partnerInitial : userInitial }}
        </div>

        <!-- 气泡 -->
        <div class="chat-bubble">
          <div class="bubble-header">
            <span class="bubble-date">
              <CalendarOutlined />
              {{ formatDate(event.event_date) }}
            </span>
            <span class="bubble-actions">
              <a-button type="text" size="small" @click="openPhotoPicker(event)">
                <template #icon><PictureOutlined /></template>照片
              </a-button>
              <a-button type="text" size="small" @click="openEventEdit(event)">
                <template #icon><EditOutlined /></template>
              </a-button>
              <a-popconfirm
                title="删除该事件及其所有照片？"
                ok-text="删除"
                cancel-text="取消"
                @confirm="handleDeleteEvent(event)"
              >
                <a-button type="text" size="small" danger>
                  <template #icon><DeleteOutlined /></template>
                </a-button>
              </a-popconfirm>
            </span>
          </div>

          <div class="bubble-title">{{ event.title }}</div>
          <div v-if="event.location" class="bubble-location">
            <EnvironmentOutlined />{{ event.location }}
          </div>
          <div v-if="event.description" class="bubble-desc">{{ event.description }}</div>

          <!-- 照片网格（仿微信朋友圈布局） -->
          <div
            v-if="event.photos && event.photos.length"
            class="photo-grid"
          >
            <a-image-preview-group class="photo-grid-inner">
              <div
                v-for="(photo, idx) in visiblePhotos(event.photos)"
                :key="photo.id"
                class="photo-item"
                @touchstart.passive="startPress($event, event, photo)"
                @touchend.passive="cancelPress"
                @touchmove.passive="cancelPress"
                @click.capture="onPhotoClickGuard"
              >
                <a-image :src="getPhotoUrl(photo.image_path)" :preview="{ src: getPhotoUrl(photo.image_path) }" />
                <div
                  v-if="overflowCount(event.photos) > 0 && idx === visiblePhotos(event.photos).length - 1"
                  class="photo-more"
                >
                  +{{ overflowCount(event.photos) }}
                </div>
                <a-popconfirm
                  title="删除这张照片？"
                  ok-text="删除"
                  cancel-text="取消"
                  @confirm="handleDeletePhoto(event, photo)"
                >
                  <div class="photo-delete">
                    <DeleteOutlined />
                  </div>
                </a-popconfirm>
              </div>
            </a-image-preview-group>
          </div>

          <!-- 隐藏的多选文件输入 -->
          <input
            :ref="(el) => setFileInput(event.id, el)"
            type="file"
            accept="image/*"
            multiple
            style="display: none"
            @change="(e) => handlePhotoChange(event, e)"
          />
        </div>
      </div>
    </div>

    <!-- 浮动添加按钮 -->
    <div v-if="memoryStore.memory" class="fab" @click="openEventCreate">
      <PlusOutlined />
    </div>

    <!-- 创建/编辑回忆空间弹窗 -->
    <a-modal
      v-model:open="memoryModalVisible"
      :title="memoryStore.memory ? '编辑回忆' : '添加对象'"
      :confirm-loading="memorySubmitting"
      ok-text="保存"
      cancel-text="取消"
      @ok="handleMemorySubmit"
    >
      <a-form layout="vertical">
        <a-form-item label="对象名称" required>
          <a-input v-model:value="memoryForm.partner_name" placeholder="给 TA 起个名字" :maxlength="50" />
        </a-form-item>
        <a-form-item label="一句话寄语">
          <a-textarea
            v-model:value="memoryForm.story"
            placeholder="写下你们的故事..."
            :rows="3"
            :maxlength="500"
            show-count
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 创建/编辑事件弹窗 -->
    <a-modal
      v-model:open="eventModalVisible"
      :title="editingEvent ? '编辑事件' : '添加事件'"
      :confirm-loading="eventSubmitting"
      ok-text="保存"
      cancel-text="取消"
      @ok="handleEventSubmit"
    >
      <a-form layout="vertical">
        <a-form-item label="谁的回忆">
          <a-radio-group v-model:value="eventForm.author">
            <a-radio value="user">我</a-radio>
            <a-radio value="partner">{{ memoryStore.memory?.partner_name || 'TA' }}</a-radio>
          </a-radio-group>
        </a-form-item>
        <a-form-item label="事件标题" required>
          <a-input v-model:value="eventForm.title" placeholder="如：第一次旅行" :maxlength="200" />
        </a-form-item>
        <a-form-item label="日期" required>
          <a-date-picker v-model:value="eventForm.event_date" value-format="YYYY-MM-DD" style="width: 100%" />
        </a-form-item>
        <a-form-item label="地点">
          <a-input v-model:value="eventForm.location" placeholder="发生在哪里（可选）" :maxlength="200" />
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea v-model:value="eventForm.description" placeholder="记录这一刻..." :rows="4" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import dayjs from 'dayjs'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  PictureOutlined,
  HeartFilled,
  EnvironmentOutlined,
  CalendarOutlined
} from '@ant-design/icons-vue'
import { useMemoryStore, useUserStore } from '@/stores'

const memoryStore = useMemoryStore()
const userStore = useUserStore()

// 图片 URL 拼接（对齐 BillDetail.vue，vite 已代理 /static → 后端 8888）
const getPhotoUrl = (path) => `/static/${path}`

// 事件级文件输入引用
const fileInputs = {}
const setFileInput = (eventId, el) => {
  if (el) fileInputs[eventId] = el
}

// 头像首字母
const userInitial = computed(() => {
  const name = userStore.user?.username || '我'
  return name.charAt(0).toUpperCase()
})
const partnerInitial = computed(() => {
  const name = memoryStore.memory?.partner_name || ''
  return name.charAt(0).toUpperCase() || '?'
})
const partnerAvatarUrl = computed(() => {
  const p = memoryStore.memory?.partner_avatar
  return p ? getPhotoUrl(p) : ''
})

// 日期格式化
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return dayjs(dateStr).format('YYYY年M月D日')
}

// 按日期范围筛选事件
const filterStart = ref(null)
const filterEnd = ref(null)
const filteredEvents = computed(() => {
  const s = filterStart.value
  const e = filterEnd.value
  if (!s && !e) return memoryStore.events
  return memoryStore.events.filter(ev => {
    const d = ev.event_date || ''
    return (!s || d >= s) && (!e || d <= e)
  })
})

// ===== 回忆空间弹窗 =====
const memoryModalVisible = ref(false)
const memorySubmitting = ref(false)
const memoryForm = ref({ partner_name: '', story: '' })

const openMemoryCreate = () => {
  memoryForm.value = { partner_name: '', story: '' }
  memoryModalVisible.value = true
}
const openMemoryEdit = () => {
  memoryForm.value = {
    partner_name: memoryStore.memory.partner_name,
    story: memoryStore.memory.story || ''
  }
  memoryModalVisible.value = true
}
const handleMemorySubmit = async () => {
  if (!memoryForm.value.partner_name.trim()) {
    message.warning('请填写对象名称')
    return
  }
  memorySubmitting.value = true
  try {
    const payload = {
      partner_name: memoryForm.value.partner_name.trim(),
      story: memoryForm.value.story?.trim() || null
    }
    if (memoryStore.memory) {
      await memoryStore.updateMemory(payload)
      message.success('已更新')
    } else {
      await memoryStore.initMemory(payload)
      message.success('回忆空间已创建')
    }
    memoryModalVisible.value = false
  } catch (e) {
    message.error(e.message || '操作失败')
  } finally {
    memorySubmitting.value = false
  }
}

// ===== 事件弹窗 =====
const eventModalVisible = ref(false)
const eventSubmitting = ref(false)
const editingEvent = ref(null)
const eventForm = ref({ title: '', event_date: '', location: '', description: '', author: 'user' })

const openEventCreate = () => {
  editingEvent.value = null
  eventForm.value = {
    title: '',
    event_date: dayjs().format('YYYY-MM-DD'),
    location: '',
    description: '',
    author: 'user'
  }
  eventModalVisible.value = true
}
const openEventEdit = (event) => {
  editingEvent.value = event
  eventForm.value = {
    title: event.title,
    event_date: event.event_date,
    location: event.location || '',
    description: event.description || '',
    author: event.author || 'user'
  }
  eventModalVisible.value = true
}
const handleEventSubmit = async () => {
  if (!eventForm.value.title.trim()) {
    message.warning('请填写事件标题')
    return
  }
  if (!eventForm.value.event_date) {
    message.warning('请选择日期')
    return
  }
  eventSubmitting.value = true
  try {
    const payload = {
      title: eventForm.value.title.trim(),
      event_date: eventForm.value.event_date,
      location: eventForm.value.location.trim() || null,
      description: eventForm.value.description?.trim() || null,
      author: eventForm.value.author || 'user'
    }
    if (editingEvent.value) {
      await memoryStore.updateEvent(editingEvent.value.id, payload)
      message.success('已更新')
    } else {
      await memoryStore.addEvent(payload)
      message.success('事件已添加')
    }
    eventModalVisible.value = false
  } catch (e) {
    message.error(e.message || '操作失败')
  } finally {
    eventSubmitting.value = false
  }
}
const handleDeleteEvent = async (event) => {
  try {
    await memoryStore.removeEvent(event.id)
    message.success('已删除')
  } catch (e) {
    message.error(e.message || '删除失败')
  }
}

// ===== 照片 =====
// 统一 3 列网格：1-3 张占 1 行，4-6 张占 2 行，7-9 张占 3 行
// 最多展示 9 张，超出在最后一张显示 +N
const visiblePhotos = (photos) => (photos || []).slice(0, 9)
const overflowCount = (photos) => Math.max(0, (photos?.length || 0) - 9)

const openPhotoPicker = (event) => {
  fileInputs[event.id]?.click()
}
const handlePhotoChange = async (event, e) => {
  const files = Array.from(e.target.files || [])
  e.target.value = '' // 重置，允许重复选择同一文件
  if (!files.length) return

  const hide = message.loading('上传中...', 0)
  try {
    await memoryStore.addPhotos(event.id, files)
    hide()
    message.success(`已上传 ${files.length} 张照片`)
  } catch (err) {
    hide()
    message.error(err.message || '上传失败')
  }
}
// 长按删除（移动端无 hover 时的入口）
let pressTimer = null
let longPressed = false
const startPress = (domEvent, eventData, photo) => {
  clearTimeout(pressTimer)
  pressTimer = setTimeout(() => {
    longPressed = true
    confirmDeletePhoto(eventData, photo)
  }, 500)
}
const cancelPress = () => {
  clearTimeout(pressTimer)
}
const onPhotoClickGuard = (e) => {
  // 长按触发删除后，拦截本次 click，避免同时打开图片预览
  if (longPressed) {
    e.stopPropagation()
    e.preventDefault()
    longPressed = false
  }
}
const confirmDeletePhoto = (eventData, photo) => {
  Modal.confirm({
    title: '删除这张照片？',
    okText: '删除',
    okType: 'danger',
    cancelText: '取消',
    onOk: async () => {
      await memoryStore.removePhoto(eventData.id, photo.id)
      message.success('已删除')
    }
  })
}

const handleDeletePhoto = async (event, photo) => {
  try {
    await memoryStore.removePhoto(event.id, photo.id)
    message.success('已删除')
  } catch (e) {
    message.error(e.message || '删除失败')
  }
}

onMounted(() => {
  memoryStore.fetchMemory()
})
</script>

<style scoped>
.memories-page {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 100%;
  background: #fff5f7;
  overflow-y: auto;
}

/* ===== 回忆头 ===== */
.memory-header {
  background: linear-gradient(135deg, #ff6b9d 0%, #ff8e9e 100%);
  color: #fff;
  padding: 20px 20px 18px;
  border-radius: 0 0 24px 24px;
  box-shadow: 0 4px 16px rgba(255, 107, 157, 0.25);
}

.header-top {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.95);
  color: #ff6b9d;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 600;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.heart-icon {
  font-size: 20px;
  color: #fff;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.2));
}

.edit-btn {
  background: rgba(255, 255, 255, 0.25) !important;
  border: none !important;
  color: #fff !important;
  backdrop-filter: blur(4px);
}

.header-text {
  flex: 1;
  min-width: 0;
}

.partner-name {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.story-text {
  font-size: 13px;
  opacity: 0.9;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.event-count {
  font-size: 12px;
  opacity: 0.8;
}

/* 空状态引导 */
.empty-hero {
  text-align: center;
  padding: 24px 0 8px;
}

.empty-heart {
  font-size: 56px;
  color: #fff;
  margin-bottom: 16px;
  filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.15));
}

.empty-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 20px;
}

.header-loading {
  text-align: center;
  padding: 40px 0;
}

/* ===== 对话式时间线 ===== */
.chat-list {
  padding: 20px 12px 90px;
  max-width: 640px;
  width: 100%;
  margin: 0 auto;
}

.filter-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-top: 12px;
}

.filter-date {
  width: 112px;
}

.range-sep {
  color: rgba(255, 255, 255, 0.75);
}

/* 月份选择器适配深色头部背景 */
.filter-bar :deep(.ant-picker) {
  background: rgba(255, 255, 255, 0.22);
  border-color: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(4px);
}

.filter-bar :deep(.ant-picker-input > input),
.filter-bar :deep(.ant-picker-input > input::placeholder) {
  color: #fff;
}

.filter-bar :deep(.ant-picker-suffix) {
  color: rgba(255, 255, 255, 0.85);
}

.chat-empty {
  text-align: center;
  padding: 40px 0;
}

.chat-row {
  display: flex;
  gap: 8px;
  margin-bottom: 18px;
  align-items: flex-start;
}

/* 当前用户：靠右，头像在右 */
.chat-row.is-user {
  flex-direction: row-reverse;
}

.chat-avatar {
  flex-shrink: 0;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.chat-avatar.user {
  background: linear-gradient(135deg, #ff6b9d, #ff8e9e);
}

.chat-avatar.partner {
  background: linear-gradient(135deg, #8e9eff, #6b7fff);
}

.chat-bubble {
  max-width: 76%;
  background: #fff;
  border-radius: 14px;
  padding: 12px 14px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
}

/* 当前用户气泡：淡粉 */
.chat-row.is-user .chat-bubble {
  background: #ffe4ec;
}

.bubble-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 6px;
}

.bubble-date {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #ff6b9d;
  font-weight: 500;
  white-space: nowrap;
}

.bubble-actions {
  display: inline-flex;
  align-items: center;
  gap: 2px;
}

.bubble-actions :deep(.ant-btn) {
  color: #999;
}

.bubble-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.bubble-location {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #888;
  margin-bottom: 4px;
}

.bubble-desc {
  font-size: 14px;
  color: #555;
  line-height: 1.6;
  white-space: pre-wrap;
}

/* ===== 照片网格（仿微信朋友圈） ===== */
.photo-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
  margin-top: 10px;
}

/* a-image-preview-group 若渲染了 DOM，透明化让 photo-item 直接参与网格 */
.photo-grid :deep(.photo-grid-inner) {
  display: contents;
}

.photo-item {
  position: relative;
  aspect-ratio: 1 / 1;
  border-radius: 8px;
  overflow: hidden;
  background: #f5f5f5;
}

.photo-item :deep(.ant-image) {
  width: 100%;
  height: 100%;
}

.photo-item :deep(.ant-image img) {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 超出 9 张的数量蒙层 */
.photo-more {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 600;
  z-index: 2;
}

.photo-delete {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s;
  z-index: 3;
}

.photo-item:hover .photo-delete {
  opacity: 1;
}

/* ===== 浮动按钮 ===== */
.fab {
  position: fixed;
  right: 22px;
  bottom: 78px;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff6b9d, #ff8e9e);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  box-shadow: 0 4px 14px rgba(255, 107, 157, 0.45);
  cursor: pointer;
  z-index: 100;
  transition: transform 0.2s;
}

.fab:active {
  transform: scale(0.92);
}
</style>
