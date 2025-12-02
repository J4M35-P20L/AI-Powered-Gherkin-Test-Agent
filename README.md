**🤖 AI-Powered Gherkin Test Agent**
An innovative testing framework that uses GenAI principles to translate natural language test steps (Gherkin) into resilient, self-healing UI actions. This moves test automation from brittle, fixed locators to intelligent, semantic understanding.

**💡 Core Architecture: From Intent to Action**
This project demonstrates a resilient approach by strictly separating the Test Intent from the Execution Strategy.

<img width="878" height="388" alt="image" src="https://github.com/user-attachments/assets/1923e763-d1ac-42ad-95ee-c7ad0a85231e" />

**✨ Key Features & Resilience**

<img width="862" height="327" alt="image" src="https://github.com/user-attachments/assets/13b4039d-7b38-4a1a-9312-86cc5285a9ba" />

**🛠️ Getting Started**
📦 Project Structure

AI-Powered-Gherkin-Test-Agent/
├── features/
│   └── login.feature             # Example Gherkin feature file
├── feature_parser.py             # Parses Gherkin into semantic maps.
├── agent_executor.py             # (To be Developed) Executes intelligent actions.
├── requirements.txt              # Project dependencies (Selenium/Playwright, BeautifulSoup).
└── README.md

**✅ Installation**
1. Clone the Repository: git clone https://github.com/[Your-Username]/AI-Powered-Gherkin-Test-Agent.git
                         cd AI-Powered-Gherkin-Test-Agent
2. Install Dependencies: pip install -r requirements.txt
   📌 Note: For GenAI features, you will need to configure your environment with necessary API keys (e.g., for Gemini or OpenAI) within the agent_executor.py module.

📝 Usage Example**
Gherkin Input (login.feature)**
Scenario: Successful login with valid credentials
  When the user enters "corp code" as "slqa"
  And the user enters "location code" as "test7"
  And the user clicks on login button

**Parser Output (Semantic Intent)**
<img width="782" height="172" alt="image" src="https://github.com/user-attachments/assets/24ccd392-c253-4024-9586-95733b4c449c" />

**Execution Logic (agent_executor.py Pseudo-Code)**
# Agent: Find and Fill
target_element = find_element_by_semantic_label("corp code", dom_snapshot)
target_element.fill("slqa")

# Agent: Find and Click
target_button = find_element_by_action_text("login button", dom_snapshot)
target_button.click()

**🤝 Contribution & Future Roadmap**
We welcome contributions to expand the framework's intelligence and scope.

Implement LLM Integration: Full GenAI API calls for element scoring and identification.

Self-Healing Logic: Code to capture errors, analyze the new DOM, and automatically suggest or apply a new locator.

Support for Assertions: Translate "Then" steps (e.g., "Then the user should see the dashboard") into intelligent verification calls.

