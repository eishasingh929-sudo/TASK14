import time
import threading
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from uniguru.service.api import app

client = TestClient(app)

def send_voice_query(i):
    audio_data = b"mock-audio-content"
    headers = {
        "X-Caller-Name": "internal-testing",
        "X-Audio-Filename": "sample-hi.wav",
        "X-Voice-Language": "hi",
        "Content-Type": "audio/wav"
    }
    start = time.perf_counter()
    response = client.post("/voice/query", content=audio_data, headers=headers)
    end = time.perf_counter()
    return response.status_code, (end - start) * 1000

def test_performance_consecutive():
    print("\nRunning 10 consecutive voice queries...")
    latencies = []
    for i in range(10):
        status, latency = send_voice_query(i)
        if status != 200:
            print(f"FAILED Query {i+1}: Status {status}, Latency {latency:.2f}ms")
            # Get response details if possible? No, we didn't return it.
        assert status == 200
        latencies.append(latency)
        print(f"Query {i+1}: {latency:.2f}ms")
    avg = sum(latencies) / len(latencies)
    print(f"Average Latency: {avg:.2f}ms")

def test_performance_concurrent():
    print("\nRunning 5 concurrent voice queries...")
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(send_voice_query, i) for i in range(5)]
        results = [f.result() for f in futures]
    
    for status, latency in results:
        assert status == 200
        print(f"Concurrent Query: {latency:.2f}ms")

if __name__ == "__main__":
    test_performance_consecutive()
    test_performance_concurrent()
