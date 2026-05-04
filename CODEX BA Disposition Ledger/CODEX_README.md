# CODEX BA Disposition Ledger

This folder stores reviewed dispositions for BA findings. Raw BA reports remain unchanged. The JSON ledger records what Codex/human review decided after investigation.

Current first use: Vellum / PG Design Ledger BA findings from 2026-05-03.

Key rule: a BA finding is a suspect until dispositioned. Only confirmed_issue findings should become fix tasks. false_positive, coverage_gap, and investigated_no_action should not be repeatedly treated as fresh emergencies.

