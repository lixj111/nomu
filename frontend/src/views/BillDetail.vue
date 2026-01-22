<template>
  <div class="bill-detail-page">
    <!-- 顶部导航栏 -->
    <a-layout class="page-layout">
      <a-layout-header class="page-header">
        <a-button type="text" @click="goBack">
          <template #icon>
            <LeftOutlined />
          </template>
          返回
        </a-button>
        <span class="header-title">账单详情</span>
        <div style="width: 60px"></div>
      </a-layout-header>

      <a-layout-content class="page-content">
        <a-spin :spinning="loading">
          <div v-if="bill" class="detail-container">
            <!-- 金额卡片 -->
            <div class="amount-card" :class="{ expense: bill.transaction_type === '支出', income: bill.transaction_type === '收入' }">
              <div class="amount-row">
                <div class="amount-value">
                  {{ bill.transaction_type === '支出' ? '-' : '+' }}¥{{ bill.amount }}
                </div>
                <div class="amount-tag">{{ bill.transaction_type }}</div>
              </div>
              <div class="amount-date">{{ bill.transaction_date }}</div>
            </div>

            <!-- 详情列表 -->
            <div class="detail-list">
              <!-- 分类 -->
              <div class="detail-item">
                <div class="item-label">分类</div>
                <div class="item-value">{{ bill.category || '未分类' }}</div>
              </div>

              <!-- 商品名称 -->
              <div class="detail-item">
                <div class="item-label">商品名称</div>
                <div class="item-value">{{ bill.item_name || '-' }}</div>
              </div>

              <!-- 备注 -->
              <div v-if="bill.notes" class="detail-item">
                <div class="item-label">备注</div>
                <div class="item-value">{{ bill.notes }}</div>
              </div>

              <!-- 地点信息 -->
              <div v-if="bill.merchant_name" class="detail-item">
                <div class="item-label">地点信息</div>
                <div class="item-value">{{ bill.merchant_name }}</div>
              </div>

              <!-- 附件 -->
              <div class="detail-item">
                <div class="item-label">附件</div>
                <div class="item-value">
                  <div v-if="bill.image_url" class="image-preview">
                    <a-image :src="getImageUrl(bill.image_url)" :preview="{ src: getImageUrl(bill.image_url) }" />
                  </div>
                  <span v-else class="no-image">无附件</span>
                </div>
              </div>

              <!-- 创建时间 -->
              <div class="detail-item">
                <div class="item-label">创建时间</div>
                <div class="item-value">{{ formatCreateTime(bill.created_at) }}</div>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="action-buttons">
              <a-button type="primary" block size="large" @click="handleEdit">
                <template #icon>
                  <EditOutlined />
                </template>
                编辑
              </a-button>
              <a-button block size="large" danger @click="handleDelete">
                <template #icon>
                  <DeleteOutlined />
                </template>
                删除
              </a-button>
            </div>
          </div>
        </a-spin>
      </a-layout-content>
    </a-layout>

    <!-- 编辑弹窗 -->
    <a-drawer v-model:open="showEditModal" title="编辑账单" placement="right">
      <AccountForm :account="bill" @success="handleEditSuccess" @cancel="showEditModal = false" />
    </a-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import { LeftOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons-vue'
import { getAccount, deleteAccount } from '@/api/account'
import AccountForm from '@/components/AccountForm.vue'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()

const billId = ref(route.params.id)
const bill = ref(null)
const loading = ref(false)
const showEditModal = ref(false)

onMounted(() => {
  loadBillDetail()
})

const loadBillDetail = async () => {
  loading.value = true
  try {
    const res = await getAccount(billId.value)
    bill.value = res.data
  } catch (error) {
    message.error('获取账单详情失败')
    goBack()
  } finally {
    loading.value = false
  }
}

const getImageUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  // path 格式: uploads/20260119/1.png
  // 访问路径: /static/uploads/20260119/1.png
  return `/static/${path}`
}

const formatCreateTime = (dateStr) => {
  if (!dateStr) return '-'
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm:ss')
}

const goBack = () => {
  router.back()
}

const handleEdit = () => {
  showEditModal.value = true
}

const handleEditSuccess = () => {
  showEditModal.value = false
  loadBillDetail()
}

const handleDelete = () => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除"${bill.value.item_name}"这条账单吗？`,
    onOk: async () => {
      try {
        await deleteAccount(bill.value.id)
        message.success('删除成功')
        goBack()
      } catch (error) {
        message.error(error.message || '删除失败')
      }
    }
  })
}
</script>

<style scoped>
.bill-detail-page {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: 100%;
  background: #f5f5f5;
}

.page-layout {
  height: 100%;
  background: #f5f5f5;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  height: 50px;
  line-height: normal;
}

.header-title {
  font-size: 16px;
  font-weight: 500;
  color: #262626;
}

.page-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.detail-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.amount-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  color: #fff;
}

.amount-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 8px;
}

.amount-tag {
  background: rgba(255, 255, 255, 0.3);
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
}

.amount-card.expense {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.amount-card.income {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.amount-value {
  font-size: 36px;
  font-weight: bold;
}

.amount-date {
  font-size: 14px;
  opacity: 0.8;
}

.detail-list {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #f5f5f5;
}

.detail-item:last-child {
  border-bottom: none;
}

.item-label {
  font-size: 14px;
  color: #8c8c8c;
  min-width: 80px;
}

.item-value {
  flex: 1;
  font-size: 14px;
  color: #262626;
  text-align: right;
}

.image-preview {
  display: flex;
  justify-content: flex-end;
}

.image-preview :deep(.ant-image) {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
}

.image-preview :deep(.ant-image img) {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image {
  color: #bfbfbf;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 0 16px;
}

.action-buttons .ant-btn {
  height: 48px;
  border-radius: 12px;
  font-size: 16px;
}
</style>
