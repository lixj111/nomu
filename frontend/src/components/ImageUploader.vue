<template>
  <div class="image-uploader">
    <div v-if="!previewUrl" class="upload-area" @click="selectImage">
      <CameraOutlined class="icon" />
      <p>点击拍摄或选择图片</p>
    </div>

    <div v-else class="preview-area">
      <a-image :src="previewUrl" class="preview-image" />
      <a-space class="preview-actions">
        <a-button @click="selectImage">重新选择</a-button>
        <a-button
          type="primary"
          :loading="uploading"
          @click="confirmUpload"
        >
          {{ uploading ? '识别中...' : '确认上传' }}
        </a-button>
      </a-space>
    </div>

    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      @change="handleFileChange"
      style="display: none"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { message } from 'ant-design-vue'
import { CameraOutlined } from '@ant-design/icons-vue'
import { uploadReceipt } from '@/api/upload'
import { useLedgerStore } from '@/stores'

const emit = defineEmits(['uploaded'])

const ledgerStore = useLedgerStore()

const fileInput = ref(null)
const selectedFile = ref(null)
const previewUrl = ref(null)
const uploading = ref(false)

const selectImage = () => {
  fileInput.value.click()
}

const handleFileChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    // 检查文件大小
    if (file.size > 10 * 1024 * 1024) {
      message.error('图片不能超过10MB')
      return
    }

    selectedFile.value = file
    previewUrl.value = URL.createObjectURL(file)
  }
}

const confirmUpload = async () => {
  if (!selectedFile.value || !ledgerStore.currentLedgerId) {
    message.warning('请先选择账本')
    return
  }

  uploading.value = true
  try {
    const res = await uploadReceipt(selectedFile.value, ledgerStore.currentLedgerId)
    emit('uploaded', res.data)
    // 重置状态
    selectedFile.value = null
    previewUrl.value = null
  } catch (error) {
    message.error(error.message || '上传失败')
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.image-uploader {
  padding: 16px;
}

.upload-area {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.3s;
}

.upload-area:hover {
  border-color: #1677ff;
}

.upload-area .icon {
  font-size: 48px;
  color: #d9d9d9;
  margin-bottom: 12px;
}

.upload-area p {
  color: #999;
  font-size: 14px;
  margin: 0;
}

.preview-area {
  text-align: center;
}

.preview-image {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.preview-actions {
  display: flex;
  justify-content: center;
}
</style>
