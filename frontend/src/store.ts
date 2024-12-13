import { ref } from 'vue';

// 定义文件名和文档的类型
interface Document {
  metadata: { name: string };
  content: { Key: string };
}

const file_names = ref<string[]>([]);
const documents = ref<Document[]>([]);
const BASE_URL = 'http://your-base-url.com'; // 请根据实际情况修改

export { file_names, documents, BASE_URL }; 