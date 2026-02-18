# Quick Start: Real MCP Server in 5 Minutes

## 🚀 Get Your MCP Server Running NOW

This guide gets you from zero to a working MCP server connected to Claude Desktop in 5 minutes.

---

## ⚡ Step 1: Install Dependencies (1 minute)

```bash
# Install MCP SDK (official)
pip install mcp

# Install other dependencies
pip install pydantic pandas

# Or use requirements.txt
pip install -r requirements.txt
```

---

## ✅ Step 2: Verify Services Work (1 minute)

```bash
# Make sure you're in the project root
python test.py

# You should see 4 JSON files created:
# - weather.json
# - files.json  
# - summary.json
# - filter.json
```

If this works, your services are ready! ✅

---

## 🧪 Step 3: Test MCP Server (2 minutes)

### Option A: Quick Manual Test

```bash
# Run the server
python data_console_mcp_server.py
```

You should see:
```
Starting Data Console MCP Server...
Server ready. Waiting for MCP client connection...
```

Press `Ctrl+C` to stop. If no errors, it works! ✅

### Option B: Automated Tests (Better)

```bash
# Run the test suite
python test_mcp_server.py
```

You should see:
```
✅ PASS - List Tools
✅ PASS - Get Weather
✅ PASS - List Files
✅ PASS - Summarize CSV

4/4 tests passed
🎉 All tests passed!
```

### Option C: Interactive Testing (Best)

```bash
# Install MCP Inspector
npx @modelcontextprotocol/inspector python data_console_mcp_server.py
```

This opens a web interface where you can:
- See all 9 tools
- Test each tool interactively
- View JSON-RPC messages

---

## 🖥️ Step 4: Connect to Claude Desktop (1 minute)

### Find Your Config File

**macOS:**
```bash
open ~/Library/Application\ Support/Claude/
# Edit: claude_desktop_config.json
```

**Windows:**
```bash
explorer %APPDATA%\Claude
# Edit: claude_desktop_config.json
```

**Linux:**
```bash
nano ~/.config/Claude/claude_desktop_config.json
```

### Add This Configuration

```json
{
  "mcpServers": {
    "data-console": {
      "command": "python",
      "args": ["/ABSOLUTE/PATH/TO/data_console_mcp_server.py"]
    }
  }
}
```

**CRITICAL:** Replace `/ABSOLUTE/PATH/TO/` with your actual path!

#### How to Get Absolute Path

**macOS/Linux:**
```bash
cd /path/to/your/project
pwd
# Copy this path, add /data_console_mcp_server.py
```

**Windows:**
```bash
cd C:\path\to\your\project
cd
# Copy this path, add \data_console_mcp_server.py
```

**Example:**
```json
{
  "mcpServers": {
    "data-console": {
      "command": "python",
      "args": ["/Users/john/projects/ai-workshop/data_console_mcp_server.py"]
    }
  }
}
```

### Restart Claude Desktop

Completely quit and reopen Claude Desktop.

---

## 🎉 Step 5: Test in Claude Desktop

### Test 1: Check Tools are Available

In Claude Desktop, type:
```
What tools do you have available?
```

Claude should list your 9 tools:
- get_weather
- list_files
- read_file
- summarize_csv
- filter_csv
- insert_database_record
- query_database_records
- get_database_summary

### Test 2: Use a Simple Tool

```
What's the weather in London?
```

Claude should call your `get_weather` tool and return results!

### Test 3: Multi-Tool Orchestration

```
Check the weather in Mumbai and save it to the database
```

Claude should:
1. Call `get_weather` for Mumbai
2. Call `insert_database_record` to save it
3. Confirm success

### Test 4: Data Analysis

```
What files do we have? Analyze any CSV files.
```

Claude should:
1. Call `list_files` to see what's available
2. Call `summarize_csv` for any CSV files found
3. Provide analysis

---

## 🐛 Troubleshooting

### Problem: "Server not found" in Claude Desktop

**Check 1:** Is the path absolute?
```bash
# Wrong (relative path)
"args": ["./data_console_mcp_server.py"]

# Wrong (using ~)
"args": ["~/project/data_console_mcp_server.py"]

# Right (absolute path)
"args": ["/Users/john/project/data_console_mcp_server.py"]
```

**Check 2:** Can Python find your services?
```bash
# Add PYTHONPATH if needed
{
  "mcpServers": {
    "data-console": {
      "command": "python",
      "args": ["/absolute/path/data_console_mcp_server.py"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/project"
      }
    }
  }
}
```

**Check 3:** Is Python in PATH?
```bash
# Check Python location
which python  # macOS/Linux
where python  # Windows

# If Python is not in PATH, use full path
{
  "mcpServers": {
    "data-console": {
      "command": "/usr/local/bin/python3",  # Full path to Python
      "args": ["/absolute/path/data_console_mcp_server.py"]
    }
  }
}
```

### Problem: Tools not showing up

1. **Restart Claude Desktop** (must fully quit and reopen)
2. **Check server logs** (Claude Desktop has a logs folder)
3. **Test server independently:**
   ```bash
   python data_console_mcp_server.py
   # Should show "Server ready..."
   ```

### Problem: Import errors

```bash
# Check all dependencies installed
pip list | grep mcp
pip list | grep pydantic
pip list | grep pandas

# Reinstall if needed
pip install --upgrade mcp pydantic pandas
```

### Problem: Service errors

```bash
# Test services independently
python test.py

# Check database initialized
cd backend
python test_db.py
```

---

## 📋 Verification Checklist

Before connecting to Claude Desktop, verify:

- [ ] ✅ `pip install mcp` completed successfully
- [ ] ✅ `python test.py` creates 4 JSON files
- [ ] ✅ `python data_console_mcp_server.py` shows "Server ready"
- [ ] ✅ `python test_mcp_server.py` shows all tests passed
- [ ] ✅ Config file has ABSOLUTE path (no `./` or `~`)
- [ ] ✅ Claude Desktop fully restarted (quit + reopen)

---

## 🎯 What's Next?

### Once Working:

**Try Complex Workflows:**
```
Generate a weather report for 3 cities, save all to database, 
then create a summary report
```

**Try Data Analysis:**
```
Analyze sample.csv and tell me which category appears most often.
Save the analysis as a report in the database.
```

**Try File Operations:**
```
Read all text files, summarize their contents, and save 
the summary to the database
```

### Advanced Testing:

```bash
# Use MCP Inspector for detailed testing
npx @modelcontextprotocol/inspector python data_console_mcp_server.py
```

### Next Steps:

1. ✅ Add more tools to your service layer
2. ✅ Connect real weather API (replace mock)
3. ✅ Add authentication
4. ✅ Deploy as HTTP service
5. ✅ Build FastAPI wrapper (for web frontend)

---

## 📚 Learn More

- **Full README:** See `MCP_SERVER_README.md`
- **Architecture Comparison:** See `ARCHITECTURE_COMPARISON.md`
- **MCP Specification:** https://modelcontextprotocol.io/
- **FastMCP Docs:** https://github.com/modelcontextprotocol/python-sdk

---

## 💡 Pro Tips

1. **Use MCP Inspector during development** - it's invaluable for testing
2. **Check Claude Desktop logs** when things don't work
3. **Test services independently** before integrating with MCP
4. **Use absolute paths** everywhere in configs
5. **Restart Claude Desktop** after any config changes

---

**You're now running a real, production-grade MCP server!** 🎉

Your services are now available to Claude Desktop and any other MCP-compatible application.
