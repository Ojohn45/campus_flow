# AI Learning Log

This document records verified AI learning interactions for the CampusFlow sprint.
Each entry follows the template from Section 5.3 of the Fellows' Engineering Guide:
problem → initial understanding → prompt → AI guidance → experiment → verification
→ decision → related file → what I can now explain without AI.

Each fellow authored at least three entries. At least one entry per fellow
documents a corrected, improved, or rejected AI suggestion.

---

## Fellow: <Your Name> (Engineer B)

### Interaction #1 — Sorting by a tuple key in Python

**Problem:**
I needed to sort open tickets by priority (critical → high → medium → low) and
break ties by the earlier *numeric* ticket ID. My first instinct was to call
`sorted()` twice or write a manual comparison loop. I did not know how to sort
by two criteria at once.

**My initial understanding:**
I knew `sorted(list)` sorts strings alphabetically. I assumed I could just sort
by the priority string and get the right order.

**Prompt to AI:**
"Explain how to sort a list of dictionaries in Python by one key, and then by a
second key when the first is tied. Give a five-line example unrelated to my
project. Do not write my project code."

**Useful AI guidance:**
AI explained that `sorted()` accepts a `key` function, and that returning a
**tuple** `(first_key, second_key)` makes Python compare the first element, then
the second on ties. It gave an example sorting a list of `(name, age)` tuples.

**My independent experiment/test:**
I wrote a 6-line script in a scratch file:
```python
data = [{"id": "T010", "p": "high"}, {"id": "T002", "p": "high"}, {"id": "T001", "p": "critical"}]
print(sorted(data, key=lambda d: d["id"]))          # string sort
print(sorted(data, key=lambda d: int(d["id"][1:]))) # numeric sort