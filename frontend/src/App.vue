<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { PlusIcon, GhostIcon } from 'lucide-vue-next'
import { useVueFlow } from '@vue-flow/core'
import { useClipboard, useEventBus } from '@vueuse/core'
import { versionInfo } from '@/lib/version'

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

import { WorkspaceManager } from '@/lib/workspace-manager'

// 1. 创建 WorkspaceManager 实例（移到最前面）
const { toast } = useToast()
const workspaceManager = new WorkspaceManager(workspace_id.value, currentProject, toast)

// 2. 默认数据现在从 WorkspaceManager 获取
const defaultData = workspaceManager.defaultData

const selectedProjectId = ref('')
const currentProjectData = ref({
  nodes: [],
  edges: [],
  position: [0, 0],
  zoom: 1,
  viewport: { x: 0, y: 0, zoom: 1 }
})

function selectProject(projectId: string) {
  if (!projectId) return
  
  // 保存当前项目
  if (currentProject.value) {
    saveProjectData(selectedProjectId.value)
  }
  
  selectedProjectId.value = projectId
  const loadedData = loadProjectData(projectId)
  
  // 只有有实际数据时才更新
  if (loadedData && (loadedData.nodes?.length > 0 || loadedData.edges?.length > 0)) {
    currentProjectData.value = loadedData
  } else {
    currentProjectData.value = {
      nodes: [],
      edges: [],
      position: [0, 0],
      zoom: 1,
      viewport: { x: 0, y: 0, zoom: 1 }
    }
  }
}

function formatDataForMainCanvas(data) {
  return workspaceManager.formatDataForMainCanvas(data)
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
  workspaceManager.saveToLocalStorage(projectId, projectData)
}

function loadProjectData(projectId: string) {
  return workspaceManager.loadFromLocalStorage(projectId)
}

const { toObject, onNodeDragStop, onEdgesChange, onNodesChange, addNodes, project, viewport, vueFlowRef } = useVueFlow()
const { copy } = useClipboard()

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
      
      // 清空现有项目列表
      projects.value = []
      
      // 清空 localStorage 中的所有项目数据
      const keysToRemove = Object.keys(localStorage).filter(key => key.startsWith('project-'))
      keysToRemove.forEach(key => localStorage.removeItem(key))
      
      // 如果没有项目，创建一个空项目并保存基本视图状态
      if (!workspaceData.projects || workspaceData.projects.length === 0) {
        const emptyProject = {
          id: 'project-1',
          flowchartData: {
            nodes: [],
            edges: [],
            position: [0, 0],
            zoom: 1,
            viewport: { x: 0, y: 0, zoom: 1 }
          }
        }
        
        localStorage.setItem(
          `project-${emptyProject.id}`, 
          JSON.stringify(emptyProject.flowchartData)
        )
        
        projects.value.push({
          id: emptyProject.id,
          name: `Project ${emptyProject.id}`,
          flowchartData: emptyProject.flowchartData
        })
      } else {
        // 处理现有项目数据
        workspaceData.projects.forEach(project => {
          // 确保 flowchartData 存在，如果不存在则使用空的数据结构
          const flowchartData = project.flowchartData || {
            nodes: [],
            edges: [],
            position: [0, 0],
            zoom: 1,
            viewport: { x: 0, y: 0, zoom: 1 }
          }
          
          // 始终保存到 localStorage，无论是否有实际数据
          localStorage.setItem(
            `project-${project.id}`, 
            JSON.stringify(flowchartData)
          )
          
          // 更新 projects 数组
          projects.value.push({
            id: project.id,
            name: `Project ${project.id}`,
            flowchartData: flowchartData
          })
        })
      }

      // 如果有项目，设置当前项目
      if (projects.value.length > 0) {
        const currentProjectId = selectedProjectId.value
        const projectToSelect = projects.value.find(p => p.id === currentProjectId) || projects.value[0]
        
        currentProject.value = projectToSelect
        selectedProjectId.value = projectToSelect.id
        
        const savedData = localStorage.getItem(`project-${projectToSelect.id}`)
        if (savedData) {
          const parsedData = JSON.parse(savedData)
          // 只有当有实际数据时才使用
          if (parsedData.nodes?.length > 0 || parsedData.edges?.length > 0) {
            currentProjectData.value = parsedData
          } else {
            currentProjectData.value = {
              nodes: [],
              edges: [],
              position: [0, 0],
              zoom: 1,
              viewport: { x: 0, y: 0, zoom: 1 }
            }
          }
        }
      } else {
        currentProject.value = null
        selectedProjectId.value = ''
        currentProjectData.value = {
          nodes: [],
          edges: [],
          position: [0, 0],
          zoom: 1,
          viewport: { x: 0, y: 0, zoom: 1 }
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

// 添加初始化标志
const initialized = ref(false)

// 修改加载函数
const loadWorkspaceAndChat = async () => {
  try {
    isLoading.value = true
    
    // 先加载工作区数据
    await loadWorkspaceData()
    
    // 然后加载聊天历史
    await loadChatHistory()
    
    // 标记初始化完成
    initialized.value = true
    
  } catch (error) {
  } finally {
    isLoading.value = false
  }
}

// 修改 onMounted
onMounted(async () => {
  // 确保在页面加载时运行 Loader API
  if (!initialized.value) {
    await loadWorkspaceAndChat()
  }
})

// 添加页面刷新监听
window.addEventListener('load', async () => {
  if (!initialized.value) {
    await loadWorkspaceAndChat()
  }
})

// 在组件卸载时清理
onUnmounted(() => {
  if (autoSaveInterval) {
    clearInterval(autoSaveInterval)
  }
  workspaceManager.cleanup()
  window.removeEventListener('load', loadWorkspaceAndChat)
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
}, 50)

// 修改 saveToLocalStorage 函数
const saveToLocalStorage = () => {
  if (currentProject.value) {
    const flowchartData = toObject()
    workspaceManager.saveToLocalStorage(currentProject.value.id, flowchartData)
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
  const bounds = vueFlowRef.value?.getBoundingClientRect()
  if (!bounds) return
  
  // 使用 project 函数将鼠标位置转换为画布坐标，考虑画布的变换
  const position = project({
    x: event.clientX - bounds.left,
    y: event.clientY - bounds.top,
  })

  // 预设节点尺寸
  const nodeWidth = 600
  const nodeHeight = 300

  // 调整位置，考虑画布的缩放
  const adjustedPosition = {
    x: position.x - (nodeWidth / 2 / viewport.value.zoom),
    y: position.y - (nodeHeight / 2 / viewport.value.zoom)
  }

  // 创建新节点
  const newNode = {
    id: generateUniqueId(),
    type,
    position: adjustedPosition,
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
            <div class="flex flex-col items-end text-sm text-gray-500">
              <span>{{ versionInfo.version }}</span>
              <span>Last updated: {{ versionInfo.lastUpdated }}</span>
            </div>
          </div>
        </div>
      </header>
      <main class="relative flex h-full w-full flex-1">
        <div class="w-96 bg-slate-50">
          <tabs default-value="basic-nodes">
            <tabs-list class="grid w-full grid-cols-3">
              <tabs-trigger value="projects"> Projects </tabs-trigger>
              <tabs-trigger value="basic-nodes"> Basic Nodes </tabs-trigger>
              <tabs-trigger value="Documents" disabled class="opacity-50 cursor-not-allowed"> Documents </tabs-trigger>
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
                  class="mx-6 mb-6 cursor-not-allowed rounded-md bg-white p-6 shadow-md opacity-50"
                  :draggable="false"
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
              <scroll-area class="h-[calc(100vh-150px)] w-full opacity-50 pointer-events-none">
                <div class="grid grid-rows-[auto_1fr]">
                  <div class="bg-slate-50 p-4 border-b">
                    <div class="flex flex-col gap-2">
                      <input 
                        type="file" 
                        disabled
                        class="w-full p-2 border border-gray-300 rounded-md cursor-not-allowed"
                      />
                      <button 
                        disabled
                        class="w-full p-2 bg-gray-300 text-white rounded-md cursor-not-allowed"
                      >
                        Upload
                      </button>
                    </div>
                  </div>
            
                  <div class="overflow-y-auto">
                    <ul class="mx-6 my-4 space-y-2">
                      <li v-for="file_name in file_names" :key="file_name" class="flex justify-between p-2">
                        <span>{{ file_name }}</span>
                        <button disabled class="text-gray-400 cursor-not-allowed">
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
