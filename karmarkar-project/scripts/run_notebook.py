"""[MasterSpec C12,11.1; BC 4.1-4.5] Headless fresh-kernel execution and audit."""
from pathlib import Path
import os
import sys
import asyncio
import faulthandler
faulthandler.enable()
import nbformat
from nbclient import NotebookClient
from karmarkar.reporting import audit_project
from karmarkar.io import write_json


def main():
    """[MS G5,G7] Run every cell using this Python environment, then audit saved output."""
    root=Path(__file__).resolve().parents[1]
    runtime=root/"outputs/jupyter-runtime"
    runtime.mkdir(parents=True,exist_ok=True)
    os.environ["JUPYTER_RUNTIME_DIR"]=str(runtime)
    nbpath=root/"notebooks/01_karmarkar_full_report.ipynb"
    nb=nbformat.read(nbpath,as_version=4)
    # [MS C12] Explicit interpreter prevents accidentally using a global kernel.
    client=NotebookClient(nb,timeout=600,resources={"metadata":{"path":str(root)}},allow_errors=False)
    # Keep owns_km=True so nbclient shuts down channels/kernel before exit.
    km=client.create_kernel_manager()
    km.kernel_spec.argv=[sys.executable,"-m","ipykernel_launcher","-f","{connection_file}"]
    # [MS C12, DX] A managed selector loop avoids Proactor/ZeroMQ helper threads
    # and sync-wrapper background event loops during Python finalization.
    loop=asyncio.SelectorEventLoop() if sys.platform=="win32" else asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        loop.run_until_complete(client.async_execute())
    finally:
        # Save partial execution as evidence even when an exception propagates.
        nbformat.write(nb,nbpath.with_name("01_karmarkar_full_report_executed.ipynb"))
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.run_until_complete(loop.shutdown_default_executor())
        loop.close()
        asyncio.set_event_loop(None)
    audit=audit_project(root,require_executed=True)
    write_json(root/"outputs/notebook_audit.json",audit)
    print(audit)


if __name__=="__main__":
    main()

