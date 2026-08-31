from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from agents._lib.llm import get_llm


@CrewBase
class DiscoveryCrew:
    """Market Research Crew - market analyst asks users to collect information.

    Single Agent Crew: PM decides each round to continue questioning or output [READY] to enter next phase.
    """

    agents: list[BaseAgent]
    tasks: list[Task]

    agents_config = "../agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def market_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["market_analyst"],
            llm=get_llm(),
            memory=False,
        )

    @task
    def interview_task(self) -> Task:
        return Task(
            config=self.tasks_config["interview_task"],
            agent=self.market_analyst(),
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=False,
        )
