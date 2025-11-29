# Integration Test Plan

## Overview
This document outlines the integration testing plan for the course database chatbot system. The goal is to validate that all system components work together correctly.

---

## 🎯 Test Plan Goals

This test plan confirms:
- ✅ Front-end and backend communication is working
- ✅ Database queries return accurate results
- ✅ LLM formatting and understanding are correct
- ✅ Logging captures user input + system responses
- ✅ Error handling is consistent
- ✅ Cross-team compatibility is validated

---

## 1. Test Environment Description

### 1.1 Tools and Technologies
- **Frontend Hosting**: **Deployed on Google Cloud Run at https://nexa-transfer-997600970262.us-west2.run.app/** 
- **Backend Framework**: Flask (Python)
- **Database**: **JSON files with course data**
- **Version Control**: Git/GitHub
- **Testing Location**: **Flask local server on port 5000 and then deployed on Google Cloud Run** (Local development vs. staging vs. production)

### 1.2 Backend & Database Setup
- **Data Source**: 
  - DVC -> UC course transfer data located in `agreements_25-26`
  - UC transfer agreements in `OpenAI_Chatbot_Integration/agreements_25-26/`
- **Backend Server**: 
  - Main application: `app.py`
  - **Run this command: python app.py** (Document backend startup procedure)

### 1.3 Required API Keys & Environment Variables
**OpenAI API key** (Document all required environment variables):
- [ ] OpenAI API Key (`OPENAI_API_KEY`)
- [ ] Environment configuration (development/production)

---

## 2. Test Scenarios & Expected Results


### Test Case 2.1: Specific UC School Transfer Requirements Query
**Objective**: Verify system returns correct DVC required courses for a specific UC school

**Steps**:
1. Open chatbot interface
2. Enter prompt: "What are the UCSD transfer requirements?"
3. Submit query

**Expected Result**:
- System queries course database for UCSD
- Returns all DVC courses required to transfer to UCSD
- Output is clear, and readable
- All information matches source data

**Actual Result**: Transfer prep for UC San Diego:

* COMSC-171/255 — Introduction to UNIX and Linux/Programming with Java — 4 units
* COMSC-200 — Object Oriented Programming C++ — 4 units
* COMSC-210/200 — Program Design and Data Structures/Object Oriented Programming C++ — 8 units
* MATH-195 — Discrete Mathematics — 4 units
* COMSC-230 — Discrete Mathematical Structures for Computer Science — 3 units
* COMSC-260 — Assembly Language Programming/Computer Organization — 4 units
* MATH-194 — Linear Algebra — 3 units
* MATH-192 — Analytic Geometry and Calculus I — 5 units
* MATH-193 — Analytic Geometry and Calculus II — 5 units
* MATH-292 — Analytic Geometry and Calculus III — 5 units
* BIOSC-130/131 — Principles of Cellular and Molecular Biology/Principles of Organismal Biology, Evolution, and Ecology — 10 units
* CHEM-120 — General College Chemistry I — 5 units
* CHEM-120/121 — General College Chemistry I/II — 10 units
* PHYS-130 — Physics for Engineers and Scientists A: Mechanics and Wave Motion — 4 units
* PHYS-230 — Physics for Engineers and Scientists B — 4 units

**Status**: ✅Pass

**Next Step**: Further improve output formatting

---

### Test Case 2.2: Course Category Query
**Objective**: Verify system provides accurate information based on the course category

**Steps**:
1. Open chatbot interface
2. Enter prompt: "What Science courses are required at UC Davis?"
3. Submit query

**Expected Result**:
- System retrieves only the courses that fall under "Science"
- Response clearly lists all courses
- Information matches database with transfer requirements to UCD

**Actual Result**: Transfer prep for UC Davis:
* MATH-195 — Discrete Mathematics — 4 units
* COMSC-110 — Introduction to Programming — 4 units
* COMSC-165 — Advanced Programming with C and C++ — 4 units
* COMSC-255 — Programming with Java — 4 units
* ENGIN-135 — Programming for Scientists and Engineers — 4 units
* COMSC-200 — Object Oriented Programming C++ — 4 units
* COMSC-210 — Program Design and Data Structures — 4 units
* COMSC-260 — Assembly Language Programming/Computer Organization — 4 units
* BIOSC-130 — Principles of Cellular and Molecular Biology — 5 units
* BIOSC-131 — Principles of Organismal Biology, Evolution, and Ecology — 5 units
* CHEM-120/121 — General College Chemistry I/II (sequence only) — sequence units
* PHYS-130 — Physics for Engineers and Scientists A: Mechanics and Wave Motion — 4 units
* PHYS-230/231 — Physics for Engineers and Scientists B & C — sequence units
* PHYS-230 — Physics for Engineers and Scientists B — 4 units

**Status**: Pass? (For Now), Need to be more clear on what counts as Science courses vs Computer Science courses

---

### Test Case 2.3: Invalid/Ambiguous Query
**Objective**: Test error handling for unclear user input

**Steps**:
1. Open chatbot interface
2. Enter prompt: "jiji"
3. Submit query

**Expected Result**:
- System handles gracefully without crashing
- Returns helpful error message or asks for clarification
- User is guided to ask a valid question

**Actual Result**: Sorry, I couldn't detect a campus. Try UC Berkeley (UCB), UC Davis (UCD), or UC San Diego (UCSD).

**Status**: ✅Pass

---

### Test Case 2.4: Multiple Course Query
**Objective**: Verify system can handle multiple course requirements in one query

**Steps**:
1. Open chatbot interface
2. Enter prompt: "Show me the required courses for UCSD and UCB."
3. Submit query

**Expected Result**:
- System searches database for both UCSD and UCB course requirements
- Accurately lists out the courses that are required based on database
- Clear output

**Actual Result**: 
Transfer prep for UC Berkeley:
* MATH-192 — Analytic Geometry and Calculus I — 5 units
* MATH-194/294 — Linear Algebra/Differential Equations — 8 units
* COMPSC-140 — Python Programming — 3 units
* COMPSC-240/MATH 192 — Advanced Python Programming/Analytic Geometry and Calculus 1 — 8 units
* COMSC-210 — Program Design and Data Structures — 4 units
* COMSC-260 — Assembly Language Programming/Computer Organization — 4 units

Transfer prep for UC San Diego:
* COMSC-171/255 — Introduction to UNIX and Linux/Programming with Java — 4 units
* COMSC-200 — Object Oriented Programming C++ — 4 units
* COMSC-210/200 — Program Design and Data Structures/Object Oriented Programming C++ — 8 units
* MATH-195 — Discrete Mathematics — 4 units
* COMSC-230 — Discrete Mathematical Structures for Computer Science — 3 units
* COMSC-260 — Assembly Language Programming/Computer Organization — 4 units
* MATH-194 — Linear Algebra — 3 units
* MATH-192 — Analytic Geometry and Calculus I — 5 units
* MATH-193 — Analytic Geometry and Calculus II — 5 units
* MATH-292 — Analytic Geometry and Calculus III — 5 units
* BIOSC-130/131 — Principles of Cellular and Molecular Biology/Principles of Organismal Biology, Evolution, and Ecology — 10 units
* CHEM-120 — General College Chemistry I — 5 units
* CHEM-120/121 — General College Chemistry I/II — 10 units
* PHYS-130 — Physics for Engineers and Scientists A: Mechanics and Wave Motion — 4 units
* PHYS-230 — Physics for Engineers and Scientists B — 4 units

**Status**: ✅Pass

---

## 3. UI/UX Tests

### Test Case 3.1: Chat Bubble Display
**Objective**: Verify messages display correctly

**Steps**:
1. Open chatbot interface
2. Send a test message
3. Observe response display

**Expected Result**:
- User messages appear in distinct bubbles (typically right-aligned)
- Bot responses appear in distinct bubbles (typically left-aligned)
- Bubbles are readable and properly styled
- Text is not cut off or overlapping

**Actual Result**: **Response from the chatbot is clearly shown and displayed to the user**

**Status**: ✅Pass

---

### Test Case 3.2: Error Message Display
**Objective**: Verify error messages are user-friendly

**Steps**:
1. Trigger an error (disconnect internet, invalid input, etc.)
2. Observe error message

**Expected Result**:
- Error message is displayed clearly
- Message is user-friendly (not technical stack traces)
- User understands what went wrong
- Guidance provided on how to proceed

**Actual Result**: ⚠️ I couldn’t reach the server. Check the base URL in .env and try again.

**Status**: ✅Pass

---

### Test Case 3.3: Mobile Responsiveness
**Objective**: Verify page is usable on mobile devices

**Steps**:
1. Open chatbot on mobile device or use browser dev tools to simulate mobile
2. Test core functionality: sending messages, scrolling, reading responses
3. Check layout and button sizes

**Expected Result**:
- Page layout adapts to mobile screen size
- All text is readable without zooming
- Input field and send button are accessible
- Chat history scrolls smoothly

**Actual Result**: **Page is not user friendly on mobile devices**

**Status**: ❌Fail, need to improve mobile interface

---

### Test Case 3.4: Loading States
**Objective**: Verify loading indicators work correctly

**Steps**:
1. Submit a query
2. Observe UI while waiting for response

**Expected Result**:
- Loading indicator appears immediately after submission
- User knows the system is processing
- Send button is disabled to prevent duplicate submissions
- Loading indicator disappears when response arrives

**Actual Result**: **Shows that the chatbot is thinking or coming up with a response and the send button is disabled while the bot is thinking**

**Status**: ✅Pass

---

### Test Case 4.2: Course List Formatting
**Objective**: Verify course information is presented clearly

**Steps**:
1. Ask for a list of courses (e.g., "What UCB courses are required?")
2. Examine how courses are displayed

**Expected Result**:
- Courses displayed in organized format (bullet points)
- Each course includes: course code, title, and units
- Format is easy to scan and read

**Actual Result**: **Format is easy to read and can see all the transferable courses for the desired school**

**Status**: ✅Pass

---

## 5. Logging Requirements

### Test Case 5.1: Timestamp Logging
**Objective**: Verify all interactions are timestamped and have their unique query number

**Steps**:
1. Send a test message
2. Check log file/database for timestamp

**Expected Result**:
- Each user query has an associated timestamp and query number
- Each bot response has an associated timestamp and query number
- Timestamps are accurate to the actual interaction time

**Verification**: **All interactions are saved in the logs folder**

**Status**: ✅Pass

---

### Test Case 5.2: User Prompt Logging
**Objective**: Verify original user prompts are saved with chatbot response data

**Steps**:
1. Send test message: "What courses transfer to UCB?"
2. Check log file

**Expected Result**:
- Exact user prompt is saved verbatim
- No truncation or modification
- Associated with correct session/user ID
- The user's prompt is logged along with the chatbot's response

**Verification**: **Original prompts are also saved in `logs/nexa_log_2025`**

**Status**: ✅Pass


---

### Test Case 5.4: Log Data Structure
**Objective**: Verify logs are properly structured for analysis

**Steps**:
1. Review log file structure
2. Attempt to parse/analyze logs

**Expected Result**:
- Logs are in structured JSON format
- Easy to query and analyze
- Contains all required fields: timestamp, session_id, user_prompt, campuses, response_preview

**Verification**: **Logs are in structured JSON format** 

**Status**: ✅Pass

---

## 7. Bug Report Template

### Bug Report 

**Summary**: Web application is very hard to use on mobile. The navigation bar format is completely messed up, and theres only a tiny space reserved for the actual chatbot window.

**Severity**: Critical

**Steps to Fix**:
1. Add a restructured webpage format that is much smaller, for mobile screens
2. Make the navigation collapsible
3. Ensure the chatbot window takes up the maximum space on a mobile screen

---