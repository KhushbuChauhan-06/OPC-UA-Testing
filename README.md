# OPC UA Client Testing & Automation Framework

<p align="center">

**A Python-based industrial communication testing and automation framework for repeatable OPC UA client-server validation.**

</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-Test%20Automation-0A9EDC?style=for-the-badge)
![OPC UA](https://img.shields.io/badge/Protocol-OPC%20UA-FF8C00?style=for-the-badge)
![asyncua](https://img.shields.io/badge/asyncua-2.x-green?style=for-the-badge)
![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)

</p>

---

# 📌 Overview

This project is a **repeatable OPC UA client testing and automation framework** built with **Python, asyncua, and Pytest**.

It provides a controlled local OPC UA environment where client-server communication can be tested automatically across functional, subscription, negative, and security scenarios.

The framework validates:

- 🔌 OPC UA connection and session handling
- 🔎 Address-space browsing
- 📖 Data read operations
- ✏️ Data write operations
- ⚙️ OPC UA method calls
- 📡 Subscriptions and monitored items
- 🔐 Username/password authentication
- 📜 X.509 certificate trust
- 🛡️ OPC UA SecureChannel security
- ❌ Negative and failure scenarios
- 📊 Automated test reporting
- 📈 Code coverage
- 🚀 Continuous Integration using GitHub Actions

The main objective is to demonstrate how industrial communication interfaces can be tested **systematically, repeatedly, and automatically** instead of relying only on manual verification.

> **Project Scope:** This is an independent portfolio and learning project using a simulated industrial plant. It is **not an ABB production system, ABB hardware integration, or a representation of ABB's internal software architecture.**

---

# 🎯 Objective & Problem Statement

Industrial automation systems depend on reliable communication between controllers, devices, applications, and supervisory systems.

Manual communication testing can become:

- Time-consuming
- Difficult to reproduce
- Inconsistent between test runs
- Difficult to scale
- Difficult to validate for failure conditions
- Difficult to maintain as test coverage increases

This framework addresses these challenges by providing a **deterministic and isolated OPC UA test environment**.

### Testing Philosophy

```text
┌──────────────────────────┐
│  Controlled Environment  │
└────────────┬─────────────┘
             ↓
┌──────────────────────────┐
│ OPC UA Client Connection │
└────────────┬─────────────┘
             ↓
┌──────────────────────────┐
│ Communication & Control  │
└────────────┬─────────────┘
             ↓
┌──────────────────────────┐
│ Functional Validation   │
└────────────┬─────────────┘
             ↓
┌──────────────────────────┐
│ Negative & Security Test │
└────────────┬─────────────┘
             ↓
┌──────────────────────────┐
│ Reports & Code Coverage  │
└────────────┬─────────────┘
             ↓
┌──────────────────────────┐
│     CI/CD Validation     │
└──────────────────────────┘
🏗️ System Architecture

The framework follows a layered architecture where Pytest drives the test scenarios, fixtures create an isolated environment, the client wrapper handles OPC UA operations, and the simulated industrial server provides the test target.

                         ┌─────────────────────────┐
                         │       PYTEST SUITE      │
                         │                         │
                         │ Functional / Security   │
                         │ Subscription / Negative │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │     TEST FIXTURES       │
                         │                         │
                         │ Server lifecycle        │
                         │ Client lifecycle        │
                         │ Test isolation          │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │    OPCUATestClient      │
                         │                         │
                         │ Connection              │
                         │ Browse                  │
                         │ Read / Write             │
                         │ Methods                 │
                         │ Subscriptions           │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │   OPC UA SECURECHANNEL  │
                         │                         │
                         │ Basic256Sha256          │
                         │ Sign                    │
                         │ SignAndEncrypt          │
                         │ Authentication          │
                         │ Certificate Trust       │
                         └────────────┬────────────┘
                                      │
                                      ▼
              ┌────────────────────────────────────────────┐
              │       SIMULATED INDUSTRIAL OPC UA SERVER   │
              │                                            │
              │              IndustrialPlant               │
              │                                            │
              │  ┌──────────────┐    ┌──────────────────┐  │
              │  │   Sensors    │    │      Motor       │  │
              │  │              │    │                  │  │
              │  │ Temperature  │    │ Speed            │  │
              │  │ Pressure     │    │ Current          │  │
              │  │ Vibration    │    │ Status           │  │
              │  └──────────────┘    └──────────────────┘  │
              │                                            │
              │  Methods: StartMotor() / StopMotor()       │
              └────────────────────────────────────────────┘


                         ┌─────────────────────────┐
                         │      TEST EVIDENCE      │
                         │                         │
                         │ HTML Reports            │
                         │ Coverage                │
                         │ Logs                    │
                         │ CI Artifacts            │
                         └─────────────────────────┘
🔗 OPC UA Test Target

The project uses a localhost-only simulated OPC UA server.

Endpoint
opc.tcp://127.0.0.1:4840/abb-test-server/

The server exposes a simplified IndustrialPlant containing representative process and motor data.

🌡️ Sensor Variables
Temperature
Pressure
Vibration
⚙️ Motor Variables
Speed
Current
Status
🕹️ Control Methods
StartMotor()
StopMotor()

This provides a realistic test target for both monitoring and control-oriented OPC UA operations.

🧪 Test Coverage

The framework separates tests according to the behavior being validated.

tests/
│
├── functional/
│   ├── connection
│   ├── browse
│   ├── read_write
│   └── methods
│
├── subscription/
│   └── monitored_items
│
├── security/
│   ├── authentication
│   ├── certificate_trust
│   └── secure_modes
│
└── negative/
    └── failure_scenarios
🔌 Functional Testing

Functional tests validate the core OPC UA communication workflow.

Covered Operations
Establishing OPC UA client connections
Creating sessions
Browsing the address space
Discovering nodes
Reading node values
Writing supported values
Calling OPC UA methods
Validating returned values
Validating operation results and failures

Example workflow:

Client
  │
  ├── Connect
  │
  ├── Browse
  │
  ├── Read Temperature
  │
  ├── Write Value
  │
  ├── Call StartMotor()
  │
  └── Validate Result
📡 Subscription & Monitored Item Testing

The framework validates OPC UA subscriptions and monitored items.

Instead of continuously polling values, the client can subscribe to changes generated by the server.

OPC UA Server
      │
      │ Value Change
      ▼
Monitored Item
      │
      ▼
Subscription
      │
      ▼
OPC UA Client
      │
      ▼
Test Assertion

This validates event-driven communication behavior commonly used in industrial monitoring systems.

❌ Negative Testing

A reliable automation framework should validate not only the happy path, but also expected failure behavior.

Negative tests cover scenarios such as:

Invalid credentials
Unknown users
Untrusted certificates
Invalid security configuration
Communication failures
Unexpected server responses
Rejected authentication attempts

The objective is to verify that failures are detected and handled predictably.

🔐 OPC UA Security Testing

Security testing uses OPC UA's native SecureChannel mechanisms.

Security Policy
Basic256Sha256
Security Modes
Sign
SignAndEncrypt
Sign

Provides message integrity and authentication at the OPC UA SecureChannel level.

SignAndEncrypt

Provides message integrity and authentication while also protecting the confidentiality of SecureChannel messages through encryption.

Security Scenarios

The framework validates:

┌──────────────────────────────┐
│ Username / Password Auth     │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ Valid Credentials            │
└──────────────────────────────┘

┌──────────────────────────────┐
│ Invalid / Unknown Credentials│
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ Authentication Rejected      │
└──────────────────────────────┘

┌──────────────────────────────┐
│ Client X.509 Certificate     │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ Trust Validation             │
└──────────────┬───────────────┘
               ↓
       ┌───────┴────────┐
       ↓                ↓
   Trusted           Untrusted
       ↓                ↓
   Accepted          Rejected

The project also validates:

Username/password authentication
Invalid credentials
Unknown users
Client certificate trust
Untrusted client certificates
Expected server certificate validation
Secure communication configuration

Important: OPC UA SecureChannel security is different from TLS transport security.

Development certificates are generated dynamically for testing.

Private keys, credentials, and secrets are not committed to the repository.

📁 Project Structure
OPC-UA-Testing/
│
├── src/
│   └── opcua_framework/
│       │
│       ├── client/
│       │   └── OPCUATestClient
│       │
│       ├── server/
│       │   └── OPCUATestServer
│       │
│       ├── config/
│       │
│       └── utils/
│           └── certificate tooling
│
├── tests/
│   ├── functional/
│   ├── subscription/
│   ├── security/
│   └── negative/
│
├── config/
│   └── framework.yaml
│
├── reports/
│
├── logs/
│
├── pyproject.toml
│
├── .gitignore
│
└── README.md

The framework separates:

Client Logic
     +
Server Simulation
     +
Configuration
     +
Certificate Utilities
     +
Test Suites
     +
Reporting

This separation makes the framework easier to maintain and extend.

🛠️ Technology Stack
Technology	Purpose
Python 3.11+	Framework implementation
asyncua 2.x	OPC UA client/server communication
Pytest	Test automation
pytest-asyncio	Async test execution
pytest-html	HTML test reports
pytest-cov	Code coverage
PyYAML	Configuration and reusable test data
GitHub Actions	Continuous Integration
X.509 Certificates	OPC UA application trust and security
🚀 Installation
1. Clone the Repository
git clone https://github.com/KhushbuChauhan-06/OPC-UA-Testing.git
cd OPC-UA-Testing
2. Create Virtual Environment
py -3.11 -m venv .venv
3. Activate Virtual Environment
.\.venv\Scripts\Activate.ps1
4. Upgrade pip
python -m pip install --upgrade pip
5. Install the Project
pip install -e .
▶️ Running the Test Suite

The test fixtures automatically start and manage the simulated OPC UA server during integration tests.

Run All Tests
pytest
Run Smoke Tests
pytest -m smoke
Run Functional Tests
pytest -m functional
Run Subscription Tests
pytest -m subscription
Run Security Tests
pytest -m security
Run Negative Tests
pytest -m negative
🖥️ Running the OPC UA Server Manually

The simulated server can also be started independently for manual experimentation.

py -3.11 -m opcua_framework.server

Default endpoint:

opc.tcp://127.0.0.1:4840/abb-test-server/

To use another local port:

$env:OPCUA_ENDPOINT="opc.tcp://127.0.0.1:4841/abb-test-server/"

Then run:

pytest
📊 Test Reports & Code Coverage
Generate HTML Test Report
pytest --html=reports/report.html --self-contained-html
Generate Code Coverage
pytest --cov=src --cov-report=html:reports/coverage

Generated artifacts:

reports/
│
├── report.html
│
└── coverage/
    └── index.html

logs/
└── test-run.log

Reports provide visibility into:

Test names
Pass/fail status
Execution duration
Captured output
Failure details
Code coverage
⚙️ Configuration

Reusable non-secret configuration is stored in:

config/framework.yaml

Configuration includes:

OPC UA endpoint
Connection timeouts
Publishing interval
Sensor ranges
Reusable test data
Security-related test configuration

The endpoint can be overridden using:

$env:OPCUA_ENDPOINT="opc.tcp://127.0.0.1:4841/abb-test-server/"
Security Rule

Credentials and private-key paths must never be committed to Git.

📜 Development Certificates

Development certificates can be generated for local security experiments.

py -3.11 -m opcua_framework.utils.generate_certificates

These certificates are intended for development and testing only.

The project does not attempt to reproduce a production PKI/CA infrastructure.

🔄 CI/CD with GitHub Actions

The project uses GitHub Actions to automatically execute the test suite on:

Pushes
Pull Requests
CI Pipeline
┌───────────────────────┐
│   Code Push / PR      │
└───────────┬───────────┘
            ↓
┌───────────────────────┐
│ Setup Python 3.11     │
└───────────┬───────────┘
            ↓
┌───────────────────────┐
│ Install Dependencies  │
└───────────┬───────────┘
            ↓
┌───────────────────────┐
│ Run Complete Test     │
│ Suite                 │
└───────────┬───────────┘
            ↓
┌───────────────────────┐
│ Generate Reports      │
│ & Coverage            │
└───────────┬───────────┘
            ↓
┌───────────────────────┐
│ Publish Test          │
│ Artifacts             │
└───────────────────────┘

The CI environment does not require a persistent OPC UA server.

Test fixtures automatically create and manage the simulated server, allowing the same integration tests to execute consistently in local development and CI.

Only appropriate test logs and reports are published as CI artifacts.

Private keys, credentials, and secrets are excluded from source control and CI artifacts.

🧩 Test Isolation & Fixture Design

The framework uses function-scoped fixtures to create controlled test environments.

Conceptually:

Test Starts
     │
     ▼
Start OPC UA Server
     │
     ▼
Create Client
     │
     ▼
Execute Test
     │
     ▼
Validate Result
     │
     ▼
Disconnect Client
     │
     ▼
Stop Server
     │
     ▼
Clean Test Environment

This approach reduces test-order dependencies and makes individual integration tests easier to reproduce.

🧠 Engineering Principles
🔁 Repeatability

The same test scenario should produce consistent results against the same deterministic environment.

🧪 Isolation

Each integration test starts from a controlled client/server state to minimize dependencies between test cases.

🧱 Abstraction

Low-level OPC UA operations are encapsulated inside OPCUATestClient, allowing test cases to focus on expected system behavior.

❌ Failure Awareness

The framework validates both successful operations and expected failure conditions.

🔐 Security Validation

Authentication, certificates, trust relationships, and SecureChannel modes are treated as testable system behavior.

🤖 Automation

The same test suite can run locally and inside CI without requiring manual server setup.

🎯 Engineering Skills Demonstrated

This project demonstrates practical skills relevant to industrial software, communication testing, QA automation, and embedded/automation-oriented development.

Industrial Communication
OPC UA client-server architecture
OPC UA address-space browsing
Node interaction
Data read/write
OPC UA methods
Subscriptions
Monitored items
Test Automation
Pytest architecture
Fixtures
Test isolation
Functional testing
Negative testing
Regression testing
Async test execution
Automated reporting
Code coverage
Security Testing
OPC UA SecureChannel
Basic256Sha256
Sign mode
SignAndEncrypt mode
Username authentication
X.509 certificates
Certificate trust validation
Security negative testing
Software Engineering
Python
Asynchronous programming
Modular architecture
Configuration-driven testing
Reusable abstractions
CI/CD
Automated test evidence
🔍 What This Project Demonstrates

The overall engineering workflow can be summarized as:

        INDUSTRIAL COMMUNICATION
                  │
                  ▼
           Simulated Plant
                  │
                  ▼
            OPC UA Server
                  │
                  ▼
             OPC UA Client
                  │
          ┌───────┼────────┐
          ▼       ▼        ▼
       Read/Write Methods Subscriptions
          │       │        │
          └───────┼────────┘
                  ▼
           Automated Tests
                  │
        ┌─────────┼──────────┐
        ▼         ▼          ▼
   Functional  Negative   Security
        │         │          │
        └─────────┼──────────┘
                  ▼
             Test Evidence
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
      Logs     Reports   Coverage
                  │
                  ▼
             GitHub Actions
🚧 Limitations & Scope

This project intentionally focuses on automated OPC UA communication testing using a deterministic local simulation.

It does not implement:

Real ABB hardware integration
Real PLC/controller communication
Production ABB systems
Production PKI/CA infrastructure
Certificate revocation infrastructure
TLS transport
Production deployment architecture
Safety-critical control logic

The simulated OPC UA server is localhost-only and is intended for automated QA, experimentation, and learning.

🔮 Future Improvements

Potential extensions include:

Parameterized test matrices for different OPC UA configurations
Fault-injection testing
Connection interruption and recovery testing
Subscription reconnect scenarios
Performance and latency measurements
Larger simulated industrial processes
Expanded security negative testing
Test-result dashboards
Containerized OPC UA test environments
Parallelized test execution
Additional protocol compliance scenarios
🏁 Key Takeaway

This project demonstrates a practical approach to testing industrial communication software:

┌───────────────┐
│    SIMULATE   │
└───────┬───────┘
        ↓
┌───────────────┐
│    CONNECT    │
└───────┬───────┘
        ↓
┌───────────────┐
│ BROWSE & READ │
└───────┬───────┘
        ↓
┌───────────────┐
│ WRITE & CONTROL│
└───────┬───────┘
        ↓
┌───────────────┐
│   MONITOR     │
└───────┬───────┘
        ↓
┌───────────────┐
│ TEST FAILURES │
└───────┬───────┘
        ↓
┌───────────────┐
│ TEST SECURITY │
└───────┬───────┘
        ↓
┌───────────────┐
│    REPORT     │
└───────┬───────┘
        ↓
┌───────────────┐
│   CI/CD       │
└───────────────┘
Core Focus

Repeatability · Test Isolation · Communication Reliability · Security Validation · Maintainable Automation

⚠️ Disclaimer

This is an independent portfolio project created for learning and demonstrating OPC UA testing, industrial communication, and automation concepts.

 

The simulated server and industrial plant are designed solely to provide a controlled environment for automated OPC UA testing.


 
