<template>
  <div class="settings-page">
    <!-- 用户信息 -->
    <a-card class="user-info" :bordered="false" @click="handleUserClick">
      <a-space align="center" :size="16" style="cursor: pointer">
        <a-avatar :size="60" class="user-avatar">
          {{ userStore.user?.username?.[0]?.toUpperCase() || 'U' }}
        </a-avatar>
        <div class="user-details">
          <div class="user-name">{{ userStore.user?.username || '未登录' }}</div>
          <div class="user-email">{{ userStore.user?.email || '点击登录' }}</div>
        </div>
      </a-space>
    </a-card>

    <!-- 账本管理 -->
    <a-card title="账本管理" class="section-card" :bordered="false">
      <a-list :data-source="ledgerActions" class="action-list">
        <template #renderItem="{ item }">
          <a-list-item @click="item.onClick" class="action-item">
            <a-list-item-meta>
              <template #title>{{ item.title }}</template>
            </a-list-item-meta>
            <template #actions>
              <RightOutlined />
            </template>
          </a-list-item>
        </template>
      </a-list>
    </a-card>

    <!-- 数据管理 -->
    <a-card title="数据管理" class="section-card" :bordered="false">
      <a-list :data-source="dataActions" class="action-list">
        <template #renderItem="{ item }">
          <a-list-item @click="item.onClick" class="action-item">
            <a-list-item-meta>
              <template #title>{{ item.title }}</template>
            </a-list-item-meta>
            <template #actions>
              <RightOutlined />
            </template>
          </a-list-item>
        </template>
      </a-list>
    </a-card>

    <!-- 其他 -->
    <a-card title="其他" class="section-card" :bordered="false">
      <a-list :data-source="otherActions" class="action-list">
        <template #renderItem="{ item }">
          <a-list-item @click="item.onClick" class="action-item">
            <a-list-item-meta>
              <template #title>{{ item.title }}</template>
            </a-list-item-meta>
            <template #actions>
              <RightOutlined />
            </template>
          </a-list-item>
        </template>
      </a-list>
    </a-card>

    <!-- 账本管理弹窗 -->
    <a-modal
      v-model:open="showLedgerManager"
      title="账本管理"
      :footer="null"
      width="90%"
    >
      <a-list :data-source="ledgerStore.ledgers" class="ledger-list">
        <template #renderItem="{ item }">
          <a-list-item class="ledger-item">
            <a-list-item-meta>
              <template #title>
                <a-space>
                  {{ item.name }}
                  <a-tag v-if="item.is_default" color="blue">默认</a-tag>
                </a-space>
              </template>
            </a-list-item-meta>
            <template #actions>
              <a-space>
                <a-button
                  size="small"
                  @click="openEditLedger(item)"
                >
                  编辑
                </a-button>
                <a-button
                  v-if="!item.is_default"
                  size="small"
                  @click="setDefaultLedger(item.id)"
                >
                  设为默认
                </a-button>
                <a-button
                  v-if="!item.is_default"
                  size="small"
                  danger
                  @click="confirmDeleteLedger(item)"
                >
                  删除
                </a-button>
              </a-space>
            </template>
          </a-list-item>
        </template>
      </a-list>
    </a-modal>

    <!-- 导出数据弹窗 -->
    <a-modal
      v-model:open="showExportModal"
      title="导出数据"
      :footer="null"
      width="90%"
    >
      <a-form layout="vertical">
        <a-form-item label="日期范围">
          <a-radio-group v-model:value="exportForm.dateRange" @change="handleDateRangeChange">
            <a-radio value="all">所有时间</a-radio>
            <a-radio value="custom">指定范围</a-radio>
          </a-radio-group>
        </a-form-item>
        <a-form-item v-if="exportForm.dateRange === 'custom'" label="选择日期">
          <a-range-picker
            v-model:value="exportForm.dateRangeValue"
            format="YYYY-MM-DD"
            :placeholder="['开始日期', '结束日期']"
            style="width: 100%"
          />
        </a-form-item>
        <a-form-item label="账本">
          <a-radio-group v-model:value="exportForm.ledgerType" @change="handleLedgerTypeChange">
            <a-radio value="current">当前账本</a-radio>
            <a-radio value="select">选择账本</a-radio>
          </a-radio-group>
          <div v-if="exportForm.ledgerType === 'current'" class="current-ledger-hint">
            当前账本：{{ ledgerStore.currentLedger?.name || '未选择' }}
          </div>
          <div v-if="exportForm.ledgerType === 'select'" class="ledger-checkbox-list">
            <a-checkbox
              :indeterminate="indeterminateState"
              :checked="selectAllChecked"
              @change="onSelectAllChange"
            >
              全选
            </a-checkbox>
            <a-divider style="margin: 8px 0" />
            <div class="ledger-checkbox-items">
              <a-checkbox
                v-for="ledger in ledgerStore.ledgers"
                :key="ledger.id"
                v-model:checked="exportForm.selectedLedgers[ledger.id]"
                class="ledger-checkbox-item"
              >
                {{ ledger.name }}
              </a-checkbox>
            </div>
          </div>
        </a-form-item>
        <a-form-item label="文件格式">
          <a-radio-group v-model:value="exportForm.fileFormat">
            <a-radio value="excel">Excel (.xlsx)</a-radio>
          </a-radio-group>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" block :loading="exporting" @click="handleStartExport">
            开始导出
          </a-button>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 编辑账本弹窗 -->
    <a-modal
      v-model:open="showEditLedger"
      title="编辑账本"
      @ok="handleUpdateLedger"
      ok-text="保存"
      cancel-text="取消"
    >
      <a-form layout="vertical">
        <a-form-item label="账本名称" required>
          <a-input
            v-model:value="editingLedger.name"
            placeholder="请输入账本名称"
          />
        </a-form-item>
        <a-form-item label="账本描述">
          <a-textarea
            v-model:value="editingLedger.description"
            placeholder="请输入账本描述（可选）"
            :rows="3"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 创建账本弹窗 -->
    <a-modal
      v-model:open="showCreateLedger"
      title="创建账本"
      @ok="createLedger"
      ok-text="创建"
      cancel-text="取消"
    >
      <a-form layout="vertical">
        <a-form-item label="账本名称" required>
          <a-input
            v-model:value="newLedger.name"
            placeholder="请输入账本名称"
          />
        </a-form-item>
        <a-form-item label="账本描述">
          <a-textarea
            v-model:value="newLedger.description"
            placeholder="请输入账本描述（可选）"
            :rows="3"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 登录/注册弹窗 -->
    <a-modal
      v-model:open="showLoginModal"
      :title="isLoginMode ? '登录' : '注册'"
      @ok="isLoginMode ? handleLogin : handleRegister"
      :ok-text="isLoginMode ? '登录' : '注册'"
      cancel-text="取消"
      width="400"
    >
      <a-form layout="vertical">
        <a-form-item label="用户名" required>
          <a-input
            v-model:value="loginForm.username"
            placeholder="请输入用户名"
            @pressEnter="isLoginMode ? handleLogin() : handleRegister()"
          />
        </a-form-item>
        <a-form-item v-if="!isLoginMode" label="邮箱">
          <a-input
            v-model:value="loginForm.email"
            placeholder="请输入邮箱（可选）"
            @pressEnter="handleRegister"
          />
        </a-form-item>
        <a-form-item label="密码" required>
          <a-input-password
            v-model:value="loginForm.password"
            placeholder="请输入密码"
            @pressEnter="isLoginMode ? handleLogin() : handleRegister()"
          />
        </a-form-item>
        <a-form-item v-if="!isLoginMode" label="确认密码" required>
          <a-input-password
            v-model:value="loginForm.confirmPassword"
            placeholder="请再次输入密码"
            @pressEnter="handleRegister"
          />
        </a-form-item>
      </a-form>
      <template #footer>
        <a-button @click="showLoginModal = false">取消</a-button>
        <a-button type="link" @click="toggleMode">
          {{ isLoginMode ? '没有账号？去注册' : '已有账号？去登录' }}
        </a-button>
        <a-button type="primary" @click="isLoginMode ? handleLogin() : handleRegister()">
          {{ isLoginMode ? '登录' : '注册' }}
        </a-button>
      </template>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted, h, computed } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { RightOutlined } from '@ant-design/icons-vue'
import { useUserStore, useLedgerStore } from '@/stores'
import dayjs from 'dayjs'

const userStore = useUserStore()
const ledgerStore = useLedgerStore()

const showLedgerManager = ref(false)
const showCreateLedger = ref(false)
const showEditLedger = ref(false)
const showLoginModal = ref(false)
const showExportModal = ref(false)
const isLoginMode = ref(true)
const newLedger = ref({ name: '', description: '' })
const editingLedger = ref({ id: null, name: '', description: '' })
const exporting = ref(false)

// 导出表单
const exportForm = ref({
  dateRange: 'all',
  dateRangeValue: null,
  ledgerType: 'current',
  fileFormat: 'excel',
  selectedLedgers: {}
})

// 全选状态计算
const indeterminateState = computed(() => {
  const selectedCount = Object.values(exportForm.value.selectedLedgers).filter(v => v).length
  return selectedCount > 0 && selectedCount < ledgerStore.ledgers.length
})

const selectAllChecked = computed(() => {
  if (ledgerStore.ledgers.length === 0) return false
  return Object.values(exportForm.value.selectedLedgers).every(v => v)
})

// 登录/注册表单
const loginForm = ref({
  username: '',
  password: '',
  email: '',
  confirmPassword: ''
})

// 切换登录/注册模式
const toggleMode = () => {
  isLoginMode.value = !isLoginMode.value
  // 清空表单
  loginForm.value = {
    username: '',
    password: '',
    email: '',
    confirmPassword: ''
  }
}

const handleUserClick = () => {
  if (userStore.isLoggedIn()) {
    // 已登录，显示登出确认
    Modal.confirm({
      title: '退出登录',
      content: '确定要退出登录吗？',
      onOk: () => {
        userStore.logout()
        message.success('已退出登录')
        ledgerStore.fetchLedgers()
      }
    })
  } else {
    // 未登录，显示登录弹窗
    showLoginModal.value = true
  }
}

const handleLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) {
    message.warning('请输入用户名和密码')
    return
  }

  try {
    await userStore.login(loginForm.value.username, loginForm.value.password)
    message.success('登录成功')
    showLoginModal.value = false
    // 登录成功后清空表单
    loginForm.value = { username: '', password: '', email: '', confirmPassword: '' }
    // 登录成功后加载账本列表
    ledgerStore.fetchLedgers()
  } catch (error) {
    // 登录失败：保留用户名，清空密码
    loginForm.value.password = ''
    message.error(error.message || '登录失败')
  }
}

const handleRegister = async () => {
  if (!loginForm.value.username || !loginForm.value.password) {
    message.warning('请输入用户名和密码')
    return
  }

  if (!isLoginMode.value && loginForm.value.password !== loginForm.value.confirmPassword) {
    message.warning('两次输入的密码不一致')
    return
  }

  try {
    await userStore.register(
      loginForm.value.username,
      loginForm.value.password,
      loginForm.value.email || ''
    )
    message.success('注册成功')
    showLoginModal.value = false
    // 注册成功后清空表单
    loginForm.value = { username: '', password: '', email: '', confirmPassword: '' }
    // 注册成功后加载账本列表
    ledgerStore.fetchLedgers()
  } catch (error) {
    // 注册失败：保留用户名和邮箱，清空密码
    loginForm.value.password = ''
    loginForm.value.confirmPassword = ''
    message.error(error.message || '注册失败')
  }
}

const exportData = () => {
  // 打开导出弹窗
  showExportModal.value = true
}

const handleDateRangeChange = () => {
  // 切换日期范围时清空选择的日期
  if (exportForm.value.dateRange === 'all') {
    exportForm.value.dateRangeValue = null
  }
}

const handleLedgerTypeChange = () => {
  // 切换账本类型时初始化选中状态
  if (exportForm.value.ledgerType === 'select') {
    // 初始化所有账本为未选中
    exportForm.value.selectedLedgers = {}
    ledgerStore.ledgers.forEach(ledger => {
      exportForm.value.selectedLedgers[ledger.id] = false
    })
  }
}

const onSelectAllChange = (e) => {
  const checked = e.target.checked
  Object.keys(exportForm.value.selectedLedgers).forEach(key => {
    exportForm.value.selectedLedgers[key] = checked
  })
}

const handleStartExport = async () => {
  // 验证账本选择
  if (exportForm.value.ledgerType === 'current' && !ledgerStore.currentLedgerId) {
    message.warning('请先选择账本')
    return
  }

  // 验证选择的账本
  if (exportForm.value.ledgerType === 'select') {
    const selectedCount = Object.values(exportForm.value.selectedLedgers).filter(v => v).length
    if (selectedCount === 0) {
      message.warning('请至少选择一个账本')
      return
    }
  }

  // 验证自定义日期范围
  if (exportForm.value.dateRange === 'custom' && (!exportForm.value.dateRangeValue || exportForm.value.dateRangeValue.length !== 2)) {
    message.warning('请选择日期范围')
    return
  }

  exporting.value = true

  try {
    const { exportAccounts } = await import('@/api/export')

    // 构建导出参数
    const params = {}
    if (exportForm.value.dateRange === 'custom' && exportForm.value.dateRangeValue) {
      params.start_date = exportForm.value.dateRangeValue[0].format('YYYY-MM-DD')
      params.end_date = exportForm.value.dateRangeValue[1].format('YYYY-MM-DD')
    }

    // 根据账本类型导出
    if (exportForm.value.ledgerType === 'current') {
      // 导出当前账本
      const response = await exportAccounts(ledgerStore.currentLedgerId, params)
      downloadFile(response)
      message.success('导出成功')
    } else {
      // 导出选中的账本
      const selectedLedgerIds = Object.keys(exportForm.value.selectedLedgers)
        .filter(key => exportForm.value.selectedLedgers[key])
        .map(id => parseInt(id))

      let count = 0
      for (const ledgerId of selectedLedgerIds) {
        const response = await exportAccounts(ledgerId, params)
        downloadFile(response)
        count++
      }
      message.success(`已导出 ${count} 个账本`)
    }

    showExportModal.value = false
    // 重置表单
    exportForm.value = {
      dateRange: 'all',
      dateRangeValue: null,
      ledgerType: 'current',
      fileFormat: 'excel',
      selectedLedgers: {}
    }
  } catch (error) {
    message.error(error.message || '导出失败')
  } finally {
    exporting.value = false
  }
}

const downloadFile = (response) => {
  const blob = response.data

  // 创建下载链接
  const url = window.URL.createObjectURL(blob)

  // 从响应头获取文件名
  const contentDisposition = response.headers?.['content-disposition'] || ''
  let filename = `账单明细_${dayjs().format('YYYYMMDD_HHmmss')}.xlsx`

  const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
  if (filenameMatch && filenameMatch[1]) {
    filename = filenameMatch[1].replace(/['"]/g, '')
  }

  // 创建下载链接并点击
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()

  // 清理
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

const showAbout = () => {
  Modal.info({
    title: '关于',
    content: h('div', [
      h('p', '自动记账系统 v1.0.0'),
      h('p', '基于AI的智能账单识别')
    ])
  })
}

const ledgerActions = [
  {
    title: '我的账本',
    onClick: () => {
      showLedgerManager.value = true
    }
  },
  {
    title: '创建新账本',
    onClick: () => {
      showCreateLedger.value = true
    }
  }
]

const dataActions = [
  {
    title: '导出数据',
    onClick: exportData
  }
]

const otherActions = [
  {
    title: '关于',
    onClick: showAbout
  }
]

onMounted(() => {
  ledgerStore.fetchLedgers()
})

const setDefaultLedger = async (id) => {
  await ledgerStore.setDefaultLedger(id)
  message.success('已设置为默认账本')
}

const confirmDeleteLedger = (ledger) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除账本"${ledger.name}"吗？`,
    onOk: async () => {
      await ledgerStore.deleteLedger(ledger.id)
      message.success('删除成功')
    }
  })
}

const createLedger = async () => {
  if (!newLedger.value.name) {
    message.warning('请输入账本名称')
    return
  }

  try {
    await ledgerStore.createLedger({
      name: newLedger.value.name,
      description: newLedger.value.description
    })

    message.success('创建成功')
    showCreateLedger.value = false
    newLedger.value = { name: '', description: '' }
  } catch (error) {
    message.error(error.message || '创建失败')
  }
}

const openEditLedger = (ledger) => {
  editingLedger.value = {
    id: ledger.id,
    name: ledger.name,
    description: ledger.description || ''
  }
  showEditLedger.value = true
}

const handleUpdateLedger = async () => {
  if (!editingLedger.value.name) {
    message.warning('请输入账本名称')
    return
  }

  try {
    await ledgerStore.updateLedger(editingLedger.value.id, {
      name: editingLedger.value.name,
      description: editingLedger.value.description
    })

    message.success('更新成功')
    showEditLedger.value = false
  } catch (error) {
    message.error(error.message || '更新失败')
  }
}
</script>

<style scoped>
.settings-page {
  flex: 1;
  overflow-y: auto;
  height: 100%;
  background: #f5f5f5;
}

.user-info {
  margin: 16px;
  border-radius: 12px;
}

.user-avatar {
  background: linear-gradient(135deg, #1890ff, #096dd9);
  color: #fff;
  font-size: 24px;
  font-weight: bold;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 4px;
}

.user-email {
  font-size: 14px;
  color: #999;
}

.section-card {
  margin: 0 16px 16px 16px;
  border-radius: 12px;
}

.section-card :deep(.ant-card-head-title) {
  font-weight: bold;
}

.action-list {
  background: #fff;
}

.action-list :deep(.ant-list-item) {
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
}

.action-list :deep(.ant-list-item:hover) {
  background: #fafafa;
}

.action-list :deep(.ant-list-item:last-child) {
  border-bottom: none;
}

.action-item {
  display: flex;
  align-items: center;
}

.ledger-list :deep(.ant-list-item) {
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.ledger-list :deep(.ant-list-item:last-child) {
  border-bottom: none;
}

.ledger-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.current-ledger-hint {
  margin-top: 8px;
  padding: 8px 12px;
  background: #f0f5ff;
  border: 1px solid #adc6ff;
  border-radius: 4px;
  font-size: 13px;
  color: #1890ff;
}

.ledger-checkbox-list {
  margin-top: 12px;
  padding: 12px;
  background: #fafafa;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
}

.ledger-checkbox-items {
  max-height: 200px;
  overflow-y: auto;
}

.ledger-checkbox-item {
  padding: 6px 0;
  display: block;
}
</style>
