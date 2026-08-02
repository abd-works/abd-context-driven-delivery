"""SkillDeployer - refresh all workspace IDE skill shims via AgentSkills.deploy_again."""
from __future__ import annotations

from utilities.agent_skills.agent_skills import AgentSkills


class SkillDeployer:
    """Re-deploy every toolset shim in the workspace using the saved deploy parameters."""

    def deploy_all(self, workspace_path: str) -> str:
        """Refresh all IDE skill shims under workspace_path.

        Loads the ide and name_filter saved by the last deploy_tools_as_skills run,
        rescans the workspace for toolset files, writes one SKILL.md shim per
        discovered toolset, removes any stale focus shortcuts, and updates the
        hooks config. Returns a summary of deployed skill slugs.
        """
        skills = AgentSkills()
        return skills.deploy_again()
