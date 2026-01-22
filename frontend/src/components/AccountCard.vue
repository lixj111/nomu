<template>
  <div class="account-card" @click="$emit('click', account)">
    <div class="card-icon" :style="{ background: categoryColor }">
      <component :is="categoryIcon" />
    </div>
    <div class="card-info">
      <div class="card-name">{{ account.item_name }}</div>
      <div class="card-meta">
        <span>{{ account.category || '未分类' }}</span>
        <span v-if="account.merchant_name">{{ account.merchant_name }}</span>
      </div>
    </div>
    <div
      class="card-amount"
      :class="{ expense: account.transaction_type === '支出', income: account.transaction_type === '收入' }"
    >
      {{ account.transaction_type === '支出' ? '-' : '+' }}¥{{ account.amount }}
    </div>
    <div class="card-actions" @click.stop>
      <a-dropdown :trigger="['click']">
        <a-button type="text" size="small">
          <template #icon>
            <MoreOutlined />
          </template>
        </a-button>
        <template #overlay>
          <a-menu>
            <a-menu-item @click="$emit('edit', account)">
              <EditOutlined />
              编辑
            </a-menu-item>
            <a-menu-item @click="$emit('delete', account)">
              <DeleteOutlined />
              删除
            </a-menu-item>
          </a-menu>
        </template>
      </a-dropdown>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { MoreOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons-vue'
import {
  CoffeeOutlined,
  CarOutlined,
  ShoppingOutlined,
  GiftOutlined,
  HomeOutlined,
  BookOutlined,
  HeartOutlined,
  MoreOutlined as MoreIconOutlined,
  WalletOutlined,
  TrophyOutlined,
  TeamOutlined,
  SwapOutlined,
  TransactionOutlined,
  DollarOutlined,
  RiseOutlined
} from '@ant-design/icons-vue'

const props = defineProps({
  account: {
    type: Object,
    required: true
  }
})

defineEmits(['click', 'edit', 'delete'])

// 支出分类图标
const expenseIcons = {
  '食品餐饮': CoffeeOutlined,
  '出行交通': CarOutlined,
  '购物消费': ShoppingOutlined,
  '休闲娱乐': GiftOutlined,
  '居家生活': HomeOutlined,
  '文化教育': BookOutlined,
  '健康医疗': HeartOutlined,
  '其他': MoreIconOutlined
}

// 收入分类图标
const incomeIcons = {
  '工资': WalletOutlined,
  '奖金': TrophyOutlined,
  '兼职外快': TeamOutlined,
  '二手闲置': SwapOutlined,
  '补贴': TransactionOutlined,
  '红包': DollarOutlined,
  '理财盈利': RiseOutlined,
  '其他': MoreIconOutlined
}

const categoryColors = {
  '食品餐饮': '#ff6b6b',
  '出行交通': '#4dabf7',
  '购物消费': '#ff922b',
  '休闲娱乐': '#cc5de8',
  '居家生活': '#20c997',
  '文化教育': '#fab005',
  '健康医疗': '#51cf66',
  '工资': '#52c41a',
  '奖金': '#73d13d',
  '兼职外快': '#95de64',
  '二手闲置': '#b7eb8f',
  '补贴': '#389e0d',
  '红包': '#5b8c00',
  '理财盈利': '#135200',
  '其他': '#adb5bd'
}

const categoryColor = computed(() => {
  return categoryColors[props.account.category] || '#1890ff'
})

const categoryIcon = computed(() => {
  if (props.account.transaction_type === '收入') {
    return incomeIcons[props.account.category] || MoreIconOutlined
  }
  return expenseIcons[props.account.category] || MoreIconOutlined
})
</script>

<style scoped>
.account-card {
  display: flex;
  align-items: center;
  padding: 14px 16px;
  background: #fff;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
}

.account-card:active {
  background: #f5f5f5;
}

.card-icon {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  margin-right: 12px;
}

.card-info {
  flex: 1;
  min-width: 0;
}

.card-name {
  font-size: 15px;
  font-weight: 500;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-meta {
  font-size: 12px;
  color: #999;
  display: flex;
  gap: 8px;
}

.card-amount {
  font-size: 18px;
  font-weight: bold;
  margin-right: 8px;
}

.card-amount.expense {
  color: #ff4d4f;
}

.card-amount.income {
  color: #52c41a;
}

.card-actions {
  display: flex;
  align-items: center;
}
</style>
