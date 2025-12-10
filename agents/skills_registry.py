"""
Skills Registry
Dynamic skill loading and management system for multi-agent framework

Author: Campaign Finance Analysis Team
Date: 2025-12-10
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Skill:
    """Represents a subagent skill"""
    name: str
    category: str
    description: str
    word_count: int
    attachable_to: List[str]
    skill_level: str
    tools: List[str]
    outputs: List[str]

    def can_attach_to(self, agent_name: str) -> bool:
        """Check if skill can be attached to given agent"""
        return agent_name in self.attachable_to

    def get_capabilities(self) -> List[str]:
        """Extract key capabilities from description"""
        # Simple extraction - in production, use NLP
        capabilities = []
        if "partisan" in self.description.lower():
            capabilities.append("partisan_analysis")
        if "donor" in self.description.lower():
            capabilities.append("donor_analysis")
        if "fec" in self.description.lower():
            capabilities.append("fec_expertise")
        return capabilities


class SkillsRegistry:
    """
    Central registry for all available skills.
    Provides skill discovery, validation, and attachment logic.
    """

    def __init__(self, config_path: Path = None):
        """
        Initialize skills registry.

        Args:
            config_path (Path): Path to subagent_skills.yaml
        """
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "subagent_skills.yaml"

        self.config_path = config_path
        self.skills: Dict[str, Skill] = {}
        self._load_skills()

    def _load_skills(self):
        """Load all skills from configuration file"""
        logger.info(f"Loading skills from {self.config_path}")

        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)

            for skill_name, skill_config in config['skills'].items():
                skill = Skill(
                    name=skill_name,
                    category=skill_config.get('category', 'general'),
                    description=skill_config.get('description', ''),
                    word_count=skill_config.get('word_count', 0),
                    attachable_to=skill_config.get('attachable_to', []),
                    skill_level=skill_config.get('skill_level', 'intermediate'),
                    tools=skill_config.get('tools', []),
                    outputs=skill_config.get('outputs', [])
                )
                self.skills[skill_name] = skill

            logger.info(f"Loaded {len(self.skills)} skills successfully")

        except Exception as e:
            logger.error(f"Failed to load skills: {str(e)}")
            raise

    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """Get a skill by name"""
        return self.skills.get(skill_name)

    def list_skills(self, category: str = None, agent_name: str = None) -> List[str]:
        """
        List available skills.

        Args:
            category (str, optional): Filter by category
            agent_name (str, optional): Filter by attachable agent

        Returns:
            List[str]: List of skill names
        """
        skills = self.skills.values()

        if category:
            skills = [s for s in skills if s.category == category]

        if agent_name:
            skills = [s for s in skills if s.can_attach_to(agent_name)]

        return [s.name for s in skills]

    def get_skills_by_category(self) -> Dict[str, List[str]]:
        """Group skills by category"""
        categories = {}
        for skill in self.skills.values():
            if skill.category not in categories:
                categories[skill.category] = []
            categories[skill.category].append(skill.name)
        return categories

    def get_skills_for_agent(self, agent_name: str) -> List[Skill]:
        """Get all skills attachable to a specific agent"""
        return [s for s in self.skills.values() if s.can_attach_to(agent_name)]

    def validate_skill_combination(self, skill_names: List[str]) -> bool:
        """
        Validate that a combination of skills is compatible.

        Args:
            skill_names (List[str]): List of skill names to validate

        Returns:
            bool: True if compatible, False otherwise
        """
        # Check for conflicts (e.g., can't have two partisan classifiers)
        categories_used = {}
        for skill_name in skill_names:
            skill = self.get_skill(skill_name)
            if not skill:
                logger.warning(f"Skill '{skill_name}' not found")
                return False

            # Limit one skill per category for some categories
            exclusive_categories = ['partisan_analysis', 'donor_analysis']
            if skill.category in exclusive_categories:
                if skill.category in categories_used:
                    logger.warning(
                        f"Cannot attach multiple skills from category '{skill.category}'"
                    )
                    return False
                categories_used[skill.category] = skill_name

        return True

    def recommend_skills(self, agent_name: str, max_recommendations: int = 3) -> List[str]:
        """
        Recommend skills for an agent based on role and existing skills.

        Args:
            agent_name (str): Name of the agent
            max_recommendations (int): Maximum number of recommendations

        Returns:
            List[str]: Recommended skill names
        """
        # Get all available skills for this agent
        available_skills = self.get_skills_for_agent(agent_name)

        # Simple recommendation logic (can be enhanced with ML)
        recommendations = []

        # Prioritize expert-level skills
        expert_skills = [s for s in available_skills if s.skill_level == 'expert']
        recommendations.extend([s.name for s in expert_skills[:max_recommendations]])

        # Fill remaining slots with advanced skills
        if len(recommendations) < max_recommendations:
            advanced_skills = [s for s in available_skills if s.skill_level == 'advanced']
            remaining = max_recommendations - len(recommendations)
            recommendations.extend([s.name for s in advanced_skills[:remaining]])

        return recommendations

    def search_skills(self, query: str) -> List[str]:
        """
        Search for skills by keyword.

        Args:
            query (str): Search query

        Returns:
            List[str]: Matching skill names
        """
        query_lower = query.lower()
        matches = []

        for skill in self.skills.values():
            if query_lower in skill.name.lower() or \
               query_lower in skill.description.lower() or \
               query_lower in skill.category.lower():
                matches.append(skill.name)

        return matches

    def get_skill_dependencies(self, skill_name: str) -> List[str]:
        """
        Get dependencies for a skill (other skills it requires).

        Args:
            skill_name (str): Skill name

        Returns:
            List[str]: List of required skill names
        """
        skill = self.get_skill(skill_name)
        if not skill:
            return []

        # In production, this would be defined in config
        # For now, return empty list
        return []

    def export_skill_documentation(self, output_path: Path):
        """Export all skills to a markdown documentation file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Subagent Skills Documentation\n\n")
            f.write(f"Total Skills: {len(self.skills)}\n\n")

            # Group by category
            categories = self.get_skills_by_category()

            for category, skill_names in sorted(categories.items()):
                f.write(f"## {category.upper().replace('_', ' ')}\n\n")

                for skill_name in sorted(skill_names):
                    skill = self.get_skill(skill_name)
                    f.write(f"### {skill.name}\n\n")
                    f.write(f"**Level:** {skill.skill_level}\n\n")
                    f.write(f"**Attachable to:** {', '.join(skill.attachable_to)}\n\n")
                    f.write(f"**Word Count:** {skill.word_count}\n\n")
                    f.write(f"**Description:**\n{skill.description}\n\n")
                    f.write(f"**Tools:** {', '.join(skill.tools)}\n\n")
                    f.write(f"**Outputs:** {', '.join(skill.outputs)}\n\n")
                    f.write("---\n\n")

        logger.info(f"Skill documentation exported to {output_path}")


# ==============================================================================
# MAIN - FOR TESTING
# ==============================================================================

if __name__ == "__main__":
    # Initialize registry
    registry = SkillsRegistry()

    print(f"\n=== SKILLS REGISTRY ===")
    print(f"Total skills loaded: {len(registry.skills)}")

    # List skills by category
    print("\n=== SKILLS BY CATEGORY ===")
    categories = registry.get_skills_by_category()
    for category, skills in categories.items():
        print(f"{category}: {len(skills)} skills")
        for skill in skills:
            print(f"  - {skill}")

    # Get skills for specific agent
    print("\n=== SKILLS FOR DATA ANALYST ===")
    data_analyst_skills = registry.get_skills_for_agent("data_analyst")
    for skill in data_analyst_skills:
        print(f"  - {skill.name} ({skill.skill_level})")

    # Recommend skills
    print("\n=== RECOMMENDED SKILLS FOR DATA ANALYST ===")
    recommendations = registry.recommend_skills("data_analyst", max_recommendations=5)
    for rec in recommendations:
        print(f"  - {rec}")

    # Search skills
    print("\n=== SEARCH: 'partisan' ===")
    search_results = registry.search_skills("partisan")
    for result in search_results:
        print(f"  - {result}")

    # Export documentation
    output_path = Path(__file__).parent / "config" / "SKILLS_DOCUMENTATION.md"
    registry.export_skill_documentation(output_path)
    print(f"\n✓ Documentation exported to {output_path}")
