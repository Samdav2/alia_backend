import httpx
import time
import subprocess
import os

def run_tests():
    base_url = "http://127.0.0.1:8000"

    # Wait for server to start
    max_retries = 5
    for i in range(max_retries):
        try:
            response = httpx.get(f"{base_url}/")
            if response.status_code == 200:
                print("Server is up!")
                break
        except:
            print(f"Waiting for server... ({i+1}/{max_retries})")
            time.sleep(2)
    else:
        print("Server failed to start")
        return

    # 1. Test Login
    print("\nTesting /api/auth/login...")
    login_data = {"username": "john_doe", "password": "password123"}
    resp = httpx.post(f"{base_url}/api/auth/login", json=login_data)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")

    # 2. Test Get Courses
    print("\nTesting /api/courses/...")
    resp = httpx.get(f"{base_url}/api/courses/")
    print(f"Status: {resp.status_code}")
    courses = resp.json()
    print(f"Courses found: {len(courses)}")
    if courses:
        course_id = courses[0]['id']

        # 3. Test Summarize Agent
        print(f"\nTesting /api/agents/summarize for course {course_id}...")
        summarize_data = {"text": courses[0]['raw_content']}
        resp = httpx.post(f"{base_url}/api/agents/summarize", json=summarize_data)
        print(f"Status: {resp.status_code}")
        print(f"Summary: {resp.json().get('summary')[:100]}...")

        # 4. Test Assessment Agent
        print(f"\nTesting /api/agents/assessment for course {course_id}...")
        assessment_data = {"course_id": course_id, "student_id": 1, "current_score": 50}
        resp = httpx.post(f"{base_url}/api/agents/assessment", json=assessment_data)
        print(f"Status: {resp.status_code}")
        print(f"Question: {resp.json().get('question')[:100]}...")

if __name__ == "__main__":
    run_tests()
