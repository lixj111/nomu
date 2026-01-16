/** 应用入口 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import AntdMobile from 'ant-design-mobile-vue'
import 'ant-design-mobile-vue/es/global/style'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(AntdMobile)

app.mount('#app')
