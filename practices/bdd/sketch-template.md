# BDD sketch — match active fidelity

Sketch the behavior outline first, then layer on test/implementation detail. Confirm the top-level subjects (the objects being described), then their states, events, and `it should` confirmations. Only once that scaffold reads cleanly, add call-surface and internals — and only as far as the active fidelity needs.

**Order:** subjects → `with` / `that` / events → `it should` leaves → public `->` / `expect` (`b`) → novel internals under calls (`d`, development only).

| Fidelity | Fill |
|---|---|
| **behavior** | Hierarchy plus public call surface (`new`, sets, calls, `expect`) — no internals |
| **development** | Behavior surface plus novel interactions under calls (domain-walk); omit paths already green |

**Notation:** plain indent / `->` at the public surface = behavior (`b`) · deeper `->` under a call = development interaction (`d`) · `//` = note. Interleave; code sits under the hierarchy line it realizes. No `beforeEach` / imports / AAA labels.

---

## Template

```
a {Subject}                                                      # b
  -> {subject} = new {Class}()                                   # b
  {with / that state elaboration}                                # b
    -> {subject}.{property} = {value}                            # b
      -> {collaborator}.{operation}({args})                      # d  novel only
        -> // {note or already covered}
  {with / that another state or narrative event}                 # b
    -> {result} = {subject}.{operation}({args})                  # b
      -> self.{collaborator}.{operation}({args})                 # d  novel only
    it should {observable result}                                # b
      -> expect({subject}.{observation}).to {matcher}            # b
```

---

## Example

Scaffold first (subjects → states/events → confirmations), then details:

```
a vehicle                                                        # b
  that is temperamental                                          # b
    it should refuse to start on the first attempt               # b
```

```
a vehicle                                                        # b
  -> vehicle = new Car()                                         # b
  that is temperamental                                          # b
    -> car.personality = CatPersonality.temperamental            # b
      -> self.attribute_factory.load_attributes(                 # d  novel
            personality=CatPersonality.temperamental)
    it should refuse to start on the first attempt               # b
      -> expect(car.start()).to be false                         # b
      -> expect(car.message).to equal "No way — I am tired!"     # b
```
