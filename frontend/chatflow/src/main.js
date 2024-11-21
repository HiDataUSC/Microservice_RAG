import { ref } from 'vue'

const file_names = ref([])
const documents = ref([])
const BASE_URL = 'http://localhost:5000'

export { file_names, documents, BASE_URL }