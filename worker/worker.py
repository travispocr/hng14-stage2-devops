import redis
import time
import os
import signal

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    password=os.getenv("REDIS_PASSWORD", None)
)

shutdown = False


def handle_sigterm(sig, frame):
    global shutdown
    shutdown = True


signal.signal(signal.SIGTERM, handle_sigterm)


def process_job(job_id):
    print(f"Processing job {job_id}")
    time.sleep(2)  # simulate work
    r.hset(f"job:{job_id}", "status", "completed")
    print(f"Done: {job_id}")


while not shutdown:
    job = r.brpop(os.getenv("QUEUE_NAME", "jobs"), timeout=5)
    if job:
        _, job_id = job
        process_job(job_id.decode())
