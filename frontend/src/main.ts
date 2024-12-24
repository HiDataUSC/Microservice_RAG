import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import { API_CONFIG } from './config'

// 将API配置注入为全局变量
window.API_CONFIG = API_CONFIG

createApp(App).mount('#app')
