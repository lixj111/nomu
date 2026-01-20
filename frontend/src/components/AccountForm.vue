<template>
  <div class="account-form">
    <a-form layout="vertical" :model="form">
      <a-form-item label="类型" required>
        <a-radio-group v-model:value="form.transaction_type" button-style="solid">
          <a-radio-button value="支出">支出</a-radio-button>
          <a-radio-button value="收入">收入</a-radio-button>
        </a-radio-group>
      </a-form-item>

      <a-form-item label="金额" required>
        <a-input-number v-model:value="form.amount" :precision="2" :min="0" placeholder="请输入金额" style="width: 100%" />
      </a-form-item>

      <a-form-item label="商品/服务名称" required>
        <a-input v-model:value="form.item_name" placeholder="请输入商品或服务名称" />
      </a-form-item>

      <a-form-item label="分类">
        <a-select v-model:value="form.category" placeholder="选择分类" :options="categoryOptions" />
      </a-form-item>

      <a-form-item label="日期">
        <a-date-picker v-model:value="formDate" format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
      </a-form-item>

      <a-form-item label="备注">
        <a-textarea v-model:value="form.notes" placeholder="选填" :rows="3" />
      </a-form-item>

      <a-form-item>
        <a-space style="width: 100%">
          <a-button @click="$emit('cancel')">取消</a-button>
          <a-button type="primary" @click="handleSubmit">保存</a-button>
        </a-space>
      </a-form-item>
    </a-form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { message } from 'ant-design-vue'
import dayjs from 'dayjs'
import { useAccountStore, useLedgerStore } from '@/stores'

const props = defineProps({
  // 编辑模式：传入要编辑的账单对象
  account: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['success', 'cancel'])

const accountStore = useAccountStore()
const ledgerStore = useLedgerStore()

const categoryOptions = [
  '食品餐饮',
  '出行交通',
  '购物消费',
  '休闲娱乐',
  '居家生活',
  '文化教育',
  '健康医疗',
  '其他'
].map(cat => ({ label: cat, value: cat }))

const form = reactive({
  transaction_type: '支出',
  amount: null,
  item_name: '',
  category: null,
  transaction_date: new Date().toISOString().split('T')[0],
  notes: ''
})

const formDate = computed({
  get: () => form.transaction_date ? dayjs(form.transaction_date) : null,
  set: (val) => {
    form.transaction_date = val ? val.format('YYYY-MM-DD') : ''
  }
})

// 监听 account prop 变化，用于编辑模式
watch(() => props.account, (newAccount) => {
  if (newAccount) {
    form.transaction_type = newAccount.transaction_type || '支出'
    form.amount = newAccount.amount
    form.item_name = newAccount.item_name || ''
    form.category = newAccount.category || null
    form.transaction_date = newAccount.transaction_date || new Date().toISOString().split('T')[0]
    form.notes = newAccount.notes || ''
  } else {
    // 重置表单
    form.transaction_type = '支出'
    form.amount = null
    form.item_name = ''
    form.category = null
    form.transaction_date = new Date().toISOString().split('T')[0]
    form.notes = ''
  }
}, { immediate: true })

const handleSubmit = async () => {
  if (!form.amount || !form.item_name) {
    message.warning('请填写必填项')
    return
  }

  try {
    if (props.account) {
      // 编辑模式
      await accountStore.updateAccount(props.account.id, {
        ledger_id: ledgerStore.currentLedgerId,
        ...form
      })
      message.success('更新成功')
    } else {
      // 新建模式
      await accountStore.createAccount({
        ledger_id: ledgerStore.currentLedgerId,
        ...form
      })
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
  background: #fff;
}

:deep(.ant-radio-group) {
  width: 100%;
}

:deep(.ant-radio-button-wrapper) {
  flex: 1;
  text-align: center;
}

:deep(.ant-space) {
  width: 100%;
}

:deep(.ant-space-item) {
  flex: 1;
}

:deep(.ant-btn) {
  width: 100%;
}
</style>
