export const API_CONFIG = {
  TEXT_GENERATION: "https://gcznsevp8g.execute-api.us-east-1.amazonaws.com/dev",
  LOADER: "https://42kxfcuxo7.execute-api.us-east-1.amazonaws.com/dev",
  SAVE_WORKSPACE: "https://0pgkogvtxi.execute-api.us-east-1.amazonaws.com/dev",
  BLOCK_ACTION: "https://rkg1zsj3hf.execute-api.us-east-1.amazonaws.com/dev"
}

declare global {
  interface Window {
    API_CONFIG: typeof API_CONFIG
  }
} 