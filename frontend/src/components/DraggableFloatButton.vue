<template>
  <div class="draggable-float-button" :style="{ left: position.x + 'px', top: position.y + 'px' }"
    @mousedown="startDrag" @touchstart="startDrag">
    <a-button type="primary" :shape="shape" :size="size" :style="{ width: width + 'px', height: height + 'px' }"
      @click="handleClick">
      <template #icon>
        <slot name="icon">
          <CameraOutlined />
        </slot>
      </template>
    </a-button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { CameraOutlined } from '@ant-design/icons-vue'

defineProps({
  shape: {
    type: String,
    default: 'circle'
  },
  size: {
    type: String,
    default: 'large'
  },
  width: {
    type: Number,
    default: 56
  },
  height: {
    type: Number,
    default: 56
  },
  initialX: {
    type: Number,
    default: null
  },
  initialY: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['click'])

const position = ref({
  x: typeof window !== 'undefined' ? window.innerWidth - 80 : 24,
  y: typeof window !== 'undefined' ? window.innerHeight - 80 : 80
})

// 定义禁止区域（导航栏和顶部栏的高度）
const HEADER_HEIGHT = 60  // 顶部栏高度
const NAV_HEIGHT = 50     // 底部导航栏高度

const isDragging = ref(false)
const dragOffset = ref({ x: 0, y: 0 })
const hasMoved = ref(false)  // 用于区分点击和拖动
const dragStartPosition = ref({ x: 0, y: 0 })  // 记录拖动起始位置
const MOVE_THRESHOLD = 15  // 移动阈值（像素），小于这个值不算拖动

// 边界检查函数（必须在初始化代码之前定义）
const ensurePositionInBounds = () => {
  if (typeof window === 'undefined') return

  const minX = 10
  const maxX = window.innerWidth - 70
  const minY = HEADER_HEIGHT + 10  // 顶部栏下方10px
  const maxY = window.innerHeight - NAV_HEIGHT - 70  // 底部导航栏上方70px

  position.value.x = Math.max(minX, Math.min(position.value.x, maxX))
  position.value.y = Math.max(minY, Math.min(position.value.y, maxY))
}

// 初始化位置
if (typeof window !== 'undefined') {
  const savedX = localStorage.getItem('floatButtonX')
  const savedY = localStorage.getItem('floatButtonY')
  if (savedX && savedY) {
    position.value.x = parseFloat(savedX)
    position.value.y = parseFloat(savedY)
  }

  // 确保初始化位置不在禁止区域内
  ensurePositionInBounds()
}

const startDrag = (e) => {
  // console.log('[DraggableFloatButton] startDrag 被调用')
  // 不阻止默认行为，让点击事件能够正常触发
  isDragging.value = true
  hasMoved.value = false

  const clientX = e.type === 'touchstart' ? e.touches[0].clientX : e.clientX
  const clientY = e.type === 'touchstart' ? e.touches[0].clientY : e.clientY

  // 记录起始位置
  dragStartPosition.value = { x: clientX, y: clientY }

  dragOffset.value = {
    x: clientX - position.value.x,
    y: clientY - position.value.y
  }

  // console.log('[DraggableFloatButton] 开始拖动，hasMoved 重置为 false')
  // console.log('[DraggableFloatButton] 起始位置:', dragStartPosition.value)

  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
  document.addEventListener('touchmove', onDrag, { passive: false })
  document.addEventListener('touchend', stopDrag)
}

const onDrag = (e) => {
  if (!isDragging.value) return

  const clientX = e.type === 'touchmove' ? e.touches[0].clientX : e.clientX
  const clientY = e.type === 'touchmove' ? e.touches[0].clientY : e.clientY

  // 计算移动距离
  const moveDistance = Math.sqrt(
    Math.pow(clientX - dragStartPosition.value.x, 2) +
    Math.pow(clientY - dragStartPosition.value.y, 2)
  )

  // 只有移动距离超过阈值才标记为已移动并阻止默认行为
  if (moveDistance > MOVE_THRESHOLD) {
    // if (!hasMoved.value) {
    //   console.log('[DraggableFloatButton] 移动距离:', moveDistance.toFixed(2), '超过阈值，标记为拖动')
    // }
    hasMoved.value = true
    e.preventDefault() // 只在真正拖动时阻止默认行为

    let newX = clientX - dragOffset.value.x
    let newY = clientY - dragOffset.value.y

    // 限制在窗口范围内，避免进入导航栏和顶部栏
    if (typeof window !== 'undefined') {
      const minX = 10
      const maxX = window.innerWidth - 70
      const minY = HEADER_HEIGHT + 10  // 顶部栏下方
      const maxY = window.innerHeight - NAV_HEIGHT - 70  // 底部导航栏上方

      newX = Math.max(minX, Math.min(newX, maxX))
      newY = Math.max(minY, Math.min(newY, maxY))
    }

    position.value = { x: newX, y: newY }
  }
}

const stopDrag = () => {
  // console.log('[DraggableFloatButton] stopDrag 被调用')
  // console.log('[DraggableFloatButton] hasMoved 最终值:', hasMoved.value)
  isDragging.value = false

  // 保存位置到 localStorage
  localStorage.setItem('floatButtonX', position.value.x.toString())
  localStorage.setItem('floatButtonY', position.value.y.toString())

  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('touchmove', onDrag)
  document.removeEventListener('touchend', stopDrag)
}

const handleClick = (e) => {
  // console.log('[DraggableFloatButton] handleClick 被调用')
  // console.log('[DraggableFloatButton] hasMoved:', hasMoved.value)

  // 如果是拖动操作，不触发点击事件
  if (hasMoved.value) {
    // console.log('[DraggableFloatButton] 这是拖动操作，不触发点击')
    hasMoved.value = false
    return
  }

  // 触发点击事件
  // console.log('[DraggableFloatButton] 触发 click 事件')
  emit('click', e)
}
</script>

<style scoped>
.draggable-float-button {
  position: fixed;
  z-index: 999;
  cursor: move;
  user-select: none;
  touch-action: none;
}

.draggable-float-button :deep(.ant-btn) {
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.4);
  transition: box-shadow 0.3s, transform 0.1s;
}

.draggable-float-button:active :deep(.ant-btn) {
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.3);
  transform: scale(0.95);
}

.draggable-float-button:hover :deep(.ant-btn) {
  box-shadow: 0 6px 16px rgba(24, 144, 255, 0.5);
}
</style>
