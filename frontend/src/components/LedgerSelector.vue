<template>
  <a-dropdown v-model:open="showPicker" :trigger="['click']">
    <div class="ledger-selector">
      <span class="current-ledger">{{ currentLedger?.name || '选择账本' }}</span>
      <DownOutlined class="icon" />
    </div>
    <template #overlay>
      <a-menu @click="onMenuClick">
        <a-menu-item
          v-for="ledger in ledgerStore.ledgers"
          :key="ledger.id"
        >
          {{ ledger.name }}
        </a-menu-item>
      </a-menu>
    </template>
  </a-dropdown>
</template>

<script setup>
import { ref, computed } from 'vue'
import { DownOutlined } from '@ant-design/icons-vue'
import { useLedgerStore } from '@/stores'

const emit = defineEmits(['change'])

const ledgerStore = useLedgerStore()

const showPicker = ref(false)

const currentLedger = computed(() => ledgerStore.currentLedger)
const currentLedgerId = computed(() => ledgerStore.currentLedgerId)

const onMenuClick = ({ key }) => {
  emit('change', key)
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
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.ledger-selector:hover {
  background: #f5f5f5;
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
