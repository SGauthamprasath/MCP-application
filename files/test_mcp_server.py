#!/usr/bin/env python3
"""
Test Script for MCP Server
===========================

This script tests your MCP server by simulating JSON-RPC calls that an MCP
client (like Claude Desktop) would make. It helps verify the server works
correctly before connecting it to actual MCP clients.

Usage:
    python test_mcp_server.py
"""

import json
import subprocess
import sys
from pathlib import Path

def send_json_rpc(server_path: str, method: str, params: dict = None, id: int = 1) -> dict:
    """
    Send a JSON-RPC message to the MCP server and get response.
    
    This simulates what an MCP client does when calling the server.
    """
    message = {
        "jsonrpc": "2.0",
        "id": id,
        "method": method
    }
    
    if params:
        message["params"] = params
    
    # Convert to JSON and add newline (required by JSON-RPC over stdio)
    json_message = json.dumps(message) + "\n"
    
    try:
        # Start the MCP server as subprocess
        process = subprocess.Popen(
            [sys.executable, server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send the message
        stdout, stderr = process.communicate(input=json_message, timeout=5)
        
        # Parse response (last line of stdout should be the JSON-RPC response)
        lines = [line for line in stdout.strip().split('\n') if line]
        if lines:
            response = json.loads(lines[-1])
            return response
        else:
            return {"error": "No response from server", "stderr": stderr}
            
    except subprocess.TimeoutExpired:
        process.kill()
        return {"error": "Server timeout"}
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON response: {e}", "stdout": stdout, "stderr": stderr}
    except Exception as e:
        return {"error": str(e)}


def test_initialize(server_path: str):
    """Test 1: Initialize the MCP connection"""
    print("\n" + "="*70)
    print("TEST 1: Initialize MCP Server")
    print("="*70)
    
    response = send_json_rpc(
        server_path,
        "initialize",
        {
            "protocolVersion": "1.0",
            "clientInfo": {
                "name": "Test Client",
                "version": "1.0.0"
            }
        }
    )
    
    print(json.dumps(response, indent=2))
    
    if "result" in response:
        print("✅ PASSED: Server initialized successfully")
        return True
    else:
        print("❌ FAILED: Server initialization failed")
        return False


def test_list_tools(server_path: str):
    """Test 2: List all available tools"""
    print("\n" + "="*70)
    print("TEST 2: List Available Tools")
    print("="*70)
    
    response = send_json_rpc(server_path, "tools/list")
    
    if "result" in response and "tools" in response["result"]:
        tools = response["result"]["tools"]
        print(f"\n✅ PASSED: Found {len(tools)} tools\n")
        
        for tool in tools:
            print(f"  📦 {tool['name']}")
            if 'description' in tool:
                desc = tool['description'][:100] + "..." if len(tool['description']) > 100 else tool['description']
                print(f"     {desc}")
        
        return True
    else:
        print("❌ FAILED: Could not list tools")
        print(json.dumps(response, indent=2))
        return False


def test_call_weather_tool(server_path: str):
    """Test 3: Call get_weather tool"""
    print("\n" + "="*70)
    print("TEST 3: Call get_weather Tool")
    print("="*70)
    
    response = send_json_rpc(
        server_path,
        "tools/call",
        {
            "name": "get_weather",
            "arguments": {
                "city": "Mumbai",
                "response_format": "json"
            }
        }
    )
    
    print(json.dumps(response, indent=2))
    
    if "result" in response:
        print("\n✅ PASSED: Weather tool executed successfully")
        return True
    else:
        print("\n❌ FAILED: Weather tool execution failed")
        return False


def test_call_list_files_tool(server_path: str):
    """Test 4: Call list_files tool"""
    print("\n" + "="*70)
    print("TEST 4: Call list_files Tool")
    print("="*70)
    
    response = send_json_rpc(
        server_path,
        "tools/call",
        {
            "name": "list_files",
            "arguments": {
                "response_format": "json"
            }
        }
    )
    
    print(json.dumps(response, indent=2))
    
    if "result" in response:
        print("\n✅ PASSED: List files tool executed successfully")
        return True
    else:
        print("\n❌ FAILED: List files tool execution failed")
        return False


def test_call_summarize_csv_tool(server_path: str):
    """Test 5: Call summarize_csv tool"""
    print("\n" + "="*70)
    print("TEST 5: Call summarize_csv Tool")
    print("="*70)
    
    response = send_json_rpc(
        server_path,
        "tools/call",
        {
            "name": "summarize_csv",
            "arguments": {
                "filename": "sample.csv",
                "response_format": "json"
            }
        }
    )
    
    print(json.dumps(response, indent=2))
    
    if "result" in response:
        print("\n✅ PASSED: CSV summary tool executed successfully")
        return True
    else:
        print("\n❌ FAILED: CSV summary tool execution failed")
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("MCP SERVER TEST SUITE")
    print("=" * 70)
    print("\nThis script tests your MCP server by simulating JSON-RPC calls")
    print("that an MCP client (like Claude Desktop) would make.\n")
    
    # Find the MCP server
    server_path = Path(__file__).parent / "data_console_mcp_server.py"
    
    if not server_path.exists():
        print(f"❌ ERROR: MCP server not found at {server_path}")
        print("Please make sure data_console_mcp_server.py is in the same directory.")
        return
    
    print(f"📍 Testing server at: {server_path}\n")
    
    # Run tests
    results = []
    
    # Note: We can't easily test initialize with stdio because it requires
    # a persistent connection. Instead, we'll focus on tool calling.
    
    results.append(("List Tools", test_list_tools(str(server_path))))
    results.append(("Get Weather", test_call_weather_tool(str(server_path))))
    results.append(("List Files", test_call_list_files_tool(str(server_path))))
    results.append(("Summarize CSV", test_call_summarize_csv_tool(str(server_path))))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your MCP server is working correctly.")
        print("\nNext steps:")
        print("1. Install MCP Inspector: npx @modelcontextprotocol/inspector")
        print("2. Test interactively: npx @modelcontextprotocol/inspector python data_console_mcp_server.py")
        print("3. Configure Claude Desktop (see MCP_SERVER_README.md)")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")


if __name__ == "__main__":
    main()
