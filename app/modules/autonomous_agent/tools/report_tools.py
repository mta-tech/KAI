"""Report generation tools."""
import os
import json
from datetime import datetime

def create_report_tool(output_dir: str = "./agent_results"):
    """Create report writing tool."""

    def write_report(
        content: str,
        filename: str | None = None,
        title: str | None = None,
        format: str = "markdown"
    ) -> str:
        """Write a formatted report to a file.

        Args:
            content: The main body of the report (Markdown supported).
            filename: Optional filename (e.g. 'sales_report.md'). If not provided, one will be generated.
            title: Optional title to prepend to the report.
            format: Report format (currently only 'markdown' is supported).

        Returns:
            JSON string with success status and file path.
        """
        try:
            # Ensure directory exists (handled by filesystem backend usually, but good to be safe if using local)
            # Note: The agent uses a backend, but this tool might run in the service context.
            # Actually, since we use StateBackend/FilesystemBackend, we should ideally use the *backend's* write capability 
            # if we want it to show up in the agent's virtual filesystem.
            # BUT, standard tools usually just perform actions. 
            # If we use `write_file` from deepagents, it writes to the backend.
            # If we write to disk here using python `open`, it bypasses the backend if the backend is StateBackend!
            
            # However, `FilesystemBackend` is mounted at `/results/` in the service:
            # routes={"/results/": FilesystemBackend(root_dir=self.results_dir)}
            
            # So if we write to `self.results_dir` on the actual disk, it SHOULD show up in `/results/` 
            # IF the backend is checking disk. FilesystemBackend DOES check disk.
            
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"report_{timestamp}.md"
            
            if not filename.endswith(".md"):
                filename += ".md"

            full_path = os.path.join(output_dir, filename)
            
            final_content = ""
            if title:
                final_content += f"# {title}\n\n"
            final_content += content

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(final_content)

            return json.dumps({
                "success": True,
                "message": f"Report written successfully to {full_path}",
                "file_path": f"/results/{filename}", # Virtual path for the agent
                "real_path": full_path
            })

        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    return write_report
