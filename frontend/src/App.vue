<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { PlusIcon, GhostIcon } from 'lucide-vue-next'
import { useVueFlow } from '@vue-flow/core'
import { useClipboard, useEventBus } from '@vueuse/core'

import { Tabs, TabsTrigger, TabsContent, TabsList } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import mainCanvas from '@/components/main-canvas.vue'
import { Button } from '@/components/ui/button'
import { Toaster, useToast } from '@/components/ui/toast'
import axios from 'axios'

import { 
  file_names, 
  documents, 
  BASE_URL, 
  workspace_id, 
  Loader, 
  blockChats, 
  Save_Workspace_API,
  currentProject,
  projects
} from './store.ts'

const defaultData = {
  nodes: [],
  edges: [],
  position: [0, 0],
  zoom: 1,
  viewport: { x: 0, y: 0, zoom: 1 }
}

const selectedProjectId = ref('project-1')
const currentProjectData = ref(defaultData)

function selectProject(projectId: string) {
  saveProjectData(selectedProjectId.value)
  selectedProjectId.value = projectId
  currentProjectData.value = loadProjectData(projectId) || defaultData
}

function formatDataForMainCanvas(data) {
  if (!data || !data.nodes) {
    data = defaultData;
  }

  return {
    nodes: data.nodes.map((node) => ({
      id: node.id,
      type: node.type,
      position: node.position,
      label: node.label,
      initialized: node.initialized,
      data: node.data || {}
    })),
    edges: data.edges || [],
    position: data.position || [0, 0],
    zoom: data.zoom || 1
  }
}
const formattedData = ref(formatDataForMainCanvas(currentProjectData.value))
watch(
  currentProjectData,
  (newData) => {
    if (newData) {
      formattedData.value = formatDataForMainCanvas(newData)
    }
  },
  { immediate: true }
)

function handleOnDragStart(event: DragEvent, nodeType: string) {
  if (event.dataTransfer) {
    event.dataTransfer.setData('application/vueflow', nodeType)
    event.dataTransfer.effectAllowed = 'move'
  }
}

function saveProjectData(projectId: string) {
  const projectData = toObject()
  localStorage.setItem(`project-${projectId}`, JSON.stringify(projectData))
}

function loadProjectData(projectId: string) {
  const projectData = localStorage.getItem(`project-${projectId}`)
  return projectData ? JSON.parse(projectData) : defaultData
}

const { toObject, onNodeDragStop, onEdgesChange, onNodesChange, addNodes, project } = useVueFlow()
const { copy } = useClipboard()
const { toast } = useToast()

function handleClickGetData() {
  copy(JSON.stringify(toObject())).then(() => {
    toast({
      title: 'copied success'
    })
  })
}

function handleClickPublishBtn() {
  toast({
    title: 'Save Data',
    description: '1.valid data 2.fetch backend api to save result'
  })
}

const loadChatHistory = async () => {
  try {
    const response = await axios.post(Loader, {
      workspace_id: workspace_id.value
    })
    
    if (response.data && response.data.body) {
      const parsedData = JSON.parse(response.data.body)
      blockChats.value = parsedData
    }
  } catch (error) {
    console.error('Error loading chat history:', error)
  }
}

const loadWorkspaceData = async () => {
  try {
    const response = await axios.post(Loader, {
      workspace_id: workspace_id.value,
      type: 'workspace'
    })
    
    if (response.data && response.data.body) {
      const workspaceData = JSON.parse(response.data.body)
      
      // 处理每个项目的数据
      workspaceData.projects.forEach(project => {
        // 将 flowchartData 保存到 localStorage
        localStorage.setItem(
          `project-${project.id}`, 
          JSON.stringify(project.flowchartData)
        )
        
        // 更新 projects 数组
        const existingProjectIndex = projects.value.findIndex(p => p.id === project.id)
        if (existingProjectIndex >= 0) {
          projects.value[existingProjectIndex] = {
            id: project.id,
            name: `Project ${project.id}`,
            flowchartData: project.flowchartData
          }
        } else {
          projects.value.push({
            id: project.id,
            name: `Project ${project.id}`,
            flowchartData: project.flowchartData
          })
        }
      })

      // 如果有项目，设置当前项目
      if (projects.value.length > 0) {
        // 如果当前有选中的项目，尝试保持选中状态
        const currentProjectId = selectedProjectId.value
        const projectToSelect = projects.value.find(p => p.id === currentProjectId) || projects.value[0]
        
        currentProject.value = projectToSelect
        selectedProjectId.value = projectToSelect.id
        
        // 更新当前项目数据
        const savedData = localStorage.getItem(`project-${projectToSelect.id}`)
        if (savedData) {
          currentProjectData.value = JSON.parse(savedData)
        }
      }
    }
  } catch (error) {
    toast({
      title: 'Error',
      description: 'Failed to load workspace data'
    })
  }
}

// 修改自动保存间隔为30秒
let autoSaveInterval: number | null = null

// 添加加载状态标志
const isLoading = ref(true)

// 修改加载函数
const loadWorkspaceAndChat = async () => {
  try {
    isLoading.value = true
    
    // 先加载工作区数据
    await loadWorkspaceData()
    
    // 然后加载聊天历史
    await loadChatHistory()
    
  } catch (error) {
    console.error('Error loading data:', error)
  } finally {
    isLoading.value = false
  }
}

// 修改 onMounted
onMounted(async () => {
  // 按顺序加载数据
  await loadWorkspaceAndChat()
  
  // 设置自动保存定时器（30秒）
  autoSaveInterval = window.setInterval(() => {
    if (currentProject.value) {
      saveWorkspaceData(currentProject.value.id)
    }
  }, 30000)
})

// 添加 onUnmounted 钩子清理定时器
onUnmounted(() => {
  if (autoSaveInterval) {
    clearInterval(autoSaveInterval)
  }
})

const switchProject = async (projectId: string) => {
  // 保存当前项目
  if (currentProject.value) {
    const projectData = toObject()
    localStorage.setItem(
      `project-${currentProject.value.id}`, 
      JSON.stringify(projectData)
    )
    
    // 保存到服务器
    await saveWorkspaceData(currentProject.value.id)
  }
  
  // 切换到新项目
  const newProject = projects.value.find(p => p.id === projectId)
  if (newProject) {
    currentProject.value = newProject
    // 从 localStorage 加载项目数据
    const savedData = localStorage.getItem(`project-${projectId}`)
    if (savedData) {
      newProject.flowchartData = JSON.parse(savedData)
    }
  }
}

const saveWorkspaceData = async (projectId: string, showToast: boolean = false) => {
  try {
    // 从 localStorage 获取数据
    const savedData = localStorage.getItem(`project-${projectId}`)
    if (!savedData) {
      return
    }

    // 保存到服务器
    const response = await axios.post(Save_Workspace_API, {
      workspace_id: workspace_id.value,
      project_id: projectId,
      flowchart_data: JSON.parse(savedData)
    })
    
    if (response.status === 200 && showToast) {
      toast({
        title: 'Workspace auto-saved successfully'
      })
    }
  } catch (error) {
    toast({
      title: 'Error',
      description: 'Failed to save project'
    })
  }
}

async function fetchFileList() {
  try {
    const response = await axios.get(`${BASE_URL}/read_file_list`);
    if (response.status === 200) {
      documents.value = response.data.files;
      file_names.value = documents.value.map(doc => doc.metadata['name']);
    } else {
      console.error('Error fetching file list:', response.data.error);
    }
  } catch (error) {
    console.error('Error making request:', error);
  }
}

async function deleteFile(fileKey) {
  try {
    const response = await axios.post(`${BASE_URL}/delete_file`, { key: fileKey });
    if (response.status === 200) {
      documents.value = documents.value.filter(doc => doc.content.Key !== fileKey);
      file_names.value = documents.value.map(doc => doc.metadata['name']);
    } else {
      console.error('Error deleting file:', response.data.error);
    }
  } catch (error) {
    console.error('Error making request:', error);
  }
}

function getFileKey(fileName) {
  const document = documents.value.find(doc => doc.metadata['name'] === fileName);
  return document ? document.content.Key : null;
}

const showDeleteConfirm = ref(false)
const fileToDelete = ref(null)

function confirmDeleteFile(fileKey) {
  fileToDelete.value = fileKey
  showDeleteConfirm.value = true
}

function cancelDelete() {
  showDeleteConfirm.value = false
  fileToDelete.value = null
}

function confirmAndDeleteFile() {
  if (fileToDelete.value) {
    deleteFile(fileToDelete.value)
    showDeleteConfirm.value = false
    fileToDelete.value = null
  }
}

const selectedFile = ref<File | null>(null)
const isUploading = ref(false)

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0]
  }
}

async function handleUpload() {
  if (!selectedFile.value) return

  const formData = new FormData()
  formData.append('file', selectedFile.value)

  isUploading.value = true
  try {
    await axios.post(`${BASE_URL}/upload`, formData)
    const response = await axios.post(`${BASE_URL}/download_vectorized_db`)
    if (response.status === 200) {
      fetchFileList()
    } else {
      console.error('Document Download Failed:', response.data.error)
    }
  } catch (error) {
    console.error('Upload Failed:', error)
    alert('Upload Failed')
  } finally {
    isUploading.value = false
  }
}

// 添加防抖函数
function debounce(fn: Function, delay: number) {
  let timer: number | null = null
  return function (...args: any[]) {
    if (timer) clearTimeout(timer)
    timer = window.setTimeout(() => {
      fn.apply(this, args)
      timer = null
    }, delay)
  }
}

// 创建防抖版本的保存函数 - 不显示提示
const debouncedSaveWorkspace = debounce((projectId: string) => {
  saveWorkspaceData(projectId, false)  // 不显示提示
}, 2000)

// 修改 saveToLocalStorage 函数
const saveToLocalStorage = () => {
  if (currentProject.value) {
    const flowchartData = toObject()
    localStorage.setItem(
      `project-${currentProject.value.id}`, 
      JSON.stringify(flowchartData)
    )
    // 触发防抖保存
    debouncedSaveWorkspace(currentProject.value.id)
  }
}

// 监听节点拖动结束
onNodeDragStop(() => {
  saveToLocalStorage()
})

// 监听边的变化
onEdgesChange(() => {
  saveToLocalStorage()
})

// 监听节点变化
onNodesChange(() => {
  saveToLocalStorage()
})

// 修改 watch 以确保数据更新时重新渲染
watch(
  [currentProjectData, currentProject],
  ([newProjectData, newCurrentProject]) => {
    if (newProjectData) {
      formattedData.value = formatDataForMainCanvas(newProjectData)
    } else if (newCurrentProject?.flowchartData) {
      formattedData.value = formatDataForMainCanvas(newCurrentProject.flowchartData)
    }
  },
  { immediate: true, deep: true }
)

// 添加新的函数来生成唯一的节点 ID
function generateUniqueId(): string {
  return Math.random().toString(36).substr(2, 9)
}

// 修改 onDrop 函数
const onDrop = (event: DragEvent) => {
  if (!event.dataTransfer) return

  const type = event.dataTransfer.getData('application/vueflow')
  
  // 获取画布元素的位置
  const bounds = (event.target as HTMLDivElement).getBoundingClientRect()
  
  // 使用 project 函数将鼠标位置转换为画布坐标
  const position = project({
    x: event.clientX - bounds.left,
    y: event.clientY - bounds.top,
  })

  // 预设节点尺寸（根据实际节点大小调整）
  const nodeWidth = 600  // conversation-node 的宽度
  const nodeHeight = 300 // 预估高度

  // 调整位置，使鼠标位置为节点中心
  const adjustedPosition = {
    x: position.x - nodeWidth / 2,
    y: position.y - nodeHeight / 2
  }

  // 创建新节点
  const newNode = {
    id: generateUniqueId(),
    type,
    position: adjustedPosition,  // 使用调整后的位置
    initialized: false,
    data: type === 'conversation' 
      ? {
          messages: [],
          systemPrompt: '',
          temperature: 0.7
        }
      : {
          selectedFiles: []
        },
    label: type
  }

  // 添加新节点
  addNodes([newNode])
}

// 添加 onDragOver 处理函数
const onDragOver = (event: DragEvent) => {
  event.preventDefault()
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = 'move'
  }
}
</script>

<template>
  <div class="absolute bottom-0 left-0 right-0 top-0">
    <div class="relative flex h-full w-full flex-col">
      <header class="h-20 border-b border-gray-200 px-4 py-3">
        <div class="flex h-full items-center justify-between">
          <div class="flex gap-x-3">
            <div class="flex items-center gap-x-1">
              <GhostIcon class="w-12 text-red-200" />
              <div class="flex flex-col">
                <div class="flex items-center gap-x-3">
                  <p class="text-bold">workflow-test</p>
                </div>
              </div>
            </div>
          </div>

          <div class="flex gap-x-3">
            <Button variant="outline" size="sm" class="text-blue-800" @click="handleClickGetData"> Get Data</Button>
            <Button variant="default" size="sm" @click="handleClickPublishBtn"> Publish </Button>
          </div>
        </div>
      </header>
      <main class="relative flex h-full w-full flex-1">
        <div class="w-96 bg-slate-50">
          <tabs default-value="basic-nodes">
            <tabs-list class="grid w-full grid-cols-3">
              <tabs-trigger value="projects"> Projects </tabs-trigger>
              <tabs-trigger value="basic-nodes"> Basic Nodes </tabs-trigger>
              <tabs-trigger value="Documents"> Documents </tabs-trigger>
            </tabs-list>

            <!-- Projects Section -->
            <tabs-content value="projects">
              <scroll-area class="h-[calc(100vh-150px)] w-full">
                <ul class="mx-6 my-4 space-y-2">
                  <li
                    v-for="project in projects"
                    :key="project.id"
                    :class="{ 'font-bold': project.id === selectedProjectId }"
                    @click="selectProject(project.id)"
                    class="cursor-pointer p-2 rounded-md hover:bg-gray-200"
                  >
                    {{ project.name }}
                  </li>
                </ul>
              </scroll-area>
            </tabs-content>

            <tabs-content value="basic-nodes">
              <scroll-area class="h-[calc(100vh-150px)] w-full">
                <div
                  class="mx-6 mb-6 cursor-grab rounded-md bg-white p-6 shadow-md"
                  :draggable="true"
                  @dragstart="handleOnDragStart($event, 'conversation')"
                >
                  <div class="flex items-center justify-between">
                    <h3 class="flex items-center gap-x-1">
                      <img src="~@/assets/images/icon_LLM.png" class="h-4 w-4" alt="LLM icon" />
                      Conversation Block
                    </h3>
                  </div>
                  <p class="mt-2 text-sm text-gray-400">
                    Create a block representing a conversation with individual messages as nodes.
                  </p>
                </div>  
                <div
                  class="mx-6 mb-6 cursor-grab rounded-md bg-white p-6 shadow-md"
                  :draggable="true"
                  @dragstart="handleOnDragStart($event, 'document_upload')"
                >
                  <div class="flex items-center justify-between">
                    <h3 class="flex items-center gap-x-1">
                      <img src="~@/assets/images/icon_Knowledge.png" class="h-4 w-4" alt="Knowledge icon" />
                      Document Upload Block
                    </h3>
                  </div>
                  <p class="mt-2 text-sm text-gray-400">
                    Create a block to upload documents.
                  </p>
                </div>  
              </scroll-area>
            </tabs-content>

            <tabs-content value="Documents">
              <scroll-area class="h-[calc(100vh-150px)] w-full">
                <div class="grid grid-rows-[auto_1fr]">
                  <div class="bg-slate-50 p-4 border-b">
                    <div class="flex flex-col gap-2">
                      <input 
                        type="file" 
                        @change="handleFileChange" 
                        class="w-full p-2 border border-gray-300 rounded-md"
                      />
                      <button 
                        @click="handleUpload" 
                        :disabled="!selectedFile || isUploading" 
                        class="w-full p-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-300"
                      >
                        {{ isUploading ? 'Processing...' : 'Upload' }}
                      </button>
                    </div>
                  </div>
            
                  <div class="overflow-y-auto">
                    <ul class="mx-6 my-4 space-y-2">
                      <li v-for="file_name in file_names" :key="file_name" class="flex justify-between p-2">
                        <span>{{ file_name }}</span>
                        <button @click="confirmDeleteFile(getFileKey(file_name))" class="text-red-500 hover:text-red-700">
                          Delete
                        </button>
                      </li>
                    </ul>
                  </div>
                </div>
              </scroll-area>
            </tabs-content>
          </tabs>
        </div>
        <div class="relative h-full flex-1 overflow-hidden">
          <template v-if="!isLoading">
            <main-canvas 
              :data="formattedData"
              @drop="onDrop"
              @dragover="onDragOver"
            />
          </template>
          <template v-else>
            <div class="flex h-full items-center justify-center">
              <div class="text-gray-400">Loading...</div>
            </div>
          </template>
        </div>
        <div v-if="showDeleteConfirm" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
          <div class="bg-white p-6 rounded shadow-md">
            <p>Are you sure you want to delete this file?</p>
            <div class="flex justify-end gap-2 mt-4">
              <button @click="cancelDelete" class="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400">Cancel</button>
              <button @click="confirmAndDeleteFile" class="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600">Delete</button>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
  <Toaster />
</template>
