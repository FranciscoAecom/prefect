import asyncio
from prefect import get_client

async def main():
    async with get_client() as client:
        runs = await client.read_flow_runs(limit=10)
        for r in runs:
            print('FLOW', r.id, r.name, r.state_name, r.state_type, 'start', r.start_time)
            tasks = await client.read_task_runs(flow_run_id=r.id, limit=50)
            for t in tasks:
                print(' TASK', t.id, t.name, t.state_name, 'start', t.start_time, 'end', t.end_time)

asyncio.run(main())
