import config

# MCP
from fastmcp.server import FastMCP

# Tools
from tools.new_scan import register_new_scan
from tools.get_scan import register_get_scan
from tools.search import register_search
from tools.fast_check import register_fast_check
from tools.get_api_docs import register_get_api_docs
from tools.queries import register_queries
from tools.brands import register_brands


def main():
    """Main entry point for the urlDNA MCP SSE server."""
    mcp = FastMCP(
        name="urlDNA MCP",
        instructions=config.INSTRUCTIONS
    )

    # Scanning tools
    register_new_scan(mcp)
    register_get_scan(mcp)
    register_fast_check(mcp)

    # Search
    register_search(mcp)

    # Saved Queries
    register_queries(mcp)

    # Brands
    register_brands(mcp)

    # API docs
    register_get_api_docs(mcp)

    # RUN
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()