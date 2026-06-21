"""Lead-generation flows built on the GoHighLevel + Kit skills.

A flow is a JSON spec (see ``ai_automation_leadgen/flow.json``) describing a
funnel: a lead-magnet opt-in, a Kit nurture sequence for deliverability, and a
GoHighLevel workflow for CRM-side automation. ``flows.deploy`` provisions the
assets from that spec — dry-run by default, ``--apply`` to execute.

Import from ``flows.deploy`` directly (kept out of this module to avoid an
import cycle warning when running ``python -m flows.deploy``).
"""
