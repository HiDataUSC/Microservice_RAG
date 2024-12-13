<script setup lang="ts">
import { ref, computed, watch, onMounted} from 'vue'
import { PlusIcon, GhostIcon } from 'lucide-vue-next'
import { useVueFlow } from '@vue-flow/core'
import { useClipboard, useEventBus } from '@vueuse/core'

import { Tabs, TabsTrigger, TabsContent, TabsList } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import mainCanvas from '@/components/main-canvas.vue'
import { Button } from '@/components/ui/button'
import { Toaster, useToast } from '@/components/ui/toast'
import axios from 'axios'

import {file_names, documents, BASE_URL} from './main.js'

const projects = ref([
  { id: 'project-1', name: 'Project 1', flowchartData: [] },
  { id: 'project-2', name: 'Project 2', flowchartData: [] }
])

const defaultData = {
  nodes: [
    { 
      id: "1", 
      type: "document_upload", 
      initialized: false, 
      position: { x: 0, y: 400 }, 
      data: {
        selectedFiles: []
      }, 
      label: "document_upload" 
    },
    { 
      id: "2", 
      type: "conversation", 
      initialized: false, 
      position: { x: 800, y: 400 }, 
      data: {
        messages: [],
        systemPrompt: "",
        temperature: 0.7
      }, 
      label: "conversation" 
    }
  ],
  edges: [
    {
      id: 'e1-2',
      source: '1',
      target: '2'
    }
  ],
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

function handleOnDragStart(event: DragEvent, nodeType: any) {
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

const { toObject } = useVueFlow()
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

onMounted(async () => {
  fetchFileList();

  try {
    const response = await axios.post(`${BASE_URL}/download_vectorized_db`)
    if (response.status === 200) {
    } else {
      console.error('Error downloading files:', response.data.error)
    }
  } catch (error) {
    console.error('Error making request:', error)
  }
})

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
          <main-canvas :data="formattedData"/>
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
