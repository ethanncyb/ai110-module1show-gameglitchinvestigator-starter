# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the secret number kept changing" or "the hints were backwards").

### Answer:
- When I first loaded the game, the UI appeared normal and the secret number was hidden as expected. I played a round and noticed that the hints for "higher" and "lower" were incorrect: for example, when I guessed a number lower than the secret, the game said "Too high" instead of "Too low." I confirmed this by checking checking the Developer Debug Info and the hint logic.
![image_1](images/img01.jpg)

- Another issue happened after finishing a game. When I clicked the “New Game” button, the game didn’t actually reset. The attempts counter and guess history were still there, so the game didn’t really start fresh unless I refreshed the page manually. This happened every time I finished a round.
- I also noticed that the attempts counter was off by one. For example, if the game allowed 8 attempts, I could only actually make 7 guesses before the game ended.
![image_2](images/img02.jpg)

- Another issue was that when selecting a difficulty level, the secret number was sometimes not within the expected range.
![image_3](images/img03.jpg)

- With help from AI (mainly Copilot), I traced these problems to specific parts of the code:
  - **Bug 1**: The hint logic in the `check_guess` function (app.py:38–49) had the messages swapped. The conditions were correct, but the messages for “Too High” and “Too Low” were reversed.
  - **Bug2**: The attempts counter was initialized at 1 instead of 0 (app.py:96), causing the first guess to count as two attempts and resulting in an off-by-one error.
  - **Bug3**: The secret number was cast to a string on even attempts (app.py:158-161), which broke comparison logic and caused unpredictable behavior when comparing guesses to the secret.
  - **Bug 4**: The “New Game” button always reset the range to 1–100 (app.py:136), even if the player had selected a custom range or difficulty.
  - **Bug 5**: The “New Game” button didn’t fully reset the game state (app.py:134-138). It didn’t reset the score, status, or guess history. If player won/lost a game, the status stayed the same, so the game wouldn’t let player play a new round properly.

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

---

## 4. What did you learn about Streamlit and state?

- In your own words, explain why the secret number kept changing in the original app.
- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
- What change did you make that finally gave the game a stable secret number?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
