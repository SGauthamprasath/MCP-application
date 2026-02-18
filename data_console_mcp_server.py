#!/usr/bin/env python3
"""
Real MCP Server for AI Data Console
====================================

This is an ACTUAL Model Context Protocol (MCP) server implementation using the
official FastMCP framework from Anthropic. It exposes your services (weather,
file operations, CSV analysis, database) as MCP tools that can be used by:
- Claude Desktop
- MCP-compatible AI clients
- Other applications that support MCP protocol

Architecture:
    MCP Client (Claude Desktop, etc.)
            ↓ (stdio/JSON-RPC protocol)
    This MCP Server (FastMCP)
            ↓ (Python imports)
    Your Service Layer (weather_service, file_service, etc.)

Unlike your previous architecture which just called Python functions directly,
this server runs as a SEPARATE PROCESS and communicates via MCP protocol.
"""

import json
import sys
from pathlib import Path
from typing import Optional, List
from enum import Enum

# Add parent directory to Python path so we can import services
sys.path.insert(0, str(Path(__file__).parent))

# FastMCP imports - this is the official MCP Python SDK
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator, ConfigDict

# Import your existing services (pure business logic)
from services.weather_service import get_weather
from services.file_service import list_files, read_file
from services.csv_service import summarize_csv, filter_csv
from database.db_service import insert_record, query_records, get_summary

# ============================================================================
# MCP SERVER INITIALIZATION
# ============================================================================

# Create FastMCP server instance
# Name follows MCP convention: {service}_mcp
mcp = FastMCP("data_console_mcp")


# ============================================================================
# PYDANTIC MODELS FOR INPUT VALIDATION
# ============================================================================
# These models define and validate inputs for each tool. FastMCP automatically
# generates the MCP tool schema from these Pydantic models.

class ResponseFormat(str, Enum):
    """Output format options for tool responses."""
    MARKDOWN = "markdown"
    JSON = "json"


class WeatherInput(BaseModel):
    """Input model for weather lookup tool."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    city: str = Field(
        ...,
        description="City name to get weather for (e.g., 'Mumbai', 'Chennai', 'London')",
        min_length=1,
        max_length=100
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for structured data"
    )


class FileListInput(BaseModel):
    """Input model for listing files."""
    model_config = ConfigDict(extra='forbid')
    
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for structured data"
    )


class FileReadInput(BaseModel):
    """Input model for reading file contents."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    filename: str = Field(
        ...,
        description="Name of the file to read (e.g., 'notes.txt', 'sample.csv'). Must be in the data/ directory.",
        min_length=1,
        max_length=255
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for structured data"
    )


class CSVSummaryInput(BaseModel):
    """Input model for CSV file summary analysis."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    filename: str = Field(
        ...,
        description="Name of the CSV file to analyze (e.g., 'sales.csv', 'data.csv'). Must be in the data/ directory.",
        min_length=1,
        max_length=255
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for structured data"
    )


class CSVFilterInput(BaseModel):
    """Input model for filtering CSV data."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    filename: str = Field(
        ...,
        description="Name of the CSV file to filter (e.g., 'sales.csv')",
        min_length=1,
        max_length=255
    )
    column: str = Field(
        ...,
        description="Column name to filter by (e.g., 'Category', 'Status', 'Region')",
        min_length=1,
        max_length=100
    )
    value: str = Field(
        ...,
        description="Value to filter for in the specified column (e.g., 'Food', 'Active', 'North')"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for structured data"
    )


class DBInsertInput(BaseModel):
    """Input model for inserting records into database."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    table: str = Field(
        ...,
        description="Table name. Must be one of: weather_logs, file_logs, reports",
        pattern="^(weather_logs|file_logs|reports)$"
    )
    data: dict = Field(
        ...,
        description="Dictionary of column-value pairs to insert. For weather_logs: {city, temperature, condition}. For file_logs: {filename, action}. For reports: {report_name, content}"
    )


class DBQueryInput(BaseModel):
    """Input model for querying database records."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    table: str = Field(
        ...,
        description="Table name to query. Must be one of: weather_logs, file_logs, reports",
        pattern="^(weather_logs|file_logs|reports)$"
    )
    limit: int = Field(
        default=10,
        description="Maximum number of records to return",
        ge=1,
        le=100
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for structured data"
    )


class DBSummaryInput(BaseModel):
    """Input model for getting database table summary."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    table: str = Field(
        ...,
        description="Table name to summarize. Must be one of: weather_logs, file_logs, reports",
        pattern="^(weather_logs|file_logs|reports)$"
    )


# ============================================================================
# HELPER FUNCTIONS FOR FORMATTING
# ============================================================================

def format_weather_markdown(data: dict) -> str:
    """Format weather data as markdown."""
    return f"""# Weather for {data['city']}

🌡️ **Temperature:** {data['temperature_celsius']}°C
💧 **Humidity:** {data['humidity']}%
☁️ **Condition:** {data['condition']}
"""


def format_file_list_markdown(files: list) -> str:
    """Format file list as markdown."""
    if not files:
        return "📂 **No files found in data directory**"
    
    file_list = "\n".join([f"- 📄 {f}" for f in files])
    return f"""# Files in Data Directory

{file_list}

**Total:** {len(files)} file(s)
"""


def format_file_content_markdown(filename: str, content: str) -> str:
    """Format file content as markdown."""
    lines = content.split('\n')
    line_count = len(lines)
    char_count = len(content)
    
    return f"""# File: {filename}

**Lines:** {line_count} | **Characters:** {char_count}

---

{content}
"""


def format_csv_summary_markdown(summary: dict) -> str:
    """Format CSV summary as markdown."""
    missing_vals = "\n".join([f"  - **{col}:** {count}" for col, count in summary['missing_values'].items()])
    cols = "\n".join([f"  - {col}" for col in summary['columns']])
    
    return f"""# CSV File Summary

📊 **Total Rows:** {summary['rows']}

## Columns ({len(summary['columns'])})
{cols}

## Missing Values
{missing_vals}
"""


def format_csv_filter_markdown(result: dict) -> str:
    """Format CSV filter results as markdown."""
    preview_table = "| " + " | ".join(result['preview'][0].keys()) + " |\n"
    preview_table += "| " + " | ".join(['---'] * len(result['preview'][0])) + " |\n"
    
    for row in result['preview']:
        preview_table += "| " + " | ".join([str(v) for v in row.values()]) + " |\n"
    
    return f"""# Filter Results

**Rows Found:** {result['rows_found']}

## Preview (first 5 rows)

{preview_table}
"""


def format_db_records_markdown(table: str, records: list) -> str:
    """Format database records as markdown."""
    if not records:
        return f"# {table}\n\n**No records found**"
    
    # Build table
    keys = records[0].keys()
    table_md = "| " + " | ".join(keys) + " |\n"
    table_md += "| " + " | ".join(['---'] * len(keys)) + " |\n"
    
    for record in records:
        table_md += "| " + " | ".join([str(v) for v in record.values()]) + " |\n"
    
    return f"""# {table} Records

**Count:** {len(records)} record(s)

{table_md}
"""


# ============================================================================
# MCP TOOLS - WEATHER
# ============================================================================

@mcp.tool(
    name="get_weather",
    annotations={
        "title": "Get Weather Information",
        "readOnlyHint": True,      # Doesn't modify any data
        "destructiveHint": False,  # Not destructive
        "idempotentHint": True,    # Same input = same output
        "openWorldHint": False     # Doesn't interact with external entities
    }
)
async def get_weather_tool(params: WeatherInput) -> str:
    """Get current weather information for a specified city.
    
    This tool fetches weather data including temperature, humidity, and current
    conditions for any city worldwide. Data is currently mocked for workshop
    reliability but can be connected to real weather APIs.
    
    Args:
        params (WeatherInput): Contains:
            - city (str): Name of the city to get weather for
            - response_format (str): 'markdown' or 'json'
    
    Returns:
        str: Weather information in requested format containing:
            - city (str): City name
            - temperature_celsius (float): Temperature in Celsius
            - humidity (int): Humidity percentage
            - condition (str): Weather condition (Sunny/Cloudy/Rainy)
    
    Example:
        Input: {"city": "Mumbai", "response_format": "markdown"}
        Output: Markdown-formatted weather report for Mumbai
    """
    try:
        # Call your existing weather service
        result = get_weather(params.city)
        
        if result['status'] != 'success':
            return f"Error: {result.get('message', 'Unknown error')}"
        
        weather_data = result['data']
        
        # Format based on requested format
        if params.response_format == ResponseFormat.MARKDOWN:
            return format_weather_markdown(weather_data)
        else:
            return json.dumps(weather_data, indent=2)
            
    except Exception as e:
        return f"Error getting weather: {str(e)}"


# ============================================================================
# MCP TOOLS - FILE OPERATIONS
# ============================================================================

@mcp.tool(
    name="list_files",
    annotations={
        "title": "List Files in Data Directory",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def list_files_tool(params: FileListInput) -> str:
    """List all files available in the data directory.
    
    This tool returns a list of all files present in the data/ directory,
    which can then be read using the read_file tool or analyzed with CSV tools.
    
    Args:
        params (FileListInput): Contains:
            - response_format (str): 'markdown' or 'json'
    
    Returns:
        str: List of filenames in requested format
    
    Example:
        Output: ["sample.csv", "notes.txt", "report.json"]
    """
    try:
        result = list_files()
        
        if result['status'] != 'success':
            return f"Error: {result.get('message', 'Unknown error')}"
        
        files = result['data']['files']
        
        if params.response_format == ResponseFormat.MARKDOWN:
            return format_file_list_markdown(files)
        else:
            return json.dumps({"files": files}, indent=2)
            
    except Exception as e:
        return f"Error listing files: {str(e)}"


@mcp.tool(
    name="read_file",
    annotations={
        "title": "Read File Contents",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def read_file_tool(params: FileReadInput) -> str:
    """Read the contents of a file from the data directory.
    
    This tool reads and returns the complete contents of text files from the
    data/ directory. Files must exist and be accessible within the restricted
    data directory for security.
    
    Args:
        params (FileReadInput): Contains:
            - filename (str): Name of file to read (must be in data/ directory)
            - response_format (str): 'markdown' or 'json'
    
    Returns:
        str: File contents in requested format
    
    Example:
        Input: {"filename": "notes.txt"}
        Output: Complete contents of notes.txt file
    """
    try:
        result = read_file(params.filename)
        
        if result['status'] != 'success':
            return f"Error: {result.get('message', 'Unknown error')}"
        
        file_data = result['data']
        
        if params.response_format == ResponseFormat.MARKDOWN:
            return format_file_content_markdown(file_data['filename'], file_data['content'])
        else:
            return json.dumps(file_data, indent=2)
            
    except Exception as e:
        return f"Error reading file: {str(e)}"


# ============================================================================
# MCP TOOLS - CSV OPERATIONS
# ============================================================================

@mcp.tool(
    name="summarize_csv",
    annotations={
        "title": "Analyze CSV File",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def summarize_csv_tool(params: CSVSummaryInput) -> str:
    """Get a statistical summary of a CSV file.
    
    This tool analyzes a CSV file and returns key statistics including row count,
    column names, data types, and missing value analysis. Useful for understanding
    the structure and quality of data before processing.
    
    Args:
        params (CSVSummaryInput): Contains:
            - filename (str): Name of CSV file to analyze
            - response_format (str): 'markdown' or 'json'
    
    Returns:
        str: Summary statistics in requested format containing:
            - rows (int): Total number of rows
            - columns (list): List of column names
            - missing_values (dict): Count of missing values per column
    
    Example:
        Input: {"filename": "sales.csv"}
        Output: Summary showing 1000 rows, 5 columns, missing value counts
    """
    try:
        result = summarize_csv(params.filename)
        
        if result['status'] != 'success':
            return f"Error: {result.get('message', 'Unknown error')}"
        
        summary = result['data']
        
        if params.response_format == ResponseFormat.MARKDOWN:
            return format_csv_summary_markdown(summary)
        else:
            return json.dumps(summary, indent=2)
            
    except Exception as e:
        return f"Error summarizing CSV: {str(e)}"


@mcp.tool(
    name="filter_csv",
    annotations={
        "title": "Filter CSV Data",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def filter_csv_tool(params: CSVFilterInput) -> str:
    """Filter CSV file by column value and return matching rows.
    
    This tool filters a CSV file based on a column name and value, returning
    all rows where the specified column matches the given value. Returns a
    preview of the first 5 matching rows and the total count.
    
    Args:
        params (CSVFilterInput): Contains:
            - filename (str): Name of CSV file to filter
            - column (str): Column name to filter by
            - value (str): Value to match in the column
            - response_format (str): 'markdown' or 'json'
    
    Returns:
        str: Filter results in requested format containing:
            - rows_found (int): Total number of matching rows
            - preview (list): First 5 matching rows as dictionaries
    
    Example:
        Input: {"filename": "sales.csv", "column": "Region", "value": "North"}
        Output: All sales records from North region with preview of first 5
    """
    try:
        result = filter_csv(params.filename, params.column, params.value)
        
        if result['status'] != 'success':
            return f"Error: {result.get('message', 'Unknown error')}"
        
        filter_result = result['data']
        
        if params.response_format == ResponseFormat.MARKDOWN:
            return format_csv_filter_markdown(filter_result)
        else:
            return json.dumps(filter_result, indent=2)
            
    except Exception as e:
        return f"Error filtering CSV: {str(e)}"


# ============================================================================
# MCP TOOLS - DATABASE OPERATIONS
# ============================================================================

@mcp.tool(
    name="insert_database_record",
    annotations={
        "title": "Insert Record into Database",
        "readOnlyHint": False,     # Modifies data
        "destructiveHint": False,  # Not destructive (just adds data)
        "idempotentHint": False,   # Each call adds a new record
        "openWorldHint": False
    }
)
async def insert_record_tool(params: DBInsertInput) -> str:
    """Insert a new record into a database table.
    
    This tool adds a new record to one of the three available tables. Each table
    has specific required fields that must be provided in the data dictionary.
    
    Available tables and their fields:
    - weather_logs: {city, temperature, condition}
    - file_logs: {filename, action}
    - reports: {report_name, content}
    
    Args:
        params (DBInsertInput): Contains:
            - table (str): Table name (weather_logs, file_logs, or reports)
            - data (dict): Dictionary of column-value pairs to insert
    
    Returns:
        str: Success confirmation with inserted data details
    
    Example:
        Input: {
            "table": "weather_logs",
            "data": {"city": "Mumbai", "temperature": 32.5, "condition": "Sunny"}
        }
        Output: Confirmation that weather log was inserted successfully
    """
    try:
        result = insert_record(params.table, params.data)
        
        if result['status'] != 'success':
            return f"Error: {result.get('message', 'Unknown error')}"
        
        return f"✅ Successfully inserted record into {params.table}\n\nData: {json.dumps(params.data, indent=2)}"
            
    except Exception as e:
        return f"Error inserting record: {str(e)}"


@mcp.tool(
    name="query_database_records",
    annotations={
        "title": "Query Database Records",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def query_records_tool(params: DBQueryInput) -> str:
    """Query and retrieve records from a database table.
    
    This tool fetches the most recent records from a specified table, with
    configurable limit. Records are returned in reverse chronological order
    (newest first).
    
    Args:
        params (DBQueryInput): Contains:
            - table (str): Table name to query
            - limit (int): Maximum number of records to return (1-100, default 10)
            - response_format (str): 'markdown' or 'json'
    
    Returns:
        str: List of records in requested format
    
    Example:
        Input: {"table": "weather_logs", "limit": 5}
        Output: 5 most recent weather log entries
    """
    try:
        records = query_records(params.table, params.limit)
        
        if params.response_format == ResponseFormat.MARKDOWN:
            return format_db_records_markdown(params.table, records)
        else:
            return json.dumps({"table": params.table, "records": records}, indent=2)
            
    except Exception as e:
        return f"Error querying records: {str(e)}"


@mcp.tool(
    name="get_database_summary",
    annotations={
        "title": "Get Database Table Summary",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def get_summary_tool(params: DBSummaryInput) -> str:
    """Get summary statistics for a database table.
    
    This tool returns high-level statistics about a table, including total
    record count. Useful for understanding database state without fetching
    all records.
    
    Args:
        params (DBSummaryInput): Contains:
            - table (str): Table name to summarize
    
    Returns:
        str: JSON-formatted summary with table statistics
    
    Example:
        Input: {"table": "weather_logs"}
        Output: {"table": "weather_logs", "total_records": 42}
    """
    try:
        summary = get_summary(params.table)
        return json.dumps(summary, indent=2)
            
    except Exception as e:
        return f"Error getting summary: {str(e)}"


# ============================================================================
# MAIN - START THE MCP SERVER
# ============================================================================

if __name__ == "__main__":
    """
    Start the MCP server.
    
    By default, FastMCP uses stdio transport, which means:
    - Server reads JSON-RPC messages from stdin
    - Server writes JSON-RPC responses to stdout
    - Perfect for local tool integration (Claude Desktop, etc.)
    
    To test this server:
    1. Run: python data_console_mcp_server.py
    2. Or use MCP Inspector: npx @modelcontextprotocol/inspector python data_console_mcp_server.py
    3. Or configure in Claude Desktop (see README for config)
    """
    print("Starting Data Console MCP Server...", file=sys.stderr)
    print("Server ready. Waiting for MCP client connection...", file=sys.stderr)
    
    # Start the server using stdio transport
    mcp.run()
