#!/usr/bin/env python3
"""#55 close-criteria packaging smokes.

Deep Agents loads `skills=` as a directory of Agent Skills (SKILL.md).
Codex loads `.codex-plugin/plugin.json` → `hooks/hooks.json`.
Neither host is installed in this sandbox; these tests prove the on-disk
contract those hosts would load after the hook rename.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


class TestDeepAgentsSkillsLayout(unittest.TestCase):
    def test_skills_dir_is_agent_skills_layout(self) -> None:
        skills = REPO / "skills"
        self.assertTrue(skills.is_dir())
        found = sorted(p for p in skills.iterdir() if p.is_dir())
        self.assertGreaterEqual(len(found), 4, found)
        for skill in found:
            md = skill / "SKILL.md"
            self.assertTrue(md.is_file(), md)
            text = md.read_text(encoding="utf-8")
            match = re.match(r"^---\n(.*?)\n---", text, re.S)
            self.assertIsNotNone(match, skill)
            block = match.group(1)
            self.assertRegex(block, r"(?m)^name: [a-z0-9-]+$")
            self.assertRegex(block, r"(?m)^description: .+$")

    def test_deep_agents_host_wrapper_points_at_skills(self) -> None:
        wrapper = (REPO / "hosts/deep-agents/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("skills=", wrapper)
        self.assertIn("docs/LANG_CHAIN_DEEP_AGENTS.md", wrapper)


class TestCodexHookPackaging(unittest.TestCase):
    def test_codex_manifest_hooks_resolve_to_validate(self) -> None:
        manifest = json.loads((REPO / ".codex-plugin/plugin.json").read_text())
        hooks_rel = manifest["hooks"]
        hooks_path = REPO / hooks_rel
        self.assertTrue(hooks_path.is_file(), hooks_rel)
        data = json.loads(hooks_path.read_text(encoding="utf-8"))
        commands = []
        for entry in (data.get("hooks") or {}).get("PostToolUse") or []:
            for hook in entry.get("hooks") or []:
                commands.append(hook.get("command") or "")
        joined = " ".join(commands)
        self.assertIn("okf-hook-validate.sh", joined)
        self.assertNotIn("okf-curate.sh", joined)
        self.assertTrue((REPO / "scripts/okf-hook-validate.sh").is_file())


if __name__ == "__main__":
    unittest.main()
