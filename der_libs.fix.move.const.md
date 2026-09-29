Correction to what I said about the move operations: I was wrong that const CFontList&& isn't a real move constructor. The standard defines a move constructor as one whose first parameter is X&&, const X&&, volatile X&&, or const volatile X&&, and the same goes for move assignment. So your duplicated signatures are legal and count as move operations. The plain X&& form is the conventional one, and it's what I'd use going forward.

For your walk-back through der_libs, that changes the urgency:

Where they're = deleted: functionally harmless. A deleted const X&& overload still gets picked for rvalues, so an attempted move fails to compile, which is the intent. You can fix these opportunistically or not at all.
Where they're actually defined (with a body): these are worth finding. A const X&& parameter can't be modified, so you can't steal the source's resources. The "move" would end up as a copy in disguise or simply fail to do its job.

A quick grep for const [A-Za-z_]*\s*&& across der_libs would list every occurrence, and you could then look only at the ones with bodies.

***
Your instincts were sound, so this is less GIGO than it feels. Private copy operations were the pre-C++11 idiom for "don't copy this class", and = delete is its modern replacement. You were right that the default copy would be a shallow one: it copies pointer values, so two objects end up owning the same allocation and you get a double free. And clang-tidy's advice was legitimate, it just never explained itself. What you were missing was the reasoning, not the judgment.

That "if you have copy operations, you need move operations" alert is the Rule of Five check, cppcoreguidelines-special-member-functions. It's a generic guideline, and for a class like yours the deleted moves are redundant. Declaring the copy operations (even as deleted) already suppresses the implicit move operations, and a would-be move on a CFontList would fall back to the deleted copy and fail to compile. So the moves add nothing except silencing the warning.

That check has an option, AllowMissingMoveFunctionsWhenCopyIsDeleted, that tells it to accept deleted copy operations without explicit moves. I'm fairly sure it exists in reasonably recent clang-tidy releases, but confirm it against your version's documentation. In .clang-tidy it looks like:

```yaml
CheckOptions:
  - key: cppcoreguidelines-special-member-functions.AllowMissingMoveFunctionsWhenCopyIsDeleted
    value: true
```

If it works for you, the walk-back gets much simpler. Instead of fixing const X&& across der_libs, you can delete the move declarations from the classes where copy is already deleted and let the option keep clang-tidy quiet. Each class shrinks to explicit constructor, destructor, and the two deleted copy operations.

Then the "oh damn" pile mostly shrinks to two questions per class: does it hold raw pointers or other owned resources (so copy really must be deleted), and does it have a single-argument constructor that needs explicit.