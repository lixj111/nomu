<template>
  <div class="ledger-page">
    <!-- 顶部栏 -->
    <a-layout class="page-layout">
      <a-layout-header class="page-header">
        <LedgerSelector @change="handleLedgerChange" />
        <a-button type="primary" @click="showAddModal = true">
          记一笔
        </a-button>
      </a-layout-header>

      <a-layout-content class="page-content">
        <!-- 账单列表 -->
        <a-spin :spinning="loading">
          <a-list
            :data-source="accounts"
            :pagination="pagination"
            class="account-list"
          >
            <template #renderItem="{ item }">
              <a-list-item>
                <AccountCard
                  :account="item"
                  @click="showDetail"
                />
              </a-list-item>
            </template>
          </a-list>
        </a-spin>
      </a-layout-content>

      <!-- 悬浮上传按钮 -->
      <a-float-button
        type="primary"
        :style="{ right: '24px', bottom: '80px' }"
        @click="showUploadModal = true"
      >
        <template #icon>
          <CameraOutlined />
        </template>
      </a-float-button>
    </a-layout>

    <!-- 上传弹窗 -->
    <a-modal
      v-model:open="showUploadModal"
      title="上传账单"
      :footer="null"
      width="90%"
    >
      <ImageUploader @uploaded="handleUploadSuccess" />
    </a-modal>

    <!-- 添加账单弹窗 -->
    <a-drawer
      v-model:open="showAddModal"
      title="记一笔"
      placement="right"
      :width="400"
    >
      <AccountForm @success="handleAddSuccess" @cancel="showAddModal = false" />
    </a-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { CameraOutlined } from '@ant-design/icons-vue'
import { useAccountStore, useLedgerStore } from '@/stores'
import AccountCard from '@/components/AccountCard.vue'
import ImageUploader from '@/components/ImageUploader.vue'
import AccountForm from '@/components/AccountForm.vue'
import LedgerSelector from '@/components/LedgerSelector.vue'

const accountStore = useAccountStore()
const ledgerStore = useLedgerStore()

const loading = ref(false)
const showUploadModal = ref(false)
const showAddModal = ref(false)

const accounts = computed(() => accountStore.accounts)

const pagination = computed(() => ({
  pageSize: 20,
  total: accounts.value.length,
  showSizeChanger: false,
  showTotal: (total) => `共 ${total} 条`
}))

onMounted(() => {
  if (ledgerStore.currentLedgerId) {
    loadAccounts()
  }
})

const handleLedgerChange = (ledgerId) => {
  ledgerStore.switchLedger(ledgerId)
  loadAccounts()
}

const loadAccounts = async () => {
  loading.value = true
  try {
    await accountStore.fetchAccounts()
  } finally {
    loading.value = false
  }
}

const showDetail = (account) => {
  Modal.info({
    title: account.item_name,
    content: h => h('div', [
      h('p', `金额: ¥${account.amount}`),
      h('p', `分类: ${account.category || '未分类'}`),
      h('p', `日期: ${account.transaction_date}`)
    ])
  })
}

const handleUploadSuccess = (result) => {
  showUploadModal.value = false
  message.success('识别成功')
  loadAccounts()
}

const handleAddSuccess = () => {
  showAddModal.value = false
  message.success('添加成功')
  loadAccounts()
}
</script>

<style scoped>
.ledger-page {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: 100%;
}

.page-layout {
  height: 100%;
  background: #f5f5f5;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  height: auto;
  line-height: normal;
}

.page-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.account-list {
  background: #fff;
  border-radius: 8px;
}

.account-list :deep(.ant-list-item) {
  padding: 0;
  border-bottom: 1px solid #f0f0f0;
}

.account-list :deep(.ant-list-item:last-child) {
  border-bottom: none;
}
</style>
