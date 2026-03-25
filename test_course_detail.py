import httpx
import time
import uuid

def test_course_detail():
    base_url = "http://127.0.0.1:8000"

    # 1. Get all courses to find a valid ID
    # Use no trailing slash to avoid 307
    print("Fetching courses...")
    resp = httpx.get(f"{base_url}/api/courses", timeout=30.0)

    if resp.status_code != 200:
        print(f"Failed to fetch courses: {resp.status_code}")
        print(f"Response: {resp.text}")
        return

    courses_data = resp.json().get("data", {})
    courses = courses_data.get("courses", [])
    if not courses:
        print("No courses found to test with.")
        return

    course_id = courses[0]["id"]
    print(f"Testing with course ID: {course_id}")

    # 2. Fetch specific course detail
    print(f"Fetching course detail for {course_id}...")
    resp = httpx.get(f"{base_url}/api/courses/{course_id}")

    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json().get("data", {})
        print("✅ Course detail fetched successfully!")
        print(f"Title: {data.get('title')}")
        modules = data.get("modules", [])
        print(f"Modules found: {len(modules)}")
        if modules:
            topics = modules[0].get("topics", [])
            print(f"Topics in first module: {len(topics)}")
            if topics:
                assessments = topics[0].get("assessments", [])
                print(f"Assessments in first topic: {len(assessments)}")
    else:
        print(f"❌ Failed to fetch course detail: {resp.status_code}")
        print(f"Error: {resp.text}")

if __name__ == "__main__":
    test_course_detail()
