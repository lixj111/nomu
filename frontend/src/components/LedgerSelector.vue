<template>
  <div class="ledger-selector" @click="showPicker = true">
    <span class="current-ledger">{{ currentLedger?.name || '选择账本' }}</span>
    <DownOutlined class="icon" />
  </div>

  <Popup v-model:show="showPicker" position="bottom" round>
    <Picker
      :columns="ledgerColumns"
      :value="currentLedgerId"
      @confirm="onConfirm"
      @cancel="showPicker = false"
    />
  </Popup>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Popup, Picker } from 'ant-design-mobile-vue'
import { DownOutlined } from '@ant-design/icons-vue'
import { useLedgerStore } from '@/stores'

const emit = defineEmits(['change'])

const ledgerStore = useLedgerStore()

const showPicker = ref(false)

const currentLedger = computed(() => ledgerStore.currentLedger)
const currentLedgerId = computed(() => ledgerStore.currentLedgerId)

const ledgerColumns = computed(() => {
  return ledgerStore.ledgers.map(ledger => ({
    label: ledger.name,
    value: ledger.id
  }))
})

const onConfirm = ({ value }) => {
  emit('change', value)
  showPicker.value = false
}
</script>

<style scoped>
.ledger-selector {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
}

.current-ledger {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.icon {
  font-size: 12px;
  color: #999;
}
</style>
