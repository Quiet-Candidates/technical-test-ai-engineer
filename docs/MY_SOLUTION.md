# My solution

Answer each question concretely, about the code you actually wrote. Naming a technology is not an
answer. Paste real numbers, real logs, real screenshots where they help.

Keep it short. We would rather read four honest paragraphs than four vague pages.

---

## 1. Scanning

How does the scan stay off the main thread, and what exactly does the user see while it runs?
What happens if they background the app or leave the screen halfway through?

## 2. Grouping

Describe your duplicate and near-duplicate detection: the signal you compare, the threshold, and why
that threshold.

Run it against `fixtures/out/` and give the numbers: how many groups you found, how many the fixtures
actually contain, and where you were wrong in each direction.

## 3. Memory

A library of several thousand photos — `fixtures/out/` at `--scale 10`. What is in memory at any
moment while the user swipes, and what stops it from growing? Give the rough figure you measured,
not the one you expect.

## 4. Deletion

Walk through the delete path. What does the OS give you, what does the user see, and what happens
when:

* the OS deletion prompt is refused,
* the user cancels halfway through a batch,
* the app is killed mid-delete.

## 5. State and the "space freed" number

Where does that number come from, and what is its source of truth?

Undo exists. Describe the state transitions for: swipe left → undo → swipe left again. Convince us
the number is still right.

## 6. Instrumentation

Name the events you would fire, with their properties, and say what question each one answers. Six is
plenty. We care about which six.

## 7. The ad break

The brief puts the ad break before the delete confirmation. If you kept it there, defend the
placement. If you moved it, defend the move. What would you expect it to do to completion rate,
and what would you watch to find out?

## 8. What you would A/B test first

One test. The hypothesis, the variant, and the metric that decides it.

## 9. Testing

What did you test, how, and what do you know is untested? Be honest about the gap — a clear-eyed
answer here beats a fake test suite.

## 10. Cuts

What did you drop, and why that instead of something else?
