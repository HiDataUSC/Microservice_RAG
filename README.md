# AI Flow - Visual AI Conversation Builder

A visual tool for building and managing AI conversations with a flowchart-like interface.

## Project Structure

### Frontend (`/frontend`)
- Built with Vue 3 + TypeScript
- Uses Vue Flow for flowchart visualization
- Components:
  - `components/vue-flow/nodes/conversation-node`: Handles chat interactions with AI
  - `components/main-canvas`: Manages the flowchart workspace
  - `components/fullscreen-conversation`: Provides fullscreen chat interface

### Backend Services (`/services`)

#### Text_Generation
- Handles AI conversation processing with following features:
  - Processes user queries using OpenAI GPT models
  - Maintains conversation history in DynamoDB
  - Supports context-aware responses by considering:
    - Current conversation history
    - Connected nodes' conversation histories
  - Handles conversation metadata and tracking

#### Store_Conversation
- Manages conversation persistence with following features:
  - Stores conversation data in DynamoDB
  - Handles conversation metadata:
    - Message IDs
    - Timestamps
    - User/Assistant roles
  - Supports workspace and block-based organization

#### Save_Workspace
- Handles workspace state management:
  - Saves flowchart data and project states
  - Features:
    - Auto-generates project IDs
    - Handles float-to-decimal conversions for DynamoDB
    - Supports workspace versioning
    - Maintains project metadata

#### Block_Action
- Manages block-level operations:
  - Supports block deletion
  - Features:
    - Conversation block cleanup
    - Batch deletion support
    - Error handling and reporting

#### Layer_Stuff
- AWS Lambda layers for shared dependencies:
  - Intent detection layer:
    - Common ML/AI libraries
    - Utility functions
    - Shared type definitions
    - Network handling utilities

#### Intent_Detection (Planned)
- Will handle user intent classification
- Route conversations based on detected intents

## Current Features

### Conversation Management
- Create and manage multiple conversation nodes
- Real-time chat with AI
- Persistent conversation history
- Fullscreen chat mode
- Node renaming capability

### Workspace Features
- Multiple project support
- Auto-saving workspace state
- Node connection management
- Drag-and-drop node creation
- Zoom and pan controls

### Data Persistence
- Local storage for workspace state
- Cloud storage for conversation history
- Automatic synchronization

## Technical Implementation

### Frontend Architecture
- Global API configuration
- State management using Vue refs
- Component-based architecture
- Responsive design

### Backend Architecture
- Serverless architecture using AWS Lambda
- DynamoDB for data persistence
- OpenAI GPT integration
- Modular service design

## Planned Features

### Short Term
- [ ] Document upload and processing
- [ ] Knowledge base integration
- [ ] Enhanced conversation context management
- [ ] Multi-language support

### Long Term
- [ ] Custom AI model integration
- [ ] Advanced node types
- [ ] Collaboration features
- [ ] Analytics and insights
- [ ] API node integration
- [ ] Export/Import functionality

## Development Status

Currently implementing:
1. Intent detection
2. Document processing
3. Enhanced conversation context
4. Node connection improvements
5. User interface refinements
6. backend logging for debugging and error handling

## Getting Started

Global variables:
- saved in .env file

Navigate to /path/to/Microservice_RAG

Install:
1. `conda create -n test_env python=3.11`
2. `conda activate test_env`
3. `pip install -r path/to/requirements.txt`

Run test for Generate microservice:
1. run `./tests/generation/generation_test.sh`

To run the development website:
1. Navigate to `frontend/chatflow`
2. open terminal 1 run `python -m tests.api_server`
3. open terminal 2 run `npm run dev`

manage vectorized db (deleted):
`python -m services.common.vectorstore_action`

To create lambda deployment package (layer):
navigate to services folder for example `services/Text_Generation`
follow the tutorial: https://www.youtube.com/watch?v=grRW1Z_C9vw

## Contributing



