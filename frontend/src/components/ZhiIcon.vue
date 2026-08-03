<template>
  <div
    class="zhi-icon"
    :style="{ width: `${size}px`, height: `${size}px` }"
  ></div>
</template>

<script setup>
defineProps({
  size: { type: Number, default: 22 }
})
</script>

<style scoped>
.zhi-icon {
  position: relative;
  display: inline-flex;
  flex-shrink: 0;
  border-radius: 50%;
  background: linear-gradient(
    135deg,
    #7c3aed 0%,
    #db2777 33%,
    #3b82f6 66%,
    #10b981 100%
  );
  box-shadow: 0 2px 8px rgba(124, 58, 237, 0.4), 0 4px 16px rgba(219, 39, 119, 0.3);
  animation: zhi-breathe 2.8s ease-in-out infinite;
}

@keyframes zhi-breathe {
  0%,
  100% {
    transform: scale(1);
    box-shadow: 0 2px 8px rgba(124, 58, 237, 0.4), 0 4px 16px rgba(219, 39, 119, 0.3);
  }
  50% {
    transform: scale(1.07);
    box-shadow: 0 4px 14px rgba(124, 58, 237, 0.55), 0 8px 28px rgba(219, 39, 119, 0.45);
  }
}
</style>
