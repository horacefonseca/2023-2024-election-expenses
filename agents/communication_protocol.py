"""
Agent Communication Protocol
Message passing and coordination between agents

Author: Campaign Finance Analysis Team
Date: 2025-12-10
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
import json
from queue import Queue, PriorityQueue

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of inter-agent messages"""
    TASK_REQUEST = "task_request"
    TASK_RESULT = "task_result"
    STATUS_UPDATE = "status_update"
    ERROR_REPORT = "error_report"
    DATA_SHARE = "data_share"
    COORDINATION = "coordination"
    APPROVAL_REQUEST = "approval_request"
    APPROVAL_RESPONSE = "approval_response"


class MessagePriority(Enum):
    """Message priority levels"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


@dataclass
class AgentMessage:
    """Represents a message between agents"""
    message_id: str
    timestamp: datetime
    sender: str
    recipient: str
    message_type: MessageType
    priority: MessagePriority
    payload: Dict[str, Any]
    requires_response: bool = False
    response_timeout_seconds: int = 300
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert message to dictionary for serialization"""
        return {
            'message_id': self.message_id,
            'timestamp': self.timestamp.isoformat(),
            'sender': self.sender,
            'recipient': self.recipient,
            'message_type': self.message_type.value,
            'priority': self.priority.value,
            'payload': self.payload,
            'requires_response': self.requires_response,
            'response_timeout_seconds': self.response_timeout_seconds,
            'metadata': self.metadata
        }

    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


class MessageBus:
    """
    Central message bus for agent communication.
    Implements publish-subscribe pattern with priority queue.
    """

    def __init__(self):
        self.message_queue = PriorityQueue()
        self.message_log: List[AgentMessage] = []
        self.subscribers: Dict[str, List[str]] = {}  # message_type -> [agent_names]
        self.pending_responses: Dict[str, AgentMessage] = {}

    def subscribe(self, agent_name: str, message_types: List[MessageType]):
        """
        Subscribe an agent to specific message types.

        Args:
            agent_name (str): Name of the agent
            message_types (List[MessageType]): Types of messages to receive
        """
        for msg_type in message_types:
            type_key = msg_type.value
            if type_key not in self.subscribers:
                self.subscribers[type_key] = []
            if agent_name not in self.subscribers[type_key]:
                self.subscribers[type_key].append(agent_name)
                logger.info(f"{agent_name} subscribed to {msg_type.value} messages")

    def publish(self, message: AgentMessage):
        """
        Publish a message to the bus.

        Args:
            message (AgentMessage): Message to publish
        """
        # Add to priority queue (lower priority number = higher priority)
        priority = message.priority.value
        self.message_queue.put((priority, message))

        # Log message
        self.message_log.append(message)

        # Track if response is required
        if message.requires_response:
            self.pending_responses[message.message_id] = message

        logger.info(
            f"Message published: {message.sender} → {message.recipient} "
            f"[{message.message_type.value}]"
        )

    def get_next_message(self, agent_name: str = None) -> Optional[AgentMessage]:
        """
        Get next message from queue.

        Args:
            agent_name (str, optional): Filter messages for specific agent

        Returns:
            AgentMessage or None
        """
        if self.message_queue.empty():
            return None

        # Get highest priority message
        priority, message = self.message_queue.get()

        # Check if message is for this agent
        if agent_name and message.recipient != agent_name:
            # Put it back if not for this agent
            self.message_queue.put((priority, message))
            return None

        return message

    def send_direct(self, sender: str, recipient: str, message_type: MessageType,
                    payload: Dict, priority: MessagePriority = MessagePriority.NORMAL,
                    requires_response: bool = False) -> str:
        """
        Send a direct message from one agent to another.

        Args:
            sender (str): Sending agent name
            recipient (str): Receiving agent name
            message_type (MessageType): Type of message
            payload (Dict): Message data
            priority (MessagePriority): Message priority
            requires_response (bool): Whether response is required

        Returns:
            str: Message ID
        """
        message_id = f"{sender}_{recipient}_{datetime.now().timestamp()}"

        message = AgentMessage(
            message_id=message_id,
            timestamp=datetime.now(),
            sender=sender,
            recipient=recipient,
            message_type=message_type,
            priority=priority,
            payload=payload,
            requires_response=requires_response
        )

        self.publish(message)
        return message_id

    def broadcast(self, sender: str, message_type: MessageType, payload: Dict,
                  priority: MessagePriority = MessagePriority.NORMAL):
        """
        Broadcast a message to all subscribers of a message type.

        Args:
            sender (str): Sending agent name
            message_type (MessageType): Type of message
            payload (Dict): Message data
            priority (MessagePriority): Message priority
        """
        subscribers = self.subscribers.get(message_type.value, [])

        for recipient in subscribers:
            if recipient != sender:  # Don't send to self
                self.send_direct(sender, recipient, message_type, payload, priority)

        logger.info(f"{sender} broadcast {message_type.value} to {len(subscribers)} agents")

    def respond(self, original_message: AgentMessage, response_payload: Dict):
        """
        Respond to a message that requires response.

        Args:
            original_message (AgentMessage): Message being responded to
            response_payload (Dict): Response data
        """
        response = AgentMessage(
            message_id=f"response_{original_message.message_id}",
            timestamp=datetime.now(),
            sender=original_message.recipient,
            recipient=original_message.sender,
            message_type=MessageType.TASK_RESULT,
            priority=original_message.priority,
            payload=response_payload,
            requires_response=False,
            metadata={'original_message_id': original_message.message_id}
        )

        self.publish(response)

        # Remove from pending responses
        if original_message.message_id in self.pending_responses:
            del self.pending_responses[original_message.message_id]

    def get_message_history(self, agent_name: str = None,
                           message_type: MessageType = None) -> List[AgentMessage]:
        """
        Get message history with optional filtering.

        Args:
            agent_name (str, optional): Filter by sender or recipient
            message_type (MessageType, optional): Filter by message type

        Returns:
            List[AgentMessage]: Filtered message history
        """
        messages = self.message_log

        if agent_name:
            messages = [m for m in messages
                       if m.sender == agent_name or m.recipient == agent_name]

        if message_type:
            messages = [m for m in messages if m.message_type == message_type]

        return messages


class CoordinationProtocol:
    """
    Coordination patterns for multi-agent workflows.
    """

    def __init__(self, message_bus: MessageBus):
        self.message_bus = message_bus

    def request_approval(self, requester: str, approver: str, request_details: Dict) -> str:
        """
        Request approval from another agent (e.g., specialist → manager).

        Args:
            requester (str): Agent requesting approval
            approver (str): Agent who can approve
            request_details (Dict): Details of what needs approval

        Returns:
            str: Message ID
        """
        return self.message_bus.send_direct(
            sender=requester,
            recipient=approver,
            message_type=MessageType.APPROVAL_REQUEST,
            payload=request_details,
            priority=MessagePriority.HIGH,
            requires_response=True
        )

    def delegate_task(self, delegator: str, delegate: str, task_details: Dict) -> str:
        """
        Delegate a task to another agent.

        Args:
            delegator (str): Agent delegating the task
            delegate (str): Agent receiving the task
            task_details (Dict): Task details

        Returns:
            str: Message ID
        """
        return self.message_bus.send_direct(
            sender=delegator,
            recipient=delegate,
            message_type=MessageType.TASK_REQUEST,
            payload=task_details,
            priority=MessagePriority.NORMAL,
            requires_response=True
        )

    def share_data(self, sender: str, recipient: str, data: Dict) -> str:
        """
        Share data between agents.

        Args:
            sender (str): Agent sharing data
            recipient (str): Agent receiving data
            data (Dict): Data to share

        Returns:
            str: Message ID
        """
        return self.message_bus.send_direct(
            sender=sender,
            recipient=recipient,
            message_type=MessageType.DATA_SHARE,
            payload=data,
            priority=MessagePriority.NORMAL
        )

    def coordinate_parallel_tasks(self, coordinator: str, participants: List[str],
                                 task_details: Dict) -> List[str]:
        """
        Coordinate parallel execution across multiple agents.

        Args:
            coordinator (str): Coordinating agent
            participants (List[str]): Agents to execute in parallel
            task_details (Dict): Task details

        Returns:
            List[str]: List of message IDs
        """
        message_ids = []

        for participant in participants:
            msg_id = self.delegate_task(coordinator, participant, task_details)
            message_ids.append(msg_id)

        logger.info(
            f"{coordinator} coordinating parallel tasks with {len(participants)} agents"
        )

        return message_ids


# ==============================================================================
# MAIN - FOR TESTING
# ==============================================================================

if __name__ == "__main__":
    # Create message bus
    bus = MessageBus()

    # Subscribe agents to messages
    bus.subscribe("data_analyst", [MessageType.TASK_REQUEST, MessageType.DATA_SHARE])
    bus.subscribe("manager", [MessageType.TASK_RESULT, MessageType.APPROVAL_REQUEST])
    bus.subscribe("backend_specialist", [MessageType.TASK_REQUEST])

    # Create coordination protocol
    protocol = CoordinationProtocol(bus)

    # Example 1: Manager delegates task to data analyst
    print("\n=== EXAMPLE 1: Task Delegation ===")
    msg_id = protocol.delegate_task(
        delegator="manager",
        delegate="data_analyst",
        task_details={
            'action': 'classify_committees',
            'parameters': {'cycle': 2024}
        }
    )
    print(f"Task delegated with message ID: {msg_id}")

    # Example 2: Data analyst requests approval from manager
    print("\n=== EXAMPLE 2: Approval Request ===")
    approval_id = protocol.request_approval(
        requester="data_analyst",
        approver="manager",
        request_details={
            'action': 'use_external_api',
            'reason': 'Need OpenSecrets data for validation'
        }
    )
    print(f"Approval requested with message ID: {approval_id}")

    # Example 3: Coordinate parallel tasks
    print("\n=== EXAMPLE 3: Parallel Coordination ===")
    parallel_ids = protocol.coordinate_parallel_tasks(
        coordinator="manager",
        participants=["network_analyst", "temporal_analyst"],
        task_details={'action': 'analyze_2024_data'}
    )
    print(f"Parallel tasks coordinated: {len(parallel_ids)} messages sent")

    # Example 4: Get message history
    print("\n=== MESSAGE HISTORY ===")
    history = bus.get_message_history(agent_name="manager")
    print(f"Manager's message history: {len(history)} messages")
    for msg in history:
        print(f"  - {msg.timestamp.strftime('%H:%M:%S')}: {msg.sender} → {msg.recipient} [{msg.message_type.value}]")
