import os
import sys
import json
import importlib
import subprocess
import atexit
def load_plugins():
    """Dynamically load plugins from repowise_config.json without editing core code."""
    # Resolve the directory where the .exe (or script) is running
    base_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
    config_path = os.path.join(base_dir, "repowise_config.json")
    
    if not os.path.exists(config_path):
        return
        
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            plugins = config.get("plugins", [])
            for plugin in plugins:
                # Add custom directory to sys.path so importlib can find uncompiled .py files
                if "path" in plugin:
                    plugin_path = os.path.abspath(os.path.join(base_dir, plugin["path"]))
                    sys.path.insert(0, plugin_path)
                
                # Load the custom module
                if "module" in plugin:
                    print(f"[Wrapper] Injecting custom plugin: {plugin['module']}")
                    importlib.import_module(plugin["module"])
    except Exception as e:
        print(f"[Wrapper] Error loading custom plugins: {e}")
def launch_node_server():
    """Launch the bundled Node.js Next.js frontend dynamically."""
    base_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
    node_exe = os.path.join(base_dir, "node.exe")
    server_js = os.path.join(base_dir, "web", "server.js")
    
    if not os.path.exists(node_exe) or not os.path.exists(server_js):
        print("[Wrapper] Frontend files not found. Starting API-only mode...")
        return None
    print("[Wrapper] Starting Next.js Web Dashboard...")
    env = os.environ.copy()
    env["PORT"] = "3000"  # Ensure Next.js binds to port 3000
    
    process = subprocess.Popen(
        [node_exe, server_js],
        env=env,
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    
    # Automatically kill the Node server when the Python app is closed
    def cleanup():
        print("[Wrapper] Shutting down frontend server...")
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            
    atexit.register(cleanup)
    return process
if __name__ == "__main__":
    # 1. Load your custom dependencies dynamically
    load_plugins()
    
    # 2. Boot up the standalone frontend
    launch_node_server()
    
    # 3. Hand over execution to the untouched Repowise core
    from repowise.cli.main import cli
    sys.exit(cli())
