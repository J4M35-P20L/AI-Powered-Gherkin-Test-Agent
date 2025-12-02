import os
import json
import hashlib
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from autotester.core.agent import get_ui_summary

class WorkflowMemory:
    """Manages the learning and saving of application workflows."""

    def __init__(self, app_name: str):
        self.app_name = app_name.replace(':', '_')
        self.workflow_dir = 'workflows'
        self.workflow_file = os.path.join(self.workflow_dir, f"{self.app_name}_workflow.json")
        os.makedirs(self.workflow_dir, exist_ok=True)
        self.graph = self.load_workflow()

    def load_workflow(self):
        if os.path.exists(self.workflow_file):
            try:
                with open(self.workflow_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {"nodes": {}, "edges": []}
        return {"nodes": {}, "edges": []}

    def save_workflow(self):
        with open(self.workflow_file, 'w') as f:
            json.dump(self.graph, f, indent=4)

    @staticmethod
    def get_app_name_from_url(url: str) -> str:
        try:
            parsed_url = urlparse(url)
            name = f"{parsed_url.netloc}{parsed_url.path}".replace('/', '_').replace(':', '_')
            return name.strip('_') or "default_app"
        except Exception:
            return "default_app"

    def get_state_hash(self, page_or_app) -> str:
        """
        Creates a highly stable hash based on STABLE, STRUCTURAL regions of a page,
        ignoring dynamic content areas like search results.
        """
        if hasattr(page_or_app, 'content'): # Playwright Page
            try:
                html_content = page_or_app.content()
                soup = BeautifulSoup(html_content, 'html.parser')

                element_signatures = []

                # --- FINAL FIX: Define stable structural regions to hash ---
                # These are CSS selectors for containers that DO NOT change, like headers or sidebars.
                # This makes the hash resilient to dynamic content in the main body.
                # These selectors are specific to Amazon and can be adapted for other sites.
                stable_region_selectors = [
                    'div#nav-belt',      # Top-most navigation bar
                    'div#nav-main',      # Main navigation bar below the top one
                    'div#leftNav'        # The left-hand filter sidebar on search results
                ]

                # We only search for elements within these stable regions.
                for selector in stable_region_selectors:
                    region = soup.select_one(selector)
                    if region:
                        for el in region.find_all(['input', 'button', 'select', 'textarea']):
                            if el.name == 'input' and el.get('type') == 'hidden':
                                continue

                            signature = {
                                "tag": el.name,
                                "id": el.get('id'),
                                "name": el.get('name'),
                                "type": el.get('type'),
                                "value": el.get('value', '')
                            }
                            element_signatures.append(signature)

                # If no stable regions were found (e.g., on a simple page), fall back to old method
                if not element_signatures:
                    for el in soup.find_all(['input', 'button', 'select', 'textarea']):
                        signature = {"tag": el.name, "id": el.get('id'),"name": el.get('name'),"type": el.get('type'),"value": el.get('value', '')}
                        element_signatures.append(signature)

                sorted_signatures = sorted(element_signatures, key=lambda x: (x['tag'], x.get('id') or '', x.get('name') or ''))
                signature_str = json.dumps(sorted_signatures, sort_keys=True)
                return hashlib.md5(signature_str.encode('utf-8')).hexdigest()

            except Exception as e:
                return hashlib.md5(f"error_getting_content:{str(e)}".encode()).hexdigest()

        else: # Desktop apps
            ui_summary = get_ui_summary(page_or_app)
            return hashlib.md5(ui_summary.encode('utf-8')).hexdigest()

    def remember_state_and_action(self, page, from_state_hash, action, logger):
        to_state_hash = self.get_state_hash(page)

        if from_state_hash == to_state_hash:
            logger.warning(f"State did not change after action {action}. Not creating new edge.")
            return

        logger.info(f"Discovered and remembered new page state: {to_state_hash}")

        new_edge = {"from": from_state_hash, "to": to_state_hash, "action": action}

        if to_state_hash not in self.graph["nodes"]:
            self.graph["nodes"][to_state_hash] = {"description": "State discovered during learning"}

        if new_edge not in self.graph['edges']:
            self.graph['edges'].append(new_edge)
            logger.info(f"Remembered new workflow edge from {from_state_hash[:8]} to {to_state_hash[:8]}")
            self.save_workflow()
        else:
            logger.info("Edge already exists in the workflow graph.")
