import { ref } from 'vue';

// 定义文件名和文档的类型
interface Document {
  metadata: { name: string };
  content: { Key: string };
}

interface ChatMessage {
  id: number;
  text: string;
  isUser: boolean;
}

interface BlockChat {
  blockId: string;
  messages: ChatMessage[];
}

interface Project {
  id: string;
  name: string;
  flowchartData: any;
}

const file_names = ref<string[]>([]);
const documents = ref<Document[]>([]);
const BASE_URL = 'http://your-base-url.com';
const workspace_id = ref('1');
const currentProject = ref<Project | null>(null);
const projects = ref<Project[]>([]);

// 存储所有block的聊天记录
const blockChats = ref<BlockChat[]>([]);

// API
const Text_Generation_API = "https://gcznsevp8g.execute-api.us-east-1.amazonaws.com/dev"
const Loader = "https://42kxfcuxo7.execute-api.us-east-1.amazonaws.com/dev"
const Save_Workspace_API = "https://0pgkogvtxi.execute-api.us-east-1.amazonaws.com/dev"
const Block_Action_API = "https://rkg1zsj3hf.execute-api.us-east-1.amazonaws.com/dev"

export { 
  file_names, 
  documents, 
  BASE_URL, 
  Text_Generation_API, 
  Loader,
  workspace_id,
  blockChats,
  Save_Workspace_API,
  currentProject,
  projects,
  Block_Action_API
}; 