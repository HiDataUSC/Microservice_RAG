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
const workspace_id = ref('1');
const currentProject = ref<Project | null>(null);
const projects = ref<Project[]>([]);

// 存储所有block的聊天记录
const blockChats = ref<BlockChat[]>([]);

export { 
  file_names, 
  documents, 
  workspace_id,
  blockChats,
  currentProject,
  projects,
}; 