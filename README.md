# AI Engineer — technical test

## Who we are

Quiet is a French app studio based in Paris. We build consumer mobile utilities — phone and photo
cleaners, an app locker, an email cleaner. We monetise through ads and subscriptions, we ship on
Android and iOS, and we do it as a very small team, on short cycles. Nobody hands you a spec, a
design, or a backend.

## The role you are applying for

**AI Engineer.** You ship apps end to end — front, back, AI, design. You do not wait on a designer
and you do not wait on a backend team. You own a project and you take it to the store. You use AI as
part of how you work, and you put AI in the product when it earns its place.

This test is a small version of that job.

---

## The test

**You have 24 hours** from the moment we send you this repo. Spend the time however you want.

Please **do not** push your work to a public repository. Set up private sharing **before** you start:
[docs/HOW_TO_SHARE_MY_CODE.md](./docs/HOW_TO_SHARE_MY_CODE.md)

### What to build

**PhotoCleaner** — an app that frees space in the user's photo library.

Android (Kotlin + Compose) **or** iOS (Swift + SwiftUI). Your choice. Native only — no React Native,
no Flutter.

**Scope:**

* Ask for photo library access. Explain why. Handle a refusal without a dead end.
* Scan the library and sort it into **duplicates and near-duplicates** (mandatory) plus at least one
  of: screenshots, blurry photos, large videos.
* A swipe deck — left deletes, right keeps — with undo.
* A review screen, a bulk delete, and a "you freed X GB" result.
* It must not freeze or run out of memory on a library of several thousand items.
* One ad break before the delete confirmation. Fake it with a placeholder screen and a timer. Our apps
  run on ads. We want to see that you understand that, not that you can integrate AppLovin.

**Out of scope:** a real ad SDK, a backend, accounts, cloud sync, a store release.

### Test data

`fixtures/` generates a photo library with known duplicates, near-duplicates, blurry shots and
screenshots, and pushes it to a device or a simulator. Everyone is graded on the same data.

```bash
python3 fixtures/generate.py          # writes fixtures/out/
./fixtures/push-to-device.sh android  # or: ios
```

Read [fixtures/README.md](./fixtures/README.md) for what it generates and what the expected counts are.

---

## What we look for

1. The app runs.
2. No crash, no bug.
3. The UX/UI is coherent.
4. How you tested it.
5. CI/CD.

You don't have to do all of it. This is just what we look at, in this order.

---

## What to write

* [docs/MY_SOLUTION.md](./docs/MY_SOLUTION.md) — specific questions about what you built. Answer them
  concretely. Naming a technology is not an answer.
* [docs/AI_LOG.md](./docs/AI_LOG.md) — how you worked with AI. We read this one first.

---

## Notes

* If something is unclear, make a call, and write down the call you made.
* Do not squash your history into one commit. We want to see how you got there.
* **Build this with AI.** That is how we work, and it is the part we are reading most closely — not
  whether you used it, but how you drove it. Document that in `docs/AI_LOG.md`.
* You still own the result. In the live debrief we go through it with you and ask you to change things
  on the spot.
