<template>
  <div class="account-form">
    <!-- 收支类型切换 -->
    <div class="type-tabs">
      <div
        class="type-tab"
        :class="{ active: form.transaction_type === '支出' }"
        @click="handleTypeChange('支出')"
      >
        <ArrowUpOutlined class="type-icon" />
        支出
      </div>
      <div
        class="type-tab"
        :class="{ active: form.transaction_type === '收入' }"
        @click="handleTypeChange('收入')"
      >
        <ArrowDownOutlined class="type-icon" />
        收入
      </div>
    </div>

    <!-- 金额输入 -->
    <div class="amount-input-wrapper">
      <div class="amount-label">金额</div>
      <div class="amount-input-row">
        <span class="currency-symbol">¥</span>
        <input
          ref="amountInput"
          v-model="amountDisplay"
          class="amount-input"
          type="text"
          inputmode="decimal"
          placeholder="0.00"
          @focus="handleAmountFocus"
          @blur="handleAmountBlur"
        />
      </div>
    </div>

    <!-- 商品名称 -->
    <div class="section">
      <div class="section-label">商品名称</div>
      <a-input :value="form.item_name" @update:value="v => form.item_name = v" placeholder="请输入商品或服务名称" />
    </div>

    <!-- 分类选择 -->
    <div class="section">
      <div class="section-label">分类</div>
      <div class="category-grid">
        <div
          v-for="cat in categoryOptions"
          :key="cat.value"
          class="category-item"
          :class="{ selected: form.category === cat.value }"
          @click="form.category = cat.value"
        >
          <div class="category-icon" :style="{ background: cat.color }">
            <component :is="cat.icon" />
          </div>
          <span class="category-name">{{ cat.label }}</span>
        </div>
      </div>
    </div>

    <!-- 日期选择 -->
    <div class="section">
      <div class="section-label">日期</div>
      <a-date-picker
        v-model:value="formDate"
        format="YYYY-MM-DD"
        placeholder="选择日期"
        style="width: 100%"
      />
    </div>

    <!-- 备注 -->
    <div class="section">
      <div class="section-label">备注</div>
      <a-input :value="form.notes" @update:value="v => form.notes = v" placeholder="选填" />
    </div>

    <!-- 保存按钮 -->
    <div class="form-actions">
      <a-button type="primary" block size="large" @click="handleSubmit">
        保存
      </a-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { message } from 'ant-design-vue'
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  CoffeeOutlined,
  CarOutlined,
  ShoppingOutlined,
  GiftOutlined,
  HomeOutlined,
  BookOutlined,
  HeartOutlined,
  MoreOutlined,
  WalletOutlined,
  TrophyOutlined,
  TeamOutlined,
  SwapOutlined,
  TransactionOutlined,
  DollarOutlined,
  RiseOutlined
} from '@ant-design/icons-vue'
import dayjs from 'dayjs'
import { useAccountStore, useLedgerStore } from '@/stores'

const props = defineProps({
  account: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['success', 'cancel'])

const accountStore = useAccountStore()
const ledgerStore = useLedgerStore()

// 支出分类
const expenseCategories = [
  { label: '食品餐饮', value: '食品餐饮', color: '#ff6b6b', icon: CoffeeOutlined },
  { label: '出行交通', value: '出行交通', color: '#4dabf7', icon: CarOutlined },
  { label: '购物消费', value: '购物消费', color: '#ff922b', icon: ShoppingOutlined },
  { label: '休闲娱乐', value: '休闲娱乐', color: '#cc5de8', icon: GiftOutlined },
  { label: '居家生活', value: '居家生活', color: '#20c997', icon: HomeOutlined },
  { label: '文化教育', value: '文化教育', color: '#fab005', icon: BookOutlined },
  { label: '健康医疗', value: '健康医疗', color: '#51cf66', icon: HeartOutlined },
  { label: '其他', value: '其他', color: '#adb5bd', icon: MoreOutlined }
]

// 收入分类
const incomeCategories = [
  { label: '工资', value: '工资', color: '#52c41a', icon: WalletOutlined },
  { label: '奖金', value: '奖金', color: '#73d13d', icon: TrophyOutlined },
  { label: '兼职外快', value: '兼职外快', color: '#95de64', icon: TeamOutlined },
  { label: '二手闲置', value: '二手闲置', color: '#b7eb8f', icon: SwapOutlined },
  { label: '补贴', value: '补贴', color: '#389e0d', icon: TransactionOutlined },
  { label: '红包', value: '红包', color: '#5b8c00', icon: DollarOutlined },
  { label: '理财盈利', value: '理财盈利', color: '#135200', icon: RiseOutlined },
  { label: '其他', value: '其他', color: '#adb5bd', icon: MoreOutlined }
]

// 根据收支类型显示对应的分类
const categoryOptions = computed(() => {
  return form.transaction_type === '支出' ? expenseCategories : incomeCategories
})

const form = reactive({
  transaction_type: '支出',
  amount: null,
  item_name: '',
  category: null,
  transaction_date: new Date().toISOString().split('T')[0],
  notes: ''
})

const amountDisplay = ref('')
const amountInput = ref(null)

const formDate = computed({
  get: () => form.transaction_date ? dayjs(form.transaction_date) : dayjs(),
  set: (val) => {
    form.transaction_date = val ? val.format('YYYY-MM-DD') : dayjs().format('YYYY-MM-DD')
  }
})

const resetForm = () => {
  form.transaction_type = '支出'
  form.amount = null
  form.item_name = ''
  form.category = null
  form.transaction_date = new Date().toISOString().split('T')[0]
  form.notes = ''
  amountDisplay.value = ''
}

watch(() => props.account, (newAccount) => {
  if (newAccount) {
    form.transaction_type = newAccount.transaction_type || '支出'
    form.amount = newAccount.amount
    form.item_name = newAccount.item_name || ''
    form.category = newAccount.category || null
    form.transaction_date = newAccount.transaction_date || new Date().toISOString().split('T')[0]
    form.notes = newAccount.notes || ''
    amountDisplay.value = form.amount ? String(form.amount) : ''
  } else {
    resetForm()
  }
}, { immediate: true })

const handleTypeChange = (type) => {
  form.transaction_type = type
  // 切换类型时清空分类，因为之前的分类可能不属于当前类型
  form.category = null
}

const handleAmountFocus = () => {
  if (!amountDisplay.value) {
    amountDisplay.value = ''
  }
}

const handleAmountBlur = () => {
  const value = parseFloat(amountDisplay.value)
  if (!isNaN(value)) {
    form.amount = value
    amountDisplay.value = value.toFixed(2)
  } else {
    form.amount = null
    amountDisplay.value = ''
  }
}

const handleSubmit = async () => {
  if (!form.amount) {
    message.warning('请输入金额')
    return
  }

  try {
    const data = {
      ledger_id: ledgerStore.currentLedgerId,
      transaction_type: form.transaction_type,
      amount: form.amount,
      item_name: form.item_name || form.category || form.transaction_type,
      category: form.category,
      transaction_date: form.transaction_date,
      notes: form.notes
    }

    if (props.account) {
      await accountStore.updateAccount(props.account.id, data)
      message.success('更新成功')
    } else {
      await accountStore.createAccount(data)
      message.success('添加成功')
    }
    emit('success')
  } catch (error) {
    message.error(error.message || '保存失败')
  }
}
</script>

<style scoped>
.account-form {
  padding: 16px;
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  background: #f5f5f5;
  touch-action: pan-y;
}

/* 收支类型切换 */
.type-tabs {
  display: flex;
  background: #fff;
  border-radius: 8px;
  padding: 4px;
  margin-bottom: 16px;
}

.type-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 15px;
  color: #666;
  transition: all 0.3s;
}

.type-icon {
  font-size: 16px;
}

.type-tab.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  font-weight: 500;
}

.type-tab.active .type-icon {
  color: #fff;
}

/* 金额输入 */
.amount-input-wrapper {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
}

.amount-label {
  font-size: 14px;
  color: #999;
  margin-bottom: 8px;
}

.amount-input-row {
  display: flex;
  align-items: baseline;
}

.currency-symbol {
  font-size: 32px;
  font-weight: bold;
  color: #333;
  margin-right: 8px;
}

.amount-input {
  flex: 1;
  border: none;
  font-size: 40px;
  font-weight: bold;
  color: #333;
  outline: none;
  background: transparent;
}

.amount-input::placeholder {
  color: #ddd;
}

/* 分类网格 */
.section {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
}

.section-label {
  font-size: 14px;
  color: #999;
  margin-bottom: 12px;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px 8px;
}

.category-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
}

.category-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  margin-bottom: 6px;
  transition: transform 0.2s;
}

.category-item.selected .category-icon {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.category-name {
  font-size: 12px;
  color: #666;
}

.category-item.selected .category-name {
  color: #333;
  font-weight: 500;
}

/* 表单操作 */
.form-actions {
  padding: 0 16px;
}

.form-actions .ant-btn {
  height: 48px;
  border-radius: 12px;
  font-size: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}
</style>
