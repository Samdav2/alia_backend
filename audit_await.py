import os
import re

services = [
    "AdminService", "AIService", "AnalyticsService", "AuthService",
    "CourseService", "FileService", "LecturerService", "NotificationService",
    "ProgressService", "UserService"
]

# Map of service -> set of async methods
async_methods = {}

def get_async_methods():
    for service_file in os.listdir("app/services"):
        if not service_file.endswith(".py") or service_file == "__init__.py":
            continue

        service_path = os.path.join("app/services", service_file)
        with open(service_path, "r") as f:
            content = f.read()

            # Find class name
            class_match = re.search(r"class (\w+):", content)
            if not class_match:
                continue
            class_name = class_match.group(1)

            if class_name not in services:
                continue

            if class_name not in async_methods:
                async_methods[class_name] = set()

            # Find async methods
            methods = re.findall(r"async def (\w+)\(", content)
            for m in methods:
                async_methods[class_name].add(m)

def audit_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if not file.endswith(".py"):
                continue

            file_path = os.path.join(root, file)
            with open(file_path, "r") as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    for service, methods in async_methods.items():
                        for method in methods:
                            pattern = f"{service}.{method}\("
                            if re.search(pattern, line):
                                if "await " not in line and "return " not in line: # Simplified check
                                     print(f"{file_path}:{i+1}: Missing await? -> {line.strip()}")
                                elif "return " in line and "await " not in line:
                                     # Could be returning a coroutine intentionally, but usually not in this app
                                     print(f"{file_path}:{i+1}: Returning coroutine? -> {line.strip()}")

if __name__ == "__main__":
    get_async_methods()
    print("Detected Async Methods:")
    for s, ms in async_methods.items():
        print(f"  {s}: {len(ms)} methods")

    print("\nAuditing app/api...")
    audit_directory("app/api")
    print("\nAuditing app/services...")
    audit_directory("app/services")
    print("\nAuditing app/core...")
    audit_directory("app/core")
    print("\nAuditing app/main.py...")
    audit_directory("app/main.py")
