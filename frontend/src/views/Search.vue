<template>
  <div class="search-page">
    <!-- 顶部搜索栏 -->
    <a-layout class="page-layout">
      <a-layout-header class="page-header">
        <a-button type="text" @click="goBack" class="back-button">
          <template #icon>
            <LeftOutlined />
          </template>
          返回
        </a-button>
        <a-input
          v-model:value="searchKeyword"
          placeholder="搜索账单"
          allow-clear
          size="large"
          @pressEnter="handleSearch"
          @change="handleInputChange"
          class="search-input"
        >
          <template #prefix>
            <SearchOutlined />
          </template>
        </a-input>
      </a-layout-header>

      <a-layout-content class="page-content">
        <!-- 搜索结果 -->
        <a-spin :spinning="loading">
          <div v-if="!hasSearched" class="empty-state">
            <a-empty description="请输入关键词搜索账单" />
          </div>
          <div v-else-if="filteredAccounts.length === 0" class="empty-state">
            <a-empty description="未找到相关账单" />
          </div>
          <div v-else class="account-groups">
            <div v-for="group in groupedAccounts" :key="group.date" class="date-group">
              <div class="date-header">
                <span class="date-title">{{ group.dateTitle }}</span>
                <span class="date-summary">
                  <span class="income-text">收 <span class="income-amount">{{ group.income.toFixed(2) }}</span></span>
                  <span class="expense-text">支 <span class="expense-amount">{{ group.expense.toFixed(2) }}</span></span>
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
    </a-layout>

    <!-- 编辑弹窗 -->
    <a-drawer v-model:open="showFormModal" :title="editingAccount ? '编辑账单' : '记一笔'" placement="right" :width="400">
      <AccountForm :account="editingAccount" @success="handleFormSuccess" @cancel="showFormModal = false" />
    </a-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import { SearchOutlined, LeftOutlined } from '@ant-design/icons-vue'
import { useAccountStore } from '@/stores'
import AccountCard from '@/components/AccountCard.vue'
import AccountForm from '@/components/AccountForm.vue'
import dayjs from 'dayjs'

const router = useRouter()
const accountStore = useAccountStore()

const loading = ref(false)
const showFormModal = ref(false)
const editingAccount = ref(null)
const searchKeyword = ref('')
const hasSearched = ref(false)

const accounts = computed(() => accountStore.accounts)

// 星期数组
const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

// 搜索过滤后的账单
const filteredAccounts = computed(() => {
  if (!searchKeyword.value || !hasSearched.value) {
    return []
  }

  const keyword = searchKeyword.value.toLowerCase().trim()
  return accounts.value.filter(account => {
    // 搜索字段：商品名称、分类、备注、商家、交易类型
    const itemMatch = account.item_name?.toLowerCase().includes(keyword)
    const categoryMatch = account.category?.toLowerCase().includes(keyword)
    const notesMatch = account.notes?.toLowerCase().includes(keyword)
    const merchantMatch = account.merchant_name?.toLowerCase().includes(keyword)
    const typeMatch = account.transaction_type?.toLowerCase().includes(keyword)
    const amountMatch = account.amount?.toString().includes(keyword)

    return itemMatch || categoryMatch || notesMatch || merchantMatch || typeMatch || amountMatch
  })
})

// 按日期分组账单
const groupedAccounts = computed(() => {
  const groups = {}

  filteredAccounts.value.forEach(account => {
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
  // 加载所有账单数据用于搜索
  loadAllAccounts()
})

const goBack = () => {
  router.back()
}

const loadAllAccounts = async () => {
  loading.value = true
  try {
    // 加载所有账单数据，不分页
    await accountStore.fetchAccounts({
      page: 1,
      page_size: 99999,
      start_date: null,
      end_date: null
    })
  } finally {
    loading.value = false
  }
}

// 实时搜索
const handleInputChange = () => {
  if (searchKeyword.value.trim()) {
    hasSearched.value = true
  } else {
    hasSearched.value = false
  }
}

// 按回车搜索
const handleSearch = () => {
  if (searchKeyword.value.trim()) {
    hasSearched.value = true
  }
}

const showDetail = (account) => {
  router.push(`/bill/${account.id}`)
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
        loadAllAccounts()
      } catch (error) {
        message.error(error.message || '删除失败')
      }
    }
  })
}

const handleFormSuccess = () => {
  showFormModal.value = false
  // 编辑时store已更新，无需重新加载；新增时需要刷新列表
  if (!editingAccount.value) {
    loadAllAccounts()
  }
  editingAccount.value = null
}
</script>

<style scoped>
.search-page {
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
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  height: auto;
  line-height: normal;
}

.back-button {
  flex-shrink: 0;
  font-size: 16px;
  color: #333;
}

.search-input {
  flex: 1;
  max-width: none;
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

.date-summary .income-text {
  color: #8c8c8c;
  margin-right: 12px;
}

.date-summary .income-amount {
  color: #52c41a;
}

.date-summary .expense-text {
  color: #8c8c8c;
}

.date-summary .expense-amount {
  color: #ff4d4f;
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
