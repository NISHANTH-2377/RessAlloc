import os
import shutil

def remove_all_cache(target_dir=None):
    if target_dir is None:
        target_dir = os.path.dirname(os.path.abspath(__file__))

    removed_dirs = 0
    removed_files = 0

    print(f"Scanning for cache files in: {target_dir}")
    for root, dirs, files in os.walk(target_dir, topdown=False):
        for file in files:
            if file.endswith((".pyc", ".pyo", ".pyd")):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    removed_files += 1
                except Exception as e:
                    print(f"  Warning: could not delete file {file_path}: {e}")

        for d in list(dirs):
            if d in ("__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache"):
                dir_path = os.path.join(root, d)
                try:
                    shutil.rmtree(dir_path, ignore_errors=True)
                    removed_dirs += 1
                    dirs.remove(d)
                except Exception as e:
                    print(f"  Warning: could not delete directory {dir_path}: {e}")

    print(f"Cleanup complete: removed {removed_dirs} cache directories and {removed_files} compiled cache files.")
    return removed_dirs, removed_files

if __name__ == "__main__":
    remove_all_cache()
