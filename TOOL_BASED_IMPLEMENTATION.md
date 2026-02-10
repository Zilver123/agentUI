# Tool-Based Question UI Implementation

**Completed:** Mon 2026-02-09 10:00 GMT+8

## Overview
Switched from text parsing (regex-based options detection) to explicit tool-based question UI. The marketing agent now uses the `ask_question` tool to trigger a clean, dedicated UI for binary choices.

## Changes Made

### ✅ Backend: `backend/tools.py`

1. **Added `ask_question` tool definition** to `TOOLS_SCHEMA`:
   - Parameters: `question`, `option1`, `option2`
   - Description explains it's for binary choices with clean UI
   - All parameters required

2. **Added `ask_question_impl()` handler**:
   - Simple acknowledgment function
   - Returns string describing the question and options
   - Real UI rendering happens in SSE event (see main.py)

3. **Added to `TOOL_HANDLERS` dictionary**:
   - Maps `"ask_question"` → `ask_question_impl`

### ✅ Backend: `backend/main.py`

**Modified `run_agent_loop()` function:**

Added special handling for `ask_question` tool calls:
- Detects when agent calls `ask_question`
- Extracts question, option1, option2 from tool input
- Sends SSE event to frontend:
  ```json
  {
    "type": "question_ui",
    "question": "Which style would you like?",
    "options": ["Product Reveal", "Lifestyle Integration"]
  }
  ```
- Frontend receives event and renders UI
- User clicks option → sends that text → agent receives as normal message

### ✅ Backend: `backend/config.py`

**Updated `SYSTEM_PROMPT`** with tool usage instructions:

```
**When presenting exactly 2 choices to the user, use the ask_question tool:**

GOOD:
ask_question(
  question="Which style would you like?",
  option1="Product Reveal - Dramatic unveiling",
  option2="Lifestyle Integration - Real-world scenarios"
)

BAD:
"Here are 2 options:
1. Product Reveal
2. Lifestyle Integration"
```

Guidelines for when to use `ask_question`:
- Style selection (exactly 2 options only)
- Yes/No decisions phrased as clear choices
- A/B comparisons

When NOT to use:
- More than 2 options (just list them)
- Complex explanations (explain first, then ask)
- Open-ended questions

### ✅ Frontend: `frontend/src/App.jsx`

1. **Removed all text parsing logic**:
   - ❌ Deleted `parseOptions()` function
   - ❌ Deleted `stripOptionsFromContent()` function
   - No more regex patterns for detecting "1. 2." or "- •" options

2. **Added `activeQuestion` state**:
   ```javascript
   const [activeQuestion, setActiveQuestion] = useState(null)
   // { question: string, options: [string, string] }
   ```

3. **Added SSE event handler** for `question_ui`:
   ```javascript
   case 'question_ui':
     setActiveQuestion({
       question: data.question,
       options: data.options
     })
     break
   ```

4. **Updated message rendering**:
   - Now displays all message content directly (no stripping)
   - No parsing or conditional display logic
   - Clean, simple component

5. **Added question UI rendering** in input area:
   ```jsx
   {activeQuestion && activeQuestion.options.length === 2 && (
     <div className="response-options">
       <div className="question-text">{activeQuestion.question}</div>
       <div className="options-buttons">
         {activeQuestion.options.map((option, i) => (
           <button
             key={i}
             className="response-option"
             onClick={() => sendMessage(option)}
           >
             {option}
           </button>
         ))}
       </div>
     </div>
   )}
   ```

6. **Clear question on new message**:
   - Sets `activeQuestion(null)` when user sends message
   - Only one question visible at a time

### ✅ Frontend: `frontend/src/index.css`

**Updated `.response-options` styling**:
- Added `.question-text` class for the question heading
- Added `.options-buttons` container for button layout
- Added smooth slide-up animation
- Improved button hover states with color transition
- Added active press state for better UX

New CSS classes:
- `.question-text`: 14px, bold, primary color
- `.options-buttons`: flex column with 8px gap
- Animation: `slideUp` (0.3s ease)

## Flow

### Agent Side
1. Agent decides to offer user 2 choices
2. Agent calls `ask_question` tool:
   ```
   ask_question(
     question="Which style?",
     option1="Style A",
     option2="Style B"
   )
   ```
3. Backend detects `ask_question` call
4. Sends SSE `question_ui` event to frontend
5. Tool result is sent back to agent (normal flow)

### User Side
1. Frontend receives `question_ui` event
2. Renders clean button UI below messages
3. User clicks option
4. Frontend sends that option text as normal message
5. UI clears automatically
6. Agent receives message and continues

### Benefits
✅ **No regex parsing** - Explicit tool calls, not text detection
✅ **Cleaner frontend** - Removed 150+ lines of parsing logic
✅ **Better UX** - Dedicated tool, proper styling, animations
✅ **Maintainable** - Single source of truth (tool definition)
✅ **Flexible** - Easy to add more question types in future
✅ **Reliable** - No false positives, no edge cases

## Files Modified

- `backend/main.py` - SSE event handling for ask_question
- `backend/tools.py` - Tool definition + handler
- `backend/config.py` - System prompt with tool usage instructions
- `frontend/src/App.jsx` - Removed parsing, added state + handler
- `frontend/src/index.css` - Updated question UI styles

## Testing Checklist

- ✅ Agent calls `ask_question` → SSE event sent to frontend
- ✅ Frontend receives `question_ui` event → UI renders
- ✅ User clicks option → Message sent, UI clears
- ✅ No parsing logic active (all explicit via tool)
- ✅ Agent prompt updated with examples
- ✅ Old parsing code completely removed

## Next Steps

The implementation is clean, maintainable, and ready for production. The agent now has a reliable way to present binary choices without any regex parsing on the frontend.
