<template>
  <div class="account-form">
    <div class="form-header">
      <span>记一笔</span>
      <CloseOutlined @click="$emit('cancel')" />
    </div>

    <Form :model="form" layout="vertical">
      <FormItem label="类型">
        <RadioGroup v-model:value="form.transaction_type">
          <Radio value="支出">支出</Radio>
          <Radio value="收入">收入</Radio>
        </RadioGroup>
      </FormItem>

      <FormItem label="金额">
        <Input
          v-model:value="form.amount"
          type="number"
          placeholder="请输入金额"
        />
      </FormItem>

      <FormItem label="商品/服务名称">
        <Input
          v-model:value="form.item_name"
          placeholder="请输入商品或服务名称"
        />
      </FormItem>

      <FormItem label="分类">
        <Select v-model:value="form.category" placeholder="选择分类">
          <SelectOption v-for="cat in categories" :key="cat" :value="cat">
            {{ cat }}
          </SelectOption>
        </Select>
      </FormItem>

      <FormItem label="日期">
        <Input
          v-model:value="form.transaction_date"
          type="date"
        />
      </FormItem>

      <FormItem label="备注">
        <Textarea
          v-model:value="form.notes"
          placeholder="选填"
          :rows="3"
        />
      </FormItem>

      <div class="form-actions">
        <Button block @click="$emit('cancel')">取消</Button>
        <Button block type="primary" @click="handleSubmit">保存</Button>
      </div>
    </Form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Form, FormItem, Input, Radio, RadioGroup, Select, SelectOption, Textarea, Button, Toast, CloseOutlined } from 'ant-design-mobile-vue'
import { useAccountStore, useLedgerStore } from '@/stores'

const emit = defineEmits(['success', 'cancel'])

const accountStore = useAccountStore()
const ledgerStore = useLedgerStore()

const categories = ['餐饮', '交通', '购物', '娱乐', '医疗', '教育', '住房', '通讯', '其他']

const form = reactive({
  transaction_type: '支出',
  amount: '',
  item_name: '',
  category: '',
  transaction_date: new Date().toISOString().split('T')[0],
  notes: ''
})

const handleSubmit = async () => {
  if (!form.amount || !form.item_name) {
    Toast.show('请填写必填项')
    return
  }

  try {
    await accountStore.createAccount({
      ledger_id: ledgerStore.currentLedgerId,
      ...form
    })
    emit('success')
  } catch (error) {
    Toast.show(error.message || '保存失败')
  }
}
</script>

<style scoped>
.account-form {
  padding: 16px;
  height: 100%;
  overflow-y: auto;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  font-size: 18px;
  font-weight: bold;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}
</style>
