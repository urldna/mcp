# MCP
from fastmcp.server import FastMCP

# Tools
from tools.new_scan import register_new_scan
from tools.get_scan import register_get_scan
from tools.search import register_search
from tools.fast_check import register_fast_check


def main():
    """Main entry point for the urlDNA MCP server."""
    # Create MCP
    mcp = FastMCP(name="urlDNA MCP", instructions="Submit and retrieve scan data from urlDNA")

    # Register tools
    register_new_scan(mcp)
    register_get_scan(mcp)
    register_search(mcp)
    register_fast_check(mcp)

    # RUN
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()