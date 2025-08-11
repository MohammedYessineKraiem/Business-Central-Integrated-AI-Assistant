# AI Copilot System for Microsoft Dynamics 365 Business Central

## 🚀 Project Overview

An **end-to-end AI Copilot system** that transforms how users interact with Microsoft Dynamics 365 Business Central through **natural language processing**. This comprehensive solution enables seamless chat interactions, automated command execution, CRUD operations, and intelligent knowledge retrieval—all integrated directly into the Business Central interface.

### The system combines:
- **AL Extensions** for custom Business Central pages and actions
- **.NET API** for multi-LLM provider integration and Business Central data operations  
- **Python FastAPI + ChromaDB** for Retrieval-Augmented Generation (RAG) and long-term memory
- **Custom HTML/CSS/JavaScript Frontend** embedded within Business Central using ControlAddIn

---

## ⚡ Quick Start - RAG & FastAPI Setup

**Before running the .NET API, ensure the RAG system is properly configured:**

### 1. **📋 Skip Processing Script** 
The RAG processing script has already been executed - **DO NOT re-run it**

### 1.2. **📋 Download the needed dataset under the label training_data.json and put it in the processing_data file under the rag directory** 
HuggingFace link : 
### 2. **🔍 Validate Setup** 
Run `setup_run` to check package validity and system configuration

### 3. **📦 Install Dependencies** 
Download and install from `requirements.txt`
```bash
pip install -r requirements.txt
```

### 4. **🤖 Start Ollama Server** 
Launch your local Mistral 7B model
```bash
ollama serve mistral:7b
```
⚠️ **Or modify the code to use your preferred model - ENSURE YOU'RE IN THE CORRECT DIRECTORY**

### 5. **🚀 Launch FastAPI Server** 
Start the RAG API server with Uvicorn
```bash
uvicorn rag_api_server:app --reload
```
⚠️ **CRITICAL: Ensure you're in the correct API directory before running this command**

### 6. **🛠️ Troubleshooting** 
The requirements folder should contain everything needed, but install any missing packages as errors occur

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# CRUD Operations - Business Central Extension

## 📋 Overview

The **CRUD Operations extension** provides the **core command execution functionality** for the AI Copilot system within Microsoft Dynamics 365 Business Central. This extension enables users to perform **Create, Read, Update, and Delete operations** on Business Central data using **natural language commands** that are processed by AI models and executed through structured API calls.

---

## 🏗️ Architecture

The extension consists of **three main layers**:

- **Command Processing Layer**: Handles AI command interpretation and execution
- **Data Management Layer**: Manages custom entities and customer service records  
- **User Interface Layer**: Provides intuitive interfaces for command input and data visualization

---

## 🔧 Components

### 1. Command Processing

#### **AgentCommandSender (Codeunit 50113)**
The **core command execution engine** that bridges natural language inputs with Business Central operations.

**Key Features:**
- **Multi-Model Support**: Integrates with various AI providers (OpenAI, Anthropic, Mistral, etc.)
- **Structured Response Parsing**: Processes JSON responses from the AI backend
- **Automatic Logging**: Records all interactions for auditing and improvement
- **Error Handling**: Provides comprehensive error reporting and status tracking

**Main Methods:**
```al
procedure SendCommand(Prompt: Text; ModelUsed: Text; var Status: Text): Text
procedure BuildCommandJson(Prompt: Text; Model: Text): Text
local procedure ParseCommandResponse(JsonText: Text; var ResponseText: Text; var StatusText: Text; var DataText: Text)
```

**Workflow:**
1. User inputs natural language command
2. Command is formatted as JSON payload
3. HTTP POST request sent to backend API (`http://localhost:5135/copilot/command`)
4. AI processes command and returns structured response
5. Response is parsed and executed within Business Central
6. Results are logged and displayed to user

### 2. Data Management

#### **CopilotEntity Table (50121)**
Custom entity table for managing **AI-created records** and tracking their lifecycle.

**Fields:**
- **Entity ID**: Unique identifier for each entity
- **Customer ID**: Associated customer reference
- **Title**: Entity title/name
- **Description**: Detailed entity description
- **Status**: Current status (Open, InProgress, Completed, Cancelled)
- **Created At**: Timestamp of creation

#### **CustomerService Table (50120)**
Specialized customer management table optimized for **AI operations**.

**Fields:**
- **Customer ID**: Unique customer identifier
- **Full Name**: Complete customer name
- **Username**: System username
- **Email**: Contact email address
- **Phone Number**: Contact phone number
- **Created At**: Record creation timestamp

### 3. User Interfaces

#### **Copilot Agent Page (50103)**
**Primary command interface** where users interact with the AI system.

**Features:**
- **Natural Language Input**: Multi-line text field for complex commands
- **Model Selection**: Dropdown to choose AI provider/model
- **Real-time Execution**: Execute commands with immediate feedback
- **Response Display**: Shows AI-generated results and execution status
- **Command History**: Maintains log of all interactions
- **Clear Functionality**: Reset interface for new commands

**Example Commands:**
- `"Create a customer named John Smith with email john@example.com"`
- `"Update customer CUST001 to have phone number +1-555-0123"`
- `"Show me all customers created in the last 7 days"`
- `"Delete the entity with ID ENT001"`

**Data List Pages:**
- **Copilot Entity List (50121)**: Browse and manage AI-created entities
- **Customer Service List (50124)**: View and manage customer service records

---

## 🔌 Integration Points

### **Backend API Communication**
- **Endpoint**: `http://localhost:5135/copilot/command`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Payload Structure**: 
```json
{
  "prompt": "Natural language command",
  "Model": "Selected AI model"
}
```

### **Response Handling**
The system processes **three types of response data**:
- **Message**: AI-generated response text
- **Success**: Boolean status indicator
- **Data**: Structured data results from command execution

### **Logging Integration**
All command interactions are automatically logged using the shared `StoreInTable` codeunit, providing:
- Complete **audit trail**
- **Performance monitoring**
- **Error tracking**
- **User interaction patterns**

---

## 💡 Usage Examples

### **Creating Records**
**User Input:** `"Create a new customer named Alice Johnson with email alice@tech.com and phone +1-555-0199"`  
**AI Response:** `"Successfully created customer CUST002 for Alice Johnson with the specified contact information."`

### **Updating Records**
**User Input:** `"Update customer CUST001 to change their status to completed"`  
**AI Response:** `"Customer CUST001 status updated to completed successfully."`

### **Querying Data**
**User Input:** `"Show me all customers created this week"`  
**AI Response:** `"Found 5 customers created this week: CUST001, CUST002, CUST003, CUST004, CUST005"`

### **Complex Operations**
**User Input:** `"Create an entity for customer CUST001 with title 'Project Alpha' and description 'AI implementation project' with status Open"`  
**AI Response:** `"Created entity ENT001 for customer CUST001 with title 'Project Alpha' and status set to Open."`

---

## ⚠️ Error Handling

The system includes **comprehensive error handling** for:
- **Network Issues**: Backend service unavailability
- **Parsing Errors**: Malformed JSON responses
- **Validation Errors**: Invalid command parameters
- **Business Logic Errors**: Constraint violations or business rule conflicts

---

## 🔒 Security Considerations

- **Data Classification**: All customer data properly classified for privacy compliance
- **Access Control**: Internal access modifiers restrict unauthorized usage
- **Audit Logging**: Complete interaction history for security monitoring
- **Input Validation**: Commands validated before execution

---

## ⚡ Performance Features

- **Efficient JSON Processing**: Optimized parsing for large responses
- **Minimal Database Impact**: Designed for high-frequency operations
- **Response Caching**: Status and results cached for improved UX
- **Batch Processing**: Support for multiple operations in single command

---

## 🛠️ Configuration

### **Setup Requirements**
1. Backend API service running on `localhost:5135`
2. Proper AL extension deployment in Business Central
3. User permissions configured for custom tables and pages
4. Network access configured for HTTP client operations

### **Model Configuration**
**Supported AI models** can be selected via the `ModelUsed` field:
- **OpenAI GPT models**
- **Anthropic Claude models**
- **Mistral AI models**
- **Local LLM implementations**

---

## 📊 Monitoring and Maintenance

### **Key Metrics**
- Command execution success rate
- Response time performance
- Error frequency and types
- User adoption patterns

### **Maintenance Tasks**
- Regular log cleanup
- Performance optimization
- Security updates
- Model performance evaluation

---

## 🚀 Future Enhancements

- **Batch Command Processing**: Execute multiple commands simultaneously
- **Advanced Query Builder**: Visual query construction interface
- **Custom Workflows**: User-defined command sequences
- **Enhanced Security**: Role-based command restrictions
- **Offline Mode**: Limited functionality without backend connectivity

---

## 🔧 Troubleshooting

### **Common Issues**
1. **"Failed to reach backend"**: Verify API service is running and accessible
2. **"Failed to parse command response"**: Check backend response format
3. **"Please enter a command"**: Ensure command field is not empty
4. **Timeout errors**: Increase HTTP client timeout settings

### **Debug Information**
The system provides **detailed logging** including:
- Raw JSON payloads
- HTTP response codes
- Parsing step results
- Command execution timestamps

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Chatbot Extension - Business Central AI Chat System

## 📋 Overview

The **Chatbot Extension** provides **conversational AI capabilities** within Microsoft Dynamics 365 Business Central, enabling users to interact with their ERP system through **natural language conversations**. This extension supports **multi-model AI integration**, contextual conversations, and comprehensive chat logging for enhanced user experience and system insights.

---

## 🏗️ Architecture

The chatbot system is built on a **layered architecture**:

- **Communication Layer**: HTTP-based API integration with AI services
- **Context Management Layer**: Intelligent conversation history and context preservation
- **Data Persistence Layer**: Comprehensive chat logging and audit trails
- **User Interface Layer**: Intuitive chat interfaces and role center integration

---

## 🔧 Core Components

### 1. HTTP Communication Engine

#### **HTTP Calls (Codeunit 50101)**
The **primary communication interface** between Business Central and external AI services.

**Key Features:**
- **Multi-Model Support**: Seamlessly switches between different AI providers
- **Context-Aware Conversations**: Maintains conversation history for better responses
- **Structured Response Processing**: Parses and validates AI responses
- **Error Handling**: Robust error management and user feedback

**Main Methods:**
```al
procedure SendPrompt(Message: Text; ModelUsed: Text): Text
procedure BuildJson(prompt: Text; model: Text; context: Text): Text
local procedure ParseLLMResponse(JsonText: Text; var ResponseText: Text; var ModelUsed: Text; var StatusText: Text)
```

**API Communication:**
- **Endpoint**: `http://localhost:5135/copilot/chat`
- **Method**: `POST`
- **Content-Type**: `application/json`

**Request Structure:**
```json
{
  "prompt": "User message",
  "modelName": "Selected AI model",
  "context": "Previous conversation history"
}
```

### 2. Context Management System

#### **StoreInTable (Codeunit 50100)**
**Advanced context management** and data persistence engine.

**Context Features:**
- **Conversation Memory**: Retrieves last 5 chat interactions for context
- **Smart Truncation**: Optimizes context size for API efficiency
- **Model Standardization**: Converts text model names to standardized enums
- **Data Validation**: Ensures data integrity before storage

**Key Methods:**
```al
procedure GetLast5ChatPrompts(): Text
procedure HandlePromptResponse(Prompt: Text; Response: Text; Model: Text; Context: Text; Status: Text; PromptTypeText: Option)
procedure ConvertTextToAIModelEnum(ModelName: Text): Enum "AI Model"
```

**Context Building Algorithm:**
1. Queries last 5 chat interactions
2. Formats as conversational context: `"User Asked [question] Your Response Was [answer]"`
3. Truncates to optimal length for API consumption
4. Provides contextual continuity across conversations

### 3. AI Model Management

#### **AI Model Enum (50100)**
**Standardized enumeration** for supported AI providers and models.

**Supported Models:**
- **GPT-3.5 Turbo**: OpenAI's efficient conversational model
- **Claude-3**: Anthropic's advanced reasoning model
- **Mistral-7B**: Open-source efficient language model
- **Together.AI**: Collaborative AI platform integration
- **Groq**: High-performance inference platform

**Benefits:**
- Consistent model referencing across the system
- Easy addition of new AI providers
- Type-safe model selection in user interfaces

### 4. Data Persistence

#### **Copilot Chat Log Table (50101)**
**Comprehensive chat logging system** for conversation tracking and analysis.

**Schema:**
```al
field(1; "Log ID"; Integer)           // Auto-incrementing unique identifier
field(2; "Message"; Text[2000])       // User input message
field(3; "Response"; Text[2048])      // AI-generated response
field(4; "ModelUsed"; Enum "AI Model") // AI model used for response
field(5; "Context"; Text[2048])       // Conversation context provided
field(6; "Status"; Text[30])          // Response status indicator
field(7; "Times-tamp"; DateTime)      // Interaction timestamp
field(8; "PromptType"; Option)        // Type classification (Question/Command)
```

**Key Features:**
- **Audit Trail**: Complete conversation history
- **Performance Monitoring**: Response times and success rates
- **Context Analysis**: Understanding conversation patterns
- **Multi-Type Support**: Distinguishes between questions and commands

### 5. User Interfaces

#### **Copilot Chat Page (50102)**
**Primary conversational interface** for user interactions.

**Interface Features:**
- **Multi-line Message Input**: Rich text input for complex queries
- **Model Selection**: Dropdown for AI provider choice
- **Real-time Responses**: Immediate AI feedback display
- **Timestamp Tracking**: Conversation chronology
- **Message Management**: Clear and reset functionality

**User Experience:**
- Clean, intuitive design
- Responsive interaction flow
- Clear visual feedback
- Accessible tooltips and guidance

#### **Chat Log List Page (50100)**
**Administrative interface** for conversation management and analysis.

**Management Features:**
- **Complete Chat History**: View all conversations
- **Searchable Records**: Find specific interactions
- **Bulk Operations**: Manage multiple records
- **Export Capabilities**: Data extraction for analysis

### **Role Center Integration**

#### **XPilot Menu Extension** - Seamless integration with Business Manager Role Center

**Menu Items:**
- **Chat XPilot**: Direct access to conversational interface
- **XPilot Agents**: Command execution system
- **Insights And AI Suggestions**: Advanced analytics dashboard
- **XPilot Chat Advanced**: Enhanced chat launcher

---

## 💬 Workflow Examples

### **Basic Conversation**
**User:** `"What are the top 3 customers by sales this month?"`  
**Context:** `[Previous 5 interactions for continuity]`  
**AI Response:** 
```
"Based on your sales data, the top 3 customers this month are:
1. Contoso Corp - $45,230
2. Adventure Works - $38,950
3. Northwind Traders - $32,100"
```

### **Contextual Follow-up**
**User:** `"What about last month?"`  
**Context:** `[Includes previous question about top customers]`  
**AI Response:** 
```
"For last month, the top 3 customers were:
1. Adventure Works - $52,100
2. Contoso Corp - $41,800
3. Fabrikam Inc - $39,200
Note the change in rankings compared to this month."
```

### **Multi-turn Analysis**
**User:** `"Explain the trend for Contoso Corp"`  
**Context:** `[Includes both previous queries]`  
**AI Response:** 
```
"Contoso Corp shows interesting patterns:
- Last month: #2 position with $41,800
- This month: #1 position with $45,230
- Growth: 8.2% month-over-month
This indicates strong business momentum."
```

---

## ⚙️ Technical Implementation

### **Request Processing Flow**
1. **User Input**: Message entered in chat interface
2. **Context Retrieval**: System fetches last 5 conversation pairs
3. **JSON Construction**: Request payload built with prompt, model, and context
4. **API Call**: HTTP POST to backend chat service
5. **Response Processing**: JSON response parsed and validated
6. **Data Storage**: Complete interaction logged to database
7. **UI Update**: Response displayed to user with timestamp

### **Context Management Strategy**
- **Rolling Context Window**: Maintains last 5 Q&A pairs
- **Intelligent Truncation**: Preserves most recent context when size limits exceeded
- **Conversation Continuity**: Enables natural follow-up questions
- **Memory Optimization**: Balances context richness with API efficiency

### **Error Handling**
- **Network Failures**: Graceful handling of connectivity issues
- **API Errors**: Comprehensive error message parsing
- **Validation Errors**: Input sanitization and validation
- **Timeout Management**: Configurable request timeout handling

---

## 🔒 Security & Compliance

### **Data Protection**
- **Data Classification**: All chat data properly classified for privacy compliance
- **Access Control**: Permission-based access to chat functionality
- **Audit Logging**: Complete interaction tracking for compliance
- **Secure Communication**: HTTPS-based API communication

### **Permission Management**
**CopilotPermSet (50103)** provides:
- Table data permissions for chat log access
- Page execution permissions for chat interfaces
- Codeunit execution permissions for HTTP calls
- Extensible permission structure for future enhancements

---

## ⚡ Performance Optimization

### **Efficiency Features**
- **Context Caching**: Optimized context retrieval queries
- **Response Streaming**: Real-time response display
- **Database Indexing**: Efficient chat log queries
- **Memory Management**: Optimized text handling and truncation

### **Scalability Considerations**
- **Asynchronous Processing**: Non-blocking API calls
- **Connection Pooling**: Efficient HTTP client management
- **Log Rotation**: Configurable chat history retention
- **Load Balancing**: Support for multiple AI service endpoints

---

## 🛠️ Configuration & Setup

### **Prerequisites**
- Business Central environment with custom extensions enabled
- Backend AI service running on `localhost:5135`
- Proper network connectivity and firewall configuration
- User permissions configured via CopilotPermSet

### **Model Configuration**
Each supported AI model can be configured for:
- **API Endpoints**: Custom service URLs
- **Authentication**: API key management
- **Rate Limiting**: Request throttling settings
- **Response Formatting**: Output customization

### **Context Settings**
- **History Length**: Number of previous interactions to include
- **Context Size Limit**: Maximum context text length
- **Truncation Strategy**: How to handle oversized context
- **Memory Retention**: Chat log storage duration

---

## 📊 Monitoring & Analytics

### **Key Metrics**
- **Conversation Volume**: Total interactions per day/week/month
- **Response Quality**: User satisfaction indicators
- **Model Performance**: Comparative analysis across AI providers
- **Context Effectiveness**: Impact of conversation history on responses

### **Debugging Features**
- **Raw JSON Logging**: Complete API request/response logging
- **Context Inspection**: View exact context sent to AI models
- **Error Tracking**: Comprehensive error classification and reporting
- **Performance Profiling**: Response time analysis

---

## 🔌 Integration Points

### **Backend API Integration**
- **Chat Endpoint**: `/copilot/chat` for conversational interactions
- **Health Check**: Service availability monitoring
- **Authentication**: Secure API access management
- **Version Control**: API compatibility tracking

### **Business Central Integration**
- **Role Center**: Seamless menu integration
- **Permission System**: Native BC security model integration
- **Data Services**: Integration with BC OData services
- **Event Handling**: Response to BC business events

---

## 🚀 Future Enhancements

### **Planned Features**
- **Multi-language Support**: Localized chat interfaces
- **Voice Integration**: Speech-to-text input capabilities
- **Custom Training**: Domain-specific model fine-tuning
- **Advanced Analytics**: Conversation pattern analysis
- **Mobile Optimization**: Enhanced mobile chat experience

### **Extensibility Points**
- **Plugin Architecture**: Custom AI provider integration
- **Workflow Integration**: Business process automation
- **Custom Commands**: User-defined chat shortcuts
- **Integration APIs**: Third-party system connectivity

---

## 🔧 Troubleshooting

### **Common Issues**
1. **"Failed to contact backend"**: Check API service status and network connectivity
2. **"Failed to parse JSON"**: Verify API response format compatibility
3. **Missing context**: Check chat log permissions and data access
4. **Slow responses**: Monitor API service performance and network latency

### **Debug Information**
The system provides **comprehensive debugging** through:
- **Message displays**: Raw JSON request/response logging
- **Status indicators**: Success/failure state tracking
- **Timestamp analysis**: Performance bottleneck identification
- **Error categorization**: Systematic issue classification

### **Support Resources**
- **Log Analysis Tools**: Built-in chat log analysis
- **Performance Monitoring**: Real-time system health checks
- **User Guides**: Comprehensive documentation
- **Training Materials**: Best practices for AI conversation design

  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

  # RAG Pipeline - Intelligent Knowledge Retrieval System

## Overview

The RAG (Retrieval-Augmented Generation) Pipeline is an advanced AI-powered knowledge retrieval and question-answering system integrated into Microsoft Dynamics 365 Business Central. This system combines vector-based semantic search with local language models to provide intelligent, context-aware responses based on preprocessed financial and business documentation.

## Architecture

The RAG Pipeline implements a sophisticated multi-component architecture:

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Business Central  │────│   JavaScript UI     │────│   Python Backend    │
│   ControlAddIn      │    │   Frontend          │    │   RAG Engine        │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
                                                                │
                           ┌─────────────────────┐    ┌─────────────────────┐
                           │   ChromaDB          │────│   Ollama LLM        │
                           │   Vector Store      │    │   (Mistral 7B)      │
                           └─────────────────────┘    └─────────────────────┘
```

## Core Components

### 1. Business Central Integration

#### ControlAddIn Integration
```al
controladdin "Rag Chat" {
    Scripts = 'xpilotrag.js';
    StartupScript = 'xpilotrag.js';
    StyleSheets = 'ragstyle.css';
    
    RequestedHeight = 1000;
    RequestedWidth = 1500;
    
    MinimumHeight = 600;
    MinimumWidth = 800;
}
```

**Features:**
- **Embedded UI**: Custom JavaScript interface within Business Central
- **Responsive Design**: Adaptive layout with minimum size constraints
- **Real-time Interaction**: Direct communication with RAG backend
- **Seamless Integration**: Native Business Central user experience

### 2. Document Processing Pipeline

#### Data Preprocessing System
The system processes various document formats into structured JSON for optimal retrieval:

**Supported Document Types:**
- PDF files (financial reports, manuals, guides)
- Text documents (policies, procedures)
- Structured data (FAQ, knowledge bases)
- Web content (articles, documentation)

**Processing Workflow:**
1. **Document Ingestion**: Multi-format document loading
2. **Text Extraction**: Clean text extraction with metadata preservation
3. **Chunking Strategy**: Intelligent text segmentation (1000 chars, 200 overlap)
4. **Embedding Generation**: Vector representation creation using ChromaDB
5. **Index Storage**: Persistent vector database storage

#### DocumentChunkProcessor Features
```python
processor = DocumentChunkProcessor(
    chunk_size=1000,      # Optimal chunk size for context retention
    chunk_overlap=200     # Overlap for continuity preservation
)
```

**Chunking Benefits:**
- **Context Preservation**: Maintains semantic meaning across chunks
- **Optimal Retrieval**: Balanced chunk size for accurate search
- **Memory Efficiency**: Manageable context windows for LLM processing
- **Scalable Processing**: Handles large document collections efficiently

### 3. Vector Database System

#### ChromaDB Integration
Advanced vector storage and retrieval using ChromaDB for semantic search capabilities.

**Key Features:**
- **Persistent Storage**: Durable vector index storage
- **Semantic Search**: Context-aware document retrieval
- **Similarity Scoring**: Relevance-based result ranking
- **Incremental Updates**: Add new documents without full rebuild
- **Collection Management**: Organized document categorization

**Vector Store Capabilities:**
```python
class VectorStoreManager:
    - create_vectorstore(chunks)      # Create embeddings and index
    - load_vectorstore()              # Load existing vector database
    - search_similar(query, k=5)      # Semantic similarity search
    - get_collection_stats()          # Database statistics
    - delete_collection()             # Database management
```

### 4. Context Retrieval Engine

#### ContextRetriever System
Intelligent context assembly for optimal LLM performance.

**Retrieval Strategy:**
1. **Query Analysis**: Understanding user intent and context
2. **Semantic Search**: Vector-based similarity matching
3. **Result Ranking**: Relevance-based chunk scoring
4. **Context Assembly**: Intelligent chunk combination
5. **Metadata Enrichment**: Source attribution and categorization

**Context Optimization:**
- **Relevance Filtering**: Only high-confidence matches included
- **Length Management**: Optimal context size for LLM processing
- **Source Tracking**: Complete audit trail for responses
- **Diversity Balance**: Multiple perspectives in context assembly

### 5. Local LLM Integration

#### Ollama + Mistral 7B Configuration
Self-hosted language model for secure, private AI processing.

**Model Specifications:**
- **Model**: Mistral 7B (mistral:latest)
- **Host**: Local Ollama server (localhost:11434)
- **Context Window**: 8K tokens
- **Response Quality**: High-quality financial and business advice
- **Privacy**: Complete data sovereignty and security

**LLM Features:**
```python
class OllamaQueryEngine:
    - Multi-model support (Mistral, Llama, etc.)
    - Configurable system prompts
    - Temperature control for response consistency
    - Token limit management
    - Response streaming capabilities
    - Error handling and retry logic
```

## System Workflow

### 1. Query Processing Flow
```
User Query → Context Retrieval → LLM Processing → Response Generation → UI Display
```

**Detailed Process:**
1. **User Input**: Natural language query via Business Central UI
2. **Vector Search**: Semantic matching against document corpus
3. **Context Assembly**: Relevant chunks combined into coherent context
4. **Prompt Construction**: System prompt + context + user query
5. **LLM Generation**: Local Mistral model processes complete prompt
6. **Response Formatting**: Structured response with source attribution
7. **UI Rendering**: Rich response display with source links

### 2. Knowledge Base Management

#### Dynamic Dataset Management
```python
# Add new documents without full rebuild
def add_to_knowledge_base(new_documents):
    chunks = processor.process_documents(new_documents)
    vector_manager.add_chunks(chunks)
    return f"Added {len(chunks)} new chunks to knowledge base"
```

**Benefits:**
- **Incremental Updates**: Add knowledge without system downtime
- **Version Control**: Track document versions and updates
- **Selective Rebuild**: Rebuild only affected portions
- **Scalable Growth**: Handle expanding knowledge bases efficiently

### 3. Interactive Query Session

#### RAGSystem Interactive Features
```python
def interactive_session(self):
    # Commands available:
    # - exit: Quit session
    # - help: Show available commands
    # - stats: Display system statistics
    # - Direct queries: Natural language questions
```

**User Experience:**
- **Natural Language Interface**: Conversational interaction style
- **Real-time Responses**: Immediate feedback and results
- **Source Attribution**: Clear citation of information sources
- **System Monitoring**: Performance and usage statistics
- **Help System**: Built-in guidance and documentation

## Technical Implementation

### Core Classes and Functions

#### RAGSystem (Main Controller)
```python
class RAGSystem:
    def setup(force_recreate_db, chunk_size, chunk_overlap)
    def query(question, **kwargs)
    def batch_query(questions, **kwargs)
    def interactive_session()
    def get_system_info()
```

#### OllamaQueryEngine (LLM Interface)
```python
class OllamaQueryEngine:
    def __init__(context_retriever, model_name, ollama_url, system_prompt)
    def query(user_query, k=5, context_options, generation_options)
    def batch_query(queries, k=5, context_options, generation_options)
    def interactive_session()
```

#### External API Function
```python
def run_rag_on_text(prompt: str, additional_context: str = "") -> str:
    """
    Entry point for external applications (FastAPI, Business Central)
    Processes queries and returns AI-generated responses
    """
```

### System Prompt Engineering

#### Financial Advisory System Prompt
```python
system_prompt = """
You are a knowledgeable financial advisor assistant. Your task is to provide helpful, accurate, and practical financial advice based on the provided context.

Guidelines:
1. Answer questions based primarily on the provided context
2. Be clear and concise in your responses
3. If the context doesn't contain relevant information, say so clearly
4. Provide practical, actionable advice when possible
5. Always be professional and helpful
6. Express uncertainty when appropriate
7. Remind users to consult qualified professionals for personalized advice
8. Provide balanced, unbiased information
9. Consider the user's financial well-being in all responses
"""
```

## Configuration and Setup

### Prerequisites
```bash
# Python Requirements
Python >= 3.8
pip install -r requirements.txt

# Ollama Installation
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull mistral:latest

# ChromaDB Setup
# Automatically handled by Python dependencies
```

### Environment Configuration
```python
# Default Configuration
DATA_PATH = "processed_data/training_data.json"
VECTOR_DB_PATH = "chroma_db"
MODEL_NAME = "mistral:latest"
OLLAMA_URL = "http://localhost:11434"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
```

### System Initialization
```python
# Automatic Setup
rag = RAGSystem()
success = rag.setup(
    force_recreate_db=False,  # Use existing DB if available
    chunk_size=1000,          # Optimal chunk size
    chunk_overlap=200         # Context preservation
)
```

## Performance Optimization

### Vector Search Optimization
- **Embedding Caching**: Reuse embeddings for repeated queries
- **Index Optimization**: Efficient vector similarity algorithms
- **Parallel Processing**: Concurrent document processing
- **Memory Management**: Optimized memory usage for large datasets

### LLM Performance Tuning
- **Context Window Management**: Optimal context size utilization
- **Temperature Control**: Balanced creativity vs. consistency
- **Token Limit Optimization**: Efficient prompt construction
- **Response Caching**: Cache common queries for speed

### Database Management
- **Collection Statistics**: Monitor database health and performance
- **Index Maintenance**: Periodic optimization and cleanup
- **Storage Optimization**: Efficient disk space utilization
- **Backup Strategies**: Regular data backup and recovery

## Integration Examples

### Business Central Integration
```javascript
// xpilotrag.js - Frontend integration
function queryRAG(userQuestion) {
    // Send query to Python backend
    fetch('/rag/query', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            prompt: userQuestion,
            context: getBusinessContext()
        })
    })
    .then(response => response.json())
    .then(data => displayResponse(data));
}
```

### FastAPI Integration
```python
# API endpoint for external access
@app.post("/rag/query")
async def query_rag(request: QueryRequest):
    response = run_rag_on_text(
        prompt=request.prompt,
        additional_context=request.context
    )
    return {"response": response, "success": True}
```

## Monitoring and Analytics

### System Statistics
```python
def get_system_stats():
    return {
        "vector_database": {
            "total_documents": count,
            "total_chunks": chunk_count,
            "embedding_model": model_name,
            "collection_size": size_mb
        },
        "llm_model": {
            "name": "mistral:latest",
            "status": "available",
            "average_response_time": time_ms,
            "total_queries": query_count
        },
        "performance": {
            "queries_per_minute": qpm,
            "average_accuracy": accuracy_score,
            "user_satisfaction": rating
        }
    }
```

### Query Analytics
- **Response Quality**: Accuracy and relevance metrics
- **Performance Metrics**: Response time and throughput
- **Usage Patterns**: Popular queries and topics
- **Error Tracking**: System reliability monitoring

## Security and Privacy

### Data Protection
- **Local Processing**: All data remains on-premises
- **No External APIs**: Complete data sovereignty
- **Encrypted Storage**: Secure vector database storage
- **Access Control**: Business Central permission integration

### Compliance Features
- **Audit Logging**: Complete interaction tracking
- **Data Classification**: Sensitive information handling
- **User Attribution**: Query source tracking
- **Retention Policies**: Configurable data lifecycle management

## Troubleshooting

### Common Issues
1. **Ollama Connection Failed**
   - Verify Ollama service is running: `systemctl status ollama`
   - Check model availability: `ollama list`
   - Verify network connectivity: `curl localhost:11434/api/tags`

2. **Vector Database Issues**
   - Recreate database: `--recreate-db` flag
   - Check disk space and permissions
   - Verify ChromaDB installation

3. **Poor Response Quality**
   - Verify training data quality and relevance
   - Adjust chunk size and overlap parameters
   - Review and optimize system prompts

4. **Performance Issues**
   - Monitor system resources (CPU, Memory, Disk)
   - Optimize chunk size for your use case
   - Consider hardware upgrades for large datasets

### Debug Information
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# System health check
def health_check():
    return {
        "ollama_status": check_ollama_connection(),
        "vector_db_status": check_vector_database(),
        "python_dependencies": check_requirements(),
        "system_resources": get_resource_usage()
    }
```

## Future Enhancements

### Planned Features
- **Multi-language Support**: Support for multiple languages
- **Advanced Analytics**: Detailed usage and performance analytics
- **Custom Models**: Support for additional LLM models
- **API Extensions**: Enhanced integration capabilities
- **Real-time Updates**: Live knowledge base synchronization

### Extensibility Options
- **Custom Embeddings**: Support for specialized embedding models
- **Plugin Architecture**: Extensible processing pipeline
- **Integration APIs**: Third-party system connectivity
- **Custom UI Components**: Enhanced Business Central interfaces

## Best Practices

### Knowledge Base Management
- **Regular Updates**: Keep knowledge base current and relevant
- **Quality Control**: Ensure document quality and accuracy
- **Version Management**: Track document versions and changes
- **Performance Monitoring**: Regular system health checks

### Query Optimization
- **Clear Questions**: Encourage specific, well-formed queries
- **Context Provision**: Include relevant business context
- **Feedback Integration**: Use response quality feedback
- **Iterative Improvement**: Continuously refine based on usage patterns

### System Maintenance
- **Regular Backups**: Protect vector database and configurations
- **Performance Tuning**: Optimize based on usage patterns
- **Security Updates**: Keep all components up to date
- **Monitoring**: Implement comprehensive system monitoring

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Hybrid Recognition Pattern - Intelligent Intent Classification System

## Overview

The Hybrid Recognition Pattern is an advanced AI-powered intent classification system that intelligently analyzes user inputs and automatically routes them to the most appropriate processing endpoint within the Business Central AI Copilot system. This pattern bridges conversational AI (questions) with command execution (actions) through sophisticated LLM-based classification, providing users with a seamless, unified interface regardless of their intent.

## Architecture

The Hybrid Recognition Pattern implements a three-tier intelligent routing architecture:

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   User Input        │────│   Intent Classifier │────│   Endpoint Router   │
│   (Natural Language)│    │   (LLM Analysis)    │    │   (Smart Dispatch)  │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
                                      │
                           ┌─────────────────────┐
                           │   Unified Interface │
                           │   (Single Entry)    │
                           └─────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
            ┌───────▼───────┐ ┌───────▼───────┐ ┌───────▼───────┐
            │   Chat        │ │   Command     │ │   RAG         │
            │   Endpoint    │ │   Execution   │ │   Knowledge   │
            │   (/chat)     │ │   (/command)  │ │   (/insights) │
            └───────────────┘ └───────────────┘ └───────────────┘
```

## Core Components

### 1. Intent Classification Engine

#### UnifiedClassifierHTTP (Codeunit 50102)
The core classification codeunit that determines user intent through LLM analysis.

**Key Features:**
- **LLM-Powered Classification**: Uses AI models to understand user intent
- **Multi-Endpoint Support**: Routes to appropriate specialized endpoints
- **Fallback Handling**: Graceful handling of ambiguous inputs
- **Real-time Processing**: Instant classification and routing

**Main Methods:**
```al
procedure ClassifyPrompt(Message: Text; ModelUsed: Text): Text
local procedure ParseLLmClassification(JsonText: Text; var Classification: Text)
local procedure BuildJson(prompt: Text; model: Text): Text
```

**Classification Workflow:**
1. **Input Analysis**: User message analyzed by LLM
2. **Intent Detection**: AI determines whether input is question or command
3. **Confidence Scoring**: Classification confidence assessment
4. **Route Selection**: Appropriate endpoint selection based on intent
5. **Response Routing**: Results channeled back through unified interface

### 2. Unified Interface System

#### Copilot Chat ControlAddIn
Advanced JavaScript-based interface providing seamless user interaction across all AI capabilities.

**ControlAddIn Configuration:**
```al
controladdin "Copilot Chat"
{
    Scripts = 'ControlAddins/xpilot.js';
    StartupScript = 'ControlAddins/xpilot.js';
    StyleSheets = 'ControlAddins/xpilotStyle.css';
    
    RequestedHeight = 1000;
    RequestedWidth = 1500;
    MinimumHeight = 600;
    MinimumWidth = 800;
}
```

**Event Architecture:**
```al
event SendPrompt(PromptText: Text; ModelName: Text);        // Question handling
event SendCommand(PromptText: Text; ModelName: Text);       // Command execution
event SendClassification(Message: Text; ModelName: Text);   // Intent classification
procedure ReceiveALResponse(ResponseText: Text);            // Unified response handling
```

### 3. Smart Routing System

#### Copilot Chat Launcher (Page 50115)
The orchestration page that manages routing between different AI capabilities based on classification results.

**Routing Logic:**
```al
trigger SendPrompt(PromptText: Text; ModelName: Text)
// Routes to conversational AI for questions and general queries

trigger SendCommand(PromptText: Text; ModelName: Text)  
// Routes to command execution for CRUD operations and actions

trigger SendClassification(Message: Text; ModelName: Text)
// Routes to intent classifier for intelligent routing decisions
```

**Integration Points:**
- **HTTP Calls Handler**: Manages conversational AI interactions
- **AgentCommandSender**: Handles structured command execution
- **UnifiedClassifierHTTP**: Provides intelligent intent classification

## Intent Classification Types

### 1. Question Classification
**Characteristics:**
- Information seeking queries
- "What", "How", "When", "Where", "Why" patterns
- Requests for explanations or data retrieval
- Conversational context requirements

**Examples:**
```
"What are my top customers this month?"
"How do I calculate VAT for international sales?"
"When was the last purchase order created?"
"Explain the difference between gross and net profit"
```

**Processing Flow:**
```
User Input → Classification → "Question" → Chat Endpoint → LLM Response → User Interface
```

### 2. Command Classification
**Characteristics:**
- Action-oriented requests
- CRUD operation indicators
- Imperative language patterns
- Specific data manipulation requests

**Examples:**
```
"Create a new customer named John Smith"
"Update customer CUST001 with new phone number"
"Delete the expired purchase order PO123"
"Add a new item to inventory with SKU ABC123"
```

**Processing Flow:**
```
User Input → Classification → "Command" → Command Endpoint → Business Logic → Database → User Interface
```

### 3. Hybrid/Complex Classification
**Characteristics:**
- Combined information and action requests
- Multi-step operations
- Conditional logic requirements
- Context-dependent processing

**Examples:**
```
"Show me customers with overdue invoices and send them reminders"
"Find items with low stock and create purchase orders"
"List today's orders and mark urgent ones as priority"
```

**Processing Flow:**
```
User Input → Classification → "Hybrid" → Multi-Endpoint → Orchestrated Response → User Interface
```

## Technical Implementation

### Classification Algorithm

#### LLM-Based Intent Recognition
```python
# Backend classification logic (conceptual)
def classify_intent(prompt: str, model: str) -> dict:
    system_prompt = """
    Analyze the user input and classify it as either:
    - "question": Information seeking, explanatory, or conversational
    - "command": Action requests, CRUD operations, or data manipulation
    - "hybrid": Complex requests requiring both information and actions
    
    Consider:
    - Language patterns (interrogative vs. imperative)
    - Action indicators ("create", "update", "delete", "add")
    - Information indicators ("what", "how", "show", "explain")
    - Business context and intent
    """
    
    response = llm.generate(
        prompt=f"{system_prompt}\n\nUser Input: {prompt}",
        model=model
    )
    
    return {
        "type": extract_classification(response),
        "confidence": calculate_confidence(response),
        "reasoning": extract_reasoning(response)
    }
```

#### Classification Response Format
```json
{
    "type": "command|question|hybrid",
    "confidence": 0.95,
    "reasoning": "Input contains imperative language with specific action request",
    "suggested_endpoint": "/copilot/command",
    "parameters": {
        "entity_type": "customer",
        "action": "create",
        "attributes": ["name", "location"]
    }
}
```

### Endpoint Routing Logic

#### Smart Dispatch Algorithm
```al
procedure RouteBasedOnClassification(Classification: Text; Message: Text; ModelUsed: Text): Text
var
    Result: Text;
begin
    case Classification of
        'question':
            Result := ProcessAsQuestion(Message, ModelUsed);
        'command':
            Result := ProcessAsCommand(Message, ModelUsed);
        'hybrid':
            Result := ProcessAsHybrid(Message, ModelUsed);
        else
            Result := ProcessWithFallback(Message, ModelUsed);
    end;
    
    exit(Result);
end;
```

### Error Handling and Fallbacks

#### Graceful Degradation Strategy
```al
local procedure HandleClassificationFailure(Message: Text; ModelUsed: Text): Text
var
    FallbackResult: Text;
begin
    // Attempt pattern-based classification
    if ContainsActionKeywords(Message) then
        FallbackResult := ProcessAsCommand(Message, ModelUsed)
    else
        FallbackResult := ProcessAsQuestion(Message, ModelUsed);
    
    // Log fallback usage for system improvement
    LogFallbackUsage(Message, 'classification_failure');
    
    exit(FallbackResult);
end;
```

## User Experience Flow

### 1. Unified Input Experience
```javascript
// xpilot.js - Simplified user interaction
function handleUserInput(userMessage, selectedModel) {
    // Single input field handles all types of requests
    showProcessingIndicator();
    
    // Send for classification first
    classifyAndRoute(userMessage, selectedModel)
        .then(response => {
            displayResponse(response);
            updateConversationHistory(userMessage, response);
        })
        .catch(error => {
            handleError(error);
        });
}
```

### 2. Progressive Enhancement
```javascript
// Enhanced UI with classification feedback
function displayClassificationFeedback(classification) {
    const indicators = {
        'question': '💬 Answering your question...',
        'command': '⚙️ Executing command...',
        'hybrid': '🔄 Processing complex request...'
    };
    
    showStatusMessage(indicators[classification.type]);
}
```

### 3. Response Integration
```javascript
// Unified response handling regardless of source endpoint
function displayResponse(response, classification) {
    const responseContainer = document.getElementById('response-area');
    
    // Add classification-specific styling and icons
    const classificationClass = `response-${classification.type}`;
    responseContainer.className += ` ${classificationClass}`;
    
    // Display response with appropriate formatting
    renderResponse(response, classification);
    
    // Show source attribution
    showSourceAttribution(classification.endpoint);
}
```

## Performance Optimization

### Classification Caching
```al
// Cache common classifications to reduce LLM calls
local procedure GetCachedClassification(Message: Text): Text
var
    ClassificationCache: Record "Classification Cache";
begin
    ClassificationCache.SetRange("Input Hash", CalculateHash(Message));
    if ClassificationCache.FindFirst() then
        exit(ClassificationCache.Classification);
    
    exit(''); // Not cached
end;
```

### Parallel Processing
```al
// Process classification and prepare endpoints simultaneously
local procedure OptimizedRouting(Message: Text; ModelUsed: Text): Text
var
    ClassificationTask: Task;
    PreparationTask: Task;
begin
    // Start classification
    ClassificationTask := StartClassificationTask(Message, ModelUsed);
    
    // Prepare endpoints in parallel
    PreparationTask := PrepareEndpointsTask();
    
    // Wait for classification and route accordingly
    WaitForClassification(ClassificationTask);
    RouteToAppropriateEndpoint(GetTaskResult(ClassificationTask));
end;
```

## Integration Examples

### Business Scenario Examples

#### Customer Management
```
Input: "Show me details for customer CUST001 and update their credit limit to 50000"
Classification: "hybrid"
Processing: 
  1. Query customer details (question endpoint)
  2. Update credit limit (command endpoint)
  3. Combine responses for unified display
```

#### Inventory Operations
```
Input: "What items have stock below 10 units?"
Classification: "question"
Processing: Query endpoint → Database search → Formatted results

Input: "Create purchase orders for items below minimum stock"
Classification: "command"  
Processing: Command endpoint → Business logic → PO creation → Confirmation
```

#### Financial Analysis
```
Input: "Generate monthly sales report"
Classification: "question"
Processing: Analytics endpoint → Report generation → PDF output

Input: "How do I post a sales invoice?"
Classification: "question"
Processing: Knowledge base → Procedure explanation → Step-by-step guide
```

## Monitoring and Analytics

### Classification Accuracy Metrics
```al
procedure TrackClassificationAccuracy(OriginalClassification: Text; UserFeedback: Text; Message: Text)
var
    AccuracyLog: Record "Classification Accuracy Log";
begin
    AccuracyLog."Message Hash" := CalculateHash(Message);
    AccuracyLog."Original Classification" := OriginalClassification;
    AccuracyLog."User Feedback" := UserFeedback;
    AccuracyLog."Accuracy Score" := CalculateAccuracy(OriginalClassification, UserFeedback);
    AccuracyLog."Timestamp" := CurrentDateTime();
    AccuracyLog.Insert();
end;
```

### Performance Metrics
```al
procedure LogClassificationPerformance(Message: Text; Classification: Text; ProcessingTime: Duration)
var
    PerformanceLog: Record "Classification Performance Log";
begin
    PerformanceLog."Classification Type" := Classification;
    PerformanceLog."Processing Time (ms)" := ProcessingTime;
    PerformanceLog."Message Length" := StrLen(Message);
    PerformanceLog."Success" := true;
    PerformanceLog."Timestamp" := CurrentDateTime();
    PerformanceLog.Insert();
end;
```

## Security and Compliance

### Input Validation
```al
local procedure ValidateInput(Message: Text): Boolean
var
    ValidationRules: Record "Input Validation Rules";
begin
    // Check message length
    if StrLen(Message) > GetMaxMessageLength() then
        exit(false);
    
    // Check for prohibited content
    if ContainsProhibitedContent(Message) then
        exit(false);
    
    // Validate against business rules
    ValidationRules.SetRange("Active", true);
    if ValidationRules.FindSet() then begin
        repeat
            if not ValidateAgainstRule(Message, ValidationRules) then
                exit(false);
        until ValidationRules.Next() = 0;
    end;
    
    exit(true);
end;
```

### Audit Trail
```al
procedure LogClassificationRequest(Message: Text; Classification: Text; UserID: Code[50])
var
    AuditLog: Record "Classification Audit Log";
begin
    AuditLog."Entry No." := GetNextEntryNo();
    AuditLog."User ID" := UserID;
    AuditLog."Message Hash" := CalculateSecureHash(Message);
    AuditLog."Classification" := Classification;
    AuditLog."Timestamp" := CurrentDateTime();
    AuditLog."Session ID" := GetSessionID();
    AuditLog.Insert();
end;
```

## Future Enhancements

### Advanced Classification Features
- **Multi-Intent Recognition**: Handle complex requests with multiple intents
- **Context-Aware Classification**: Consider conversation history in classification
- **Learning from Corrections**: Improve classification based on user feedback
- **Custom Classification Rules**: Business-specific classification logic

### Enhanced Routing Capabilities
- **Load Balancing**: Distribute requests across multiple endpoint instances
- **Priority Routing**: Route urgent requests to high-priority endpoints
- **Conditional Routing**: Route based on user roles and permissions
- **Async Processing**: Handle long-running operations asynchronously

### User Experience Improvements
- **Classification Confidence Display**: Show classification certainty to users
- **Route Explanation**: Explain why a particular endpoint was chosen
- **Manual Override**: Allow users to manually specify routing
- **Feedback Integration**: Incorporate user feedback for continuous improvement

## Best Practices

### Classification Prompt Engineering
- **Clear Instructions**: Provide specific classification criteria to LLM
- **Example-Based Learning**: Include examples of each classification type
- **Context Consideration**: Account for business domain and user context
- **Confidence Calibration**: Request confidence scores with classifications

### Error Handling Strategies
- **Graceful Fallbacks**: Always provide a reasonable default behavior
- **User Communication**: Clearly explain what happened when classification fails
- **Retry Logic**: Implement intelligent retry mechanisms
- **Logging and Monitoring**: Comprehensive error tracking and analysis

### Performance Optimization
- **Classification Caching**: Cache frequent classifications
- **Parallel Processing**: Process classification and endpoint preparation concurrently
- **Resource Management**: Optimize memory and CPU usage
- **Response Time Monitoring**: Track and optimize classification speed

## Troubleshooting

### Common Issues

1. **Classification Accuracy Problems**
   ```al
   // Diagnostic procedure
   procedure DiagnoseClassificationIssues()
   begin
       // Check model availability
       VerifyLLMModelAccess();
       
       // Validate prompt engineering
       TestClassificationPrompts();
       
       // Review feedback logs
       AnalyzeUserFeedbackPatterns();
   end;
   ```

2. **Routing Failures**
   ```al
   // Endpoint health check
   procedure VerifyEndpointHealth()
   begin
       CheckChatEndpointAvailability();
       CheckCommandEndpointAvailability();
       CheckRAGEndpointAvailability();
   end;
   ```

3. **Performance Issues**
   ```al
   // Performance analysis
   procedure AnalyzePerformanceBottlenecks()
   begin
       MeasureClassificationLatency();
       AnalyzeEndpointResponseTimes();
       ReviewCacheHitRates();
   end;
   ```

### Debug Information
```al
procedure GetClassificationDebugInfo(Message: Text): Text
var
    DebugInfo: JsonObject;
begin
    DebugInfo.Add('message_length', StrLen(Message));
    DebugInfo.Add('contains_action_keywords', ContainsActionKeywords(Message));
    DebugInfo.Add('contains_question_patterns', ContainsQuestionPatterns(Message));
    DebugInfo.Add('classification_cache_hit', IsCachedClassification(Message));
    DebugInfo.Add('endpoint_availability', CheckAllEndpoints());
    
    exit(FormatJson(DebugInfo));
end;
```

This Hybrid Recognition Pattern represents a sophisticated approach to creating truly intelligent, unified AI interfaces that can seamlessly handle diverse user intents while maintaining optimal performance and user experience.


------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# AI Copilot .NET API - Project Structure Overview

This .NET API serves as the backend service for the AI Copilot system integrated with Microsoft Dynamics 365 Business Central. It acts as a middleware layer between the Business Central AL extensions and multiple LLM providers, handling natural language processing, command execution, and data operations.

## 🏗️ Architecture Overview

The API follows a clean, layered architecture pattern implementing the **Controller-DTO-DAO-Service** pattern with clear separation of concerns:

```
📁 AI-Copilot-API/
├── 📁 Controllers/          # API endpoints and request handling
├── 📁 DTOs/                 # Data Transfer Objects for API communication
├── 📁 DAOs/                 # Data Access Objects for database operations
├── 📁 Services/             # Business logic and external integrations
├── 📁 Models/               # Domain entities and data models
├── 📁 Mappers/              # Object mapping between layers
├── 📁 Interfaces/           # Contracts and service abstractions
├── 📁 Utils/                # Utility classes and helpers
└── 📁 Connected Services/   # External service references
```

## 🎯 Core Components

### Controllers Layer
- **ChatController.cs**: Handles natural language chat interactions with LLMs
- **CopilotCommandController.cs**: Processes structured commands and Business Central operations
- **UnifiedIntentController.cs**: Routes requests based on intent classification (chat vs command)

### Data Access Layer (DAOs)
- **CopilotEntityDao.cs**: Manages AI interaction logs and metadata
- **CustomerDao.cs**: Handles customer data operations (example BC entity)
- **ICopilotEntityDao.cs**: Interface for copilot entity operations
- **ICustomerDao.cs**: Interface for customer operations

### Data Transfer Objects (DTOs)
- **CommandParsedDTO.cs**: Structured command parsing results
- **CommandRequestDTO.cs**: Incoming command request format
- **CommandResponseDTO.cs**: Command execution response format
- **PromptClassificationRequestDTO.cs**: Intent classification input
- **PromptClassificationResponseDTO.cs**: Intent classification output
- **PromptRequestDTO.cs**: LLM prompt request structure
- **PromptResponseDTO.cs**: LLM response structure

### Business Logic Layer (Services)
- **ChatService.cs**: Core chat functionality and LLM integration
- **CommandService.cs**: Command parsing and Business Central operations
- **ICommandService.cs**: Command service interface
- **IIntentParserService.cs**: Intent classification service interface
- **ILlmService.cs**: LLM provider abstraction
- **IntentParserService.cs**: AI-powered intent recognition
- **LlmService.cs**: Multi-provider LLM integration
- **ModelRouter.cs**: Dynamic LLM provider routing

### Domain Models
- **CopilotEntity.cs**: Represents AI interaction records in BC
- **Customer.cs**: Represents customer entities from BC
- **LLMProviderConfig.cs**: LLM provider configuration model
- **LLMSettings.cs**: LLM service settings

### Object Mappers
- **ILlmToDomainMapper.cs**: Interface for LLM response mapping
- **LlmToCopilotEntityMapper.cs**: Maps LLM responses to copilot entities
- **LlmToCustomerMapper.cs**: Maps LLM responses to customer entities

## 🔌 Integration Points

### Business Central Integration
- **OData Web Services**: Direct integration with BC's REST APIs
- **Two Custom Tables**: 
  - `CopilotEntity`: Stores AI interactions, commands, and responses
  - `CustomerOdata`: Extended customer data for AI operations
- **NTLM Authentication**: Secure connection to BC environment

### Multi-LLM Provider Support
- **OpenAI**: GPT models for conversational AI
- **Anthropic**: Claude models for advanced reasoning
- **Mistral**: Open-source LLM integration
- **Together AI**: Mixtral model access
- **Groq**: High-performance LLaMA3 inference

## 🔧 Configuration Requirements

### ⚠️ **CRITICAL: Configuration Setup**

The application requires two configuration files that are **excluded from version control**:

#### 1. `appsettings.json` (Add to .gitignore)
```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  },
  "AllowedHosts": "*",
  "LLMProviders": [
    {
      "Name": "GPT-4",
      "Provider": "openai",
      "ModelName": "gpt-3.5-turbo",
      "Model": "gpt-3.5-turbo",
      "BaseUrl": "https://api.openai.com/v1/chat/completions",
      "ApiKey": "OPENAI_API_KEY",
      "RequiresKey": true
    },
    {
      "Name": "Claude 3 Opus",
      "Provider": "anthropic",
      "ModelName": "claude-3-opus-20240229",
      "Model": "claude-3",
      "BaseUrl": "https://api.anthropic.com/v1/messages",
      "ApiKey": "ANTHROPIC_API_KEY",
      "RequiresKey": true
    },
    {
      "Name": "Mistral Medium",
      "Provider": "mistral",
      "ModelName": "mistral-medium-latest",
      "Model": "mistral-7b",
      "BaseUrl": "https://api.mistral.ai/v1/chat/completions",
      "ApiKey": "MISTRAL_API_KEY",
      "RequiresKey": true
    },
    {
      "Name": "Together AI Mixtral",
      "Provider": "together",
      "ModelName": "mistralai/Mixtral-8x7B-Instruct-v0.1",
      "Model": "together-ai",
      "BaseUrl": "https://api.together.xyz/v1/chat/completions",
      "ApiKey": "TOGETHER_API_KEY",
      "RequiresKey": true
    },
    {
      "Name": "Groq LLaMA3",
      "Provider": "groq",
      "ModelName": "llama3-8b-8192",
      "Model": "groq",
      "BaseUrl": "https://api.groq.com/openai/v1/chat/completions",
      "ApiKey": "GROQ_API_KEY",
      "RequiresKey": true
    }
  ],
  "OData": {
    "AuthType": "NTLM",
    "Username": "",
    "Password": "",
    "CustomerUrl": "http://yessine:7048/BC250/ODataV4/Company('CRONUS France S.A.')",
    "CopilotEntityUrl": "http://yessine:7048/BC250/ODataV4/Company('CRONUS France S.A.')",
    "CustomerUrlFull": "http://yessine:7048/BC250/ODataV4/Company('CRONUS France S.A.')/CustomerOdata",
    "CopilotEntityUrlFull": "http://yessine:7048/BC250/ODataV4/Company('CRONUS France S.A.')/CopilotEntityOData"
  }
}
```

#### 2. `secrets.json` (User Secrets - Never commit)
```json
{
  "LLMApiKeys": {
    "OPENAI_API_KEY": "your-openai-api-key",
    "ANTHROPIC_API_KEY": "your-anthropic-api-key",
    "MISTRAL_API_KEY": "your-mistral-api-key",
    "TOGETHER_API_KEY": "your-together-api-key",
    "GROQ_API_KEY": "your-groq-api-key"
  }
}
```

## 🔄 Data Flow Architecture

1. **Request Reception**: Controllers receive HTTP requests from BC AL extensions
2. **Intent Classification**: UnifiedIntentController determines if request is chat or command
3. **Processing Pipeline**:
   - **Chat Flow**: ChatService → LlmService → LLM Provider → Response
   - **Command Flow**: CommandService → BC OData → Action Execution → Response
4. **Data Persistence**: All interactions logged to CopilotEntity table via DAO layer
5. **Response Mapping**: Mappers convert internal models to appropriate DTOs
6. **Response Delivery**: Structured JSON response sent back to BC interface

## 🚀 Key Features

### Multi-Provider LLM Integration
- Dynamic provider selection based on request type
- Unified interface for different LLM APIs
- Automatic fallback and error handling
- Provider-specific response parsing

### Intelligent Command Processing
- Natural language to structured command conversion
- Business Central OData operation execution
- CRUD operations on BC entities
- Real-time data validation and error handling

### Agentic Architecture
- Intent-based request routing
- Context-aware response generation
- Interaction logging for continuous improvement
- Stateful conversation management

### Scalable Design
- Clean separation of concerns
- Interface-driven development
- Dependency injection ready
- Easy to extend with new providers or entities

## 🔮 Future Enhancements

- **Full Database Integration**: Expand beyond two custom tables to entire BC database
- **RAG Implementation**: Integration with ChromaDB and FastAPI for enhanced context
- **Advanced Caching**: Response caching for improved performance
- **Monitoring & Analytics**: Comprehensive logging and metrics collection
- **Multi-tenant Support**: Support for multiple BC companies/environments

## ⚠️ **Environment-Specific Implementation Notice**

**This project is configured for Business Central version 250 on a specific development instance.** 

If you plan to use this code:
- **Adapt all configurations** to match your BC environment and version
- **Create equivalent custom tables** in your BC instance (CopilotEntity and CustomerOdata)  
- **Update all OData URLs** in appsettings.json to point to your BC server
- **Modify company names** and database references accordingly

For complete setup instructions and table structures, refer to the **full project report** and BC AL extension documentation.

---

**Next Steps**: Continue with detailed documentation for each layer, starting with Models and Interfaces, then moving through DAOs, Services, DTOs, and finally Controllers.

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
**Contributing**
Fork the repository.
Create a feature branch.
Commit changes.
Push and open a Pull Request.
**License**
MIT License. See LICENSE for details.
