"""
Multi-Agent Orchestrator
Coordinates execution of core and specialized agents with skill management

Author: Campaign Finance Analysis Team
Date: 2025-12-10
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING = "waiting"


@dataclass
class AgentTask:
    """Represents a task assigned to an agent"""
    task_id: str
    agent_name: str
    action: str
    parameters: Dict[str, Any]
    priority: int = 5
    dependencies: List[str] = None
    status: AgentStatus = AgentStatus.WAITING

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class Agent:
    """Base Agent class"""

    def __init__(self, name: str, config: Dict):
        self.name = name
        self.config = config
        self.status = AgentStatus.IDLE
        self.attached_skills = []
        self.task_history = []

    def attach_skill(self, skill_name: str, skill_config: Dict):
        """Attach a subagent skill to this agent"""
        if len(self.attached_skills) >= self.config.get('skill_slots', 5):
            logger.warning(f"{self.name}: Skill slot limit reached")
            return False

        self.attached_skills.append({
            'name': skill_name,
            'config': skill_config
        })
        logger.info(f"{self.name}: Attached skill '{skill_name}'")
        return True

    def detach_skill(self, skill_name: str):
        """Detach a skill from this agent"""
        self.attached_skills = [s for s in self.attached_skills if s['name'] != skill_name]
        logger.info(f"{self.name}: Detached skill '{skill_name}'")

    def execute_task(self, task: AgentTask) -> Dict:
        """
        Execute an assigned task.

        Args:
            task (AgentTask): Task to execute

        Returns:
            dict: Task execution results
        """
        logger.info(f"{self.name}: Executing task {task.task_id} - {task.action}")
        self.status = AgentStatus.RUNNING

        try:
            # Task execution logic (placeholder - implement specific actions)
            result = {
                'task_id': task.task_id,
                'agent': self.name,
                'status': 'success',
                'output': f"Task {task.action} completed",
                'data': {}
            }

            self.status = AgentStatus.COMPLETED
            self.task_history.append(task.task_id)
            return result

        except Exception as e:
            logger.error(f"{self.name}: Task {task.task_id} failed: {str(e)}")
            self.status = AgentStatus.FAILED
            return {
                'task_id': task.task_id,
                'agent': self.name,
                'status': 'failed',
                'error': str(e)
            }

    def can_execute(self, task: AgentTask) -> bool:
        """Check if agent can execute the task"""
        return self.status in [AgentStatus.IDLE, AgentStatus.COMPLETED]


class MultiAgentOrchestrator:
    """
    Orchestrates multiple agents working together on campaign finance analysis.
    """

    def __init__(self, config_dir: Path = None):
        """
        Initialize the orchestrator.

        Args:
            config_dir (Path): Directory containing agent config files
        """
        if config_dir is None:
            config_dir = Path(__file__).parent / "config"

        self.config_dir = config_dir
        self.core_agents: Dict[str, Agent] = {}
        self.specialized_agents: Dict[str, Agent] = {}
        self.skills_registry = {}
        self.task_queue: List[AgentTask] = []
        self.completed_tasks: List[str] = []

        # Load configurations
        self._load_configurations()

    def _load_configurations(self):
        """Load agent and skill configurations from YAML files"""
        logger.info("Loading agent configurations...")

        # Load core agents
        core_config_path = self.config_dir / "core_agents.yaml"
        if core_config_path.exists():
            with open(core_config_path, 'r') as f:
                core_config = yaml.safe_load(f)
                for agent_name, agent_config in core_config['agents'].items():
                    self.core_agents[agent_name] = Agent(agent_name, agent_config)
                    logger.info(f"Loaded core agent: {agent_name}")

        # Load specialized agents
        specialized_config_path = self.config_dir / "specialized_agents.yaml"
        if specialized_config_path.exists():
            with open(specialized_config_path, 'r') as f:
                specialized_config = yaml.safe_load(f)
                for agent_name, agent_config in specialized_config['agents'].items():
                    self.specialized_agents[agent_name] = Agent(agent_name, agent_config)
                    logger.info(f"Loaded specialized agent: {agent_name}")

        # Load skills registry
        skills_config_path = self.config_dir / "subagent_skills.yaml"
        if skills_config_path.exists():
            with open(skills_config_path, 'r') as f:
                skills_config = yaml.safe_load(f)
                self.skills_registry = skills_config['skills']
                logger.info(f"Loaded {len(self.skills_registry)} skills")

        logger.info(
            f"Orchestrator initialized: {len(self.core_agents)} core agents, "
            f"{len(self.specialized_agents)} specialized agents, "
            f"{len(self.skills_registry)} skills available"
        )

    def attach_skill_to_agent(self, agent_name: str, skill_name: str) -> bool:
        """
        Attach a skill to an agent.

        Args:
            agent_name (str): Name of the agent
            skill_name (str): Name of the skill

        Returns:
            bool: Success status
        """
        # Find agent
        agent = self.core_agents.get(agent_name) or self.specialized_agents.get(agent_name)
        if not agent:
            logger.error(f"Agent '{agent_name}' not found")
            return False

        # Find skill
        if skill_name not in self.skills_registry:
            logger.error(f"Skill '{skill_name}' not found in registry")
            return False

        skill_config = self.skills_registry[skill_name]

        # Check if skill is attachable to this agent
        if 'attachable_to' in skill_config:
            if agent_name not in skill_config['attachable_to']:
                logger.error(f"Skill '{skill_name}' cannot be attached to '{agent_name}'")
                return False

        return agent.attach_skill(skill_name, skill_config)

    def submit_task(self, task: AgentTask):
        """Add a task to the queue"""
        self.task_queue.append(task)
        logger.info(f"Task {task.task_id} submitted to queue (priority {task.priority})")

    def execute_workflow(self, workflow: List[AgentTask]) -> List[Dict]:
        """
        Execute a workflow of multiple tasks across agents.

        Args:
            workflow (List[AgentTask]): List of tasks to execute

        Returns:
            List[Dict]: Results from each task
        """
        logger.info(f"Executing workflow with {len(workflow)} tasks")

        results = []

        # Sort by priority (lower number = higher priority)
        workflow.sort(key=lambda t: t.priority)

        for task in workflow:
            # Check dependencies
            if not all(dep in self.completed_tasks for dep in task.dependencies):
                logger.warning(f"Task {task.task_id} dependencies not met, skipping")
                continue

            # Find agent and execute
            agent = self.core_agents.get(task.agent_name) or \
                    self.specialized_agents.get(task.agent_name)

            if not agent:
                logger.error(f"Agent '{task.agent_name}' not found for task {task.task_id}")
                continue

            if not agent.can_execute(task):
                logger.warning(f"Agent '{task.agent_name}' cannot execute task {task.task_id}")
                continue

            # Execute task
            result = agent.execute_task(task)
            results.append(result)

            if result['status'] == 'success':
                self.completed_tasks.append(task.task_id)

        logger.info(f"Workflow completed: {len(results)} tasks executed")
        return results

    async def execute_parallel(self, tasks: List[AgentTask]) -> List[Dict]:
        """
        Execute multiple independent tasks in parallel.

        Args:
            tasks (List[AgentTask]): Tasks to execute in parallel

        Returns:
            List[Dict]: Results from each task
        """
        logger.info(f"Executing {len(tasks)} tasks in parallel")

        async def run_task(task: AgentTask):
            agent = self.core_agents.get(task.agent_name) or \
                    self.specialized_agents.get(task.agent_name)
            if agent and agent.can_execute(task):
                return agent.execute_task(task)
            return {'error': f'Cannot execute task {task.task_id}'}

        results = await asyncio.gather(*[run_task(task) for task in tasks])
        return list(results)

    def get_agent_status(self) -> Dict:
        """Get status of all agents"""
        status = {
            'core_agents': {name: agent.status.value for name, agent in self.core_agents.items()},
            'specialized_agents': {name: agent.status.value for name, agent in self.specialized_agents.items()},
            'task_queue_size': len(self.task_queue),
            'completed_tasks': len(self.completed_tasks)
        }
        return status

    def get_agent_skills(self, agent_name: str) -> List[str]:
        """Get list of skills attached to an agent"""
        agent = self.core_agents.get(agent_name) or self.specialized_agents.get(agent_name)
        if not agent:
            return []
        return [skill['name'] for skill in agent.attached_skills]


# ==============================================================================
# EXAMPLE WORKFLOWS
# ==============================================================================

def analyze_new_fec_data_workflow(orchestrator: MultiAgentOrchestrator):
    """
    Example workflow: Analyzing new FEC dataset

    Steps:
    1. Backend downloads files
    2. Data analyst classifies committees (with FEC code expert skill)
    3. Data analyst determines partisan lean (with partisan classifier skill)
    4. Network analyst builds graph (parallel)
    5. Temporal analyst analyzes trends (parallel)
    6. Frontend updates dashboards
    7. Manager validates results
    """
    workflow = [
        AgentTask(
            task_id="download_fec",
            agent_name="backend_specialist",
            action="download_fec_data",
            parameters={'cycle': 2024},
            priority=1
        ),
        AgentTask(
            task_id="classify_committees",
            agent_name="data_analyst",
            action="classify_committees",
            parameters={'use_skill': 'fec_code_expert'},
            priority=2,
            dependencies=["download_fec"]
        ),
        AgentTask(
            task_id="determine_partisan",
            agent_name="data_analyst",
            action="classify_partisan",
            parameters={'use_skill': 'partisan_classifier'},
            priority=2,
            dependencies=["classify_committees"]
        ),
        AgentTask(
            task_id="network_analysis",
            agent_name="network_analyst",
            action="build_donor_network",
            parameters={},
            priority=3,
            dependencies=["determine_partisan"]
        ),
        AgentTask(
            task_id="temporal_analysis",
            agent_name="temporal_analyst",
            action="detect_late_cycle_spikes",
            parameters={},
            priority=3,
            dependencies=["determine_partisan"]
        ),
        AgentTask(
            task_id="update_dashboard",
            agent_name="frontend_specialist",
            action="refresh_charts",
            parameters={},
            priority=4,
            dependencies=["network_analysis", "temporal_analysis"]
        ),
        AgentTask(
            task_id="validate_results",
            agent_name="manager",
            action="validate_pipeline",
            parameters={},
            priority=5,
            dependencies=["update_dashboard"]
        )
    ]

    return orchestrator.execute_workflow(workflow)


# ==============================================================================
# MAIN - FOR TESTING
# ==============================================================================

if __name__ == "__main__":
    # Initialize orchestrator
    orchestrator = MultiAgentOrchestrator()

    # Attach skills to agents
    orchestrator.attach_skill_to_agent("data_analyst", "fec_code_expert")
    orchestrator.attach_skill_to_agent("data_analyst", "partisan_classifier")
    orchestrator.attach_skill_to_agent("data_analyst", "donor_tier_analyzer")
    orchestrator.attach_skill_to_agent("sentiment_analyst", "topic_modeler")

    # Check status
    print("\n=== AGENT STATUS ===")
    status = orchestrator.get_agent_status()
    print(f"Core agents: {list(status['core_agents'].keys())}")
    print(f"Specialized agents: {list(status['specialized_agents'].keys())}")

    # Check skills
    print("\n=== DATA ANALYST SKILLS ===")
    skills = orchestrator.get_agent_skills("data_analyst")
    print(f"Attached skills: {skills}")

    # Run example workflow
    print("\n=== RUNNING EXAMPLE WORKFLOW ===")
    results = analyze_new_fec_data_workflow(orchestrator)
    print(f"Workflow completed with {len(results)} tasks")
    for result in results:
        print(f"  - {result['task_id']}: {result['status']}")
