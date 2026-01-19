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
import { ref, onMounted, h } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { RightOutlined } from '@ant-design/icons-vue'
import { useUserStore, useLedgerStore } from '@/stores'

const userStore = useUserStore()
const ledgerStore = useLedgerStore()

const showLedgerManager = ref(false)
const showCreateLedger = ref(false)
const showLoginModal = ref(false)
const isLoginMode = ref(true)
const newLedger = ref({ name: '', description: '' })

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
    loginForm.value = { username: '', password: '', email: '', confirmPassword: '' }
    // 登录成功后加载账本列表
    ledgerStore.fetchLedgers()
  } catch (error) {
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
    loginForm.value = { username: '', password: '', email: '', confirmPassword: '' }
    // 注册成功后加载账本列表
    ledgerStore.fetchLedgers()
  } catch (error) {
    message.error(error.message || '注册失败')
  }
}

const exportData = () => {
  message.info('导出功能开发中')
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

  await ledgerStore.createLedger({
    name: newLedger.value.name,
    description: newLedger.value.description
  })

  message.success('创建成功')
  showCreateLedger.value = false
  newLedger.value = { name: '', description: '' }
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
</style>
