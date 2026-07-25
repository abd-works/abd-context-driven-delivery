# checks — BDD sketch (development fidelity)

## Scope (agreed)
check_spec.py only — a Check. OpposedCheck / TeamCheck deferred.

## Agreed
- Optional dice on Check; default 1d20; stub/mock in tests.
- Critical near-miss: stub die=20; rank=0, DC=21 → total 20 fails; crit +1° → succeeded.
- Fixtures: tiny fakes (`SimpleNamespace`) with `.rank` / `.target` / `.amount` — not `measurement.Rank` yet.
- Prefer stubbed dice in every context so expects are deterministic.

a Check
  that is resolved with no modifiers
    -> trait = SimpleNamespace(rank=5)
    -> dc = SimpleNamespace(target=10)
    -> stub_dice = SimpleNamespace(roll=lambda: 8)
    -> check = Check(trait, dc, dice=stub_dice)
    -> result = check.resolve([])
    -> // total = 8+5 = 13; DC 10 → succeed 1° (3 over, fraction ignored)
    it should expose the die roll that was used
      -> expect(check.die_roll).to(equal(8))
    it should report whether the total met the difficulty
      -> expect(result.succeeded).to(be_true)
    it should report the total of the outcome
      -> expect(result.total).to(equal(13))
    it should report the degree of the outcome
      -> expect(result.degree).to(equal(1))
  that is resolved as routine
    -> trait = SimpleNamespace(rank=5)
    -> dc = SimpleNamespace(target=10)
    -> check = Check(trait, dc)                    # dice unused when routine
    -> result = check.resolve([], routine=True)
    -> // die treated as 10; total = 10+5 = 15; succeed 1°
    it should treat the die as ten
      -> expect(check.die_roll).to(equal(10))
      -> // total/succeeded covered under no-modifiers; routine only proves die override
  that rolls a natural twenty
    -> stub_dice = SimpleNamespace(roll=lambda: 20)
    -> trait = SimpleNamespace(rank=0)
    -> dc = SimpleNamespace(target=21)
    -> // total 20 < 21 → fail 1°; crit +1° → succeeded with degree 1
    -> check = Check(trait, dc, dice=stub_dice)
    -> result = check.resolve([])
    it should gain one degree of success
      -> expect(check.die_roll).to(equal(20))
      -> expect(result.degree).to(equal(1))
    it should succeed when the critical flips a near miss into a hit
      -> expect(result.succeeded).to(be_true)
  with modifiers that raise the total
    -> trait = SimpleNamespace(rank=5)
    -> dc = SimpleNamespace(target=15)
    -> stub_dice = SimpleNamespace(roll=lambda: 10)
    -> mod = SimpleNamespace(amount=5, reason="circumstance")
    -> check = Check(trait, dc, dice=stub_dice)
    -> result = check.resolve([mod])
    -> // total = 10+5+5 = 20; DC 15 → succeed 1°
    it should include the modifier amounts in the total
      -> expect(result.total).to(equal(20))
      -> expect(check.die_roll).to(equal(10))
      -> expect(result.succeeded).to(be_true)
