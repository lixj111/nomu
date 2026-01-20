<template>
  <div class="ledger-page">
    <!-- 顶部栏 -->
    <a-layout class="page-layout">
      <a-layout-header class="page-header">
        <LedgerSelector @change="handleLedgerChange" />
        <a-button type="primary" @click="openAddModal">
          记一笔
        </a-button>
      </a-layout-header>

      <a-layout-content class="page-content">
        <!-- 账单列表（按日期分组） -->
        <a-spin :spinning="loading">
          <div v-if="groupedAccounts.length === 0" class="empty-state">
            <a-empty description="暂无账单，点击右上角记一笔或上传账单" />
          </div>
          <div v-else class="account-groups">
            <div v-for="group in groupedAccounts" :key="group.date" class="date-group">
              <div class="date-header">
                <span class="date-title">{{ group.dateTitle }}</span>
                <span class="date-summary">
                  收 {{ group.income.toFixed(2) }} 支 {{ group.expense.toFixed(2) }}
                </span>
              </div>
              <div class="date-accounts">
                <AccountCard v-for="account in group.accounts" :key="account.id" :account="account" @click="showDetail"
                  @edit="handleEdit" @delete="handleDelete" />
              </div>
            </div>
          </div>
        </a-spin>
      </a-layout-content>

      <!-- 可拖动悬浮上传按钮 -->
      <DraggableFloatButton @click="showUploadModal = true">
        <template #icon>
          <CameraOutlined />
        </template>
      </DraggableFloatButton>
    </a-layout>

    <!-- 上传弹窗 -->
    <a-modal v-model:open="showUploadModal" title="上传账单" :footer="null" width="90%">
      <ImageUploader @uploaded="handleUploadSuccess" />
    </a-modal>

    <!-- 添加/编辑账单弹窗 -->
    <a-drawer v-model:open="showFormModal" :title="editingAccount ? '编辑账单' : '记一笔'" placement="right" :width="400">
      <AccountForm :account="editingAccount" @success="handleFormSuccess" @cancel="showFormModal = false" />
    </a-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { CameraOutlined } from '@ant-design/icons-vue'
import { useAccountStore, useLedgerStore } from '@/stores'
import AccountCard from '@/components/AccountCard.vue'
import ImageUploader from '@/components/ImageUploader.vue'
import AccountForm from '@/components/AccountForm.vue'
import LedgerSelector from '@/components/LedgerSelector.vue'
import DraggableFloatButton from '@/components/DraggableFloatButton.vue'
import dayjs from 'dayjs'

const accountStore = useAccountStore()
const ledgerStore = useLedgerStore()

const loading = ref(false)
const showUploadModal = ref(false)
const showFormModal = ref(false)
const editingAccount = ref(null)

const accounts = computed(() => accountStore.accounts)

// 星期数组
const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

// 按日期分组账单
const groupedAccounts = computed(() => {
  const groups = {}

  accounts.value.forEach(account => {
    const date = account.transaction_date
    if (!groups[date]) {
      groups[date] = {
        date,
        accounts: [],
        income: 0,
        expense: 0
      }
    }
    groups[date].accounts.push(account)

    // 计算收支
    if (account.transaction_type === '收入') {
      groups[date].income += parseFloat(account.amount)
    } else {
      groups[date].expense += parseFloat(account.amount)
    }
  })

  // 转换为数组并添加日期标题
  const result = Object.values(groups).map(group => {
    const dateObj = dayjs(group.date)
    const today = dayjs()
    const yesterday = today.subtract(1, 'day')
    const weekDay = weekDays[dateObj.day()]

    let dateTitle = ''
    if (dateObj.isSame(today, 'day')) {
      dateTitle = `今天 ${weekDay}`
    } else if (dateObj.isSame(yesterday, 'day')) {
      dateTitle = `昨天 ${weekDay}`
    } else {
      dateTitle = `${dateObj.format('M月D日')} ${weekDay}`
    }

    return {
      ...group,
      dateTitle
    }
  })

  // 按日期降序排序
  return result.sort((a, b) => dayjs(b.date).valueOf() - dayjs(a.date).valueOf())
})

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

const openAddModal = () => {
  editingAccount.value = null
  showFormModal.value = true
}

const handleEdit = (account) => {
  editingAccount.value = account
  showFormModal.value = true
}

const handleDelete = (account) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除"${account.item_name}"这条账单吗？`,
    onOk: async () => {
      try {
        await accountStore.deleteAccount(account.id)
        message.success('删除成功')
        loadAccounts()
      } catch (error) {
        message.error(error.message || '删除失败')
      }
    }
  })
}

const handleUploadSuccess = (result) => {
  console.log('[Ledger] handleUploadSuccess 被调用，结果:', result)
  showUploadModal.value = false
  message.success('识别成功')
  loadAccounts()
}

const handleFormSuccess = () => {
  showFormModal.value = false
  editingAccount.value = null
  // message.success(editingAccount.value ? '更新成功' : '添加成功')
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

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.account-groups {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.date-group {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.date-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fafafa;
  border-bottom: 1px solid #f0f0f0;
}

.date-title {
  font-size: 14px;
  font-weight: 500;
  color: #262626;
}

.date-summary {
  font-size: 13px;
  color: #8c8c8c;
}

.date-accounts {
  padding: 0;
}

.date-accounts :deep(.account-card:first-child) {
  border-top: none;
}

.date-accounts :deep(.account-card:last-child) {
  border-bottom: none;
}
</style>
