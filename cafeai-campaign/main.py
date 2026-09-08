import uuid

from graphs import AdCampaignBuilderWorkflow


def start_agent():
    agent = AdCampaignBuilderWorkflow()
    agent.start(
        input_obj={
            "user_id": str(uuid.uuid4()),
        },
        session_id=str(uuid.uuid4())
    )

if __name__ == '__main__':
    start_agent()