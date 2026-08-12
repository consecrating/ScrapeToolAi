"""MCP Server for AI agent integration (Kiro, Claude, Cursor)."""

def start_server(port: int = 8080):
    """Start a simple JSON-RPC style server for MCP integration."""
    import json
    from http.server import HTTPServer, BaseHTTPRequestHandler
    
    class MCPHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            
            method = body.get("method", "")
            params = body.get("params", {})
            
            if method == "fetch":
                from scrapetoolai import fetch
                page = fetch(params["url"], tier=params.get("tier", "auto"))
                result = {"html": page.html[:5000], "text": page.get_text()[:3000]}
            elif method == "extract":
                from scrapetoolai import smart_extract
                result = smart_extract(params["url"], params["intent"])
            elif method == "search":
                from scrapetoolai import search
                result = search(params.get("query", ""), **{k:v for k,v in params.items() if k != "query"})
            elif method == "sync_prompts":
                from scrapetoolai.organizer.prompt_sync import sync_prompts
                sync_prompts()
                result = {"status": "synced"}
            else:
                result = {"error": f"Unknown method: {method}", "available": ["fetch","extract","search","sync_prompts"]}
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"result": result}).encode())
        
        def log_message(self, *args): pass
    
    print(f"MCP Server ready on http://localhost:{port}")
    print("Methods: fetch, extract, search, sync_prompts")
    HTTPServer(("0.0.0.0", port), MCPHandler).serve_forever()
