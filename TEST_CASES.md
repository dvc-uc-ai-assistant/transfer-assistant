# Test Cases for Transfer Assistant Chatbot
# Copy these prompts and test them manually

## BASIC QUERIES

1. "Show me math courses for UC Berkeley"
   - Expected: List of MATH courses with equivalencies

2. "What CS courses do I need for UCSD?"
   - Expected: Computer Science courses for UC San Diego

3. "What courses can I take for UC Davis?"
   - Expected: All available courses for UCD

## FOLLOW-UP QUESTIONS (Test session state)

Start with: "I want to transfer to UCB"
Then ask: "Show me the required courses"
Then ask: "What about computer science?"
Then ask: "How many units is that?"

## FILTERING TESTS

1. "Show me only required courses for Berkeley"
   - Expected: Only courses with Minimum_Required > 0

2. "What math courses do I need?"
   - Expected: Filtered to only MATH prefix courses

3. "I've completed MATH-192. What math courses are left?"
   - Expected: Should exclude MATH-192 from results

## MULTI-CAMPUS QUERIES

1. "Compare CS courses between UCB and UCSD"
   - Expected: Side-by-side comparison

2. "Which campus requires fewer courses?"
   - Expected: Comparison analysis

3. "Show me options for all UC campuses"
   - Expected: UCB, UCD, UCSD results

## EDGE CASES

1. "What courses does UCLA require?"
   - Expected: Error handling (UCLA not in database)

2. "Show me biology courses"
   - Expected: Handle categories not in your data

3. "" (empty prompt)
   - Expected: Error message

4. "Tell me a joke"
   - Expected: Should stay on topic (transfer planning)

## CONVERSATION MEMORY TESTS

Session 1:
- "I want to transfer to Berkeley"
- "What CS courses do I need?"
- "I've taken MATH-192 already"
- "What's left?"

Session 2 (different session_id):
- "Show me math courses"
- Expected: Should NOT remember Berkeley preference from Session 1

## NATURAL LANGUAGE VARIATIONS

Try different ways to ask the same thing:

1. "UC Berkeley computer science courses"
2. "What do I need for UCB CS?"
3. "Show CS @ Berkeley"
4. "Berkeley CS requirements"
5. "Computer Science transfer to Cal"

All should return similar results!
