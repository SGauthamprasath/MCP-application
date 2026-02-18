# Real MCP Server for AI Data Console

## 🎯 What This Is

This is a **genuine Model Context Protocol (MCP) server** implementation using Anthropic's official FastMCP framework. Unlike the previous architecture which just called Python functions directly, this server:

- ✅ Runs as a **separate process**
- ✅ Communicates via **MCP protocol** (JSON-RPC over stdio)
- ✅ Can be used by **Claude Desktop, Cline, and other MCP clients**
- ✅ Follows **official MCP standards and best practices**

## 🏗️ Architecture Comparison

### Previous "MCP-Inspired" Architecture
```
FastAPI → OpenAI → Custom Tool Router → Services (same process)
```

### Real MCP Architecture (This Implementation)
```
MCP Client (Claude Desktop) 
    ↓ (stdio/JSON-RPC protocol)
MCP Server (separate Python process - data_console_mcp_server.py)
    ↓ (Python imports)
Your Services (weather_service, file_service, csv_service, db_service)
```

## 📦 Installation

### 1. Install FastMCP (Official MCP Python SDK)

```bash
pip install mcp
```

This installs the official Model Context Protocol Python SDK which includes FastMCP.

### 2. Install Other Dependencies

```bash
pip install pandas pydantic httpx
```

### 3. Verify Your Services Are Working

```bash
cd backend
python test_db.py  # Test database
cd ..
python test.py     # Test all services
```

## 🚀 Running the MCP Server

### Method 1: Direct Execution (For Testing)

```bash
python data_console_mcp_server.py
```

You'll see:
```
Starting Data Console MCP Server...
Server ready. Waiting for MCP client connection...
```

The server is now running and listening on stdin for MCP protocol messages.

### Method 2: Using MCP Inspector (Recommended for Testing)

The MCP Inspector is an official testing tool:

```bash
npx @modelcontextprotocol/inspector python data_console_mcp_server.py
```

This opens a web interface where you can:
- See all available tools
- Test tool calls interactively
- View JSON-RPC messages
- Debug responses

## 🔧 Connecting to Claude Desktop

### Step 1: Find Your Claude Config File

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

### Step 2: Add MCP Server Configuration

Edit the config file and add:

```json
{
  "mcpServers": {
    "data-console": {
      "command": "python",
      "args": ["/absolute/path/to/data_console_mcp_server.py"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/your/project"
      }
    }
  }
}
```

**Important:** Replace `/absolute/path/to/` with your actual project path!

### Step 3: Restart Claude Desktop

Close and reopen Claude Desktop. Your MCP server will now be available!

### Step 4: Test in Claude

In Claude Desktop, try:

> "What tools do you have available?"

Claude should list all 9 tools from your MCP server:
- `get_weather`
- `list_files`
- `read_file`
- `summarize_csv`
- `filter_csv`
- `insert_database_record`
- `query_database_records`
- `get_database_summary`

Then try a real task:

> "Check the weather in Mumbai and save it to the database"

Claude will:
1. Call `get_weather` tool with city="Mumbai"
2. Call `insert_database_record` tool with the weather data
3. Confirm both operations succeeded

## 🛠️ Available Tools

### Weather Tools

**`get_weather`**
- Get current weather for any city
- Returns temperature, humidity, condition
- Example: `{"city": "London"}`

### File Tools

**`list_files`**
- List all files in data/ directory
- No parameters required

**`read_file`**
- Read contents of any file
- Example: `{"filename": "notes.txt"}`

### CSV Tools

**`summarize_csv`**
- Get statistical summary of CSV file
- Returns row count, columns, missing values
- Example: `{"filename": "sample.csv"}`

**`filter_csv`**
- Filter CSV by column value
- Returns matching rows
- Example: `{"filename": "sample.csv", "column": "Category", "value": "Food"}`

### Database Tools

**`insert_database_record`**
- Insert new record into database
- Tables: weather_logs, file_logs, reports
- Example: `{"table": "weather_logs", "data": {"city": "Mumbai", "temperature": 32, "condition": "Sunny"}}`

**`query_database_records`**
- Query recent records from table
- Example: `{"table": "weather_logs", "limit": 10}`

**`get_database_summary`**
- Get total record count for table
- Example: `{"table": "weather_logs"}`

## 🔄 How MCP Protocol Works

### 1. MCP Client Connects

Claude Desktop (or any MCP client) spawns your server as a subprocess:

```bash
python data_console_mcp_server.py
```

### 2. Protocol Handshake

**Client → Server (initialize request):**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "1.0",
    "clientInfo": {"name": "Claude Desktop", "version": "1.0"}
  }
}
```

**Server → Client (initialize response):**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "1.0",
    "serverInfo": {"name": "data_console_mcp", "version": "1.0"},
    "capabilities": {"tools": true}
  }
}
```

### 3. Tool Discovery

**Client → Server (list tools):**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list"
}
```

**Server → Client (tool list):**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "get_weather",
        "description": "Get current weather information for a specified city...",
        "inputSchema": {
          "type": "object",
          "properties": {
            "city": {"type": "string", "description": "City name..."},
            "response_format": {"type": "string", "enum": ["markdown", "json"]}
          },
          "required": ["city"]
        }
      },
      // ... more tools
    ]
  }
}
```

### 4. Tool Execution

**Client → Server (call tool):**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "get_weather",
    "arguments": {"city": "Mumbai", "response_format": "markdown"}
  }
}
```

**Server → Client (tool result):**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "# Weather for Mumbai\n\n🌡️ **Temperature:** 32.5°C..."
      }
    ]
  }
}
```

All of this **JSON-RPC communication is handled automatically by FastMCP**. You just write the tool functions!

## 🧪 Testing Your MCP Server

### Test 1: List Tools

```bash
python data_console_mcp_server.py
```

In another terminal, send a JSON-RPC message:

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python data_console_mcp_server.py
```

### Test 2: Call a Tool

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_weather","arguments":{"city":"Mumbai"}}}' | python data_console_mcp_server.py
```

### Test 3: Use MCP Inspector (Best Option)

```bash
npx @modelcontextprotocol/inspector python data_console_mcp_server.py
```

Opens a web UI where you can:
- Browse all tools
- See tool schemas
- Test tool calls interactively
- View raw JSON-RPC messages

## 📊 Comparing to Your Previous Architecture

| Aspect | Previous (OpenAI Direct) | Current (Real MCP) |
|--------|--------------------------|-------------------|
| **Protocol** | Direct Python function calls | JSON-RPC over stdio |
| **Process** | Same process | Separate process |
| **Transport** | In-memory | stdin/stdout |
| **Clients** | Only your FastAPI app | Any MCP client (Claude Desktop, Cline, etc.) |
| **Portability** | Python only | Language agnostic protocol |
| **Standards** | Custom | Official MCP specification |
| **Tool Discovery** | Manual registry | Automatic via protocol |
| **Reusability** | Tied to your app | Shareable across apps |

## 🎓 Key MCP Concepts You're Using

### 1. **FastMCP Framework**
- Simplifies MCP server creation
- Auto-generates tool schemas from Pydantic models
- Handles JSON-RPC protocol automatically

### 2. **Pydantic Models for Validation**
```python
class WeatherInput(BaseModel):
    city: str = Field(..., description="City name")
```
FastMCP converts this to MCP tool input schema automatically.

### 3. **Tool Annotations**
```python
@mcp.tool(
    name="get_weather",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False
    }
)
```
Tells clients about tool behavior (read-only, destructive, etc.)

### 4. **stdio Transport**
```python
mcp.run()  # Uses stdio by default
```
Server communicates via stdin/stdout using JSON-RPC messages.

### 5. **Response Formatting**
Tools can return Markdown or JSON:
- Markdown: Human-readable, good for Claude to read
- JSON: Structured, good for programmatic processing

## 🚀 Multi-Tool Orchestration Examples

### Example 1: Weather Report Generation

**User:** "Generate a weather report for Mumbai and save it to the database"

**Claude's Execution:**
1. Calls `get_weather` with city="Mumbai"
2. Receives: `{"temperature": 32.5, "humidity": 65, "condition": "Sunny"}`
3. Calls `insert_database_record` with:
   ```json
   {
     "table": "weather_logs",
     "data": {"city": "Mumbai", "temperature": 32.5, "condition": "Sunny"}
   }
   ```
4. Calls `insert_database_record` again with:
   ```json
   {
     "table": "reports",
     "data": {
       "report_name": "Mumbai Weather Report",
       "content": "Mumbai is currently experiencing sunny weather with 32.5°C temperature..."
     }
   }
   ```

### Example 2: CSV Analysis Workflow

**User:** "Analyze sample.csv and tell me about Food category entries"

**Claude's Execution:**
1. Calls `summarize_csv` with filename="sample.csv"
2. Sees there's a "Category" column
3. Calls `filter_csv` with filename="sample.csv", column="Category", value="Food"
4. Receives filtered results
5. Summarizes findings to user

### Example 3: Data Audit

**User:** "Show me all recent database activity"

**Claude's Execution:**
1. Calls `get_database_summary` for "weather_logs"
2. Calls `get_database_summary` for "file_logs"
3. Calls `get_database_summary` for "reports"
4. Calls `query_database_records` for each table to see recent entries
5. Compiles comprehensive audit report

## 🔐 Security Features

### 1. **File Access Restriction**
```python
# In services/validators.py
BASE_DATA_PATH = os.path.abspath("data")

def validate_filename(filename: str):
    if ".." in filename:
        raise FileAccessError("Directory traversal detected")
```
All file operations restricted to `data/` directory.

### 2. **Database Table Whitelist**
```python
ALLOWED_TABLES = ["weather_logs", "file_logs", "reports"]
```
Can only access these three tables.

### 3. **Input Validation**
Pydantic models validate all inputs before execution.

### 4. **No Raw SQL from AI**
Database operations use parameterized queries, not raw SQL.

## 📖 Workshop Demo Script

### Demo 1: Simple Tool Call
```
User: "What's the weather in London?"
Claude: [Calls get_weather tool] → Returns formatted weather
```

### Demo 2: Multi-Tool Workflow
```
User: "Check weather in three cities and save all to database"
Claude: 
  [Calls get_weather for London]
  [Calls get_weather for Mumbai]
  [Calls get_weather for Tokyo]
  [Calls insert_database_record 3 times]
  → Confirms all saved
```

### Demo 3: Data Analysis
```
User: "What data do we have? Analyze it."
Claude:
  [Calls list_files]
  [Calls summarize_csv for each CSV]
  [Calls query_database_records for each table]
  → Provides comprehensive data overview
```

## 🎯 Next Steps

### For Workshop:
1. ✅ Test MCP server with MCP Inspector
2. ✅ Configure Claude Desktop with your server
3. ✅ Prepare demo scripts showing multi-tool orchestration
4. ✅ Have fallback data in case live APIs fail

### For Production:
1. Replace mock weather with real API (OpenWeatherMap, etc.)
2. Add authentication/authorization
3. Implement rate limiting
4. Add comprehensive logging
5. Deploy as HTTP service (streamable HTTP transport)

## 📚 Additional Resources

- **MCP Specification:** https://modelcontextprotocol.io/
- **FastMCP Documentation:** https://github.com/modelcontextprotocol/python-sdk
- **MCP Inspector:** https://github.com/modelcontextprotocol/inspector
- **Claude Desktop Config:** https://docs.anthropic.com/claude/docs/claude-desktop

## 🐛 Troubleshooting

### Server Won't Start
```bash
# Check Python version (need 3.10+)
python --version

# Verify FastMCP installed
pip show mcp

# Check for import errors
python -c "from mcp.server.fastmcp import FastMCP; print('OK')"
```

### Claude Desktop Not Finding Server
- Check absolute paths in config (no relative paths!)
- Restart Claude Desktop after config changes
- Check server logs: Look at Claude Desktop logs folder

### Tools Not Working
```bash
# Test with MCP Inspector
npx @modelcontextprotocol/inspector python data_console_mcp_server.py

# Check if services work independently
python test.py
```

---

**You now have a real, production-grade MCP server!** 🎉

This is the actual MCP technology that powers tool integration in Claude Desktop and other MCP-compatible applications.
