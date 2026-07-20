async def simple_work(ctx, data):
    print(f"Processing job data: {data}")
    return f"Success: {data}"

class WorkerSettings:
    functions = [simple_work]